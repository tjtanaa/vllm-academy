#!/usr/bin/env python3
"""KV Budget — the memory math interviewers love (episode E07), shown step by step.

Zero install: Python 3.10+ standard library only.

    python academy/labs/kv_budget.py --model llama-3.1-70b --context 131072 --gpus 4 --gpu-mem 80
    python academy/labs/kv_budget.py --model llama-3.1-8b --context 8192 --gpu H100 --compare
    python academy/labs/kv_budget.py --list
    python academy/labs/kv_budget.py --layers 40 --kv-heads 8 --head-dim 128 --params 14 --context 32768

The model presets and formulas are shared with the Discord bot's /kvcalc
(discord_bot/academy_bot/kvcalc.py), so both always give the same answer.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

try:
    from _term import bar, c, rule, set_color
except ImportError:
    from ._term import bar, c, rule, set_color

_KVCALC = Path(__file__).resolve().parents[2] / "discord_bot" / "academy_bot" / "kvcalc.py"


def _load_kvcalc():
    spec = importlib.util.spec_from_file_location("academy_kvcalc", _KVCALC)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclasses need the module registered
    spec.loader.exec_module(mod)
    return mod


kv = _load_kvcalc()


def explain(res, out=print) -> None:
    m = res.model
    hb = kv.human_bytes
    out(rule(f"KV budget · {m.name} · {res.context:,} tokens · {res.users} sequence(s)"))
    out(c(" Step 1 · KV bytes per token", "bold"))
    if m.attention == "mla":
        out(f"   MLA stores one compressed latent + a RoPE key per layer (no separate K and V):")
    else:
        if m.attention == "mha":
            kind = "MHA: every query head has its own KV head"
        elif m.query_heads:
            kind = f"GQA: {m.query_heads} query heads share {m.kv_heads} KV heads"
        else:
            kind = f"{m.kv_heads} KV heads per layer"
        out(f"   {kind}. ×2 because we store both K and V.")
    out(f"   {res.formula} = {c(hb(res.kv_per_token), 'byellow', 'bold')} per token")
    out(c(" Step 2 · per sequence", "bold"))
    out(f"   {hb(res.kv_per_token)} × {res.context:,} tokens = {c(hb(res.kv_per_seq), 'byellow', 'bold')}")
    out(c(" Step 3 · weights", "bold"))
    out(f"   {m.params_b:g}B params × {kv.DTYPES[res.weight_dtype]:g} B ({res.weight_dtype}) = {hb(res.weights)}")
    out(c(" Step 4 · what's left for KV", "bold"))
    out(f"   {res.gpus} GPU(s) × {res.gpu_mem_gib:g} GiB × {res.util:.0%} usable = {hb(res.budget)}; "
        f"minus weights = {c(hb(max(0, res.kv_room)), 'bgreen' if res.kv_room > 0 else 'bred', 'bold')}")
    out(c(" Step 5 · how many full-length sequences fit", "bold"))
    if not res.weights_fit:
        out(c("   ❌ The weights alone don't fit. Add GPUs (tensor parallel) or quantize the weights.", "bred", "bold"))
    else:
        out(f"   {hb(res.kv_room)} ÷ {hb(res.kv_per_seq)} = {c(str(res.max_seqs), 'bgreen', 'bold')} sequences")
        verdict = "✅ fits" if res.fits else "❌ does NOT fit"
        out(f"   You asked for {res.users}: {c(verdict, 'bgreen' if res.fits else 'bred', 'bold')}")
    total = res.budget
    w = min(1.0, res.weights / total) if total else 0
    k = min(1.0 - w, res.kv_total / total) if total else 0
    width = 48
    nw, nk = round(w * width), round(k * width)
    out("")
    out("   memory │" + c("█" * nw, "bmagenta") + c("█" * nk, "byellow") + c("·" * max(0, width - nw - nk), "gray")
        + f"│  {c('■ weights', 'bmagenta')} {c('■ KV', 'byellow')} {c('· free', 'gray')}")
    out(c("   Real capacity is lower: activations, CUDA graphs and fragmentation take a few GiB. "
          "Trust the 'GPU KV cache size' line in vLLM's startup log.", "dim"))


def compare(model, context: int, gpus: int, gpu_mem: float, out=print) -> None:
    out(rule(f"Same {model.name}, same {gpus}×{gpu_mem:g} GiB: how the KV dtype changes capacity"))
    base = None
    for dtype in ("bf16", "fp8", "fp4"):
        r = kv.compute(model, context=context, gpus=gpus, gpu_mem_gib=gpu_mem, kv_dtype=dtype)
        base = base or max(1, r.max_seqs)
        out(f"   KV {dtype:<5} {kv.human_bytes(r.kv_per_seq):>10}/seq  → {r.max_seqs:>5} sequences  "
            f"{bar(r.max_seqs / (base * 4.2), 28, style='byellow')} {r.max_seqs / base:.1f}×")
    out(c("   → Halving KV bytes roughly doubles concurrency. Check quality on YOUR task before shipping FP8/FP4 KV.", "bold"))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="llama-3.1-8b", help="preset name (see --list)")
    p.add_argument("--context", type=int, default=8192)
    p.add_argument("--users", type=int, default=1, help="concurrent full-length sequences you want")
    p.add_argument("--gpus", type=int, default=1)
    p.add_argument("--gpu", help="GPU preset, e.g. H100, A100-80G, MI300X, RTX-4090 (sets --gpu-mem)")
    p.add_argument("--gpu-mem", type=float, default=80.0, help="GiB per GPU")
    p.add_argument("--kv-dtype", default="bf16", choices=sorted(kv.DTYPES))
    p.add_argument("--weight-dtype", default="bf16", choices=sorted(kv.DTYPES))
    p.add_argument("--util", type=float, default=0.92, help="fraction of GPU memory for weights + KV")
    p.add_argument("--compare", action="store_true", help="compare BF16 / FP8 / FP4 KV capacity")
    p.add_argument("--list", action="store_true", help="list model and GPU presets")
    g = p.add_argument_group("custom model (instead of --model)")
    g.add_argument("--layers", type=int)
    g.add_argument("--kv-heads", type=int)
    g.add_argument("--head-dim", type=int)
    g.add_argument("--params", type=float, default=0.0, help="billions of parameters")
    p.add_argument("--no-color", action="store_true")
    a = p.parse_args(argv)
    if a.no_color:
        set_color(False)
    if a.list:
        print(rule("Model presets"))
        for m in kv.MODELS.values():
            print(f"   {m.name:<18} {m.attention.upper():<4} layers={m.layers:<4} kv_heads={m.kv_heads:<3} "
                  f"head_dim={m.head_dim:<4} params={m.params_b:g}B  KV/token={kv.human_bytes(m.kv_bytes_per_token(2))}")
        print(rule("GPU presets (usable GiB)"))
        for name, mem in kv.GPUS.items():
            print(f"   {name:<16} {mem:g}")
        return 0
    if a.layers:
        if not (a.kv_heads and a.head_dim):
            p.error("a custom model needs --layers, --kv-heads and --head-dim")
        model = kv.ModelSpec("custom", layers=a.layers, kv_heads=a.kv_heads, head_dim=a.head_dim, params_b=a.params)
    else:
        model = kv.find_model(a.model)
        if model is None:
            p.error(f"unknown model {a.model!r}; try --list")
    gpu_mem = a.gpu_mem
    if a.gpu:
        found = kv.find_gpu(a.gpu)
        if not found:
            p.error(f"unknown GPU {a.gpu!r}; try --list")
        gpu_mem = found[1]
    try:
        res = kv.compute(model, context=a.context, users=a.users, kv_dtype=a.kv_dtype, weight_dtype=a.weight_dtype,
                         gpus=a.gpus, gpu_mem_gib=gpu_mem, util=a.util)
    except ValueError as exc:
        p.error(str(exc))
    explain(res)
    if a.compare:
        print()
        compare(model, a.context, a.gpus, gpu_mem)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
