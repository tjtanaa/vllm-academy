# 12 · Backends, compilation and graph execution

**Material status:** Advanced workshop brief. **Source-check date:** 2026-09-22.

This workshop is a test plan and source-reading assignment, not an implemented graph or kernel extension. Run it only after a hardware-specific baseline passes.

## Learning objective and mental model

Separate the model API, dispatch policy, attention implementation, tensor layout, compiler transformations and execution graph. A flag being accepted proves only that configuration parsing succeeded. The selected path and its numerical behavior still need evidence.

Compilation and graph replay are related but distinct. Compilation may transform operations or generate kernels; graph capture/replay organizes launches under execution constraints. The official graph design describes runtime choices that depend on batch composition and backend capability. Do not label all “graph on” runs as the same experiment, or assume a CUDA Graph-named Python abstraction establishes ROCm feature parity.

## Workshop sequence

Start from a fixed model and identical input token IDs. Capture environment and backend-selection logs. Measure an eager baseline, then one verified graph/compile configuration from the documentation matching the pinned runtime. Warm up each configuration independently and record capture/compilation startup cost separately from steady-state latency.

Compare outputs before comparing speed. Record dtype, tensor shapes, attention mode, cache state, graph mode actually selected and any fallback. Run short/long input and low/high concurrency cases. An unsupported path should be recorded as unsupported for that exact configuration, not generalized to the whole platform.

## CUDA and ROCm porting review

Classify a candidate change as shared host logic, portable tensor code, compiler/backend dispatch, custom kernel, numeric-format-specific code, collective/communication code, or a device memory-transfer path. Then identify the real dependency: warp/wave assumptions, intrinsics, layout, format semantics, synchronization, allocator registration or backend availability.

Use `templates/HARDWARE_MATRIX.md`. Separate **API present**, **backend selected**, **correctness tested**, and **performance measured**. AITER is a useful ROCm investigation target, but its version, architecture support and selected operation must be recorded; its name is not a universal enable-all switch.

## Acceptance artifact

Submit a dispatch diagram, one correctness comparison, three measured repetitions per chosen mode when hardware is available, and a portability assessment. Without the GPU, provide a source-backed test plan and mark execution `not_run`. Do not replace missing evidence with an estimated speedup.

## References

- [S3] [vLLM platform-specific GPU installation](https://docs.vllm.ai/en/latest/getting_started/installation/gpu/)
- [S15] [vLLM CUDA Graph design](https://docs.vllm.ai/en/latest/design/cuda_graphs/)
- [gpu-runner-v2] [vllm/v1/worker/gpu/model_runner.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/worker/gpu/model_runner.py)
