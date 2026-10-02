# 04 — KV cache accounting and paging

**Material status:** Core lesson draft. **Source-check date:** 2026-09-22.

KV cache capacity is not a single fixed model property. It depends on the number and lengths of active histories, their attention/state representation, dtype, cache groups, partitioning, and reusable prefixes. Begin with an explicit dense-attention model, then identify when its assumptions fail.

## Learning objectives

Calculate dense MHA/GQA cache size, map logical token positions to physical pages, and distinguish memory waste, eviction, recomputation and offloading.

## Dense MHA/GQA formula

For one full-attention sequence of `T` tokens with `L` layers, `H_kv` KV heads, head dimension `D`, and `b` bytes per cached scalar:

`KV bytes = 2 × L × T × H_kv × D × b`.

The leading factor accounts for keys and values. For GQA, use the number of KV heads, not query heads. For multiple unshared sequences, sum their lengths. This formula excludes quantization scales, allocator metadata, workspaces, model weights, and any tensor-parallel replication or partitioning.

A deliberately hypothetical model with 32 layers, 8 KV heads, head dimension 128 and two-byte elements uses `131072` bytes, or `128 KiB`, of KV per token across its layers. An 8192-token sequence uses exactly `1 GiB` under those assumptions. These are arithmetic examples, not specifications for the default Qwen model.

```bash
python labs/kv_budget.py --layers 32 --kv-heads 8 --head-dim 128 \
  --bytes-per-element 2 --tokens 8192 --requests 1 --block-size 16
```

## Logical versus physical positions

With block size `B`, logical token position `t` belongs to logical block `t // B` at offset `t % B`. A request's block table maps that logical block to a physical pool block. If `B=4` and the table is `[7, 2, 11]`, token position 5 is at physical block 2, offset 1.

A request need not occupy contiguous physical memory. It can grow by acquiring another block. That flexibility reduces the need to reserve a maximum-length contiguous region per request. Paging does not inherently compress each KV scalar or reduce the mathematical size of the attention state.

For an unshared sequence of length `T`, allocated token slots are `B × ceil(T/B)`. The final block wastes between zero and `B-1` slots. Shared prefixes can reduce physical occupancy further, while metadata and fragmentation add other costs. Compare logical occupancy with actual pool allocation rather than silently equating them.

## Retention, eviction and offloading

Retention keeps reusable blocks available after a request finishes. Eviction discards a retained representation so memory can be reused. Recomputing a later prefix rebuilds the missing state. Offloading transfers state to another memory/storage tier. These choices have different compute, bandwidth and latency costs.

A referenced block cannot be safely recycled merely because the originating request completed: another request or in-flight transfer may still depend on it. Ownership, not just request status, determines when reuse is safe.

## Where the formula stops working

A sliding-window layer need not retain the same history as a full-attention layer. A recurrent or state-space layer may store a fixed-size state or snapshots rather than dense per-token K/V. MLA uses a different stored representation. Hybrid models need group-specific accounting. Tensor parallelism does not guarantee an exact `1/TP` reduction when KV heads or state are replicated. Start from the actual cache specification and sum groups.

## Lab, exercises and acceptance

Calculate the tail waste for 8193 tokens at block size 16, then verify with the calculator. Draw a three-block noncontiguous table and map six logical positions. Explain why changing query-head count alone need not change GQA KV size. Find the cache-group boundary in the pinned `KVCacheManager` initialization. Pass when your memory estimate states both what is included and what has been deliberately excluded.

## References

- [S8] [vLLM hybrid KV cache manager](https://docs.vllm.ai/en/latest/design/hybrid_kv_cache_manager/)
- [kv-manager] [vllm/v1/core/kv_cache_manager.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/core/kv_cache_manager.py)
- [S4] [vLLM automatic prefix caching design](https://docs.vllm.ai/en/latest/design/prefix_caching/)
