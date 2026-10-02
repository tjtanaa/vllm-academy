# 16 — Measure and debug the whole path

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

A service can be slow before the first GPU kernel starts, while waiting for cached data, or after tokens leave the model. Measurements should identify the boundary of the problem before prescribing an optimization.

## Define the clock and workload

Separate request arrival, validation, rendering, media acquisition/preprocessing, queueing, encoder work, prefill, first token selection, output processing and client observation. Some stages overlap; an end-to-end latency model follows the critical path rather than blindly summing every recorded duration.

TTFT depends on the stated request-start and first-token observation boundaries. ITL concerns intervals between token observations; a streamed text chunk need not correspond one-to-one with a token. End-to-end completion latency includes all work until the chosen terminal event. A percentile is not a confidence interval.

Use both workload and system identity: model/tokenizer revisions, length distributions, offered arrival pattern, concurrency limits, cache state, decoding policy, dtype, backend and hardware/software stack. Synthetic systems workloads and model-quality evaluations answer different questions.

## Interleave prediction with experiment

Propose four controlled comparisons: cached versus uncached input; low versus higher concurrency; text-only versus image-bearing requests; co-located versus separated rendering. For each, predict the changed stage and name an alternative explanation for an apparent gain.

A warm kernel path and a warm prefix cache are separate conditions. Similarly, a processor hit does not prove an encoder hit or a KV hit. Request failures must remain in the report rather than disappearing from throughput calculations.

## Hands-on routes

On CPU only, use the mechanism trace and construct a measurement plan. Do not report the tiny Python model's timing as evidence about production GPU efficiency.

With a separately validated vLLM environment, use the existing Academy serving/benchmark labs and record the exact CLI version. First collect an ordinary working baseline; add one variable at a time. The current supplement did not execute those GPU recipes.

The model-runner design reading is useful for explaining why persistent request state differs from packed per-step inputs, but it is not evidence that the selected runtime uses a particular runner. [R30](../REFERENCES.md)

## Source-guided debugging

Choose one unexpected observation and identify the earliest boundary where it appears. Wrong prompt IDs point toward rendering/tokenization. Mismatched image positions point toward processor/model contracts. A cache hit that still waits may involve readiness or scheduling. A malformed stream can occur after correct token generation.

Do not begin by changing a kernel merely because the service uses a GPU.

## Exercise and exit ticket

Submit the hypothesis, fixed variables, changed variable, raw data location, error counts, repeated-run plan, interpretation and exclusions. A proposed speedup must be measured; a valid plan without hardware is still useful but remains a plan.
