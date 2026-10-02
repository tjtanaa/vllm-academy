# 14 — Schedule and cache multimodal work

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

A request with an image can involve work before any language-model prefill. Its reusable state can also live at several levels. A single “cache hit” counter is not enough to explain what was saved.

## Ask what object is cached

A processor cache can avoid repeated media preprocessing. An encoder cache can avoid rerunning a vision tower on compatible input. Decoder prefix KV can avoid recomputing compatible contextual language states. Application response/history storage is a different semantic object again. The vLLM processing and encoder-disaggregation material gives concrete production boundaries for the first two distinctions. [R28–R29](../REFERENCES.md)

For an image-only encoder independent of text, the same image may yield reusable encoder features across different questions. But decoder KV after those features can depend on preceding text and positions. Other architectures can have different dependencies, so the cache key must follow the actual computation graph.

Do not key image reuse by shape alone. Two RGB tensors with identical dimensions can have different content. Processor revision, image transformations, encoder weights and relevant conditioning can change the result as well.

## Readiness is not identity

```bash
python -m labs.cache_lifecycle
python -m pytest -q tests/test_mechanisms.py -k 'load or recycle or cache_stage'
```

The independent state machine begins in `loading`. A content identity may already be known, but no reader is allowed until publication marks the data ready. After readiness, active readers prevent recycling. The final release makes reuse possible; a request's visible completion does not automatically replace those steps.

The lab does not move data between hosts. It teaches an invariant that must still hold when transport is introduced.

## Connect scheduling to the model path

A request may need encoder work, decoder input work and cache capacity with different budgets. A scheduler cannot infer that an image is free merely because the prompt text is short. Conversely, an encoder cache hit may remove neural work while leaving language-model prefill and decode untouched.

Inspect the source-map scheduler entry and the documented encoder-transfer boundary. Treat the constructor excerpt as evidence of configuration responsibilities, not as proof of the entire algorithm.

## Exercise and exit ticket

Compare three cases: same image/same text, same image/different preceding text, and different same-shaped image/same text. For each, identify potentially reusable processor output, encoder features and decoder KV under a stated LLaVA-like assumption.

Then introduce a failed asynchronous transfer. Explain whether a lookup can still be considered a completed hit, what state must remain alive, and which fallback is safe. The answer must name data and ownership, not simply “retry.” [Architecture cache table](../ARCHITECTURE_ATLAS.md)
