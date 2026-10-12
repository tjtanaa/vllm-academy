"""The zero-install labs promise exact numbers in their checkpoints. Keep them honest."""
import batching_arena as ba
import kv_budget
import paged_playground as pp

quiet = lambda *_: None  # noqa: E731


def test_paged_basic():
    r = pp.run("basic", out=quiet)
    assert (r["tokens"], r["paged_slots"], r["contiguous_slots"]) == (22, 24, 64)
    assert pp.run("basic", block_size=16, out=quiet)["paged_slots"] == 32


def test_paged_prefix_and_break():
    assert pp.run("prefix", out=quiet)["hit_tokens"] == 24
    broken = pp.run("prefix", out=quiet, break_prefix=True)
    assert broken["hit_tokens"] == 0 and broken["computed_tokens"] == 54


def test_paged_offload():
    r = pp.run("offload", out=quiet)
    assert r["offloaded"] == 6 and r["loaded_tokens"] == 12


def test_paged_agent():
    r = pp.run("agent", out=quiet)
    assert (r["computed_on"], r["computed_off"]) == (74, 214)
    assert r["rows_on"][3]["computed"] == 9 and r["rows_off"][3]["computed"] == 73


def test_refcounts_return_to_zero():
    kv = pp.PagedKV(16, 4, out=quiet)
    kv.add("A", pp.SYSTEM + ["x"])
    kv.add("B", pp.SYSTEM + ["y"])
    kv.finish("A")
    kv.finish("B")
    assert all(b.ref == 0 for b in kv.blocks) and len(kv.free) == 16


def test_roofline_shape():
    rows = ba.roofline(out=quiet)
    assert abs(rows[0]["ms"] - 7.5) < 0.1 and rows[3]["ms"] < 8.0
    assert all(r["bound"] == "memory" for r in rows)


def test_race_numbers():
    import argparse
    res = ba.race(argparse.Namespace(requests=24, seed=7, no_whale=False, batch=8, chunk=512), out=quiet)
    st, co, ch = res["static"], res["continuous"], res["chunked"]
    assert round(st["throughput"]) == 468 and round(co["throughput"]) == 1192
    assert round(co["itl_max"] * 1e3) == 401 and round(ch["itl_max"] * 1e3) == 14
    assert co["throughput"] > 2 * st["throughput"]
    # every request gets exactly its output tokens under every policy
    for r in res.values():
        assert all(len(q.token_times) == q.output for q in r["reqs"])


def test_kv_budget_cli(capsys):
    assert kv_budget.main(["--model", "llama-3.1-70b", "--context", "131072", "--gpus", "4", "--no-color"]) == 0
    out = capsys.readouterr().out
    assert "40.0 GiB" in out and "4 sequences" in out
