# 17 · Turn a finding into a useful contribution

**Material status:** Advanced workshop brief. **Source-check date:** 2026-09-22.

The course should produce engineers who reduce uncertainty for maintainers, not a queue of superficial pull requests. A well-reproduced bug, an accurate source explanation or a small tested fix can be a strong outcome.

## Learning objective and mental model

Move from observation to hypothesis, minimal reproduction, failing test, scoped change and reviewable evidence. Distinguish a correctness fix, a performance optimization and an unsupported-feature proposal.

## Start with a real question

Choose an issue discovered during the labs: unclear installation behavior, a misleading example, missing boundary coverage, an unsafe lifetime condition, or a measurable dispatch/performance problem. Search existing issues and recent changes before duplicating work. An exercise does not obligate you to open an upstream PR; a local investigation report can be the correct result.

For a performance problem, profile only after establishing the relevant baseline. Identify where time is spent and how measurement was performed. A kernel may be slow in isolation yet irrelevant to end-to-end latency; a CPU bottleneck may dominate despite fast kernels. Keep startup, warmup, steady-state and tail behavior separate.

## Construct the evidence package

Record the source SHA, environment, exact commands, input shape/token lengths, expected behavior, actual behavior, and a small reproduction. Remove private prompts, credentials and sensitive logs. For a fix, add a regression test that fails before the change and passes after. For an optimization, retain correctness tests and report workload coverage, repetitions, regressions and the observed execution path.

Use `templates/PR_REVIEW.md`. Explain whether a change is hardware-neutral, CUDA-specific, ROCm-specific, or shared logic with platform-dependent kernels. A “portable” label is a testable claim, not a substitute for identifying dependencies.

## Follow the actual project's current workflow

Read the official vLLM contribution guide immediately before contributing. The inspected guide covers formatting/tests, DCO sign-off, and expectations for AI-assisted contributions, including human responsibility and disclosure. Do not assume that this course's own CPU CI replaces upstream tests or that any maintainer has preapproved the patch.

A normal local workflow is to create a branch, make a focused change, run the relevant tests and formatting checks, review the diff, and prepare a commit with the required sign-off. Commands such as `git commit -s` add an attestation: use them only when you can make that attestation honestly. Include the current AI-use disclosure required by the project rather than hiding how a contribution was prepared.

## Review and collaboration exercise

Exchange reports with another learner. The reviewer should try to reproduce the result and challenge one assumption. Ask for changes only when you can explain the failure, risk or missing evidence. Keep personal criticism out of technical review. When feedback reveals a mistake, update the claim and the test instead of defending the original conclusion.

## Acceptance artifact

Submit a reproducible finding, a proposed or implemented narrow change, tests, and a draft review description. Upstream submission is optional; the maintainer still decides whether the issue and approach belong in the project. Grade correctness, evidence and communication, not the number of PRs opened or whether a PR happens to merge during the course.

## References

- [S7] [vLLM contribution guide](https://docs.vllm.ai/en/latest/contributing/)
- [S6] [vLLM serving benchmark CLI](https://docs.vllm.ai/en/latest/cli/bench/serve/)
