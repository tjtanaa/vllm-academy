# 09 · Reuse the right prefix without corrupting a request

**Material status:** Core lesson draft. **Source-check date:** 2026-09-22.

Two prompts can share earlier computation, but an identical-looking text fragment is not sufficient evidence that its KV state is reusable. Prefix caching needs identity, a valid computed boundary, and safe storage lifetime.

## Learning objectives

Construct a context-sensitive block identity. Explain why full-prompt cache reuse may still require work to produce logits. Test divergence, eviction and cancellation together.

## Why parent context belongs in the key

The K and V for a token depend on earlier context. The same block of token IDs after two different prefixes generally represents different model states. The toy computes a SHA-256 chain over a namespace, the parent's hash and the exact token IDs in the next full block. The namespace identifies the tiny model's weights and configuration for this engine instance.

Production identity is richer. The official vLLM prefix-caching design describes a parent hash, block tokens and additional identity such as adapter, multimodal and cache-salt information. The correct reuse boundary follows the model computation, not the user-visible conversation label. Avoid teaching a key such as `hash(prompt_string)` as a complete production solution.

Weights must remain unchanged during the toy engine's lifetime. Changing them without invalidating the cache would make the existing namespace/state relationship false. The toy is an in-process educational cache, not a multi-tenant security boundary or a durable cross-version cache format.

## Only share committed full blocks

With a block size of four, prompt `[1,2,3,4,5,6,7,8,9]` can reuse the first two full blocks, then compute token 9. If two prompts diverge at token 6, only the preceding fully matching block is reusable in this simple design. Matching token suffixes after divergence do not restore identical state.

A cache hit supplies K and V, not necessarily the final hidden state or logits needed for sampling. The toy deliberately leaves at least one prompt token to compute: its maximum reusable prefix is `floor((prompt_length - 1) / block_size)` full blocks. For an eight-token prompt and block size four, this means reusing four tokens, then recomputing the final four-token block. The rule is conservative and makes the final-logit requirement obvious. It is not a universal statement about every model and cache implementation.

## Why eviction is separate from finishing

When a request finishes, its request-owned references are released. Prefix-index references may remain. If cache capacity is needed later, removing an index entry releases only its own reference. A running request that acquired that page still protects it. Cancellation must follow the same ownership discipline, whether it happens before admission or during execution.

The toy does not rewrite an existing active table merely because another block with the same hash exists. The inspected production block cache likewise supports a hash mapping to more than one block and documents why allocated block IDs are not always deduplicated. Identity equivalence and physical object identity are different concepts.

## Lab

```bash
python -m mini_vllm.demo
python -m pytest -q tests/test_engine.py -k 'prefix or evict or cancel'
```

The supplied demo checks equal cold, warm and dense-reference outputs and reports reused-token counts. Those are measured CPU correctness results, not latency measurements. Add divergent-prefix and different-namespace controls. Exercise lengths `B-1`, `B`, `B+1`, `2B` and `2B+1`.

## Exercises and acceptance

Explain why “hit rate went up” alone is not a serving speedup claim. Construct a case with a high hit rate but little saved input computation. Show how a stale-key bug differs from a premature-free bug. Submit a trace proving that the repeated prefix was actually reused and that all generated token IDs still match the independent reference.

## References

- [S4] [vLLM automatic prefix caching design](https://docs.vllm.ai/en/latest/design/prefix_caching/)
- [block-pool] [vllm/v1/core/block_pool.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/core/block_pool.py)
