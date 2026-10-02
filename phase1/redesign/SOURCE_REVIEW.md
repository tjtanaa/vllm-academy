# Source analysis: what to keep, what to reorganize

## Why this is not a rewritten zero-to-sglang

The inspected reference README groups no-code foundations before building a small engine and later studying production optimizations. It is useful as a progression from understanding to construction to contribution. It is not evidence that a long theory-first sequence is the best fit for this Academy. Its project-specific cache and serving emphasis also should not be renamed and presented as vLLM internals. [R31](REFERENCES.md)

**Our design judgment:** retain incremental construction and contribution culture, but introduce a real request boundary immediately, add a runnable observation to every foundational lesson, and make API/rendering/multimodal ownership first-class Phase 1 concepts. Do not require learners to implement every production subsystem merely because they need to understand it.

The review uses primary abstracts/text where available, official course descriptions, documentation and selected source excerpts; it is not an exhaustive reading of every linked lecture or paper appendix. For the Annotated Transformer, the author's [source notebook/script](https://github.com/harvardnlp/annotated-transformer/blob/master/the_annotated_transformer.py) and introduction provide a readable primary-source counterpart to the large HTML page.

## Source-selection matrix

| Source | What it contributes | What not to import wholesale | Academy adaptation |
|---|---|---|---|
| Neural LM / attention / Transformer papers [R01–R03] | The problem each architecture responds to | A full survey or every derivation before any code | A history lesson organized by bottleneck, followed by a small failed baseline. |
| Annotated Transformer [R08] | Direct connections between equations and executable operations | Full translation-training infrastructure and the assumption that the original encoder-decoder is a current Llama | A shape ledger and a short decoder whose causal property can be tested. |
| Illustrated Transformer [R09] | Progressive visual decomposition | Reproducing figures or treating an intuitive illustration as a correctness test | New diagrams reveal only the next necessary level; assertions accompany them. |
| Stanford CS336, Spring 2025 [R10] | Implementation-oriented assignments covering tokenizer/model/training and systems | Its complete training/data/alignment syllabus or stronger prerequisites | Borrow the implement-and-measure discipline; center serving rather than training a competitive LM. |
| GPT, BERT, GPT-3, InstructGPT [R04–R07] | Objective and interaction distinctions | A linear “new model replaces all old models” story | Contrast causal, bidirectional, in-context and post-training behavior in one request-focused history. |
| HF templates and official model files [R11–R14] | Concrete serialization and architecture contracts | Universal hand-written special-token strings | Inspect local checkpoint configuration, tokenizer and generation settings. |
| GQA, RoPE, RMSNorm, GLU [R15–R18] | Modern model building blocks | A name-only catalog with no changed tensor shapes | A “naive → real” configuration audit before the native model gate. |
| ViT, CLIP, LLaVA [R19–R21] | Patch encoding, image-text representation and visual instruction conditioning | Claiming every VLM uses the same projector/prefix construction | Teach one LLaVA-like route, then explicitly name counterexamples and model-specific contracts. |
| Orca, PagedAttention, FlashAttention [R22–R24] | Scheduling, storage management and IO-aware attention as different questions | Old benchmark gains applied to current GPUs or current vLLM internals | Workload prediction and invariant tests; source pin determines present implementation. |
| Current vLLM docs and pinned excerpts [R25–R30] | Production responsibilities, APIs, renderer and encoder disaggregation | One giant class diagram or claims that all configurations use one runner | Bounded “find the contract” readings, including input, output and lifetime. |

## A recurring extraction method

For each source, write four sentences in your own words: **problem, mechanism, trade-off, boundary of applicability**. Then identify a small experiment that could contradict the explanation. Finally locate a production responsibility, where applicable. A citation is not a replacement for an experiment, and a toy experiment is not a replacement for production evidence.

Example: the PagedAttention paper motivates flexible persistent KV storage. The course turns that into logical-to-physical mapping and ownership exercises. FlashAttention concerns how attention computation moves data; it is assigned later as a contrasting optimization axis. A dense gather-based educational cache is not a fused PagedAttention kernel. [R23–R24](REFERENCES.md)

## How to read history without teaching mythology

A useful historical account is not “RNNs disappeared, then Transformers became chatbots.” Older and newer architectures coexist, and model objectives branch. A causal decoder, a bidirectional text encoder and an image encoder have different jobs. Pretraining, post-training, retrieval, prompting and serving are also different activities. The course uses selected milestones to explain those distinctions, not to claim an exhaustive or inevitable progression. [R01–R07, R19–R21](REFERENCES.md)

## Citation and reuse practice

Cite the original paper for its mechanism and date, the model artifact for its configuration, and pinned code for an implementation claim. Latest documentation is navigational and may change. No citation counts were measured, so the package does not label a source “most cited.” Tutorial sources are credited to their authors; the package does not reproduce their text or artwork. Model files and third-party examples retain their own access and license requirements.

## Review before publication

Review explanations separately from executable checks. Source reviewers verify that a claimed path is actually selected under the stated configuration. Model reviewers inspect checkpoint/tokenizer compatibility. Instructors pilot pacing. Hardware reviewers attach concrete environment and execution evidence. None of these reviews is replaced by the presence of a reference list.
