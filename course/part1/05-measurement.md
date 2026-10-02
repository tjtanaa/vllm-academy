# 05 — Measure a workload, not a slogan

**Material status:** Core lesson draft; GPU recipe unverified. **Source-check date:** 2026-09-22.

A throughput number is meaningful only after its workload and measurement boundary are defined. Two apparently identical commands can exercise different cache states, output lengths, arrival patterns, execution modes, or hardware paths.

## Learning objectives

Define request metrics, distinguish open-loop offered load from a concurrency cap, design a controlled comparison, and preserve raw results alongside an interpretation.

## Definitions to put in the report

TTFT is the elapsed time from the chosen request-start boundary to the first generated token reaching the chosen observation boundary. End-to-end latency is measured to completion. ITL is an interval between successive output-token observations. TPOT is often summarized per request as `(completion_time - first_token_time)/(output_tokens - 1)` for outputs longer than one token; state the exact implementation used. These are not interchangeable distributions.

A streamed network chunk is not necessarily a single token. Do not rename “time to first response byte,” “time to first nonempty text chunk,” or chunk-to-chunk intervals as token metrics without verifying the measurement semantics. Prefer the benchmark tool's documented metric definitions and preserve its version.

Output throughput counts generated tokens over a stated interval. Total-token throughput mixes prompt and generation work and answers a different question. Goodput counts work satisfying declared service-level objectives. Percentiles describe distributions, not uncertainty in an estimated mean; repeated independent runs and raw request data address other aspects of variability.

## Baseline workload

Start the first server with prefix caching disabled and eager execution explicitly recorded. Run a small warmup separately, then the measured workload:

```bash
NUM_PROMPTS=8 RUN_DIR=results/warmup bash labs/bench.sh
NUM_PROMPTS=128 CONCURRENCY=4 RUN_DIR=results/baseline-c4 bash labs/bench.sh
```

The supplied client uses synthetic random input, the completions endpoint, fixed target output lengths via `--ignore-eos`, and saved detailed results. That makes it a systems workload, not an instruction-following evaluation. Do not combine its scores with a quality benchmark.

The default `REQUEST_RATE=inf` with a concurrency cap is a load-saturating experiment constrained by the client. It does not represent a realistic independent Poisson arrival process. Use a finite request rate for offered-load sweeps, and remember that a binding client concurrency limit can suppress the actual arrival rate. Record both parameters and failures.

The benchmark tokenizer must match the intended model revision. Set `TOKENIZER` to a pinned local tokenizer snapshot where necessary; the default identifier can resolve to a moving remote revision. Record the resolved tokenizer identity with the server model revision.

## Four experiments worth teaching

First sweep concurrency while fixing lengths, mode and cache policy. Then sweep input length at fixed output length and low load. Next compare eager and the default graph/compilation behavior with appropriate warmup. Finally compare cold and warm prefix-reuse workloads with deliberately shared prefixes, unrelated-prefix controls, and cache-hit evidence.

For a cold-cache experiment, restart or use a verified reset mechanism and document what “cold” means. Warm model kernels and cold prefix state are independent axes. Identical random seeds across repeated benchmark runs may accidentally create prefix reuse; an explicit no-cache baseline prevents that confound.

For each comparison, use at least three measured repetitions as a starting classroom requirement, alternate A/B order where practical, report variability, and inspect failure counts. A tiny 64-request pilot does not justify confident p99 claims. Increase samples before interpreting tails.

## Interpretation

Increasing a batching token budget may improve device efficiency while delaying some requests. Prefix caching primarily removes repeated input work; it does not make future novel decode tokens free. Faster device compute can expose CPU or transport bottlenecks. A result can improve average throughput while worsening a latency objective. State the tradeoff rather than declaring an unconditional winner.

## Exercises and acceptance

Submit `templates/EXPERIMENT_REPORT.md` with a prediction, fixed variables, raw JSON, repetitions, failure counts and a negative control. Explain one alternative cause for an apparent speedup. Without a GPU, submit a complete experimental plan and analyze the supplied toy trace; leave performance fields as unmeasured rather than inventing numbers.

## References

- [S6] [vLLM serving benchmark CLI](https://docs.vllm.ai/en/latest/cli/bench/serve/)
