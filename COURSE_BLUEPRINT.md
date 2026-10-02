# Course blueprint: vLLM Academy — Phase 1

This is the Phase 1 teaching blueprint. The repository-wide three-phase plan is in [ROADMAP.md](ROADMAP.md).

## The course promise

A learner should finish able to explain where a request spends time, construct and test a small KV-aware generation engine, locate the corresponding production vLLM components, and prepare a useful issue or patch with reproducible evidence. The outcome is engineering competence, not memorizing launch flags or collecting superficial pull requests.

The assumed reader knows Python, elementary PyTorch, matrices, and basic Git. CUDA/HIP programming, distributed training, and a large GPU are not prerequisites for the beginner sequence. Instructors who know vLLM should resist starting with their favorite advanced model: the first causal-attention example should be small enough to reason about completely.

## What to preserve from the reference course

Preserve its staged transition from concepts to construction to production-source reading and contribution. Preserve exercises, a consistent chapter structure, a community notes area, and reviewable source references. Its README describes an evolving course, with later sections still under development when inspected; this package does not assume that a finished SGLang book can simply be translated.

What changes is the technical center. Use vLLM's token-work scheduler, logical-to-physical KV mapping, full-block hash-based prefix reuse, engine/worker separation, and backend selection. Do not teach RadixAttention as vLLM's cache structure. Do not use a historic V0 request path as an unqualified description of current execution. A short historical note is useful; a stale architectural diagram is not.

## Three complementary learning surfaces

**Mechanism labs.** The small engine isolates invariants. A learner can inspect every token, block reference, schedule decision, and generated output on a CPU. The reference intentionally trades speed for visibility.

**Production labs.** A small pretrained model served by real vLLM gives the learner an operational baseline. The same workload is exercised on a separately validated CUDA or ROCm environment. Students record backend selection rather than infer it from a model name or a launch command.

**Contributor workshops.** Students start from a reproduction, identify ownership boundaries, write a failing test, make the smallest useful change, and explain evidence and limitations. A technically useful issue with a clean reproduction can satisfy the course even when a PR is not yet justified.

## Recommended launch scope

Publish the first cohort as the 12 core lessons and a selected advanced workshop. Keep the remaining briefs visible as briefs, rather than advertising a completed textbook on every backend, MoE architecture, and storage connector.

Use a small public model for real serving, the random-weight toy for mechanism correctness, and a larger model only after students can interpret their baseline. Avoid making an eight-GPU system the price of admission.

A reasonable teaching format is an eight-week cohort, two meetings per week: one conceptual/code-reading session and one lab/review session. These are curriculum allocations, not promises about how quickly every student will master inference. An accelerated workshop can select lessons 01, 04, 06, 07, 08, 09 and 11, but must not claim to cover the full contributor track.

## Weekly sequence

| Week | Main work | Evidence produced |
|---|---|---|
| 1 | Orientation, real server, inference phases | Environment manifest, smoke response, request lifecycle explanation |
| 2 | Hardware model, KV accounting, metrics | Memory calculation and a controlled measurement plan |
| 3 | Dense decoder and incremental execution | Logit-equivalence tests across token positions |
| 4 | Paged storage and scheduling | Noncontiguous-page test and bounded token-budget trace |
| 5 | Prefix reuse and integration | Cold/warm equivalence, eviction and cancellation checks |
| 6 | Pinned vLLM source walkthrough | Annotated request-to-worker trace and component map |
| 7 | One hardware or distributed workshop | Correctness evidence plus a performance/compatibility report |
| 8 | Debugging and contribution review | Reproduction, failing test, patch or actionable issue |

## Assessment

Use a 100-point rubric: mechanism correctness 35, experimental design 25, source understanding 20, communication and contribution quality 20. Require correctness and safety of resource ownership independently of the score. A fast result produced by leaking blocks or ignoring failed requests cannot pass.

For learners without a GPU, the core mechanism tests and source-reading exercises are fully meaningful. They submit a benchmark plan instead of fabricated performance data. A recorded trace supplied by an instructor can support analysis, but must be labeled as instructor data.

## Your maintainer role

Use your vLLM/ROCm experience at review boundaries: selecting realistic reproductions, explaining why a change belongs in a backend instead of a global path, comparing functional with performance parity, and showing what makes a PR reviewable. Guest reviewers can cover scheduler, model, or kernel topics without making you the sole author of every chapter.

The distinctive course should be **vLLM-first and hardware-aware**, not an AMD-only deployment cookbook. Teach shared concepts once. Give CUDA and ROCm separate evidence lanes. A ROCm adaptation should be evaluated as a behavior-and-backend problem, not as a mechanical replacement of `cuda` with `hip` in Python.

## Course governance

Every chapter has a named reviewer, source pin, runnable command or explicit workshop-only status, expected observations, failure cases, and acceptance criteria. Every performance claim includes workload shape, length distributions, arrival process, cache state, output length policy, hardware/software versions, raw results, and repetitions. Educational code stays small; production-quality extensions should move to a separate project or upstream rather than bury the course in infrastructure.

Use the issue backlog and templates included in this package to distribute work. Do not auto-open upstream issues, publish benchmarks, or submit AI-assisted code without a human review of every relevant line and the currently applicable contribution rules.

## References

The design is original. Reference-course structure: [S1](https://github.com/datawhalechina/zero-to-sglang). vLLM prefix caching: [S4](https://docs.vllm.ai/en/latest/design/prefix_caching/). Current contribution expectations: [S7](https://docs.vllm.ai/en/latest/contributing/). Source pin and inspected excerpts: [source map](maintainers/source-map.json).
