# Phase 1 curriculum and pacing

## The change in teaching strategy

Do not teach an entire theory block, then a complete engine, and only afterward reveal that real requests also need APIs, templates, media processing and output handling. Give the learner an early five-box map, deepen one mechanism at a time, and return to the same request whenever a new abstraction becomes necessary.

The two parallel questions are **“What mathematical operation happens next?”** and **“Which component owns that work and its state?”** A learner should eventually answer both for text and for an image-conditioned request.

This is a proposed instructional design, not a claim that this pacing has been experimentally shown to be optimal. Pilot it with learners and record where they stall before declaring the course complete.

## A repeatable 90-minute session

| Time | Activity | Example: cached attention |
|---|---|---|
| 0–10 min | Recall and predict | Which earlier computations are being repeated? |
| 10–25 min | One compact conceptual explanation | K/V persist; a new query still reads earlier state. |
| 25–45 min | Guided runnable exercise | Compare dense logits with cached chunks. |
| 45–55 min | Explain the observation | Why does the rectangular mask need an offset? |
| 55–75 min | Fault injection or bounded source reading | Break the mask, then locate the scheduling counters. |
| 75–85 min | Transfer to a different case | What changes with two requests or a prefix hit? |
| 85–90 min | Exit ticket | State the invariant without copying code. |

Do not allocate all 90 minutes to a lecture. Do not insist on rigid timing when a difficult dependency deserves another session. Longer checkpoint runs and production experiments are separately scheduled labs, not hidden inside a “five-minute exercise.”

## Learning sequence

### 00 — One request, five boxes

[Lesson](lessons/00-first-request.md)

**Theory:** Predict what a model needs; distinguish model, engine and API.

**Practice:** Inspect a request and the naive-decoder trace.

**Evidence:** One labeled request sketch; 5 boxes, not the full atlas.

### 01 — History as a sequence of design problems

[Lesson](lessons/01-history.md)

**Theory:** Counts → learned representations; attention; pretraining; post-training; serving.

**Practice:** Compare histories that a bigram model cannot distinguish.

**Evidence:** A problem/response/cost timeline, not a list of model brands.

### 02 — Text, tokens and conversation contracts

[Lesson](lessons/02-tokens.md)

**Theory:** Token IDs, special tokens, chat serialization and context limits.

**Practice:** Roundtrip a synthetic rendered request; inspect a real local tokenizer later.

**Evidence:** Predict why a role or template change changes the model input.

### 03 — Build a naive Transformer decoder

[Lesson](lessons/03-naive-transformer.md)

**Theory:** Embeddings, Q/K/V, masking, residuals, normalization and FFN.

**Practice:** Inspect every tensor shape; mutate future tokens.

**Evidence:** Causal invariance test and shape ledger.

### 04 — Training is not generation

[Lesson](lessons/04-training-inference.md)

**Theory:** Shifted targets, teacher forcing, loss, logits and sampling.

**Practice:** Train on a synthetic periodic sequence; compare with an autoregressive loop.

**Evidence:** Explain why lower training loss is not language-quality evidence.

### 05 — From naive code to Llama and Qwen

[Lesson](lessons/05-real-models.md)

**Theory:** RoPE, GQA, RMSNorm, SwiGLU, configuration and checkpoint contracts.

**Practice:** Audit Qwen head_dim; execute both native pretrained demos when patch is integrated.

**Evidence:** Mandatory checkpoint evidence gate, not random-weight equivalence alone.

### 06 — Remember computation: KV and token work

[Lesson](lessons/06-kv-cache.md)

**Theory:** Prefill/decode, computed vs sampled, cached chunk masks.

**Practice:** Compare dense recomputation with cached chunks and greedy generation.

**Evidence:** Cached and uncached logits agree within an explicit tolerance.

### 07 — One model, many requests

[Lesson](lessons/07-scheduling.md)

**Theory:** Iteration-level scheduling, admission, token budgets, completion and cancellation.

**Practice:** Replay a hand-worked schedule and the existing mini-engine trace.

**Evidence:** Explain logical scheduling versus physical GPU batching.

### 08 — Pages, prefixes and ownership

[Lesson](lessons/08-pages-prefix.md)

**Theory:** Logical/physical addressing, identity, references, eviction.

**Practice:** Use existing block-table tests; break a lifetime or prefix-identity assumption.

**Evidence:** Show exactly when a page is reusable.

### 09 — The complete production abstraction map

[Lesson](lessons/09-system-map.md)

**Theory:** API, renderer, input processor, core, scheduler, executor, worker, runner, model.

