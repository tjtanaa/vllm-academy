# 02 — Autoregressive inference, prefill, and decode

**Material status:** Core lesson draft. **Source-check date:** 2026-09-22.

A language model does not generate an entire answer in one ordinary autoregressive forward pass. It repeatedly conditions on a growing token history. The engine's scheduling and memory decisions follow from that dependency.

## Learning objectives

Track which tokens have been computed versus sampled, distinguish prefill from decode work, and avoid a common off-by-one error when reasoning about KV caches.

## A concrete token history

Take prompt IDs `[11, 22, 33]`. A causal forward computes representations for these positions and produces logits whose final row predicts a next token, say `44`. The cache now contains state for `11, 22, 33`; it does not yet contain state for `44`. Sampling a token and executing that token are different operations.

On the next iteration, execute `44` while reading the cached earlier keys and values. Its logits can predict `55`. After this execution, the cache includes `44`, while `55` remains uncomputed. In a simple greedy path, after each sampling event the logical history has one more token than the number already executed. Prefix hits, chunked prefill, speculation, and asynchronous execution complicate that relation, so production schedulers track the counters explicitly rather than infer them from the number of responses.

## Prefill is work on known input

During initial prefill, all prompt IDs are known. Their causal representations can be computed in a parallel sequence operation, subject to causal masking. Prefill can be split into chunks so a long prompt does not monopolize an iteration's token budget. A chunk boundary does not erase causality or the need to preserve earlier state.

Decode usually executes a small amount of new token work per request while reading a potentially long history. With multiple requests, an engine can combine their work even though each request's next token depends on its own previous result. Continuous batching changes the membership of the working set over time.

In the teaching implementation, `TinyDecoder.cached` intentionally executes even prompt tokens one by one. That is a correctness simplification, not the production prefill implementation or a proposed optimization.

## Why a cache helps, precisely

Without a cache, a naive generator recomputes previous-token representations every iteration. Cached inference preserves their keys and values so new queries can attend to prior state without recomputing those projections and all earlier hidden states.

Caching does **not** turn full-context attention into constant-time decode. With ordinary dense attention, a new query still interacts with a growing set of prior keys and values. State what quantity an asymptotic claim measures: one new query's attention, a full prompt forward, the whole generation sequence, or a complete decoder layer. “KV caching changes O(n²) to O(n)” without that context is not a sufficiently precise lesson.

## Lab: inspect computed versus sampled

Run the demo, then open the trace. For each event, compare `computed_before`, `scheduled`, `computed_after`, and `emitted`. Reconstruct the prompt and output lists for `cold`. Confirm that not every scheduled token immediately emits an output: an intermediate prefill chunk has not yet reached the end of the known prompt.

In `Engine.step`, find the condition that permits sampling. Then inspect the production scheduler's `schedule` method at the pinned source: it reasons about outstanding token work, including speculative and asynchronous bookkeeping, rather than relying on a simplistic global prefill/decode switch.

## Exercises and acceptance

For a prompt of five tokens and three requested output tokens, write the sequence of known-history and computed-token counts in an uncached-prefix greedy run. Explain why an exact prefix hit may still need some prompt computation to recover final logits. Explain why two requests can participate in one scheduler iteration without their histories being combined. Pass when your trace prediction agrees with the implementation and you can state its simplifying assumptions.

## References

- [scheduler] [vllm/v1/core/sched/scheduler.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/core/sched/scheduler.py)
- [S5] [vLLM architecture overview (background; verify against pinned source)](https://docs.vllm.ai/en/latest/design/arch_overview/)
