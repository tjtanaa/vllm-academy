# 00 — One request, five boxes

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

A beginner's first question should be “What happens to my input?” rather than “Which installation flags should I memorize?” Start with one text request and reveal only five responsibilities: **prepare input → schedule work → execute model → choose output → return response**. Later lessons will open these boxes.

## Predict and explain

Write a user message on paper. Which part is a model input: the JSON object, its text, token IDs, or embedding vectors? The answer changes as the request travels through the service. Preserve that distinction rather than calling all of them “the prompt.”

A model's computation is only part of an inference service. Request validation, tokenization, state allocation, iteration scheduling and response formatting have different purposes. A matrix multiplication can be correct while the wrong request receives its result. A valid response can conceal a cache leak. The architecture overview motivates this division; it does not require every responsibility to occupy its own process. [R25](../REFERENCES.md)

Ask learners to mark which boxes might run on the CPU, accelerator, or either. These are initial hypotheses; do not assert a universal deployment from this sketch.

## Run a first observation

```bash
python -m labs.naive_transformer
```

The output describes input IDs, embedding shapes, attention shapes and vocabulary logits. It also checks a cached continuation against full recomputation. At this point learners need only identify that a `[batch,tokens]` integer input becomes a `[batch,tokens,vocabulary]` numeric output. Explain the calculations in lesson 03, not all at once now.

The generated IDs are from random weights. They are not a meaningful language demo. Introduce the two later required checkpoints now so learners see the destination: Llama-3.2-1B completion and Qwen3-0.6B chat through native mini-vLLM. [R12–R14](../REFERENCES.md)

## First source encounter

Open the `api` source-map entry. Read only the endpoint handler's validation/delegation and its JSON-versus-stream response branches. The question is **“Where does this function delegate the computation?”** It is not necessary to understand the entire web framework or every handler parameter yet.

Do not install the full production runtime to complete this observation. A local source checkout or the pinned source link is enough.

## Explain back

Draw the five boxes again without looking. Add a different noun on each arrow: message, tokenized request, scheduled work, logits/tokens, response. The drawing passes when the learner can explain which arrows are conceptual and which were actually observed in the lab.

Exit question: a server returns a plausible sentence. Which of numerical correctness, resource cleanup, model quality and throughput have been established? None is established comprehensively by that smoke test alone.

## Reading

[Architecture background R25](../REFERENCES.md); [bounded API source](../SOURCE_MAP.md). The full [atlas](../ARCHITECTURE_ATLAS.md) is a future reference, not day-one memorization.
