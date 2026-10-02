"""Token-budget scheduling, prefix reuse and incremental generation.

A logical iteration may include multiple requests, but their forwards execute
sequentially. This is NOT a physically batched GPU implementation. No HTTP,
preemption, async execution, EOS, distributed execution or error recovery.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
import hashlib
import torch
from .cache import BlockPool, PagedKV, PrefixIndex
from .model import TinyDecoder


@dataclass
class Request:
    request_id: str
    prompt: list[int]
    max_new_tokens: int
    tokens: list[int] = field(init=False)
    output: list[int] = field(default_factory=list)
    computed: int = 0
    cache: PagedKV | None = None
    status: str = "waiting"
    reused_tokens: int = 0

    def __post_init__(self):
        self.tokens = list(self.prompt)


class Engine:
    def __init__(self, model: TinyDecoder, *, num_blocks: int = 64,
                 block_size: int = 4, token_budget: int = 8,
                 max_active: int = 4, prefill_chunk: int = 4,
                 prefix_caching: bool = True, namespace: str = "teaching-session"):
        if min(token_budget, max_active, prefill_chunk) <= 0:
            raise ValueError("Scheduling limits must be positive")
        self.model = model
        c = model.config
        self.pool = BlockPool(num_blocks, block_size, c.num_layers, c.num_heads,
                              c.head_dim, device=str(model.device),
                              dtype=next(model.parameters()).dtype)
        # A per-engine index cannot be shared across models. Include a weight
        # digest anyway so the namespace lesson is concrete. Expensive but tiny.
        digest = hashlib.sha256()
        digest.update(repr(model.config).encode("utf-8"))
        digest.update(str(next(model.parameters()).dtype).encode("utf-8"))
        for value in model.state_dict().values():
            digest.update(value.detach().float().cpu().contiguous().numpy().tobytes())
        self.prefix = PrefixIndex(self.pool, namespace + ":" + digest.hexdigest()) if prefix_caching else None
        self.token_budget, self.max_active = token_budget, max_active
        self.prefill_chunk = prefill_chunk
        self.requests: dict[str, Request] = {}
        self.waiting: deque[Request] = deque()
        self.active: list[Request] = []
        self.trace: list[dict] = []
        self.tick = 0
        self.closed = False

    def add(self, request_id: str, prompt: list[int], max_new_tokens: int = 8) -> Request:
        if self.closed or not request_id or request_id in self.requests:
            raise ValueError("Engine closed, empty ID, or duplicate request ID")
        self.model._validate(prompt)
        if max_new_tokens <= 0 or len(prompt) + max_new_tokens > self.model.config.max_length:
            raise ValueError("Invalid generation length")
        request = Request(request_id, list(prompt), max_new_tokens)
        self.requests[request_id] = request
        self.waiting.append(request)
        return request

    def _admit(self) -> None:
        while self.waiting and len(self.active) < self.max_active:
            request = self.waiting.popleft()
            pages, length = self.prefix.acquire(request.prompt) if self.prefix else ([], 0)
            request.cache = PagedKV(self.pool, pages, length,
                                    self.prefix.evict_one if self.prefix else None)
            request.computed = request.reused_tokens = length
            request.status = "running"
            self.active.append(request)

    @torch.inference_mode()
    def step(self) -> bool:
        if self.closed:
            raise RuntimeError("Engine is closed")
        self._admit()
        if not self.active:
            return False
        self.tick += 1
        budget, plan = self.token_budget, []
        # Teaching policy: requests that already generated a token first.
        # This is NOT an exact transcription of vLLM's running-queue policy.
        order = sorted(self.active, key=lambda r: not bool(r.output))
        for request in order:
            needed = len(request.tokens) - request.computed
            cap = 1 if request.output else self.prefill_chunk
            count = min(needed, cap, budget)
            if count:
                plan.append((request, count))
                budget -= count
        events = []
        for request, count in plan:
            assert request.cache is not None
            before = request.computed
            logits = self.model.cached(request.tokens[before:before + count], request.cache)
            request.computed += count
            if self.prefix:
                self.prefix.publish(request.tokens, request.cache)
            emitted = None
            if request.computed == len(request.tokens):
                emitted = int(logits[-1].argmax())
                request.tokens.append(emitted)
                request.output.append(emitted)
                if len(request.output) == request.max_new_tokens:
                    request.status = "finished"
                    request.cache.close()
            events.append({"request": request.request_id, "computed_before": before,
                           "scheduled": count, "computed_after": request.computed,
                           "emitted": emitted, "status": request.status})
        self.active = [r for r in self.active if r.status == "running"]
        self.pool.validate()
        self.trace.append({"tick": self.tick, "scheduled_tokens": self.token_budget - budget,
                           "events": events, "free_blocks": len(self.pool.free)})
        return True

    def run(self) -> dict[str, list[int]]:
        while self.step():
            pass
        return {key: list(r.output) for key, r in self.requests.items() if r.status == "finished"}

    def cancel(self, request_id: str) -> None:
        request = self.requests[request_id]
        if request.status in ("finished", "cancelled"):
            return
        self.waiting = deque(r for r in self.waiting if r is not request)
        self.active = [r for r in self.active if r is not request]
        if request.cache:
            request.cache.close()
        request.status = "cancelled"
        self.pool.validate()

    def close(self) -> None:
        if not self.closed:
            for request in self.requests.values():
                if request.status in ("waiting", "running"):
                    self.cancel(request.request_id)
                elif request.cache:
                    request.cache.close()
            if self.prefix:
                self.prefix.clear()
            self.waiting.clear()
            self.active.clear()
            self.closed = True
            self.pool.validate()

    def __enter__(self) -> Engine:
        return self

    def __exit__(self, *_args) -> None:
        self.close()