**Practice:** Assign one responsibility and data contract to each selected code excerpt.

**Evidence:** A request ledger with placement and lifetime, not class-name memorization.

### 10 — APIs and the return path

[Lesson](lessons/10-apis.md)

**Theory:** Completion/chat/Responses/pooling/audio; stream/error/abort contracts.

**Practice:** Split UTF-8 SSE data at arbitrary network boundaries.

**Evidence:** Explain why an API name does not imply model capability.

### 11 — Local and disaggregated rendering

[Lesson](lessons/11-rendering.md)

**Theory:** Template rendering/tokenization/derendering as service boundaries.

**Practice:** Serialize, transmit and verify a rendering contract; reject mismatched revisions.

**Evidence:** Distinguish renderer scaling from TP and from encoder/P-D separation.

### 12 — Import an image without losing its meaning

[Lesson](lessons/12-multimodal-inputs.md)

**Theory:** Media decoding, preprocessing, hashes, placeholders and metadata.

**Practice:** Inspect ordered processor outputs; change same-shaped media content.

**Evidence:** Separate compressed bytes, tensors and token placeholders.

### 13 — From image patches to language tokens

[Lesson](lessons/13-vision-language.md)

**Theory:** ViT, vision features, projector/merger and decoder conditioning.

**Practice:** Run a random-weight image→patches→vision→projection→causal-decoder path.

**Evidence:** Shape trace plus mismatch rejection; not an image-understanding claim.

### 14 — Schedule and cache multimodal work

[Lesson](lessons/14-multimodal-cache.md)

**Theory:** Processor cache, encoder cache, contextual KV, readiness and lifetimes.

**Practice:** Attempt reads before readiness and recycling with live readers.

**Evidence:** Explain which cache can be reused across different text prefixes.

### 15 — Put the boundaries on machines

[Lesson](lessons/15-placement.md)

**Theory:** Render/encode/prefill/decode disaggregation; TP/PP/DP/EP as different axes.

**Practice:** Design three placements and label every transferred object.

**Evidence:** Ownership and fallback table for a failed transfer.

### 16 — Measure and debug the whole path

[Lesson](lessons/16-measurement.md)

**Theory:** TTFT, ITL, queueing, preprocessing, encode, prefill, decode and network.

**Practice:** Design a controlled warm/cold comparison; follow a trace into one source helper.

**Evidence:** Raw evidence and a bottleneck hypothesis with a negative control.

### 17 — First useful contribution

[Lesson](lessons/17-contribution.md)

**Theory:** Reproduce, isolate, test, patch, review and document evidence.

**Practice:** Review one injected bug, then choose a bounded real issue.

**Evidence:** Useful draft PR or actionable reproduction plus Phase 2/3 mapping.

## Cohort grouping

A proposed ten-week delivery uses two sessions per week: week 1 covers 00–01, week 2 covers 02–03, week 3 covers 04–05, week 4 covers 06–07, week 5 covers 08–09, week 6 covers 10–11, week 7 covers 12–13, week 8 covers 14–15, and week 9 covers 16–17. Week 10 is reserved for model-demo evidence, capstone review and remediation. Those are instructor planning allocations, not learner time guarantees.

The course is not only for kernel contributors. Frontend, tokenizer/processor, scheduler, cache, model-integration, observability, documentation and test contributions all have legitimate routes to the capstone.

## Three levels of work, kept separate

**Implemented here:** the standalone CPU mechanism labs and their tests. These are deliberately small and observable.

**Existing Academy exercises:** the block pool, prefix index and mini-engine scheduling labs already on main. The supplement points to them instead of copying the engine again.

**Required integration gates:** the two actual native pretrained model demos. They depend on integrating and reviewing the previously prepared patch. Multimodal serving and render/encode/P-D deployment are production-source investigations or optional hardware labs, not implemented mini-engine features in this package.

## Prevent unnecessary prerequisites

Explain tensor dimensions before projection kernels. Explain a single-process function boundary before drawing a network hop. Explain a private KV cache before a shared one. Explain image patches before a full VLM. Explain an ordinary generated response before tool parsing and response-state management. Explain TP/PP/DP/EP as categories, but defer implementing production collectives, MoE and optimized kernels to later phases.

## Passing criteria

A learner must produce a correct naive decoder trace, a causal/cached-equivalence test, the two required model-demo records, a request-flow ledger including the output path, a multimodal shape-and-ownership explanation, and a useful contribution artifact. Lack of hardware or gated-model access does not justify fabricated results: mark that gate pending while recognizing completion of the other modules.
