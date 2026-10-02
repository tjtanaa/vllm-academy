# vLLM Academy — Phase 1, redesigned

**Understand the model. Follow a request. Build the engine. Explain the boundaries. Make a useful contribution.**

Prepared October 2, 2026. This is a repository-ready curriculum supplement, not a published Academy release. It replaces a long no-code introduction with repeated **predict → explain → run → inspect → explain back** cycles. The complete route is intended for Python developers with elementary tensor knowledge; no CUDA/HIP programming is assumed.

## Start here

Read [the curriculum](CURRICULUM.md), then work through [lesson 00](lessons/00-first-request.md). The [architecture atlas](ARCHITECTURE_ATLAS.md) is a reference to revisit, not a 20-box diagram to memorize on day one. The [source review](SOURCE_REVIEW.md) explains how the materials were selected and reorganized. All prose and diagrams here are original synthesis; source figures and tutorial passages have not been copied.

The package includes 18 lesson drafts, eight executable lab modules plus a local source reader, a CPU test suite, an instructor guide, a pinned source map, original editable architecture figures, and explicit model-demo acceptance requirements. Check [validation evidence](results/validation.json) for execution scope.

## Run the independent CPU labs

In a separate environment with a CPU-capable PyTorch and pytest already installed:

```bash
cd phase1/redesign
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m pytest -q
python -m labs.bigram
python -m labs.naive_transformer
OMP_NUM_THREADS=1 python -m labs.train_tiny
python -m labs.render_contract
python -m labs.vision_path
python -m labs.cache_lifecycle
python -m labs.streaming
```

These commands need no network, checkpoint, vLLM install or API key. Optional snapshot inspection requires your local model/tokenizer snapshot; optional real tokenization requires Transformers. The source reader requires a local checkout of the exact reference commit. Do not install these CPU dependencies over an established ROCm or CUDA environment.

## The two mandatory model demos remain mandatory

Phase 1 graduates should run the **actual** `meta-llama/Llama-3.2-1B` base checkpoint and `Qwen/Qwen3-0.6B` through the native mini-vLLM path. The small random-weight lab is the prerequisite, not a substitute. Both named checkpoints are text models; the separate multimodal laboratory does not make them vision-capable. See [model acceptance](MODEL_ACCEPTANCE.md).

The previously prepared pretrained-engine patch is not part of this change. This supplement does not import its loader or assert that either full-checkpoint model gate passed. The new vision lab demonstrates tensor contracts with random weights; it is not a pretrained VLM implementation.

## Status and scope

Academy main was read at `40ad5af88b3f8acf426393f8b440cff3a3dfd453`. The new supplemental production-source pin is `b558f160a2c0abcb5902acc3c91a14c38a4af173`, resolved from vLLM main on October 2, 2026. Selected excerpts were inspected; other entries are explicitly symbol-search navigation targets. This is neither runtime validation nor a claim that every configuration selects Model Runner V2.

This supplement is published for review, not as a tagged Academy release. GPU execution and full-checkpoint validation remain unperformed. Existing Academy v0.29.0 references remain distinguishable. See [integration](INTEGRATION.md) for the non-destructive layout.

## Reading order

[Curriculum](CURRICULUM.md) → lessons → [architecture atlas](ARCHITECTURE_ATLAS.md) → [model acceptance](MODEL_ACCEPTANCE.md) → [source map](SOURCE_MAP.md). Instructors also use [the teaching guide](INSTRUCTOR_GUIDE.md). The source register is in [REFERENCES.md](REFERENCES.md); machine-readable references and mappings are provided alongside it.

## Build reading copies

The committed Markdown, lab sources, editable DOT figures and rendered SVGs are the source of truth. Generate the standalone HTML/Markdown handbooks locally from this directory:

```bash
python -m pip install 'mistune>=3,<4'
python build_handbook.py
# Optional: regenerate SVG and PNG figures; needs the Graphviz dot executable.
python figures/render.py
```

Generated `START_HERE.html`, `HANDBOOK.md` and PNG copies are intentionally not committed. The scoped GitHub Actions workflow builds the handbook and uploads it with the figures as a downloadable artifact. Local execution evidence is not a claim that a hosted workflow has passed.
