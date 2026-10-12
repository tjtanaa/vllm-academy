#!/usr/bin/env python3
"""Paged Playground — watch a paged KV cache work, one event at a time.

Zero install: Python 3.10+ standard library only. No GPU, no PyTorch.

    python academy/labs/paged_playground.py                      # basic: pages vs contiguous
    python academy/labs/paged_playground.py --scenario prefix    # two chats share a system prompt
    python academy/labs/paged_playground.py --scenario offload   # GPU full -> spill to CPU -> load back
    python academy/labs/paged_playground.py --scenario agent     # 4-turn agent session, offload on vs off

This is a teaching model of the ideas in vLLM's KV cache manager (block pool, block
tables, reference counts, chained prefix hashes, LRU free queue, CPU offload tier).
It mirrors the *concepts*, not vLLM's exact code or numbers. Real vLLM uses 16-token
blocks and thousands of them; we use 4-token blocks so you can see every slot.
"""
from __future__ import annotations

import argparse
import hashlib
from collections import OrderedDict
from dataclasses import dataclass, field

try:  # running as `python academy/labs/paged_playground.py`
    from _term import PALETTE, c, default_delay, pause, rule, set_color
except ImportError:  # imported as academy.labs.paged_playground
    from ._term import PALETTE, c, default_delay, pause, rule, set_color


# --------------------------------------------------------------------------- model
@dataclass
class Block:
    id: int
    ref: int = 0
    hash: str | None = None
    owner: str | None = None  # request that first filled it (for coloring)
    tokens: list[str] = field(default_factory=list)


@dataclass
class Request:
    rid: str
    tokens: list[str]
    table: list[int] = field(default_factory=list)
    color: str = "bcyan"


@dataclass
class Stats:
    hit_tokens: int = 0
    loaded_tokens: int = 0
    computed_tokens: int = 0
    offloaded_blocks: int = 0
    evicted_blocks: int = 0


def block_hash(parent: str | None, tokens: list[str]) -> str:
    """Chained hash: a block's identity includes everything before it (like vLLM's prefix hashes)."""
    h = hashlib.sha256(((parent or "root") + "|" + " ".join(tokens)).encode()).hexdigest()
    return h[:8]


