# Source register

Inspected on October 2, 2026. Primary papers, original-author tutorials, official model artifacts and official vLLM material. Publication dates are distinct from inspection dates. These are selected for their instructional roles; no bibliometric ranking or citation-count claim is made.

## R01 — A Neural Probabilistic Language Model

Bengio et al., 2003. [Source](https://jmlr.org/papers/v3/bengio03a.html).

**Use in this course:** Learned representations instead of exact-count generalization; historical context.

## R02 — Neural Machine Translation by Jointly Learning to Align and Translate

Bahdanau et al., 2014 preprint / ICLR 2015. [Source](https://arxiv.org/abs/1409.0473).

**Use in this course:** Attention as a response to a fixed-vector bottleneck.

## R03 — Attention Is All You Need

Vaswani et al., 2017. [Source](https://arxiv.org/html/1706.03762v7).

**Use in this course:** Attention equations and original encoder-decoder architecture; not a modern Llama implementation.

## R04 — Improving language understanding with unsupervised learning

OpenAI, 2018. [Source](https://openai.com/index/language-unsupervised/).

**Use in this course:** Generative pretraining and downstream adaptation.

## R05 — BERT: Pre-training of Deep Bidirectional Transformers

Devlin et al., 2018. [Source](https://arxiv.org/abs/1810.04805).

**Use in this course:** Contrast bidirectional representation learning with causal generation.

## R06 — Language Models are Few-Shot Learners

Brown et al., 2020. [Source](https://arxiv.org/abs/2005.14165).

**Use in this course:** In-context task examples versus updating weights.

## R07 — Training language models to follow instructions with human feedback

Ouyang et al., 2022. [Source](https://arxiv.org/abs/2203.02155).

**Use in this course:** Why base and instruction-following models are different artifacts.

## R08 — The Annotated Transformer

Harvard NLP, 2022 edition. [Source](https://nlp.seas.harvard.edu/annotated-transformer/).

**Use in this course:** Equation-to-code reading technique; do not copy its full training course.

## R09 — The Illustrated Transformer

Jay Alammar, original tutorial. [Source](https://jalammar.github.io/illustrated-transformer/).

**Use in this course:** Progressive visual decomposition; distinguish explanatory pictures from learned evidence.

## R10 — Language Modeling from Scratch

Stanford CS336, Spring 2025 archive. [Source](https://cs336.stanford.edu/spring2025/).

**Use in this course:** Implement, test, profile; the full course has stronger prerequisites and a training emphasis.

## R11 — Chat templates

Hugging Face Transformers documentation, inspected 2026-10-02. [Source](https://huggingface.co/docs/transformers/main/en/chat_templating).

**Use in this course:** Messages, serialization, control tokens and generation boundaries.

## R12 — Qwen3-0.6B model card

Qwen, inspected 2026-10-02. [Source](https://huggingface.co/Qwen/Qwen3-0.6B).

**Use in this course:** Required demo and explicit thinking-mode configuration.

## R13 — Qwen3-0.6B config.json

Qwen, inspected 2026-10-02; floating model file. [Source](https://huggingface.co/Qwen/Qwen3-0.6B/raw/main/config.json).

**Use in this course:** Explicit head_dim; record a local immutable model snapshot for executable evidence.

## R14 — Llama-3.2-1B model card

Meta, released September 25, 2024. [Source](https://huggingface.co/meta-llama/Llama-3.2-1B).

**Use in this course:** Required base-model demo; this checkpoint is text-only.

## R15 — GQA: Training Generalized Multi-Query Transformer Models

Ainslie et al., 2023. [Source](https://arxiv.org/abs/2305.13245).

**Use in this course:** Query-head and KV-head counts need not agree.

## R16 — RoFormer: Enhanced Transformer with Rotary Position Embedding

Su et al., 2021. [Source](https://arxiv.org/abs/2104.09864).

**Use in this course:** Position-dependent rotations; configuration matters.

## R17 — Root Mean Square Layer Normalization

Zhang and Sennrich, 2019. [Source](https://arxiv.org/abs/1910.07467).

**Use in this course:** RMSNorm is not interchangeable with LayerNorm.

## R18 — GLU Variants Improve Transformer

Shazeer, 2020. [Source](https://arxiv.org/abs/2002.05202).

**Use in this course:** Gated feed-forward variants; avoid teaching GELU as universal.

## R19 — An Image is Worth 16x16 Words

Dosovitskiy et al., 2020 preprint / ICLR 2021. [Source](https://arxiv.org/abs/2010.11929).

**Use in this course:** Patches as Transformer inputs; classification is not image-conditioned language generation.

## R20 — Learning Transferable Visual Models From Natural Language Supervision

Radford et al., 2021. [Source](https://arxiv.org/abs/2103.00020).

**Use in this course:** Contrastive image-text representation learning, not an autoregressive chat decoder.

## R21 — Visual Instruction Tuning

Liu et al., 2023. [Source](https://arxiv.org/abs/2304.08485).

**Use in this course:** Vision encoder + learned connection + LLM as a first VLM teaching example.

## R22 — Orca: A Distributed Serving System for Transformer-Based Generative Models

Yu et al., OSDI 2022. [Source](https://www.usenix.org/conference/osdi22/presentation/yu).

**Use in this course:** Iteration-level scheduling; do not transplant paper benchmark numbers.

## R23 — Efficient Memory Management for Large Language Model Serving with PagedAttention

Kwon et al., 2023. [Source](https://arxiv.org/abs/2309.06180).

**Use in this course:** Logical blocks, physical storage and sharing; paper is historical, source determines current code.

## R24 — FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness

Dao et al., 2022. [Source](https://arxiv.org/abs/2205.14135).

**Use in this course:** Attention IO optimization is distinct from persistent KV allocation.

## R25 — Architecture Overview

vLLM docs, inspected 2026-10-02. [Source](https://docs.vllm.ai/en/latest/design/arch_overview/).

**Use in this course:** Frontend/core/worker/model responsibilities; actual processes depend on configuration.

## R26 — OpenAI-Compatible Server

vLLM docs, inspected 2026-10-02. [Source](https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/).

**Use in this course:** API capability families and model-specific applicability.

## R27 — Renderer APIs

vLLM docs and pinned repository document. [Source](https://docs.vllm.ai/en/latest/serving/online_serving/renderer/).

**Use in this course:** Render/derender, opt-in scale-out endpoints and multimodal transport contract.

## R28 — Multi-Modal Data Processing

vLLM docs, inspected 2026-10-02. [Source](https://docs.vllm.ai/en/latest/design/mm_processing/).

**Use in this course:** Processor outputs, placeholder updates and processor-output caching.

## R29 — Disaggregated Encoder

vLLM docs, inspected 2026-10-02. [Source](https://docs.vllm.ai/en/latest/features/disagg_encoder/).

**Use in this course:** Encoder-cache transfer is different from decoder KV transfer.

## R30 — Model Runner V2 Design Document

vLLM docs, inspected 2026-10-02. [Source](https://docs.vllm.ai/en/latest/design/model_runner_v2/).

**Use in this course:** Persistent state versus step input; inspect runtime dispatch rather than infer it.

## R31 — zero-to-sglang README

Datawhale / RadixArk, inspected 2026-10-02. [Source](https://github.com/datawhalechina/zero-to-sglang/blob/main/README.md).

**Use in this course:** Reference course structure, not evidence that one learning sequence is best.
