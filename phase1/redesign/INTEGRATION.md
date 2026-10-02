# Integrate without discarding existing work

## Non-destructive starting point

This supplement lives in `phase1/redesign/` of the Academy checkout. Its `labs/`, `tests/` and project settings remain scoped there. Do **not** overlay its lab namespace or `pyproject.toml` onto the repository root. The supplement's lab modules are distinct from the existing native mini engine.

Run from that directory:

```bash
cd phase1/redesign
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m pytest -q
```

The publication change uses a separate documentation/lab review branch. Its source-map metadata records the Academy commit observed during preparation, not a requirement to overwrite newer work.

## Entry-point integration

The existing `phase1/README.md` links to `redesign/CURRICULUM.md` and preserves the old `course/partN` sequence for existing cohorts. Do not describe lesson drafts as reviewer-approved. Pilot the revised sequence before making it the default.

## Mapping from the original chapters

| Existing material | Revised use |
|---|---|
| Orientation / first server | Lesson 00 preview and lesson 10 API/operational revisit; no early installation wall. |
| Inference / hardware / KV / measurement | Distribute across 03–08 and 16, adding an experiment before each next abstraction. |
| Tiny decoder and engine implementation | Preserve as reference implementation; introduce new minimal tensor and training labs first. |
| Paging / scheduling / prefix reuse | Lessons 07–08 refer to existing engine tests; do not create a second production-style engine. |
| Source walkthrough | Lesson 09 expanded through frontend, renderer, multimodal processing and return path. |
| Advanced attention / quantization / parallelism | High-level distinctions in Phase 1; performance implementations remain electives/Phase 2–3. |
| Contribution workshop | Lesson 17 with an explicit bounded artifact and reviewer checklist. |

## Source-version rules

Keep the existing v0.29.0 baseline and this October 2 main snapshot as distinct records. The supplement pin is `b558f160a2c0abcb5902acc3c91a14c38a4af173`; it is not a release tag. Update the central manifest only in a reviewed change that explains which source-reading claims moved. File existence alone is not runtime dispatch evidence.

The new map distinguishes excerpts actually inspected from symbols only located. A future source update should check that the contract still exists, not merely adjust line numbers. Capture model runner selection and deployment configuration in real execution records.

## Reviews before promotion

Have a frontend reviewer check API/render/derender semantics, a multimodal reviewer check preprocessing/encoder/placeholder boundaries, and a core reviewer check scheduling/cache/runner descriptions. A model reviewer owns the two native checkpoint gates. One instructor should pilot at least the naive decoder, rendering and vision lessons with a learner before assigning a cohort tag.

No upstream PRs, scheduling jobs, tags or automated merges are created by these instructions. Future Phase 2 notes should explain changed contracts; Phase 3 adaptations should link both an explanation and a small regression test.

## Build outputs and CI

The source commit retains SVG/DOT diagrams; PNG images and the aggregated HTML/Markdown handbook are reproducible outputs rather than duplicate tracked files. Run `python figures/render.py` with Graphviz installed to regenerate figures, and `python build_handbook.py` with Mistune installed to build the reading copies. The scoped CI job runs from this directory, independently of the root test namespace, then builds and uploads the handbook with the figures.
