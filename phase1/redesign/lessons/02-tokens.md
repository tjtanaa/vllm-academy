# 02 — Text, tokens and conversation contracts

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

A user sees messages. A text decoder sees a numeric representation of a serialized sequence. Between them sits a contract: tokenizer, special tokens, role markers, template rules, truncation and generation boundaries.

## Explain one representation change at a time

A token is not necessarily a word or a character. A token ID is an index, not a semantic scalar whose arithmetic distance has a direct meaning. The embedding lookup gives that ID a learned vector. Byte boundaries, characters and tokens can also differ.

Role-based chat inputs must be serialized in the format expected by the selected checkpoint. A rendered assistant prefix affects where generation continues. Two superficially identical messages can produce different IDs when templates or options differ. The official template documentation is a guide; the actual model snapshot is the artifact to inspect. [R11](../REFERENCES.md)

Do not teach a single hand-written special-token string as “the LLM chat format.” Do not tokenize an already formatted sequence while unknowingly duplicating beginning/end markers. These errors occur before attention executes.

## Run a visible, synthetic renderer

```bash
python -m labs.render_contract
```

This lab uses length-delimited messages and byte IDs so every change is visible. It is **not** a Llama or Qwen tokenizer or template. Inspect the wire object and change one role while keeping the text fixed. Predict which IDs and cache keys change.

The identity record includes model, tokenizer, template, processor and tenant fields. This is an intentionally explicit teaching contract, not a claim that current vLLM uses this exact JSON schema. The acceptor rejects mismatched identities; later lessons ask how a deployed system enforces equivalent compatibility.

## Move to a real snapshot

Once an authorized tokenizer snapshot is available:

```bash
python -m labs.inspect_snapshot /path/to/snapshot --tokenize
```

The optional path uses installed Transformers, local files only, and no remote code. Inspect rendered IDs and generation markers for the actual checkpoint. For Qwen3, record thinking-mode options explicitly. For Llama's base checkpoint, use a completion prompt; do not invent an instruction-tuned chat contract. [R12–R14](../REFERENCES.md)

## Source detour

Read the `renderer` map entry and identify the tokenizer work and the distinct multimodal processor. A renderer's CPU executor is not the model executor that sends neural computation to workers. Naming both “executor” does not make them the same abstraction.

## Exercise and exit ticket

Explain what changes when the same user text moves from a completion API to a chat API. Explain why token count must be taken after relevant rendering and multimodal placeholder processing, not from the number of words in the original input.

Submit a text → serialized text/structure → IDs → embeddings ledger, marking which parts were synthetic and which came from an actual model snapshot.
