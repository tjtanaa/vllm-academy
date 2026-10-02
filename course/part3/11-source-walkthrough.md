# 11 · From teaching objects to the real vLLM source

**Material status:** Core lesson draft. **Source-check date:** 2026-09-22.

Now use the small engine as a question generator, not as a diagram that production must follow. The purpose of a source tour is to find responsibility boundaries and invariants at a known revision.

## Learning objectives

Navigate an immutable source checkout. Distinguish a verified source excerpt from an observed runtime call path. Map the toy's responsibilities to production without equating their implementations.

## Freeze the reading surface

The source-reading baseline is vLLM `v0.29.0`, commit `98dff2a81d747d1dba01a47f939f48c3526d4206`. The tag and six listed file excerpts were inspected on 2026-09-22. This is not a statement that the GPU labs were executed on that release.

```bash
git clone https://github.com/vllm-project/vllm.git ../vllm-source
git -C ../vllm-source checkout 98dff2a81d747d1dba01a47f939f48c3526d4206
python labs/verify_source_map.py ../vllm-source
```

The local checker verifies the commit, paths and search terms. It does not prove that a runtime uses every listed file. It requires a separate source checkout; no production source tree is bundled with this course.

## Read six responsibility boundaries

| Responsibility | Verified source entry | Question to answer |
|---|---|---|
| Engine orchestration | `vllm/v1/engine/core.py` | How are scheduling, execution and connector metadata coordinated? |
| Work assignment | `vllm/v1/core/sched/scheduler.py` | Which counts and budgets determine outstanding work? |
| Cache coordination | `vllm/v1/core/kv_cache_manager.py` | Where are cache groups and the block pool coordinated? |
| Physical block reuse | `vllm/v1/core/block_pool.py` | What separates a reusable cached block from a reclaimable one? |
| Model execution | `vllm/v1/worker/gpu/model_runner.py` | How are backend initialization, block tables and model execution connected? |
| External cache boundary | `vllm/distributed/kv_transfer/kv_connector/v1/base.py` | What must the scheduler know, and what must workers actually transfer? |

The runner path above is the inspected V2 runner entry. Do not assume every platform/model/configuration selects it. For a runtime walkthrough, record the runner and backend actually instantiated and follow the dispatch to the relevant implementation. “The file exists” is not an execution trace.

## Key differences from the toy

The inspected scheduler accounts for computed tokens, speculative and asynchronous state, input/scheduling budgets, and other constraints. Its design is broader than a rigid global prefill phase followed by a global decode phase. The cache manager creates a coordinator and supports multiple cache groups rather than assuming every layer has the same state layout. The production block cache may hold several blocks for the same key. External connectors introduce worker-side transfers and deferred lifetime decisions.

The toy's direct Python calls intentionally hide process boundaries and communication. A production request path also involves API handling, input processing and output handling. These are useful follow-on tracing tasks; this package does not claim to have inspected every API endpoint or produced a complete live trace for them.

## Guided source exercise

Start at scheduler `schedule()`. Identify the outstanding-work calculation, one token-budget clamp, and one condition that skips a request. Then inspect cache-manager construction to identify the coordinator and block pool. Finally read the connector interface's documentation and explain why `request_finished()` can affect when blocks are freed.

Record each answer with a commit, path, symbol and short reasoning. Search terms in `maintainers/source-map.json` are navigation anchors, not a replacement for reading surrounding control flow.

## Acceptance

Submit a source map with at least one counterexample to the naive statement “the toy and production engine work exactly the same way.” A good answer explains an invariant and where it is enforced. A list of class names without responsibilities is not enough.

## References

- [S12] [vLLM v0.29.0 release](https://github.com/vllm-project/vllm/releases/tag/v0.29.0)
- [engine-core] [vllm/v1/engine/core.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/engine/core.py)
- [scheduler] [vllm/v1/core/sched/scheduler.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/core/sched/scheduler.py)
- [kv-manager] [vllm/v1/core/kv_cache_manager.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/core/kv_cache_manager.py)
- [block-pool] [vllm/v1/core/block_pool.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/core/block_pool.py)
- [gpu-runner-v2] [vllm/v1/worker/gpu/model_runner.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/worker/gpu/model_runner.py)
- [kv-connector] [vllm/distributed/kv_transfer/kv_connector/v1/base.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/distributed/kv_transfer/kv_connector/v1/base.py)
