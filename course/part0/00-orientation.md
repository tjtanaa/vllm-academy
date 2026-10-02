# 00 — The contract of an inference engineer

**Material status:** Core lesson draft. **Source-check date:** 2026-09-22.

A service that returns one plausible sentence has passed a smoke test, not a correctness proof or a throughput evaluation. This course starts by distinguishing those claims. You will make a small system understandable before trying to make a large system fast.

## Learning objectives

Explain the difference between a model and a serving engine, separate correctness from performance evidence, and prepare a reproducible technical notebook without collecting secrets or private prompts.

## Model versus engine

A model maps token histories to next-token distributions. An engine decides which histories to process, how to store intermediate state, when to launch computation, which device implementation to use, and how to return outputs. The user-facing HTTP server is only one part of that engine.

For a request, distinguish the prompt's text, its token IDs, model inputs after processing, cached state, generated token IDs, and decoded output text. A tokenizer mismatch can change the computation before a GPU kernel runs. A scheduler bug can select the wrong work even when every matrix multiplication is correct. A lifetime bug can corrupt a perfectly correct cache representation.

Our first invariant is therefore broader than “the model works”: a given request must receive output from its own token history and compatible model state, with no accidental cross-request mutation or reuse.

## The evidence ladder

A smoke test demonstrates that a selected path starts and returns a response. A numerical test compares a defined computation against a reference with a stated tolerance. An end-to-end test checks a workflow under realistic request and cancellation behavior. A benchmark measures a declared workload. A portability report repeats the relevant correctness and execution checks on a different backend. None substitutes for the others.

Use `results/validation.json` as an example of honest scope. CPU tests of this tutorial do not validate the release, installation, GPU kernels, network transport, or distributed behavior of real vLLM.

## Lab: establish your notebook

Create a notebook using `templates/EXPERIMENT_REPORT.md`. Record a prediction before running an experiment. For the first experiment, predict whether reusing an exact prefix should alter greedy output IDs. Run `python -m mini_vllm.demo`, inspect `results/toy-trace.json`, and compare the prediction with the trace.

Record commands exactly. Do not collect your entire shell environment; it may contain access tokens. The included environment collector intentionally captures only technical fields. Keep human names, private conversation data, and proprietary prompts out of public bug reports unless separately authorized and necessary.

## Responsible contribution

Understand and review what you submit, including generated code. Report actual tests, not tests a tool suggested. Avoid submitting a cosmetic patch merely to obtain a contribution badge. A good reproduction, corrected technical explanation, or regression test can be more valuable than a large new abstraction.

The upstream contribution guide is the authority for current DCO, formatting, testing, and AI-assistance disclosure requirements. Read it immediately before submitting; this course does not freeze community policy forever.

## Exercises and acceptance

Explain why an identical answer to one prompt is insufficient to validate prefix caching. Name a test for incorrect page ownership. Describe a useful contribution that does not require a GPU. Your notebook passes when another learner can distinguish measured observations from predictions and run the same mechanism test without private context.

## References

- [S7] [vLLM contribution guide](https://docs.vllm.ai/en/latest/contributing/)
- [S1] [Tutorial inspiration: zero-to-sglang](https://github.com/datawhalechina/zero-to-sglang)
