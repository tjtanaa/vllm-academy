# 12 — Import an image without losing its meaning

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

An image request starts with a representation supplied by a client, not with ready-to-use language-model embeddings. Trace each transformation before discussing a vision kernel.

## Open the input object

A service may receive an uploaded image, an encoded payload or a permitted reference to media. After validation and acquisition, image decoding produces pixel data. Model-specific preprocessing can resize, normalize, crop or arrange patches. The processor also maintains the correspondence between modality items and the prompt positions where their features belong. [R28](../REFERENCES.md)

These are different stages: parsing a message content item, decoding a JPEG/PNG, preparing numeric tensors, and running a trained vision encoder. Calling all of them “image processing” hides both costs and correctness failures.

Use local synthetic data for the lab. Publicly exposed services need limits and safe media acquisition policies; no exercise requires fetching an arbitrary user-controlled URL or exposing a server.

## Run a representation ledger

```bash
python -m labs.vision_path
```

For now stop at the image and patch shapes. The synthetic input is `[1,3,8,8]`; patch size is 4. Four patch vectors result. These dimensions are intentionally tiny and are not a specification for any production model.

Inspect `patchify` and compare its row-major patch order with the test fixture. Shuffling patches or modality items while keeping shapes unchanged can silently change the model input. Shape compatibility is necessary but not sufficient.

## Placeholders are a contract

Text positions must align with the feature sequence produced by the relevant processor/model path. An image marker is not automatically a single normal token representing the entire image. Crops, grids or mergers can change feature counts and positional metadata. The processor and model together determine the representation.

The lab's `fuse` operation requires exactly one distinct placeholder position per synthetic projected feature. It rejects count and index mismatches. Production abstractions are richer; do not hard-code this toy's four-token image rule into a real loader.

## Audio and video as extensions

Apply the same questions to audio samples and video frames: what sampling/frame policy produced the tensors, which temporal metadata is retained, and what encoder is trained for them? Do not assume every model uses image-style patch placeholders or that a text-only model can consume arbitrary audio/video fields. Supported tasks depend on the selected model and server configuration. [R26, R28](../REFERENCES.md)

## Source detour and exit ticket

Find `BaseMultiModalProcessor` through the `processor` map entry. It was located by symbol search; read its prompt updates and item correspondence before claiming a detailed execution path.

Submit the ordered ledger: client representation → decoded media → processor tensors → placeholder metadata. Explain two failures that pass a tensor-shape check but still produce the wrong input.
