#!/usr/bin/env python3
"""Batching Arena — static vs continuous batching vs chunked prefill, simulated head-to-head.

Zero install: Python 3.10+ standard library only. No GPU, no PyTorch.

    python academy/labs/batching_arena.py                 # the race (same workload, three schedulers)
    python academy/labs/batching_arena.py --roofline      # why decode is memory-bound (E05)
    python academy/labs/batching_arena.py --chunk 512     # chunked prefill with a 512-token step budget
    python academy/labs/batching_arena.py --chunk 0       # ...and with chunking off: watch the stall

The cost model is a roofline: each engine step takes
    overhead + max(bytes_moved / bandwidth, flops / peak_flops)
for an 8B BF16 model on an H100-class GPU. It ignores attention FLOPs, kernel details and
CUDA graphs, so absolute numbers are illustrative. The *shape* of the results (who wins,
and why) is what transfers to real vLLM. Compare with real measurements in Q7.
"""
from __future__ import annotations

import argparse
import math
import random
from dataclasses import dataclass, field

try:
    from _term import PALETTE, bar, c, rule, set_color
except ImportError:
    from ._term import PALETTE, bar, c, rule, set_color


# --------------------------------------------------------------------------- hardware + model
@dataclass(frozen=True)
class Hardware:
    name: str = "H100-SXM-80G (approx.)"
    bandwidth: float = 3.35e12  # bytes/s, HBM3
    peak_flops: float = 989e12  # dense BF16
    bw_eff: float = 0.80
    flops_eff: float = 0.65
    mem_gib: float = 80.0
    step_overhead_s: float = 0.0015  # scheduling + launch overhead per step


@dataclass(frozen=True)
class Model:
    name: str = "Llama-3.1-8B (BF16)"
    params: float = 8.03e9
    bytes_per_param: float = 2.0
    kv_bytes_per_token: float = 2 * 32 * 8 * 128 * 2  # 128 KiB

    @property
    def weight_bytes(self) -> float:
        return self.params * self.bytes_per_param


HW, MODEL = Hardware(), Model()


def step_time(prefill_tokens: int, decode_seqs: int, decode_ctx_tokens: int, hw: Hardware = HW,
              m: Model = MODEL) -> tuple[float, str]:
    """Seconds for one engine step, and which roof bounds it ('memory' or 'compute')."""
    tokens = prefill_tokens + decode_seqs
    if tokens == 0:
        return 0.0, "idle"
    bytes_moved = m.weight_bytes + decode_ctx_tokens * m.kv_bytes_per_token  # weights once + KV reads
    flops = 2 * m.params * tokens
    t_mem = bytes_moved / (hw.bandwidth * hw.bw_eff)
    t_cmp = flops / (hw.peak_flops * hw.flops_eff)
    return hw.step_overhead_s + max(t_mem, t_cmp), ("memory" if t_mem >= t_cmp else "compute")