class PagedKV:
    def __init__(self, gpu_blocks: int, block_size: int, cpu_blocks: int = 0, out=print, delay: float = 0.0):
        self.bs = block_size
        self.blocks = [Block(i) for i in range(gpu_blocks)]
        self.free: OrderedDict[int, None] = OrderedDict((i, None) for i in range(gpu_blocks))  # LRU: evict from front
        self.cached: dict[str, int] = {}  # hash -> gpu block id
        self.cpu: OrderedDict[str, list[str]] = OrderedDict()  # hash -> tokens (offload tier)
        self.cpu_capacity = cpu_blocks
        self.reqs: dict[str, Request] = {}
        self.stats = Stats()
        self.out = out
        self.delay = delay
        self.quiet_evictions = False
        self._colors = iter(PALETTE * 4)

    # ---- low-level allocator
    def _take_free_block(self) -> Block:
        if not self.free:
            raise MemoryError("out of KV blocks")
        bid, _ = self.free.popitem(last=False)  # least recently used first
        b = self.blocks[bid]
        if b.hash is not None:  # evicting a cached-but-unused block
            self.stats.evicted_blocks += 1
            say = (lambda *_: None) if self.quiet_evictions else self.say
            self.cached.pop(b.hash, None)
            if self.cpu_capacity:
                self.cpu[b.hash] = list(b.tokens)
                self.cpu.move_to_end(b.hash)
                while len(self.cpu) > self.cpu_capacity:
                    self.cpu.popitem(last=False)
                self.stats.offloaded_blocks += 1
                say(f"   ↘ evict block #{bid} ({c(' '.join(b.tokens), 'dim')}) → {c('offloaded to CPU', 'bblue')}")
            else:
                say(f"   ✗ evict block #{bid} ({c(' '.join(b.tokens), 'dim')}) → {c('gone (would recompute)', 'bred')}")
        b.ref, b.hash, b.owner, b.tokens = 0, None, None, []
        return b

    def _register_if_full(self, req: Request, idx: int) -> None:
        b = self.blocks[req.table[idx]]
        if len(b.tokens) == self.bs and b.hash is None:
            parent = self.blocks[req.table[idx - 1]].hash if idx > 0 else None
            b.hash = block_hash(parent, b.tokens)
            self.cached.setdefault(b.hash, b.id)

    # ---- public API
    def add(self, rid: str, tokens: list[str]) -> Request:
        req = Request(rid, [], color=next(self._colors))
        self.reqs[rid] = req
        n_full = len(tokens) // self.bs
        parent = None
        i = 0
        hit = loaded = 0
        # 1) walk full prompt blocks while they're cached on GPU (or CPU)
        while i < n_full:
            chunk = tokens[i * self.bs:(i + 1) * self.bs]
            h = block_hash(parent, chunk)
            if h in self.cached:
                b = self.blocks[self.cached[h]]
                if b.ref == 0:
                    self.free.pop(b.id, None)
                b.ref += 1
                req.table.append(b.id)
                hit += 1
            elif h in self.cpu:
                b = self._take_free_block()
                b.tokens, b.hash, b.ref, b.owner = list(chunk), h, 1, rid
                self.cached[h] = b.id
                self.cpu.move_to_end(h)
                req.table.append(b.id)
                loaded += 1
            else:
                break
            req.tokens += chunk
            parent = h
            i += 1
        self.stats.hit_tokens += hit * self.bs
        self.stats.loaded_tokens += loaded * self.bs
        # 2) compute the rest (prefill)
        rest = tokens[i * self.bs:]
        for tok in rest:
            self.append(rid, tok, quiet=True)
        self.stats.computed_tokens += len(rest)
        parts = []
        if hit:
            parts.append(c(f"{hit} block(s) HIT on GPU", "bgreen", "bold"))
        if loaded:
            parts.append(c(f"{loaded} block(s) LOADED from CPU", "bblue", "bold"))
        parts.append(f"{len(rest)} token(s) computed")
        self.say(f"➕ {c(rid, req.color, 'bold')} arrives with {len(tokens)} prompt tokens: " + ", ".join(parts))
        return req

    def append(self, rid: str, token: str, quiet: bool = False) -> None:
        req = self.reqs[rid]
        if not req.table or len(self.blocks[req.table[-1]].tokens) == self.bs:
            b = self._take_free_block()
            b.ref, b.owner = 1, rid
            req.table.append(b.id)
        last = self.blocks[req.table[-1]]
        if last.ref > 1:  # never write into a shared block: copy-on-write
            nb = self._take_free_block()
            nb.ref, nb.owner, nb.tokens = 1, rid, list(last.tokens)
            last.ref -= 1
            req.table[-1] = nb.id
            last = nb
        last.tokens.append(token)
        req.tokens.append(token)
        self._register_if_full(req, len(req.table) - 1)
        if not quiet:
            self.say(f"✏️  {c(rid, req.color, 'bold')} decodes {c(repr(token), req.color)}")

    def finish(self, rid: str) -> None:
        req = self.reqs.pop(rid)
        # free in reverse so the *tail* of a sequence is evicted before its shared prefix
        for bid in reversed(req.table):
            b = self.blocks[bid]
            b.ref -= 1
            if b.ref == 0:
                if b.hash is None:  # partial block: nothing reusable, wipe it
                    b.tokens, b.owner = [], None
                self.free[bid] = None
        self.say(f"🏁 {c(rid, req.color, 'bold')} finishes. Its full blocks stay {c('cached', 'dim')} until evicted.")

    # ---- views
    def say(self, line: str) -> None:
        self.out(line)

    def grid(self) -> str:
        cells = []
        color_of = {r.rid: r.color for r in self.reqs.values()}
        for b in self.blocks:
            if b.ref > 0:
                tag = (b.owner or "?")[:1] + (str(b.ref) if b.ref > 1 else " ")
                style = color_of.get(b.owner, "white")
                cells.append(c(f"[{tag}]", style, "bold" if b.ref > 1 else "reset"))
            elif b.hash is not None:
                cells.append(c("[c ]", "gray"))
            else:
                cells.append(c("[  ]", "gray"))
        rows = [" ".join(cells[i:i + 8]) for i in range(0, len(cells), 8)]
        return "\n".join("   GPU " + r if k == 0 else "       " + r for k, r in enumerate(rows))

    def tables(self) -> str:
        lines = []
        for r in self.reqs.values():
            last_fill = len(self.blocks[r.table[-1]].tokens) if r.table else 0
            lines.append(f"   {c(r.rid, r.color, 'bold')} block table → {r.table}  "
                         f"({len(r.tokens)} tokens, last block {last_fill}/{self.bs} full)")
        if self.cpu_capacity:
            lines.append(f"   CPU tier: {len(self.cpu)}/{self.cpu_capacity} blocks")
        return "\n".join(lines) if lines else "   (no running requests)"

    def show(self, title: str = "") -> None:
        if title:
            self.say(c(f"   ── {title}", "gray"))
        self.say(self.grid())
        self.say(self.tables())
        self.say("")
        pause(self.delay)


