# 03 — A hardware model that guides experiments

**Material status:** Core lesson draft. **Source-check date:** 2026-09-22.

“GPU utilization is high” does not identify the limiting resource. An inference path may be limited by arithmetic, device memory traffic, launch overhead, synchronization, communication, or host-side scheduling. Build a rough cost model, then use measurements to refine it.

## Learning objectives

Use arithmetic intensity as a hypothesis, distinguish latency from throughput, and describe the CUDA/ROCm boundary without assuming a Python API name determines the hardware implementation.

## A useful lower bound

For a selected operation, estimate work `F` in floating-point operations and data movement `D` in bytes. If the relevant attainable arithmetic rate is `C` and attainable bandwidth is `B`, a simple lower bound is `max(F/C, D/B)`. Arithmetic intensity is `F/D`. This is a model of a chosen scope, not a proof of real latency: launch costs, dependencies, imperfect occupancy, caches, and synchronization can dominate.

For a matrix multiplication with dimensions `M × K` and `K × N`, a conventional multiply-add count is approximately `2MKN`. A minimal operand/output byte estimate depends on dtype and reuse. Counting each weight once may be reasonable for one idealized operation but wrong for an entire execution with multiple launches or cache misses. Always name the scope of the byte count.

Prefill often presents more reuse opportunities than a single-request decode step. A larger decode batch can also increase useful reuse. “Prefill is compute-bound and decode is memory-bound” is a helpful starting hypothesis, not a law across every model, batch size, GPU and kernel.

## Host and device timelines

A CPU can enqueue work before the device finishes it. A wall-clock timer around enqueueing measures a different quantity from synchronized device execution. Conversely, synchronizing after every operation can destroy the overlap you intended to measure. Use device events for isolated kernel timing and a correctly defined wall clock for an end-to-end service experiment. Record when synchronization occurs.

In a serving system, a good kernel microbenchmark can coexist with bad user latency because requests are queued, tokenized slowly, scheduled poorly, or waiting on remote data. A GPU optimization is useful only when its improved work lies on a consequential path of the target workload.

## Hardware lanes, shared semantics

The same high-level PyTorch program can execute through different backends, but an optimized kernel, dtype, layout, graph path, or collective may have hardware-specific constraints. On ROCm, seeing `torch.cuda` in Python is normal. A name-based search for CUDA is therefore only a first hint, not a portability audit.

The course uses separate evidence for NVIDIA CUDA and AMD ROCm, with MI300-class and MI350/MI355-class configurations treated as separately tested targets when available. Do not claim all AMD architectures behave identically. The foundational CPU implementation establishes a reference behavior; it does not establish GPU performance parity.

## Lab: make a bottleneck prediction

Before benchmarking, predict what changes when you increase concurrent requests while fixing input/output lengths. Predict what changes when you increase context while keeping concurrency low. Write down a competing explanation for each prediction: for example, improved weight reuse versus increased queueing and KV pressure.

Use the real-vLLM benchmark lesson to test those predictions. Do not report CPU timings of the tiny Python engine as evidence about GPU serving efficiency. Its dense gathers and per-token Python loops are intentionally unsuitable for that comparison.

## Exercises and acceptance

Give one scenario in which improving an attention kernel would not improve TTFT. Explain why forcing a backend without recording the selected implementation weakens an experiment. Calculate a simple roofline lower bound with explicitly hypothetical rates and compare it with an observed operation only after naming all omitted costs.

## References

- [S3] [vLLM platform-specific GPU installation](https://docs.vllm.ai/en/latest/getting_started/installation/gpu/)
- [S6] [vLLM serving benchmark CLI](https://docs.vllm.ai/en/latest/cli/bench/serve/)
