# 08 · Schedule tokens, not whole conversations

**Material status:** Core lesson draft. **Source-check date:** 2026-09-22.

A request can be waiting, partially computed, producing outputs, or finished. A serving engine must make progress across many such requests while respecting compute and memory limits. The small engine exposes these decisions without multiprocessing or device kernels hiding them.

## Learning objectives

Separate admission, token scheduling, execution and completion. Explain chunked prefill and changing batch membership. Audit token-budget and lifecycle invariants in a trace.

## The bookkeeping model

For each request, track the input/output token list and how many tokens have already had their model state computed. The outstanding work is the gap between those counts. A long prompt creates a large initial gap; ordinary decode typically creates another one-token gap after a sample is appended. Speculation and asynchronous execution add more state in production and are not implemented in the toy.

Admission chooses which waiting requests become active. Scheduling assigns some number of outstanding tokens to eligible requests. Execution computes those tokens. Sampling occurs only when sufficient state and logits are ready. Completion removes the request and releases its ownership. Calling all of those steps “batching” hides the interesting failure cases.

## The toy policy

Read `Engine.step` in `mini_vllm/engine.py`. The toy admits up to `max_active`, gives already-generating requests priority, and limits long input work using `prefill_chunk` and a shared `token_budget`. New requests may arrive between steps. Completed requests leave the active set so another request can be admitted.

This is **logical continuous batching**: membership changes over time. The toy executes selected requests serially in Python; it does not pack them into one physically batched model forward. Therefore a logical schedule trace is not evidence of GPU batching throughput.

The simple policy is also not a line-for-line replica of vLLM. In the pinned vLLM scheduler, the central operation assigns work using computed-token counts, tokens including speculative work, and budgets; it is not restricted to two global prefill/decode phases. Inspect `schedule()` and its surrounding configuration instead of assuming that the toy's decode-first sort is the production scheduling algorithm.

## Trace an example

Suppose A has two outstanding decode tokens under a hypothetical extension, B has a 12-token prompt, and the token budget is four. Different policies can give A two and B two, B all four, or defer admission of B. The policy affects latency and fairness; the budget alone does not determine the outcome.

For the actual non-speculative toy, construct one long-prompt request and one short-prompt request, start the engine, then insert another request between steps. For each step, record request IDs, assigned token counts, computed counts, output length and whether a request finished. The sum of assigned tokens must never exceed the budget.

## Lab and acceptance

Run the dynamic-arrival and cancellation tests in `tests/test_engine.py`, then inspect `results/toy-trace.json`. Add a test that changes the chunk size while preserving final generated tokens. Add an assertion that a request is never sampled from an unfinished prefill chunk.

Explain a starvation risk in a strict-priority policy and propose a bounded fairness rule. Do not claim the proposed rule is implemented or universally faster. The accepted artifact is a trace plus invariants and a policy argument, not a throughput chart from this serial simulator.

## References

- [scheduler] [vllm/v1/core/sched/scheduler.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/core/sched/scheduler.py)
- [engine-core] [vllm/v1/engine/core.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/engine/core.py)
