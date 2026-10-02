# Publication backlog

These are prepared tasks, not issues created on GitHub. The archive contains no automated upstream publishing action.

| Priority | Task | Acceptance | Suggested reviewer expertise |
|---|---|---|---|
| P0 | Review all core explanations and numerical examples | Every claim has a derivation, primary source or executed test; scope labels preserved | Inference engineer + educator |
| P0 | Validate a CUDA baseline | Exact image/model pins, selected backend, smoke output, quality/correctness checks, raw benchmark logs | CUDA maintainer |
| P0 | Validate a ROCm baseline | Same evidence plus HIP/Python/wheel correctness and GPU architecture | ROCm maintainer |
| P0 | Run the source checker against pinned vLLM | No missing symbols; record runtime path separately | vLLM core contributor |
| P0 | Reproduce CPU setup in clean Python 3.12 | Tests pass from documented installation, dependency evidence saved | CI maintainer |
| P0 | Trial lessons with two beginners | Record confusing steps and completion evidence; revise before scaling cohort | Instructor |
| P1 | Add CPU vectorized prefill as an optional milestone | Dense/incremental/chunked results remain equivalent; causal masks tested | Model implementation contributor |
| P1 | Add real-vLLM prefix-cache experiment harness | Cold/warm/no-cache and unrelated-prefix controls, hit evidence, repetitions | KV cache contributor |
| P1 | Write one complete backend/graph lab per lane | Runtime mode/dispatch verified; correctness before performance | Backend maintainers |
| P1 | Add one narrow upstream debugging case study | Fixed source/issue history, minimal failure and tested resolution | Relevant code owner |
| P1 | Add CI/docs publication in chosen repository | Hosted CPU CI passes; no public self-hosted GPU execution | Repository administrator |
| P1 | Translate core to Traditional Chinese | Matched source pin, same equations/tests, independent terminology review | Bilingual technical reviewer |
| P2 | Extend parallelism workshop with a tested two-GPU configuration | Topology, per-rank placement, communication and scaling evidence | Distributed runtime contributor |
| P2 | Extend a single connector workshop end-to-end | Exact transport/tier path, completion/lifetime proofs, fault cases | Connector maintainer |
| P2 | Add hybrid/multimodal or vLLM-Omni elective | Own source pin, state inventory and end-to-end correctness | Model / Omni maintainer |

## Recommended first public release

Publish the core only after review and baseline validation. Advertise advanced material as briefs until its executable labs exist. Use a stable source pin for the cohort; keep changing frontier features in optional modules rather than rewriting prerequisites every week.

## Candidate contributor-friendly tasks

Improve an unclear error message only when a real reproduction exists. Add a boundary test near a block-size transition. Clarify a platform-specific install step after reproducing it. Add missing negative controls to an example. Do not manufacture upstream issues merely to give every learner a PR number.
