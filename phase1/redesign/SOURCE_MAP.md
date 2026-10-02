# Production source-reading map

Reading pin: `b558f160a2c0abcb5902acc3c91a14c38a4af173`, resolved from upstream main on October 2, 2026. This supplement does **not** silently replace the Academy v0.29.0 baseline. Sources below are navigation targets, not a proof that every configuration takes the same path.

## api

[vllm/entrypoints/openai/chat_completion/api_router.py](https://github.com/vllm-project/vllm/blob/b558f160a2c0abcb5902acc3c91a14c38a4af173/vllm/entrypoints/openai/chat_completion/api_router.py#L1-L130)

Follow validation, handler delegation, errors and SSE. Do not begin by reading the whole server.

Evidence: selected excerpt inspected.

## renderer

[vllm/renderers/base.py](https://github.com/vllm-project/vllm/blob/b558f160a2c0abcb5902acc3c91a14c38a4af173/vllm/renderers/base.py#L70-L170)

Distinguish tokenizer and multimodal-processing executors from the GPU model executor.

Evidence: selected excerpt inspected.

## render-wire

[docs/serving/online_serving/renderer.md](https://github.com/vllm-project/vllm/blob/b558f160a2c0abcb5902acc3c91a14c38a4af173/docs/serving/online_serving/renderer.md)

Read Responses statelessness and multimodal kwargs_data/mm_metadata requirements.

Evidence: selected excerpt inspected.

## input

[vllm/v1/engine/input_processor.py](https://github.com/vllm-project/vllm/blob/b558f160a2c0abcb5902acc3c91a14c38a4af173/vllm/v1/engine/input_processor.py#L50-L155)

Inspect task-specific parameter validation and renderer ownership.

Evidence: selected excerpt inspected.

## processor

[vllm/multimodal/processing/processor.py](https://github.com/vllm-project/vllm/blob/b558f160a2c0abcb5902acc3c91a14c38a4af173/vllm/multimodal/processing/processor.py)

Located by symbol search; read prompt updates, item correspondence and cache handling locally.

Evidence: symbol search located.

## core

[vllm/v1/engine/core.py](https://github.com/vllm-project/vllm/blob/b558f160a2c0abcb5902acc3c91a14c38a4af173/vllm/v1/engine/core.py)

Located by symbol search; trace the scheduled work object into execution and the returned output.

Evidence: symbol search located.

## scheduler

[vllm/v1/core/sched/scheduler.py](https://github.com/vllm-project/vllm/blob/b558f160a2c0abcb5902acc3c91a14c38a4af173/vllm/v1/core/sched/scheduler.py#L85-L135)

Compare admission constraints and runner slots, then locate schedule and update_from_output(s).

Evidence: selected excerpt inspected.

## runner

[vllm/v1/worker/gpu/model_runner.py](https://github.com/vllm-project/vllm/blob/b558f160a2c0abcb5902acc3c91a14c38a4af173/vllm/v1/worker/gpu/model_runner.py#L1-L100)

Read model-agnostic design constraint and imports; follow selected helper functions, not every line.

Evidence: selected excerpt inspected.

## vlm

[vllm/model_executor/models/llava.py](https://github.com/vllm-project/vllm/blob/b558f160a2c0abcb5902acc3c91a14c38a4af173/vllm/model_executor/models/llava.py#L450-L670)

Read _process_image_input and embed_multimodal. Follow vision tower, projector and language model.

Evidence: selected excerpt inspected.

Run `python -m labs.source_walk --checkout /path/to/vllm` from this package to resolve symbols in a local checkout. It verifies the exact Git commit first. Read a bounded excerpt, name the input/output contract, then close the file. The default reader makes no network requests.