def words(text: str) -> list[str]:
    return text.split()


LEGEND = (f"   Legend: {c('[A ]', 'bcyan')} block owned by A · {c('[A2]', 'bold')} shared by 2 requests · "
          f"{c('[c ]', 'gray')} cached, free to reuse · {c('[  ]', 'gray')} empty")


# --------------------------------------------------------------------------- scenarios
def scenario_basic(kv: PagedKV, max_model_len: int = 32) -> dict:
    kv.say(rule("Scenario: basic — pages instead of one big reservation"))
    kv.say(LEGEND)
    kv.add("A", words("Explain PagedAttention in one short sentence please"))
    kv.show("A's prompt is split into 4-token blocks; physical blocks need not be adjacent")
    kv.add("B", words("什麼 是 KV cache ?"))
    kv.show("B gets whatever blocks are free")
    for tok_a, tok_b in zip(words("It pages the KV cache like virtual memory"), words("它 是 注意力 的 記憶")):
        kv.append("A", tok_a)
        kv.append("B", tok_b)
    kv.show("Both decoded 5 tokens; a new block is grabbed only when the last one fills")
    used_tokens = sum(len(r.tokens) for r in kv.reqs.values())
    paged_slots = sum(len(r.table) for r in kv.reqs.values()) * kv.bs
    contiguous_slots = len(kv.reqs) * max_model_len
    kv.finish("A")
    kv.show("A finished: its blocks are free again")
    res = {"tokens": used_tokens, "paged_slots": paged_slots, "contiguous_slots": contiguous_slots}
    kv.say(rule("Result"))
    kv.say(f"   Tokens actually stored ........ {used_tokens}")
    kv.say(f"   Paged slots allocated ......... {paged_slots}  "
           f"(waste {100 * (paged_slots - used_tokens) / paged_slots:.0f}%: at most one partly-filled block per request)")
    kv.say(f"   Contiguous, reserve {max_model_len}/request {contiguous_slots}  "
           f"(waste {100 * (contiguous_slots - used_tokens) / contiguous_slots:.0f}%)")
    kv.say(c("   → This is the PagedAttention insight: allocate KV in small pages on demand, "
             "so memory waste is tiny and more requests fit.", "bold"))
    return res


SYSTEM = words("You are a friendly vLLM tutor . Answer in English or 中文 .")  # 12 tokens = 3 blocks


def scenario_prefix(kv: PagedKV, break_prefix: bool = False) -> dict:
    kv.say(rule("Scenario: prefix — two chats share one system prompt"))
    kv.say(LEGEND)
    stamp = (lambda t: [f"[{t}]"]) if break_prefix else (lambda t: [])
    kv.add("A", stamp("12:00:01") + SYSTEM + words("What is a token ?"))
    kv.show("A computed everything; its 3 system-prompt blocks are now hashed and cached")
    kv.add("B", stamp("12:00:02") + SYSTEM + words("什麼 是 batching ?"))
    if break_prefix:
        kv.show("B's prompt starts with a different timestamp, so its FIRST block hash differs and nothing matches")
    else:
        kv.show("B matched A's 3 blocks by hash: shared, ref count 2, zero recompute")
    kv.append("A", "A")
    kv.append("B", "它")
    kv.finish("A")
    kv.show("A finished: the shared blocks survive because B still references them")
    kv.finish("B")
    kv.add("C", stamp("12:00:03") + SYSTEM + words("Explain prefix caching"))
    kv.show("C arrives after everyone left: the cached blocks are still there and get reused")
    s = kv.stats
    kv.say(rule("Result"))
    kv.say(f"   Prompt tokens reused from cache ... {c(str(s.hit_tokens), 'bgreen', 'bold')}")
    kv.say(f"   Prompt tokens computed ............ {s.computed_tokens}")
    kv.say(c("   → Put stable text (system prompt, tools) FIRST. Hashes are chained, so one changed "
             "token early on breaks every block after it.", "bold"))
    return {"hit_tokens": s.hit_tokens, "computed_tokens": s.computed_tokens}


