# Hardware and portability evidence — template

A row describes one exact feature/configuration. Do not mark a vendor “supported” from a single passing model or a configuration flag. Preserve `not_run`, `not_applicable`, `failed`, and `unsupported_at_pin` as distinct states.

| Feature / input shapes / dtype | Source pin | CUDA GPU + stack | ROCm GPU + stack | API present | Backend actually selected | Correctness evidence | Performance evidence | Missing dependency / action |
|---|---|---|---|---|---|---|---|---|
| Teaching dense/cache reference | This archive | not_run | not_run | Implemented in PyTorch | CPU eager locally | `results/validation.json` (CPU only) | not measured | GPU evidence still required |
| Real-vLLM baseline server | Choose runtime pin | not_run | not_run | Recipe prepared | not_run | not_run | not_run | Instructor must validate image/model |
| Candidate feature | Fill | not_run | not_run | unverified | unverified | not_run | not_run | Identify dependency before estimating effort |

## Porting assessment dimensions

**Shared logic:** scheduler policy, metadata or Python state changes. Inspect device assumptions despite shared placement.

**Tensor/compiler code:** operators, dtypes, strides, shapes and compiler behavior. Successful compilation does not prove numerical correctness or performance.

**Custom kernels:** intrinsics, warp/wave assumptions, memory layout, reductions, synchronization and architecture constraints.

**Quantization:** representation, scales, conversion semantics, accumulation, checkpoint metadata and kernel support.

**Communication and offload:** topology, transport, registration, completion ordering, staging, ownership and error propagation.

## Effort statement

Identify the smallest missing dependency, the likely change scope, available tests, hardware access and the largest unknown. Qualitative categories such as configuration/test-only, localized implementation, backend/kernel work, and architectural work are preferable to invented day estimates. Label the assessment provisional until a proof of concept runs.
