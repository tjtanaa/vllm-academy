# Version, alignment and evidence policy

## Three distinct versions

| Identity | Meaning | Current seed |
|---|---|---|
| Academy content version | Reviewed curriculum snapshot and learning route | `0.1.0-dev`; no release tag created |
| mini-vLLM version | Educational implementation/API | `0.1.0` |
| Upstream source reference | Exact vLLM code being explained | `v0.29.0` / `98dff2a81d747d1dba01a47f939f48c3526d4206` |

The authoritative mapping is [versions/manifest.json](versions/manifest.json). It must agree with `mini_vllm.__version__`, `pyproject.toml`, the release-note paths and the source map. `python labs/check_versions.py` validates those local relationships. It does not query upstream, verify the semantic explanation, or prove compatibility.

The upstream tag mapping was rechecked on 2026-10-02. It is a source-reading baseline, not a claim to represent the latest vLLM release. Previously imported source-check dates and test records retain their original provenance. Fresh execution is recorded separately in `results/bootstrap-validation.json`.

## Version changes and frozen cohorts

Use a patch change for a compatible teaching-code fix, a minor change for a backward-compatible concept/lab addition, and a major change for a breaking teaching API or exercise migration. Pre-1.0 development may use minor bumps for breaking changes only when the changelog explicitly calls them out. Source-note-only changes do not require a mini-vLLM bump.

Keep `main` as reviewed development and use PR branches for new concepts. Tag a reviewed curriculum as `academy-vX.Y.Z` and a reviewed teaching engine as `mini-vX.Y.Z`; create those tags only after acceptance. A cohort records its frozen tag and upstream pin so active assignments do not drift. No release/cohort tags are created by the initial import.

## Every upstream release gets an explicit disposition within the chosen coverage window

Record one of: pending review, source-only analysis, proposed toy adaptation, implemented adaptation, or no teaching-relevant change. Do not imply complete history before a coverage window has been selected and its index filled. Important transitions deserve a deep dive; small releases can link a compact reviewed disposition.

Each adaptation links both the Phase 2 explanation and Phase 3 proposal, identifies source symbols and immutable commits, records intentional omissions, and updates affected exercises/tests. A future watcher may propose an issue or draft PR, not merge or promote changes by itself.

## Promotion gates

A teaching release needs passing CPU tests, course/link and version-manifest checks, current source references, a human technical review, a readable size/scope review, migration notes and explicit evidence status. A production/GPU claim additionally needs execution on the advertised hardware/software combination. Passing a toy test does not satisfy that gate.

For each CUDA or ROCm lane record driver, image digest, vLLM/PyTorch/runtime/Triton/AITER versions as applicable, model/tokenizer revisions, GPU architecture and the backend actually selected. Keep independent environments; do not install a CUDA wheel into a working ROCm stack. Never infer performance parity from API compatibility.

## Evidence labels

| Label | Meaning |
|---|---|
| CPU-tested | Actual execution of the recorded educational code in the recorded CPU environment. |
| Source-checked | A source or documentation reference was inspected; runtime execution is not implied. |
| GPU recipe, unverified | Prepared commands without an attached GPU execution record. |
| Workshop brief | A teaching plan/acceptance criteria, not an implemented toy feature. |
| Pending review | Proposed material or mapping not yet promoted by a reviewer. |

Retain failures and exclusions. Record command, environment, commit/file hashes, raw outputs and hardware separately from anticipated effects. Do not change `not_run` to `supported` because another backend's CI passed.
