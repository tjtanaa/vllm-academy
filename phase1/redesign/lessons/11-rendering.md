# 11 — Local and disaggregated rendering

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

In this course, rendering means constructing model inputs from a request, not drawing an image and not generating the assistant's answer. Separating rendering into a service changes placement and transport; it should not silently change what the model receives.

## Begin with an ordinary function boundary

A local path can render a conversation and pass its resulting inputs directly to execution. A disaggregated path sends equivalent inputs across a process or network boundary. Rendering replicas can handle different complete requests. This is distinct from tensor-parallelizing a neural layer and does not require splitting one Jinja template across GPUs.

The current vLLM renderer material describes preprocessing and postprocessing separation. At the inspected pin, the Responses rendering route is self-contained and stateless: stored history must be resolved before rendering. The generation side also needs compatible model, tokenizer, template and preprocessing settings. [R27](../REFERENCES.md)

## Make the transport contract observable

```bash
python -m labs.render_contract
python -m pytest -q tests/test_mechanisms.py -k 'render or revision or serialization'
```

Inspect the synthetic record before and after JSON serialization. The lab does not create a real distributed service; it isolates the information-preservation requirement. Change a template or tokenizer identity and confirm rejection rather than accepting a subtly different input.

Now consider truncation, tool descriptions, system instructions and output-start markers. Different options can alter the effective context even when the latest user text is unchanged. Cache routing based only on that user text would ignore relevant input information.

## Add the multimodal complication

For text, token IDs may carry most of the model input information. For multimodal generation they are not sufficient by themselves. The pinned renderer contract includes processor payload and matching hashes/placeholders/metadata. A processed payload can be larger than the compressed media that produced it. Lesson 12 opens that object rather than pretending it is an opaque string.

Some documented E/P separation paths forward encoder tensors to E while P receives metadata and an encoder-transfer reference. That is an explicit path with readiness requirements, not permission to discard processor data from any ordinary request. [Pinned renderer document](https://github.com/vllm-project/vllm/blob/b558f160a2c0abcb5902acc3c91a14c38a4af173/docs/serving/online_serving/renderer.md)

## Source detour

Read the `render-wire` source entry before writing deployment commands. Endpoint enablement and schema evolve, so verify the local version and avoid exposing internal services casually. A production deployment also needs appropriate authentication, size limits and tenant isolation; the synthetic lab provides none of that infrastructure.

## Exercise and exit ticket

Draw co-located rendering and one remote-renderer alternative. Name the object crossing the new boundary, its version identity, who retains it and what happens if the renderer retries. Explain why “more renderers” and “larger tensor-parallel size” solve different problems.
