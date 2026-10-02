"""Paged KV storage with explicit lifetime management.

All attention reads gather pages into a dense tensor. This teaches indexing and
ownership, NOT a fast PagedAttention kernel. Full cached pages are immutable;
partial-page sharing and copy-on-write are deliberately not implemented.
"""
from __future__ import annotations

import hashlib
import json
from collections import OrderedDict, deque
from collections.abc import Callable, Sequence

import torch


class CacheFull(RuntimeError):
    """No free block and no evictable, inactive prefix entry."""


class BlockPool:
    def __init__(self, num_blocks: int, block_size: int, layers: int,
                 heads: int, head_dim: int, *, device: str = "cpu",
                 dtype: torch.dtype = torch.float32):
        if min(num_blocks, block_size, layers, heads, head_dim) <= 0:
            raise ValueError("All dimensions must be positive")
        self.num_blocks, self.block_size = num_blocks, block_size
        self.layers = layers
        # [layer, physical block, token in block, KV head, head dimension]
        shape = (layers, num_blocks, block_size, heads, head_dim)
        self.k = torch.zeros(shape, device=device, dtype=dtype)
        self.v = torch.zeros_like(self.k)
        self.refs = [0] * num_blocks
        self.free = deque(range(num_blocks))

    def _check(self, block: int) -> None:
        if not 0 <= block < self.num_blocks:
            raise IndexError("Invalid physical block")

    def allocate(self, evict: Callable[[], bool] | None = None) -> int:
        while not self.free:
            if evict is None or not evict():
                raise CacheFull("No reclaimable pages. Reduce active requests or increase num_blocks; toy engine has no preemption.")
        block = self.free.popleft()
        if self.refs[block] != 0:
            raise RuntimeError("Free-list corruption")
        self.refs[block] = 1
        self.k[:, block].zero_()
        self.v[:, block].zero_()
        return block

    def retain(self, block: int) -> None:
        self._check(block)
        if self.refs[block] <= 0:
            raise RuntimeError("Cannot retain a freed block")
        self.refs[block] += 1

    def release(self, block: int) -> None:
        self._check(block)
        if self.refs[block] <= 0:
            raise RuntimeError("Double release")
        self.refs[block] -= 1
        if self.refs[block] == 0:
            self.free.append(block)

    def validate(self) -> None:
        free = set(self.free)
        assert len(free) == len(self.free), "Duplicate free block"
        assert all(r >= 0 for r in self.refs)
        assert free == {i for i, r in enumerate(self.refs) if r == 0}


