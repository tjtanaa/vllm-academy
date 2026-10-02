# 07 · Paged storage is an ownership problem

**Material status:** Core lesson draft. **Source-check date:** 2026-09-22.

A block table is not just an address translation trick. It creates obligations: who owns a physical block, which tokens are complete, and when the block may be reused. This lesson makes those obligations executable.

## Learning objectives

Translate logical token positions into physical pages. Implement retain/release safely. Distinguish allocated, computed, published and reclaimable state.

## Four objects

`BlockPool` owns the physical K and V tensors, free IDs, and reference counts. Its tensor layout is `[layer, physical_block, slot, head, head_dim]`. A `PagedKV` instance owns a request's logical block table and the number of committed tokens. `PrefixIndex` can independently retain a full page for reuse. The decoder writes token state through `PagedKV`, not by assuming consecutive physical IDs.

For block size B, logical position p maps to `logical_block = p // B` and `offset = p % B`. The physical block is `table[logical_block]`. A non-contiguous table such as `[2, 3, 0]` is a normal case, not an exceptional slow path in the abstract addressing model.

## A token is not committed after the first layer

The teaching cache uses three operations: reserve a token slot, write that token's state for every layer, then commit. During a layer's attention operation, its newly written K and V must be visible along with prior committed positions. Before that layer has written, they must not be treated as initialized data.

`commit_token()` refuses to advance the logical length until all layers have written. That invariant prevents a seemingly valid cache length from hiding missing state in later layers. A production design may use a different representation or synchronization mechanism; the correctness question remains the same.

## Ownership and eviction

A request reference protects every page in its table. A prefix-index reference may keep a completed page resident after a request finishes. Removing an index entry releases that index reference; it does not revoke references held by active requests. Reallocation becomes legal only after the last owner releases the block.

The toy uses a deliberately simple model: cache entries retain pages, and LRU eviction releases those retains. Production vLLM's block-pool bookkeeping differs. Its inspected cache representation can track cached blocks that are either active or on a free queue. Never infer that the toy's reference count values or queue implementation must match production exactly.

The toy shares only complete, immutable pages. It does not share a mutable partial tail and therefore does not need partial-page copy-on-write. If you add branching from a partial tail, either copy that tail or implement an equivalent safe ownership scheme. Do not claim copy-on-write is implemented merely because reference counting exists.

## Persistent placement versus attention IO

The original PagedAttention paper motivates managing a growing KV cache with paging and sharing. FlashAttention instead emphasizes reducing attention IO through tiling. These concerns are different; a persistent block table does not by itself provide an IO-efficient attention kernel. The toy implements the addressing/ownership lesson, not either paper's optimized kernel. See the linked papers before treating the two names as competing complete engines.

## Lab

```bash
python -m pytest -q tests/test_engine.py
```

Find the test that forces a non-contiguous table. Track the table and reference counts on paper before running it. Find the test that tries to evict an actively used prefix. Then reduce the pool size until exhaustion and check cleanup through the engine context manager.

## Exercises and acceptance

Present a lifecycle table with events allocate, attach, write, commit, publish, release-request, evict-index and reuse. For each event, state which reference changes and whether a write is allowed. Explain the difference between a free block ID and a published reusable prefix.

A successful submission has a failing test for premature reuse and a passing implementation. The visual appearance of the free-list diagram is not evidence of memory safety.

## References

- [S4] [vLLM automatic prefix caching design](https://docs.vllm.ai/en/latest/design/prefix_caching/)
- [block-pool] [vllm/v1/core/block_pool.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/core/block_pool.py)
- [kv-manager] [vllm/v1/core/kv_cache_manager.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/core/kv_cache_manager.py)

- [PagedAttention paper](https://arxiv.org/abs/2309.06180)
- [FlashAttention paper](https://arxiv.org/abs/2205.14135)
