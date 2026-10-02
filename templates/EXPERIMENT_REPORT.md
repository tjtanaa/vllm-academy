# Experiment report — template

## Question and preregistered expectation

Question:
Hypothesis and why:
Correctness/quality acceptance criterion:
Performance objective (including latency target when applicable):
What result would disprove the hypothesis:

## Environment and workload identity

Source SHA / package version / container digest:
GPU model, architecture, count and topology:
Driver, Python, PyTorch, CUDA/HIP, Triton, AITER/other backend versions:
Selected model runner, attention/linear/collective backend and graph mode:
Model and tokenizer identifiers plus immutable revisions:
Exact command and raw environment-file path:
Dataset or synthetic generator, seed and license:
Target and actual input/output token distributions:
Request rate, concurrency cap, client placement and timeout:
Sampling and EOS policy:
Prefix-cache enabled/disabled, cache state, cold/warm definition:
Other applications sharing the hardware:

## Method

Baseline and changed variable:
Controlled variables:
Warmup protocol (separate compilation, model warmup and prefix warmup):
Measured repetition count and A/B order:
Timing boundary and synchronization method:
Failure/retry/cancellation accounting:
Negative control:

## Results — fill only after execution

| Repetition | Configuration | Successful / failed requests | Output tokens/s | TTFT p50 / p95 / p99 | TPOT p50 / p95 / p99 | E2E latency | Evidence path |
|---|---|---|---|---|---|---|---|
| Not measured | | | | | | | |

State units, metric definitions, actual sample sizes and variability. Separate token- and chunk-level timing. Do not estimate p99 confidence from a tiny pilot or hide failures by dropping requests from denominators.

## Interpretation

Observed effect and uncertainty:
Quality/correctness outcome:
Evidence that the intended execution path actually ran:
Alternative explanations / confounders:
Regressions or workload regimes where it does not help:
Scope of the conclusion, including unsupported or untested hardware:
Next falsifiable experiment:
