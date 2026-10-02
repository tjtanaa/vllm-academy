# 13 · Change the bytes or change the work

**Material status:** Advanced workshop brief. **Source-check date:** 2026-09-22.

Quantization and speculative decoding both aim to change inference cost, but they change different contracts. This workshop keeps those contracts explicit instead of treating both as generic “speedup flags.” Neither is implemented in the tiny engine.

## Quantization: specify the representation

Start with a named, documented checkpoint and backend combination. Record what is quantized: weights, activations, KV, or some combination. Record format, scale granularity, scale dtype, calibration provenance and computation/accumulation behavior. “FP8” or “INT4” alone is not a complete configuration.

Evaluate memory footprint, output quality and performance separately. A smaller checkpoint does not by itself prove lower serving latency, and a hardware format name does not establish availability of the required kernel for that model. The official quantization documentation includes an implementation/hardware matrix; recheck its underlying backend for the exact revision and GPU.

For the workshop, compare the chosen quantized model with an appropriate reference on a fixed evaluation subset and a separate systems workload. State tolerances or quality acceptance before running. Do not compare a different model/checkpoint and attribute every change only to numeric precision.

## Speculation: propose, verify, commit or discard

A speculative path generates candidate tokens and verifies them using the target path. The draft length is not the accepted length. Rejected work creates bookkeeping obligations for token counts and model/cache state. Distinguish an algorithm intended to preserve the target sampling distribution from a heuristic or deliberately modified sampling policy; exact equivalence is not a universal property of every option called speculative decoding.

A simple reasoning model is:

```text
amortized time per emitted token
  = (draft time + verification time + bookkeeping time)
    / expected committed output tokens per cycle
```

This equation organizes measurements; it is not a device performance prediction. Larger drafts can raise verification cost and memory pressure. Acceptance rates depend on the workload and method. Concurrent serving can change whether a low-concurrency benefit survives.

## Exercises and acceptance

For quantization, submit an exact representation/backend description and separate quality and systems reports. For speculation, trace one all-accepted cycle and one partially rejected cycle, including which cache/token state is committed. Identify how the production scheduler's speculative bookkeeping exceeds the toy's model.

The optional GPU exercise uses one method explicitly supported by the selected release and model. Record the method, draft/target identities, actual acceptance statistics, correctness criterion, and latency/throughput under two load levels. No speculative implementation or checkpoint is bundled here.

## References

- [S13] [vLLM quantization and hardware support](https://docs.vllm.ai/en/latest/features/quantization/)
- [S14] [vLLM speculative decoding](https://docs.vllm.ai/en/latest/features/speculative_decoding/)
- [scheduler] [vllm/v1/core/sched/scheduler.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/core/sched/scheduler.py)
