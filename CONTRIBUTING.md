# Contributing to this course

Discuss curriculum changes before reordering prerequisites. Keep lessons, exercises, source maps and validation labels consistent. This is an independent course; contributing here is not the same as contributing to vLLM itself.

Every content change should answer a concrete learner question. Every code change should state its invariant, add or retain tests, and update the limitation statement if capabilities change. Attribute external material and verify permission/license before importing text, diagrams or code. Do not remove honest `not_run` labels without execution evidence.

```bash
python -m pytest -q
python -m mini_vllm.demo
python labs/check_course.py
python -m compileall -q mini_vllm labs tests
bash -n labs/serve.sh
bash -n labs/bench.sh
```

Use `templates/CHAPTER_TEMPLATE.md` for lessons and `templates/EXPERIMENT_REPORT.md` for measurements. Request a technical review and a reproducibility review. Keep one substantive topic per pull request. Disclose AI assistance and retain human responsibility for accuracy, test quality and rights to contributed material.

Do not publish private prompts, model access keys, hostnames, logs or dataset contents. CPU hosted CI is supplied as a starting workflow. Do not allow arbitrary external PR code to execute on privileged self-hosted GPU infrastructure; establish a reviewed, repository-specific trusted workflow first.

## Release analysis and engine evolution

Use the Phase 2 and Phase 3 entry points for version-specific work. Add exact upstream commits, evidence status and an explicit teaching adaptation decision. Changes to teaching APIs must update the version manifest, package/code versions, lessons and changelog together. Run `python labs/check_versions.py` alongside the existing checks. Do not auto-promote a baseline because a new upstream tag appears.
