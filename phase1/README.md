# Phase 1 — Zero → mini-vLLM → first PR

The stable introduction to inference-engine engineering. Start from a working request and end with a useful, reviewable contribution, not a collection of copied launch commands.

## Revised theory-to-practice route — draft

The [redesigned Phase 1](redesign/README.md) interleaves LLM history and model theory with CPU labs, source reading, and practical request-lifecycle exercises. It adds API families, rendering/derendering, multimodal input processing, vision-to-language computation, and deployment boundaries to the beginner route.

Start with the [curriculum and pacing](redesign/CURRICULUM.md), then revisit the [architecture atlas](redesign/ARCHITECTURE_ATLAS.md) as the lessons progress. The supplement includes 18 lesson drafts, 44 locally passing CPU tests, four editable diagrams, cited references and an instructor guide. [Validation records](redesign/VALIDATION.md) distinguish those tests from unperformed integration work.

The native Llama-3.2-1B and Qwen3-0.6B demos remain [required acceptance gates](redesign/MODEL_ACCEPTANCE.md). Their separate pretrained-engine patch is not included in this curriculum change, and full-checkpoint/GPU execution is not claimed. Keep the original route below for existing cohorts while the redesign is reviewed and piloted.

## Learning sequence

| Step | Materials | Evidence to submit |
|---|---|---|
| Orientation and first server | [00](../course/part0/00-orientation.md), [01](../course/part0/01-first-server.md) | Environment record and smoke response; CPU-only learners can defer the server lab |
| Inference foundations | [02](../course/part1/02-inference.md), [03](../course/part1/03-hardware.md), [04](../course/part1/04-kv-memory.md), [05](../course/part1/05-measurement.md) | Token trace, KV calculation and controlled measurement plan |
| Build mini-vLLM | [06](../course/part2/06-tiny-decoder.md), [07](../course/part2/07-paged-kv.md), [08](../course/part2/08-scheduling.md), [09](../course/part2/09-prefix-cache.md), [10](../course/part2/10-engine-integration.md) | Passing numerical and resource-lifetime tests |
| Read production vLLM | [11](../course/part3/11-source-walkthrough.md) | Pinned source map; explain how the toy differs |
| First useful contribution | [17](../course/part4/17-contributing.md) | Reproduction, failing test and focused draft PR or actionable issue |

Read [the syllabus](../SYLLABUS.md) and [build milestones](../labs/MILESTONES.md). Chapters 12–16 are optional systems workshops; the first-PR chapter is also still a workshop brief and needs instructor development. The existing curriculum's `partN` folders are chapter organization, not the repository's three long-term phases.

## Protect the beginner path

Teach one small model and explicit invariants before exposing optimized production paths. Retain a dense reference when introducing cached execution. Label serial logical scheduling separately from physical GPU batching. Keep the first run CPU-friendly and a benchmark plan valid when learners have no GPU.

A cohort should record a reviewed academy tag and upstream source commit. Future Phase 3 changes may improve the teaching engine without silently changing an active cohort's assignments. No frozen cohort tag has been created by the initial seed.

## Completion standard

Explain the mechanism, prove the relevant property with a test, find the corresponding production responsibility, and communicate a useful change. Upstream merge acceptance is not controlled by this course and is not required to recognize good work.