# --------------------------------------------------------------------------- roofline table
def roofline(context: int = 1024, out=print) -> list[dict]:
    out(rule(f"Roofline: decode-only steps, {MODEL.name}, {context}-token contexts, {HW.name}"))
    kv_room = HW.mem_gib * 1024**3 * 0.9 - MODEL.weight_bytes
    max_fit = int(kv_room // (context * MODEL.kv_bytes_per_token))
    out(f"   {'batch':>6} {'step ms':>8} {'total tok/s':>12} {'per-user tok/s':>15}  bound     tokens/s")
    rows = []
    best = 0.0
    sizes = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    for b in sizes:
        t, bound = step_time(0, b, b * context)
        rows.append({"batch": b, "ms": t * 1e3, "tps": b / t, "per_user": 1 / t, "bound": bound, "fits": b <= max_fit})
        best = max(best, b / t)
    for r in rows:
        fits = "" if r["fits"] else c("  ✗ KV doesn't fit", "bred")
        style = "bcyan" if r["bound"] == "memory" else "bmagenta"
        out(f"   {r['batch']:>6} {r['ms']:>8.1f} {r['tps']:>12,.0f} {r['per_user']:>15.1f}  "
            f"{c(f'{r['bound']:<8}', style)}  {bar(r['tps'] / best, 24, style=style)}{fits}")
    ridge = HW.peak_flops * HW.flops_eff / (HW.bandwidth * HW.bw_eff)
    out("")
    out(f"   Weights: {MODEL.weight_bytes / 1e9:.0f} GB read every step · ridge point ≈ {ridge:.0f} FLOPs/byte · "
        f"max sequences that fit at {context} ctx ≈ {max_fit}")
    out(c("   → Batch 1 → 8 costs almost nothing extra per step: the GPU was waiting on memory anyway.", "bold"))
    out(c("   → But KV reads grow with batch × context, so long-context decode stays memory-bound. "
          "Bigger batches trade per-user speed for total throughput.", "bold"))
    return rows


# --------------------------------------------------------------------------- workload
@dataclass
class Req:
    rid: int
    arrival: float
    prompt: int
    output: int
    whale: bool = False
    prefilled: int = 0
    generated: int = 0
    start: float | None = None  # first scheduled
    token_times: list[float] = field(default_factory=list)
    done: float | None = None

    @property
    def ttft(self) -> float:
        return self.token_times[0] - self.arrival

    @property
    def itls(self) -> list[float]:
        return [b - a for a, b in zip(self.token_times, self.token_times[1:])]


def make_workload(n: int = 24, seed: int = 7, whale: bool = True, whale_tokens: int = 16000) -> list[Req]:
    rng = random.Random(seed)
    reqs, t = [], 0.0
    for i in range(n):
        t += rng.expovariate(12.0)  # ~12 requests/s
        reqs.append(Req(i, round(t, 4), rng.randint(200, 1500), rng.randint(60, 400)))
    if whale:
        reqs.append(Req(n, 0.8, whale_tokens, 50, whale=True))
    reqs.sort(key=lambda r: (r.arrival, r.rid))
    return reqs


def _clone(reqs: list[Req]) -> list[Req]:
    return [Req(r.rid, r.arrival, r.prompt, r.output, r.whale) for r in reqs]


# --------------------------------------------------------------------------- schedulers
def simulate(policy: str, reqs: list[Req], *, batch: int = 8, max_seqs: int = 64, chunk: int = 512) -> dict:
    """policy: static | continuous | chunked. Returns metrics and a per-step trace."""
    reqs = _clone(reqs)
    pending = list(reqs)  # sorted by arrival
    waiting: list[Req] = []
    running: list[Req] = []
    now = 0.0
    steps: list[dict] = []
    static_batch: list[Req] = []
    while pending or waiting or running or static_batch:
        while pending and pending[0].arrival <= now + 1e-12:
            waiting.append(pending.pop(0))
        if not waiting and not running and not static_batch:
            now = pending[0].arrival
            continue
        prefill_plan: list[tuple[Req, int]] = []
        decoders: list[Req] = []
        if policy == "static":
            if not static_batch:
                static_batch = waiting[:batch]
                del waiting[:batch]
                for r in static_batch:
                    r.start = now
                    prefill_plan.append((r, r.prompt))
            else:
                decoders = [r for r in static_batch if r.generated < r.output]
            slots = len(static_batch)  # finished requests still occupy their slot (padding)
        else:
            decoders = [r for r in running if r.prefilled == r.prompt and r.generated < r.output]
            budget = math.inf if (policy == "continuous" or chunk <= 0) else chunk
            budget -= len(decoders)
            # continue partial prefills first, then admit new requests (FCFS)
            for r in [r for r in running if r.prefilled < r.prompt] + list(waiting):
                if budget <= 0:
                    break
                if r in waiting:
                    if len(running) >= max_seqs:
                        break
                    waiting.remove(r)
                    running.append(r)
                    r.start = now
                take = int(min(r.prompt - r.prefilled, budget))
                prefill_plan.append((r, take))
                budget -= take
            slots = len(decoders)
        prefill_tokens = sum(n for _, n in prefill_plan)
        ctx = sum(r.prompt + r.generated for r in decoders)
        if policy == "static":
            decode_seqs, ctx = (slots, sum(r.prompt + r.generated for r in static_batch)) if decoders else (0, 0)
        else:
            decode_seqs = len(decoders)
        dt, bound = step_time(prefill_tokens, decode_seqs, ctx)
        now += dt
        for r, n in prefill_plan:
            r.prefilled += n
            if r.prefilled == r.prompt:  # prefill done → first token
                r.generated += 1
                r.token_times.append(now)
        for r in decoders:
            r.generated += 1
            r.token_times.append(now)
        steps.append({"t": now, "dt": dt, "prefill": prefill_tokens, "decode": len(decoders), "bound": bound})
        for r in (static_batch if policy == "static" else running):
            if r.generated >= r.output and r.done is None:
                r.done = now
        if policy == "static":
            if all(r.done is not None for r in static_batch):
                static_batch = []
        else:
            running = [r for r in running if r.done is None]
    return {"policy": policy, "reqs": reqs, "steps": steps, **metrics(reqs, steps)}


def pct(xs: list[float], p: float) -> float:
    if not xs:
        return 0.0
    xs = sorted(xs)
    k = (len(xs) - 1) * p / 100
    lo, hi = math.floor(k), math.ceil(k)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def metrics(reqs: list[Req], steps: list[dict]) -> dict:
    normal = [r for r in reqs if not r.whale]
    itls = [x for r in normal for x in r.itls]
    makespan = max(r.done for r in reqs) - min(r.arrival for r in reqs)
    out_tokens = sum(r.output for r in reqs)
    return {
        "makespan": makespan,
        "throughput": out_tokens / makespan,
        "ttft_p50": pct([r.ttft for r in normal], 50),
        "ttft_p99": pct([r.ttft for r in normal], 99),
        "itl_p50": pct(itls, 50),
        "itl_p99": pct(itls, 99),
        "itl_max": max(itls) if itls else 0.0,
    }


# --------------------------------------------------------------------------- views
def timeline(res: dict, width: int = 64, rows: int = 10, t_end: float | None = None) -> list[str]:
    reqs = sorted(res["reqs"], key=lambda r: (not r.whale, r.rid))[:rows]
    reqs.sort(key=lambda r: r.arrival)
    t_end = t_end or max(r.done for r in res["reqs"])
    lines = []
    for i, r in enumerate(reqs):
        color = "bred" if r.whale else PALETTE[i % len(PALETTE)]
        cells = []
        for k in range(width):
            t = (k + 0.5) * t_end / width
            if t < r.arrival or (r.done is not None and t > r.done):
                cells.append(" ")
            elif r.start is None or t < r.start:
                cells.append(c("·", "gray"))
            elif not r.token_times or t < r.token_times[0]:
                cells.append(c("▒", color))
            else:
                cells.append(c("█", color))
        name = "🐋 whale" if r.whale else f"req {r.rid:>2}"
        lines.append(f"   {name:>8} │{''.join(cells)}│")
    lines.append(f"   {'':>8}  0s{' ' * (width - 8)}{t_end:5.1f}s")
    return lines


def stall_chart(res: dict, width: int = 64, t_end: float | None = None, top: float | None = None) -> str:
    """Sparkline of the decode inter-token gap (step time while someone was decoding)."""
    marks = "▁▂▃▄▅▆▇█"
    t_end = t_end or res["steps"][-1]["t"]
    cols = [0.0] * width
    for s in res["steps"]:
        if s["decode"]:
            k = min(width - 1, int(s["t"] / t_end * width))
            cols[k] = max(cols[k], s["dt"])
    worst = max(cols)
    top = top or worst or 1.0
    spark = "".join(c(marks[min(7, int(v / top * 7.999))], "bred" if v > 0.1 else "bcyan") if v else " " for v in cols)
    return f"   decode gap │{spark}│ worst {worst * 1e3:.0f} ms"


LABEL = {"static": "Static batching (batch=8)", "continuous": "Continuous batching",
         "chunked": "Continuous + chunked prefill"}


def race(args, out=print) -> dict:
    wl = make_workload(args.requests, args.seed, whale=not args.no_whale)
    out(rule(f"Batching Arena · {len(wl)} requests · {MODEL.name} on {HW.name}"))
    out(f"   Workload: {args.requests} chats (200–1500-token prompts, 60–400-token answers, ~12 req/s)"
        + ("" if args.no_whale else " + 🐋 one 16,000-token paste arriving at t=0.8 s"))
    policies = ["static", "continuous", "chunked"]
    results = {p: simulate(p, wl, batch=args.batch, chunk=args.chunk) for p in policies}
    t_end = max(r["makespan"] for r in results.values()) + min(r.arrival for r in wl)
    top = max(s["dt"] for r in results.values() for s in r["steps"] if s["decode"])
    for p in policies:
        res = results[p]
        title = LABEL[p] + (f" ({args.chunk}-token budget)" if p == "chunked" and args.chunk > 0 else "")
        if p == "chunked" and args.chunk <= 0:
            title = LABEL[p] + " (chunk=0 → OFF, same as continuous)"
        out("")
        out(c(f" ▶ {title}", "bold"))
        for line in timeline(res, t_end=t_end):
            out(line)
        out(stall_chart(res, t_end=t_end, top=top))
    out("")
    out(rule("Scoreboard (normal requests; lower is better except throughput)"))
    out(f"   {'scheduler':<34} {'tok/s':>7} {'TTFT p50':>9} {'TTFT p99':>9} {'ITL p50':>8} {'ITL p99':>8} {'worst gap':>10}")
    best_tps = max(r["throughput"] for r in results.values())
    for p in policies:
        r = results[p]
        name = LABEL[p]
        tps = f"{r['throughput']:>7.0f}"
        out(f"   {name:<34} {c(tps, 'bgreen', 'bold') if r['throughput'] == best_tps else tps} "
            f"{r['ttft_p50']:>8.2f}s {r['ttft_p99']:>8.2f}s {r['itl_p50'] * 1e3:>6.0f}ms {r['itl_p99'] * 1e3:>6.0f}ms "
            f"{r['itl_max'] * 1e3:>8.0f}ms")
    out("")
    out("   Legend: · waiting   ▒ prefill   █ decoding   🐋 = the 16k-token paste")
    out(c("   → Static batching makes everyone wait for the slowest request in the batch.", "bold"))
    out(c("   → Continuous batching admits and retires requests every step: same GPU, far more throughput.", "bold"))
    out(c("   → Without chunking, the whale's prefill runs as one giant step and every decoding user freezes. "
          "Chunked prefill caps each step's tokens, so the freeze becomes a few slightly slower steps "
          "(at the cost of a little TTFT).", "bold"))
    return results


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--roofline", action="store_true", help="print the decode roofline table and exit")
    p.add_argument("--context", type=int, default=1024, help="context length for --roofline")
    p.add_argument("--chunk", type=int, default=512, help="token budget per step for chunked prefill (0 = off)")
    p.add_argument("--batch", type=int, default=8, help="static batch size")
    p.add_argument("--requests", type=int, default=24)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--no-whale", action="store_true", help="drop the 16k-token request")
    p.add_argument("--no-color", action="store_true")
    a = p.parse_args(argv)
    if a.no_color:
        set_color(False)
    if a.roofline:
        roofline(a.context)
    else:
        race(a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
