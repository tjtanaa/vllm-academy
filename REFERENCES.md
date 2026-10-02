# References and source provenance

Checked on **2026-09-22**. Documentation URLs containing `latest` can change. Source walkthroughs use an immutable vLLM commit; runtime evidence is tracked separately.

**[S1]** [Tutorial inspiration: zero-to-sglang](https://github.com/datawhalechina/zero-to-sglang)

**[S2]** [vLLM quickstart](https://docs.vllm.ai/en/latest/getting_started/quickstart/)

**[S3]** [vLLM platform-specific GPU installation](https://docs.vllm.ai/en/latest/getting_started/installation/gpu/)

**[S4]** [vLLM automatic prefix caching design](https://docs.vllm.ai/en/latest/design/prefix_caching/)

**[S5]** [vLLM architecture overview (background; verify against pinned source)](https://docs.vllm.ai/en/latest/design/arch_overview/)

**[S6]** [vLLM serving benchmark CLI](https://docs.vllm.ai/en/latest/cli/bench/serve/)

**[S7]** [vLLM contribution guide](https://docs.vllm.ai/en/latest/contributing/)

**[S8]** [vLLM hybrid KV cache manager](https://docs.vllm.ai/en/latest/design/hybrid_kv_cache_manager/)

**[S9]** [vLLM disaggregated prefill](https://docs.vllm.ai/en/latest/features/disagg_prefill/)

**[S10]** [Qwen2.5-0.5B-Instruct model card](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)

**[S11]** [Nano-vLLM: optional independent reading](https://github.com/GeeeekExplorer/nano-vllm)

**[S12]** [vLLM v0.29.0 release](https://github.com/vllm-project/vllm/releases/tag/v0.29.0)

**[engine-core]** [vllm/v1/engine/core.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/engine/core.py)

**[scheduler]** [vllm/v1/core/sched/scheduler.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/core/sched/scheduler.py)

**[kv-manager]** [vllm/v1/core/kv_cache_manager.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/core/kv_cache_manager.py)

**[block-pool]** [vllm/v1/core/block_pool.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/core/block_pool.py)

**[gpu-runner-v2]** [vllm/v1/worker/gpu/model_runner.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/worker/gpu/model_runner.py)

**[kv-connector]** [vllm/distributed/kv_transfer/kv_connector/v1/base.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/distributed/kv_transfer/kv_connector/v1/base.py)

**[S13]** [vLLM quantization and hardware support](https://docs.vllm.ai/en/latest/features/quantization/)

**[S14]** [vLLM speculative decoding](https://docs.vllm.ai/en/latest/features/speculative_decoding/)

**[S15]** [vLLM CUDA Graph design](https://docs.vllm.ai/en/latest/design/cuda_graphs/)

## Originality

The learning progression is inspired by [S1]. The prose, exercises, diagrams, teaching implementation and tests were authored for this course. No Datawhale chapter text, images, branding or source files are included. Nano-vLLM is optional reading, not a dependency or claimed ROCm reference. No official affiliation or endorsement is implied.


## Foundational papers

See [the primary-source reading guide](READING_GUIDE.md) for PagedAttention, FlashAttention, Orca and speculative decoding, with questions matched to the curriculum.
