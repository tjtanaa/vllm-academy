# 10 · Assemble a small engine and defend its boundaries

**Material status:** Core lesson draft. **Source-check date:** 2026-09-22.

An engine is a composition of stateful components. Most useful bugs appear where two components disagree: a scheduler thinks tokens are computed when a cache is incomplete, or a request finishes while an index still expects to retain a block. The capstone checks the interfaces, not just each object in isolation.

## Learning objectives

Follow a request from submission through completion. Validate resource cleanup on cancellation and failure. Describe what the implementation does and does not demonstrate.

## The reference architecture

```text
submit(prompt IDs, generation limit)
                |
            waiting queue
                |
       admission + token budget
                |
     per-request scheduled token slice
                |
  TinyDecoder.cached <-> PagedKV <-> BlockPool
                |                      ^
        sample when ready              |
                |                  PrefixIndex
     append output / continue          |
                +--- finish or cancel -+
```

The constructor fixes the model and cache configuration. Submission validates token IDs and context limits. Admission optionally acquires reusable prefix pages. Each step schedules outstanding work, executes it, publishes completed prefix blocks, and either samples or completes the request. Closing the engine cancels remaining requests and clears cache-index ownership.

The output token list is part of a request's next input history. A final sampled token need not be forwarded when the generation limit has already been reached. That is why `computed`, cache length and the total known token list are related but not always equal.

## Development milestones

Use `labs/MILESTONES.md` to rebuild the engine on a scratch branch. Start with dense generation, then private cached generation, paged storage, multiple requests, prefix reuse and lifecycle stress tests. The reference implementation is included for comparison; learners should write down a design before reading each solution.

The order is intentional. Adding a transport first would make a missing token indistinguishable from an HTTP streaming bug. Adding an optimized kernel before numerical tests would obscure whether bad outputs originated in address mapping, masking, or compute.

## Faults worth injecting

Reduce the physical pool size until allocation fails. Cancel a waiting request and then an active request. Repeat a prefix after unrelated requests force eviction. Reuse a shared prefix while another request holding it is still active. Change the chunk budget while keeping the model and prompt fixed.

The current toy raises an explicit cache-exhaustion error rather than implementing preemption or a production recovery policy. Use its context manager to guarantee cleanup around such an experiment. This behavior is a teaching boundary, not a recommended service-availability design.

## What is intentionally missing

There is no tokenizer, pretrained checkpoint, vectorized prefill, physically batched forward, optimized paged-attention kernel, HTTP transport, sampling distribution, EOS policy, tensor parallelism, speculative verification, asynchronous scheduler, hybrid state, or external KV connector. The generated token IDs are not intended to be readable text. The real-vLLM labs provide the actual server path without pretending that this toy is a drop-in service.

## Capstone and acceptance

Submit an architecture diagram, a dynamic-arrival trace, numerical comparisons, cancellation/exhaustion results, and a one-page limitation statement. Run the entire test suite. Inspect reference counts after cleanup. A robust capstone explains why its invariants hold and identifies unsupported states; it does not simply show a successful normal request.

As an optional next implementation, vectorize the known-token prefill path while preserving the incremental reference. Only after that succeeds should a learner attempt a packed multi-request forward. Both are extensions to implement and test, not features supplied by this starter.

## References

- [engine-core] [vllm/v1/engine/core.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/engine/core.py)
- [scheduler] [vllm/v1/core/sched/scheduler.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/core/sched/scheduler.py)
- [S5] [vLLM architecture overview (background; verify against pinned source)](https://docs.vllm.ai/en/latest/design/arch_overview/)
