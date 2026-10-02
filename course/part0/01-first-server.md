# 01 — Your first real vLLM server

**Material status:** Core lesson draft; GPU recipe unverified. **Source-check date:** 2026-09-22.

Begin with a small, ordinary text model and a single device. The goal is a known-good request path, not a maximum-throughput configuration. Keep this production environment separate from the CPU toy environment.

## Learning objectives

Choose the correct platform build, identify the installed runtime, launch a local service, send a chat request, and capture enough information to reproduce the run.

## Environment preparation

Use the official GPU installation instructions for your selected release and hardware [S3]. The course's source-reading pin is recorded in `VERSION_POLICY.md`; a compatible instructor-tested image may be a different release, but that difference must be explicit. Do not invent an image tag or assume that a release tag guarantees a matching ROCm wheel.

For CUDA, verify the driver and device exposure before installing. For ROCm, verify device access, the HIP-enabled PyTorch build, and the supported GPU architecture. Python's `torch.cuda` namespace also appears in ROCm environments; that spelling is not proof of an NVIDIA binary. Inspect `torch.version.hip`, the device properties, and the actual selected backend.

The install guide checked for this course warns about Python-version constraints on prebuilt ROCm wheels and possible accidental selection of a CUDA wheel. Use a supported interpreter and a platform-specific index or a validated image. Treat this as a versioned constraint, not a permanent rule about all future releases.

No automatic install script is supplied for production: overwriting a working GPU stack is a poor first lesson. An instructor should supply exact validated install commands or an image digest for each class.

## First launch

The default model is `Qwen/Qwen2.5-0.5B-Instruct` [S10]. This is a modest teaching choice, not a performance recommendation for your production workload. Read its model card and obtain a stable model/tokenizer revision before publishing results.

```bash
# AMD example, inside a prepared ROCm vLLM environment:
BACKEND=rocm bash labs/serve.sh
# NVIDIA counterpart:
# BACKEND=cuda bash labs/serve.sh
```

Use only one of these commands per server. The script checks the runtime and visible accelerator, binds to `127.0.0.1`, caps context and batch work, records its exact command, and saves logs. Eager execution and disabled prefix caching give the first experiments an explicit baseline. Do not add quantization, custom collectives, speculative decoding, or every AITER environment variable at once.

From another terminal:

```bash
python labs/smoke_client.py
```

The client waits for health, submits a non-streaming chat completion, validates a nonempty message, and prints the response. This does not require the OpenAI Python SDK or an external hosted API.

## Read the startup evidence

Find the runtime version, chosen model architecture, attention backend, model runner when logged, effective dtype, KV allocation, and any compatibility warnings. Save those observations with the model revision and command. An accepted flag is not proof that its desired kernel was selected.

Do not assume one prose answer is reproducible byte-for-byte across hardware, versions, or execution modes. For correctness comparisons, control tokenization and sampling, compare defined numerical outputs where available, and report tolerances. For the first smoke test, require a valid response and no server error rather than a particular sentence.

## Failure triage

No device visible: fix host/container access before changing model flags. A missing CUDA library on an AMD host: inspect the wheel and PyTorch runtime. Out of memory: first inspect the model size, context cap, concurrent sequences, and other users of device memory. Unsupported attention path: record the exact model, dtype, cache layout, architecture, and backend selection. A server that starts but rejects chat requests may need a compatible chat template or tokenizer rather than a kernel fix.

Keep the tutorial local. Exposing a server beyond localhost requires authentication, network policy, and operational review; that is not a beginner-lab default.

## Exercises and acceptance

Produce a clean environment manifest and smoke response. Identify three facts from the startup log rather than guessing from the command. Restart with prefix caching enabled using `PREFIX_CACHING=1`, but do not yet claim it is faster. The lab passes when a peer can repeat the launch on the same recorded environment and explain which checks were not performed.

## References

- [S2] [vLLM quickstart](https://docs.vllm.ai/en/latest/getting_started/quickstart/)
- [S3] [vLLM platform-specific GPU installation](https://docs.vllm.ai/en/latest/getting_started/installation/gpu/)
- [S10] [Qwen2.5-0.5B-Instruct model card](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)
