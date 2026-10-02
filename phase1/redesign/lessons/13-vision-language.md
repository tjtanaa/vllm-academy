# 13 — From image patches to language tokens

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

Use a LLaVA-like design as the first understandable vision-language route: an image encoder creates features, a learned connection maps them into a representation the language model uses, and the decoder conditions on that representation. This is a chosen example, not the architecture of every VLM. [R19–R21](../REFERENCES.md)

## Distinguish three neural jobs

A Vision Transformer treats image patches as a sequence of learned representations. Image self-attention is commonly bidirectional within that representation, unlike a causal text decoder's restriction on future tokens. A learned projector or merger adapts the vision representation to the language path. The language model then computes contextual hidden states and output logits.

A contrastively trained image/text representation model such as CLIP is not, by that fact alone, an autoregressive assistant. A learned image-to-language connection and suitable training are important. An untrained projector with matching dimensions proves only tensor compatibility. [R19–R21](../REFERENCES.md)

## Execute the tiny route

```bash
python -m labs.vision_path
python -m pytest -q tests/test_mechanisms.py -k 'patch or placeholder or fusion or vision'
```

The lab uses four image patches, one random-weight vision block and a projector. Its trace is:

```text
image                   [1, 3, 8, 8]
flattened patches       [1, 4, 48]
vision features         [1, 4, 12]
projected features      [1, 4, 24]
fused decoder sequence  [1, 9, 24]
vocabulary logits       [1, 9, 32]
```

The unfilled text positions remain unchanged when features are inserted. One fewer placeholder is an error, not a reason to truncate a feature silently. The resulting random-weight logits do not demonstrate that the system understands the image.

## Open one real implementation

Use the `vlm` source-map entry. In the inspected LLaVA class, follow image-input validation into the vision tower and multimodal projector, then locate the language model. Notice the precomputed-image-embedding path as a distinct input possibility.

A neural projector is not the same thing as a transfer connector. One transforms representations; the other coordinates movement/lifetime of data between components. Both may be called “connectors” informally, so insist on the actual function.

Other VLMs may use token mergers, multiple crops, different positional systems or cross-attention rather than the exact prefix-replacement pattern. The learner should look for a contract, not force every model into this diagram.

## Exercise and exit ticket

Explain which weights would need to be trained or loaded to produce useful image-conditioned text. Identify which parts of the lab establish ordering, numerical shapes and causal handling, and which semantic properties it never tests.

Submit a tensor trace and a source-backed comparison with the selected LLaVA route. Do not claim the required Llama-1B/Qwen-0.6B text models are now multimodal.
