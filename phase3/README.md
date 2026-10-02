# Phase 3 — An evolving mini-vLLM

The goal is to keep the teaching engine aligned with important ideas in new vLLM engine/core/runner designs while keeping it readable. Alignment means a documented concept and invariant, not a line-for-line fork or production API compatibility.

## Current teaching implementation

`mini_vllm/` is version `0.1.0`. Its [manifest](../versions/manifest.json) maps it to the course's source-reading baseline, not to a certified runtime-compatibility range.

| Concept | Current teaching status |
|---|---|
| Dense reference and incremental KV | Implemented with equivalence tests |
| Noncontiguous pages and explicit ownership | Implemented with lifecycle tests |
| Token-budget scheduling and arrivals | Implemented as serial logical scheduling, not physical GPU batching |
| Complete-block prefix reuse | Implemented; private incomplete tails, no copy-on-write |
| Completion and cancellation cleanup | Implemented; no asynchronous GPU work |
| Runner/core process separation and overlapped execution | Not implemented; candidate future teaching extension |
| Graph dispatch, speculation, hybrid KV/state, distributed transfer | Source/workshop topics; not implemented in the toy |

## Adaptation choices

For each important upstream change, select one of four outcomes: a small core-engine adaptation, an optional isolated experiment, a source-only explanation, or an explicitly deferred topic. Avoid adding every hardware/backend detail to the beginner implementation.

Use [the evolution proposal](../templates/ENGINE_EVOLUTION.md). State the motivation, upstream commit and symbols, old/new toy dataflow, correctness invariant, deliberate simplifications, regression tests and impact on the beginner lessons. Include failure or cancellation behavior when lifetime changes. Show before/after evidence for any performance claim; otherwise describe expected effects as hypotheses.

## Versioning model

Keep academy content versions, mini-vLLM implementation versions, and upstream vLLM refs distinct. Publish reviewed snapshots with descriptive Git tags such as `academy-v0.1.0` and `mini-v0.1.0`; these names are a policy, not tags already created. Develop future adaptations in PR branches. Do not duplicate the entire teaching engine for every upstream release.

A new upstream release does not automatically require a mini-vLLM version bump. Record `source-only` or `no teaching-relevant change` when appropriate. When a new abstraction changes public teaching APIs or invalidates exercises, explicitly migrate the lessons and preserve the old cohort tag. The [version policy](../VERSION_POLICY.md) defines promotion gates.

## Keeping up without destabilizing the course

Review new upstream releases and relevant engine/runner changes. First update the Phase 2 evidence, then implement selected concepts, run CPU regression checks and required hardware experiments, and obtain human review. Update the manifest and changelog in the same PR as the adaptation. Automatic discovery may eventually assist this workflow; automatic merging is not part of the plan.