def scenario_offload(kv: PagedKV) -> dict:
    kv.say(rule("Scenario: offload — GPU is full, spill KV to a CPU tier"))
    kv.say(LEGEND)
    doc = words("Long document : vLLM pages KV blocks ; evicted blocks can spill to CPU memory .")  # 16
    kv.add("A", doc)
    kv.finish("A")
    kv.show("A's 4 blocks are cached on GPU")
    kv.add("B", words("Totally different question that needs lots of fresh blocks right now please ok"))
    kv.add("D", words("Another unrelated long request to push memory pressure higher"))
    kv.show("B and D needed room: the LRU cached blocks were evicted")
    kv.finish("B")
    kv.finish("D")
    kv.add("A2", doc + words("Summarize it ."))
    kv.show("A2 re-sends A's document")
    s = kv.stats
    kv.say(rule("Result"))
    kv.say(f"   Blocks offloaded to CPU ......... {s.offloaded_blocks}")
    kv.say(f"   Tokens loaded back from CPU ..... {c(str(s.loaded_tokens), 'bblue', 'bold')}")
    kv.say(f"   Tokens hit on GPU ............... {s.hit_tokens}")
    kv.say(f"   Tokens computed, all requests ... {s.computed_tokens}")
    kv.say(c("   → Copying KV back over PCIe is usually much cheaper than recomputing it. "
             "That's tiered KV offloading (E21).", "bold"))
    return {"offloaded": s.offloaded_blocks, "loaded_tokens": s.loaded_tokens}


def _agent_session(kv: PagedKV, verbose: bool) -> list[dict]:
    """A 4-turn agent; between turns other users' chats churn the GPU cache."""
    tools = words("tools : search ( q ) ; read_file ( path ) ; run_tests ( ) ; edit ( path , diff ) .")  # 20
    ctx = SYSTEM + tools + words("user : fix the failing test in scheduler.py")  # 32 + 8 = 40
    tool_results = [words("result : test_preempt fails at line 88 ok"),
                    words("result : file shows budget off by one bug"),
                    words("result : 41 passed 0 failed all green yes")]
    calls = [words("call : run_tests ( )"), words("call : read_file ( scheduler.py )"),
             words("call : edit ( scheduler.py , fix )"), words("done : fixed off by one")]
    noise = [words(f"background chat {i} : how much HBM bandwidth does an H100 have and why does decode "
                   f"care about bandwidth more than FLOPs ? please explain with numbers {i}") for i in range(3)]
    rows = []
    for turn in range(4):
        before = Stats(**vars(kv.stats))
        rid = f"T{turn + 1}"
        kv.add(rid, ctx)
        for tok in calls[turn]:
            kv.append(rid, tok, quiet=True)
        after = kv.stats
        rows.append({"turn": turn + 1, "prompt": len(ctx),
                     "hit": after.hit_tokens - before.hit_tokens,
                     "loaded": after.loaded_tokens - before.loaded_tokens,
                     "computed": after.computed_tokens - before.computed_tokens})
        ctx = ctx + calls[turn]
        kv.finish(rid)
        if turn < 3:
            ctx = ctx + tool_results[turn]
            # while the tool runs, three other users chat at the same time and need GPU blocks
            out, kv.out = kv.out, (lambda *_: None)
            ev0, off0 = kv.stats.evicted_blocks, kv.stats.offloaded_blocks
            ids = [f"bg{turn}{k}" for k in range(3)]
            for k, nid in enumerate(ids):
                kv.add(nid, noise[(turn + k) % len(noise)] + [f"#{turn}"])
            for nid in ids:
                kv.finish(nid)
            kv.out = out
            ev = kv.stats.evicted_blocks - ev0
            off = kv.stats.offloaded_blocks - off0
            fate = c(f"{off} offloaded to CPU", "bblue") if kv.cpu_capacity else c(f"{ev} gone for good", "bred")
            kv.say(f"⏸  {rid} waits for its tool. 💬 3 other users chat meanwhile → {ev} cached blocks evicted ({fate})")
            if verbose:
                kv.show(f"GPU while {rid}'s tool runs")
    return rows


