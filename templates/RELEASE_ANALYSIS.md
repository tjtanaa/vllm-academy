# vLLM <version> — <abstraction or optimization>

**Status:** pending review / baseline map / source-checked / experimentally validated.
**Upstream target:** exact tag and full commit. **Comparison base:** exact prior commit, or explicitly none for the first baseline.
**Author/reviewer:** unassigned until accepted. **Evidence date:** actual inspection/execution date.

## Problem and workload

What bottleneck, correctness issue or engineering constraint motivated the change? Describe the workload shapes and relevant platform. Distinguish source-stated motivation from your inference.

## Before → after

Trace one request through both pinned implementations. Include responsibility boundaries, data structures, interfaces, token accounting, KV/state ownership and the selected execution path. Use permanent source links and introducing PRs. Do not infer a runtime-selected runner solely from a filename.

## Mechanism and invariants

Explain what computation, allocation, transfer, synchronization or metadata construction is removed or rearranged. Identify the invariant that keeps it correct. Cover cancellation, failure and buffer reuse when applicable. Include a small example and a counterexample that would fail.

## Trade-offs and compatibility

State intended benefits, overheads, restrictions, fallback paths, configuration/default changes and affected tests. Treat CUDA and ROCm separately: API present, backend selected, correctness run, performance measured. Mark missing evidence explicitly.

## Experiment or source-only evidence

Record exact commands, hardware/image/package/model pins, workload, warmup/cache state, repetitions, raw results and failures. A paper or release-note number is not a reproduced result. With no hardware run, label this section source-only and provide a falsifiable experiment plan.

## mini-vLLM disposition

Choose core adaptation / optional lab / source-only / deferred / no teaching-relevant change. Explain why it improves the course and what remains simplified. Link a Phase 3 proposal and affected chapters/tests. Add the version manifest entry in the same change.

## References and review

Link target/base commits, relevant PRs, implementation symbols and tests. Confirm every claim against the cited revision; list unresolved questions separately. A reviewer approves source interpretation independently of whether the scripts pass.
