# vLLM Academy roadmap

This roadmap implements the repository owner's three-phase plan. It is a sequence of deliverables and acceptance gates, not a claim that all phases are complete or an automatically scheduled service.

## Phase 1 — Zero → mini-vLLM → first PR

Build a welcoming path for Python/PyTorch developers: serve a first request, understand prefill/decode and KV memory, write dense-reference generation, introduce cached execution and paged storage, schedule multiple requests, add prefix reuse, then trace a pinned production request and prepare a contribution.

The seed provides 12 core lesson drafts, 6 advanced/contributor workshop briefs, the runnable reference implementation, 30 baseline correctness tests, lab scripts and instructor templates. Keep advanced distributed and GPU topics optional for the first cohort.

**Release gate:** a fresh learner can run the documented CPU environment, complete the milestones, explain the toy/production differences, and produce a reproducible finding or small draft PR. Every advertised GPU configuration needs its own recorded run. Review all draft chapters and convert the first-PR brief into a fully taught workshop before calling Phase 1 complete. An actionable bug report can be a better outcome than a low-value upstream PR.

## Phase 2 — Explain abstractions and optimizations at each vLLM version

Maintain a release index, plus focused deep dives. Each reviewed release identifies its exact commit, previous comparison point, relevant upstream PRs, changed abstractions, motivation, behavior, correctness invariants, constraints and evidence. Explain the mechanism rather than repeat the release notes.

Use a compact entry when a release has no new teaching-relevant core concept; do not omit it silently. Use separate deep dives for important changes. Cover scheduler, engine orchestration, model runner, KV ownership/layout, attention backends, graph execution, model/hybrid-state support and distributed interactions when relevant. Keep CUDA and ROCm support/performance evidence separate.

**Release gate:** every published release entry has immutable before/after references or is clearly marked as an initial baseline; claims link to implementation evidence; untested observations are not presented as benchmark results. The initial v0.29.0 note is a baseline map, not a completed historical survey.

## Phase 3 — Evolve mini-vLLM with new engine/core/runner concepts

Keep `mini_vllm/` as the current readable implementation. Represent past teaching versions with Git tags after review, not copied engines scattered across version directories. Keep the introductory learning route reproducible at a frozen cohort tag while development proceeds on `main` and review branches.

For a new upstream concept, first write a Phase 2 explanation. Decide whether the concept belongs in the common toy path, an optional lab, a source-reading note only, or a deferred backlog entry. A deliberate simplification is acceptable when its invariant and limitations are explicit.

**Release gate:** the selected mechanism is explained, covered by dense-reference or lifecycle tests, connected to a pinned upstream implementation, and recorded in the version manifest. Hardware-dependent claims require separate evidence. Do not equate a new upstream tag with a mandatory toy-engine bump.

## Release intake workflow

`New upstream release → pin and compare → classify changes → write release note → choose teaching adaptation → implement/test → human review → update manifest → tag teaching release`

This workflow is manual initially. A future watcher may open a review issue or draft PR, but must not silently change curriculum baselines, publish performance claims, or promote an engine release. No scheduled monitoring is installed by this bootstrap.

## Immediate backlog

| Priority | Deliverable | Acceptance evidence |
|---|---|---|
| P0 | Review Phase 1 prose, exercises and reference code | Named reviewer and passing clean-environment checks |
| P0 | Validate one CUDA and one ROCm serving lane | Version/image/model pins, actual backend, raw smoke and benchmark results |
| P0 | Teach the first-PR workshop end to end | Reproduction, failing test, focused patch and review exercise |
| P1 | Select the historical starting release for Phase 2 | Explicit coverage window; no implied completeness |
| P1 | Complete the first before/after architecture deep dive | Exact commits, implementation/PR links, invariants and trade-offs |
| P1 | Select the first new mini-vLLM concept | Approved evolution proposal and regression tests |
| P2 | Publish a reviewed cohort snapshot and offline/site edition | Reproducible build, version manifest and release notes |
| P2 | Consider supervised upstream tracking automation | Explicit opt-in, review-only output, no autonomous merges |