def scenario_agent(kv: PagedKV, args) -> dict:
    kv.say(rule("Scenario: agent — giant shared prefix, short outputs, pauses (E27)"))
    kv.say(LEGEND)
    kv.quiet_evictions = True
    rows_on = _agent_session(kv, verbose=True)
    shadow = PagedKV(args.gpu_blocks, args.block_size, cpu_blocks=0, out=lambda *_: None)
    rows_off = _agent_session(shadow, verbose=False)
    kv.say(rule("Result: the same 4-turn session, CPU offload ON vs OFF"))
    kv.say(f"   {'turn':>4} {'prompt':>7} │ {'ON: hit':>8} {'loaded':>7} {'computed':>9} │ {'OFF: hit':>9} {'computed':>9}")
    for a, b in zip(rows_on, rows_off):
        kv.say(f"   {a['turn']:>4} {a['prompt']:>7} │ {c(f'{a['hit']:>8}', 'bgreen')} {c(f'{a['loaded']:>7}', 'bblue')} "
               f"{a['computed']:>9} │ {c(f'{b['hit']:>9}', 'bgreen')} {c(f'{b['computed']:>9}', 'bred')}")
    tot_on = sum(r["computed"] for r in rows_on)
    tot_off = sum(r["computed"] for r in rows_off)
    kv.say(f"   Total prefill tokens computed: offload ON {c(str(tot_on), 'bold')} vs OFF {c(str(tot_off), 'bred', 'bold')}")
    kv.say(c("   → Agent turns re-send the whole history. Whatever the cache keeps, you don't pay for twice.", "bold"))
    return {"computed_on": tot_on, "computed_off": tot_off, "rows_on": rows_on, "rows_off": rows_off}


SCENARIOS = {
    "basic": dict(gpu_blocks=16, cpu_blocks=0),
    "prefix": dict(gpu_blocks=16, cpu_blocks=0),
    "offload": dict(gpu_blocks=8, cpu_blocks=16),
    "agent": dict(gpu_blocks=28, cpu_blocks=64),
}


def run(scenario: str, *, block_size: int = 4, gpu_blocks: int | None = None, cpu_blocks: int | None = None,
        delay: float = 0.0, out=print, break_prefix: bool = False) -> dict:
    cfg = dict(SCENARIOS[scenario])
    if gpu_blocks is not None:
        cfg["gpu_blocks"] = gpu_blocks
    if cpu_blocks is not None:
        cfg["cpu_blocks"] = cpu_blocks
    kv = PagedKV(cfg["gpu_blocks"], block_size, cfg["cpu_blocks"], out=out, delay=delay)
    if scenario == "basic":
        return scenario_basic(kv)
    if scenario == "prefix":
        return scenario_prefix(kv, break_prefix)
    if scenario == "offload":
        return scenario_offload(kv)
    ns = argparse.Namespace(gpu_blocks=cfg["gpu_blocks"], block_size=block_size)
    return scenario_agent(kv, ns)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scenario", choices=sorted(SCENARIOS), default="basic")
    p.add_argument("--block-size", type=int, default=4, help="tokens per block (vLLM's default is 16)")
    p.add_argument("--gpu-blocks", type=int, help="override the number of GPU blocks")
    p.add_argument("--cpu-blocks", type=int, help="override the CPU offload tier size (0 = off)")
    p.add_argument("--delay", type=float, default=None, help="seconds between frames (default: 0.35 on a terminal)")
    p.add_argument("--break-prefix", action="store_true",
                   help="prefix scenario: put a timestamp at the start of every prompt (a classic mistake)")
    p.add_argument("--no-color", action="store_true")
    a = p.parse_args(argv)
    if a.no_color:
        set_color(False)
    try:
        run(a.scenario, block_size=a.block_size, gpu_blocks=a.gpu_blocks, cpu_blocks=a.cpu_blocks,
            delay=default_delay() if a.delay is None else a.delay, break_prefix=a.break_prefix)
    except MemoryError as exc:
        print(c(f"\n💥 {exc}: in vLLM the scheduler would now preempt a request. Try --gpu-blocks 32.", "bred"))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
