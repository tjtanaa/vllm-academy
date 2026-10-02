# vLLM Academy

**Learn inference from zero. Build mini-vLLM. Make your first useful PR. Keep learning as vLLM evolves.**

An independent, hands-on learning project maintained in `tjtanaa/vllm-academy`. The beginner course was seeded from the original `zero-to-vllm` materials prepared for this project, inspired by the learning progression of Datawhale's [zero-to-sglang](https://github.com/datawhalechina/zero-to-sglang). This is not an official vLLM course or a renamed implementation of SGLang.

## Three phases, one learning journey

| Phase | Goal | Entry point | Initial state |
|---|---|---|---|
| **1. Zero → mini-vLLM → first PR** | Understand inference, construct and test a small engine, trace production source, and prepare a useful contribution. | [Phase 1](phase1/README.md) · [Syllabus](SYLLABUS.md) | 12 core lesson drafts, 6 workshop briefs, runnable CPU reference engine and tests. |
| **2. Understand vLLM's evolution** | Explain the problem, abstraction, optimization, trade-offs, and implementation changes at each reviewed vLLM version. | [Phase 2](phase2/README.md) | Release-analysis framework and a pinned baseline note; historical release-by-release analysis is not yet complete. |
| **3. Keep mini-vLLM evolving** | Bring important new engine/core/runner concepts into a readable teaching engine without turning it into a second production runtime. | [Phase 3](phase3/README.md) | Evolution policy and version manifest; future adaptations require reviewed changes and tests. |

Start with Phase 1. Phase 2 explains **why production design changes**. Phase 3 makes selected changes **small enough to implement and understand**. These are project phases, not three mandatory consecutive courses for every learner.

## Run the teaching engine

Use a separate CPU sandbox with Python, PyTorch and pytest. No vLLM package, downloaded model, GPU, or API key is needed after dependency installation.

```bash
git clone https://github.com/tjtanaa/vllm-academy.git
cd vllm-academy
python3 -m venv .venv
source .venv/bin/activate
python -m pip install 'torch==2.10.0' --index-url https://download.pytorch.org/whl/cpu
python -m pip install 'pytest>=8,<10'
python labs/check_course.py
python labs/check_versions.py
python -m pytest -q
python -m mini_vllm.demo
```

See [the build milestones](labs/MILESTONES.md) before opening the solutions. The baseline has 30 engine/memory tests; repository-policy tests are additional. [Validation evidence](results/README.md) distinguishes imported records, current local execution, and GPU work that has not been run.

The toy uses random weights, not a pretrained language model. It implements incremental KV, noncontiguous pages, reference ownership, chained full-block prefix reuse, token-budget scheduling, cancellation and cleanup. Attention gathers pages into dense tensors; forwards execute serially and prefill is token-by-token. It does **not** implement fast paged-attention kernels, physical GPU batching, graph capture, async execution, preemption, distributed transfer, speculation, or hybrid-state execution.

## Run real vLLM

Complete [the first-server lesson](course/part0/01-first-server.md) in a separately prepared, platform-specific vLLM environment:

```bash
BACKEND=rocm bash labs/serve.sh  # Use BACKEND=cuda for the CUDA lane.
# In another terminal:
python labs/smoke_client.py
bash labs/bench.sh
```

These are **GPU recipes, not GPU-validated results**. API availability, backend selection, numerical correctness, and measured performance are separate claims. The initial source-reading baseline is vLLM `v0.29.0` at `98dff2a81d747d1dba01a47f939f48c3526d4206`; it is not a claim to track the latest upstream release or to certify runtime compatibility.

## Repository map

```text
phase1/             Stable beginner-course entry point
course/             Lessons, source walkthrough and advanced workshop briefs
mini_vllm/          Current small reference implementation
tests/              CPU mechanism tests and repository-policy tests
labs/               Build milestones, serving/benchmark recipes and checks
phase2/             Version-by-version architecture and optimization notes
phase3/             Teaching-engine evolution process and concept coverage
versions/           Machine-readable upstream ↔ teaching-engine mapping
templates/          Chapter, experiment, release-analysis and evolution templates
maintainers/        Instructor guide, source map, review criteria and backlog
tools/              Offline handbook builder
```

Read [the roadmap](ROADMAP.md), [version policy](VERSION_POLICY.md), and [contribution guide](CONTRIBUTING.md). English lessons are included; [繁體中文入口](README_zh-TW.md) is a landing page, not a full translation.

Generate the optional offline handbook locally with `python -m pip install 'mistune>=3,<4'` followed by `python tools/build_handbook.py --html`. Generated `HANDBOOK.md` and `START_HERE.html` are not source-of-truth course files.

## Evidence and publication status

The seed contains draft instructional material and CPU-tested educational code. Human technical/editorial review, real GPU validation, and complete release analyses remain open work. A passing local test is not a GitHub Actions result and is not proof of production compatibility. Future releases and scheduled monitoring are not enabled merely by this roadmap.

Original-material attribution and license terms are retained in [NOTICE.md](NOTICE.md) and [LICENSE](LICENSE).
