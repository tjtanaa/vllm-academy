# 16 · Know where the simple KV model stops

**Material status:** Advanced workshop brief. **Source-check date:** 2026-09-22.

The tiny engine assumes every layer has the same dense-attention cache structure. This is a useful starting point, not a universal law of inference engines.

## Learning objective and mental model

Distinguish a grow-with-context dense KV history from windowed attention state, compressed attention representations and recurrent/state-space state. A hybrid model can place different state requirements in different layer groups. Reusing one group's prefix without valid matching state for another group can be incorrect even when the prompt token IDs match.

The inspected vLLM cache manager constructs a coordinator and records cache groups; the official hybrid-cache design explains why a single uniform allocation view is insufficient. Use the actual architecture's state specification before applying a memory formula or prefix-boundary rule.

## Multimodal identity

A text prompt can contain placeholders whose meaning depends on image, audio or other processed inputs. Identical text token IDs are not necessarily enough to identify identical model computation. The official prefix-caching design includes additional hashes for such identity. The toy has no multimodal processor, encoder cache, modality positions or feature tensors, so its namespace/hash demonstration is not a ready-made multimodal cache.

## Workshop exercise

Choose a supported model whose architecture is documented at the selected version. Draw its state inventory by layer group: what grows, what is fixed-size, what can be shared, and what boundary is safe to resume from. Identify which state must accompany a cache hit. Design a negative control where identical visible text corresponds to different non-text input.

Do not start with a large model download. Begin with documentation and source specifications, then a small model/configuration already validated by the instructor. A successful import or first token does not prove correct prefix reuse for that architecture.

## Optional vLLM-Omni extension

A later elective can trace a multi-stage multimodal pipeline and ask where stage outputs, temporal alignment, streaming boundaries and cancellation differ from text-token serving. That elective needs its own vLLM-Omni source pin and end-to-end tests. No vLLM-Omni runtime or current support matrix was validated for this package, so it is intentionally outside the first cohort's core acceptance criteria.

## Acceptance artifact

Submit a state inventory, one safe/unsafe reuse example, and a source-backed explanation of why the dense-attention memory estimator is insufficient. Hardware results are optional and must be separately labeled. The ability to identify an invalid simplifying assumption is the main assessment.

## References

- [S8] [vLLM hybrid KV cache manager](https://docs.vllm.ai/en/latest/design/hybrid_kv_cache_manager/)
- [kv-manager] [vllm/v1/core/kv_cache_manager.py](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/vllm/v1/core/kv_cache_manager.py)
- [S4] [vLLM automatic prefix caching design](https://docs.vllm.ai/en/latest/design/prefix_caching/)