class PagedKV:
    """One request's block table. Supplied pages already have an owned ref."""
    def __init__(self, pool: BlockPool, pages: Sequence[int] = (),
                 length: int = 0, evict: Callable[[], bool] | None = None):
        if length < 0 or length != len(pages) * pool.block_size:
            raise ValueError("A reused prefix must contain only complete pages")
        if len(set(pages)) != len(pages):
            raise ValueError("Duplicate physical page in a request")
        for block in pages:
            pool._check(block)
            if pool.refs[block] <= 0:
                raise ValueError("Prefix pages must be retained before construction")
        self.pool, self.pages, self.length = pool, list(pages), length
        self.evict = evict
        self.closed = False
        self._reserved = False
        self._written: set[int] = set()

    def reserve_token(self) -> None:
        if self.closed or self._reserved:
            raise RuntimeError("Closed cache or unfinished token")
        if self.length % self.pool.block_size == 0:
            self.pages.append(self.pool.allocate(self.evict))
        elif self.pool.refs[self.pages[-1]] != 1:
            raise RuntimeError("Cannot append to a shared partial page")
        self._reserved = True
        self._written.clear()

    def write_layer(self, layer: int, k: torch.Tensor, v: torch.Tensor) -> None:
        if self.closed or not self._reserved or layer in self._written:
            raise RuntimeError("Token must be reserved; each layer is written once")
        if not 0 <= layer < self.pool.layers:
            raise IndexError("Invalid layer")
        logical, offset = divmod(self.length, self.pool.block_size)
        block = self.pages[logical]
        expected = self.pool.k[layer, block, offset].shape
        if k.shape != expected or v.shape != expected:
            raise ValueError(f"Expected K/V shape {tuple(expected)}")
        self.pool.k[layer, block, offset].copy_(k)
        self.pool.v[layer, block, offset].copy_(v)
        self._written.add(layer)

    def read_layer(self, layer: int, *, include_pending: bool = False) -> tuple[torch.Tensor, torch.Tensor]:
        if self.closed:
            raise RuntimeError("Cache has been closed")
        if include_pending and (not self._reserved or layer not in self._written):
            raise RuntimeError("Current layer has no pending K/V")
        length = self.length + int(include_pending)
        page_count = (length + self.pool.block_size - 1) // self.pool.block_size
        ids = self.pages[:page_count]
        # Advanced indexing makes a dense copy: pedagogical, not performant.
        k = self.pool.k[layer, ids].flatten(0, 1)[:length]
        v = self.pool.v[layer, ids].flatten(0, 1)[:length]
        return k, v

    def commit_token(self) -> None:
        if not self._reserved or len(self._written) != self.pool.layers:
            raise RuntimeError("All layers must be written before committing")
        self.length += 1
        self._reserved = False
        self._written.clear()

    def close(self) -> None:
        if not self.closed:
            for block in self.pages:
                self.pool.release(block)
            self.pages.clear()
            self.closed = True
            self._reserved = False


def prefix_keys(tokens: Sequence[int], block_size: int, namespace: str) -> list[str]:
    """A parent-chained key, not a security boundary or vLLM wire format."""
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    parent = ""
    keys = []
    for start in range(0, len(tokens) - block_size + 1, block_size):
        payload = [namespace, parent, list(tokens[start:start + block_size])]
        parent = hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()
        keys.append(parent)
    return keys


class PrefixIndex:
    """Toy LRU: an index entry holds one extra pool ref.

    vLLM's real cached/free-queue bookkeeping differs. This implementation keeps
    the ownership rule visible. Only entries without active readers are evicted.
    """
    def __init__(self, pool: BlockPool, namespace: str):
        self.pool, self.namespace = pool, namespace
        self.entries: OrderedDict[str, int] = OrderedDict()
        self.hit_tokens = 0

    def acquire(self, tokens: Sequence[int]) -> tuple[list[int], int]:
        # K/V alone does not contain the logits needed for the first output.
        # Leave at least one prompt token for execution, even on an exact hit.
        max_blocks = max(0, (len(tokens) - 1) // self.pool.block_size)
        pages = []
        for key in prefix_keys(tokens, self.pool.block_size, self.namespace)[:max_blocks]:
            block = self.entries.get(key)
            if block is None:
                break
            self.pool.retain(block)
            self.entries.move_to_end(key)
            pages.append(block)
        length = len(pages) * self.pool.block_size
        self.hit_tokens += length
        return pages, length

    def publish(self, tokens: Sequence[int], cache: PagedKV) -> None:
        if cache.pool is not self.pool or cache.closed:
            raise ValueError("Invalid cache")
        keys = prefix_keys(tokens[:cache.length], self.pool.block_size, self.namespace)
        for key, block in zip(keys, cache.pages):
            if key not in self.entries:
                self.pool.retain(block)
                self.entries[key] = block
            else:
                self.entries.move_to_end(key)

    def evict_one(self) -> bool:
        for key, block in list(self.entries.items()):
            if self.pool.refs[block] == 1:  # Only the index owns it.
                del self.entries[key]
                self.pool.release(block)
                return True
        return False

    def clear(self) -> None:
        for block in self.entries.values():
            self.pool.release(block)
        self.entries.clear()
