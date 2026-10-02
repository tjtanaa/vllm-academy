# Phase 2 — How vLLM evolves

Explain the abstraction and optimization approaches in each reviewed vLLM version: what problem changed, how the design responds, and which new constraints it creates. This is an architecture history and source-reading track, not a list of release-note headlines.

## Release index

| Upstream version | Comparison | Material | Status |
|---|---|---|---|
| v0.29.0 | Initial source-reading baseline; no prior-release diff claimed | [Baseline map](releases/v0.29.0.md) | Source baseline only; no GPU validation |

The index is deliberately incomplete. Select and record a historical coverage window before advertising coverage of every release. Add a compact entry even when a reviewed release has no new core concept worth a full chapter. For an important transition, link a deeper article from the relevant release entries.

## Questions every release analysis answers

Start with the workload or engineering pressure: compute, memory bandwidth/capacity, dispatch overhead, queueing, cache reuse, synchronization, or maintainability. Identify the old responsibility boundary and the new one. Trace a request and its state through both implementations.

Then cover scheduler/token accounting, engine↔runner interfaces, KV ownership/layout, attention metadata/backends, graph or eager execution, failure/cancellation behavior and distributed interactions where they actually changed. State the intended benefit and costs. Separate algorithmic reasoning from measured performance, and separate CUDA from ROCm validation.

End with one educational decision: adapt mini-vLLM, add an optional lab, keep the topic source-only, or defer it with a reason.

## Authoring workflow

Use [the release-analysis template](../templates/RELEASE_ANALYSIS.md), immutable commit links, and [the version manifest](../versions/manifest.json). A current `main` link can help navigation but must not serve as the evidence pin. A renamed file alone is not evidence that the runtime selected a different runner.

Every comparison must identify both refs and which upstream PRs introduced the behavior; do not infer introduction dates merely because a symbol exists at the later ref. The release note should make clear whether it is a source inspection, an executed experiment, or an unresolved hypothesis.
