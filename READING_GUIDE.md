# Primary-source reading guide

Read to answer a question, not to accumulate a bibliography. The links below are primary papers and official documentation. Paper landing pages and abstracts were checked on 2026-09-22; this package does not claim a full new review or reproduction of their results. Historical benchmark numbers are not current vLLM performance guarantees.

| Read after | Primary source | Question to bring to the code |
|---|---|---|
| KV memory and pages | [Efficient Memory Management for Large Language Model Serving with PagedAttention](https://arxiv.org/abs/2309.06180) | How do fragmentation and sharing affect how many requests can fit? Where does logical-to-physical translation occur? |
| Hardware and attention backends | [FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](https://arxiv.org/abs/2205.14135) | Which memory traffic does tiling reduce? How is that different from deciding where persistent KV blocks live? |
| Scheduling | [Orca: A Distributed Serving System for Transformer-Based Generative Models](https://www.usenix.org/conference/osdi22/presentation/yu) | What changes when scheduling decisions happen at iteration granularity rather than request completion? |
| Speculative workshop | [Fast Inference from Transformers via Speculative Decoding](https://arxiv.org/abs/2211.17192) | What must verification establish before candidate tokens can be committed? Which assumptions are needed for distribution preservation? |
| Prefix reuse | [vLLM prefix-cache design](https://docs.vllm.ai/en/latest/design/prefix_caching/) | What identities belong in a reuse key? What makes a cached block safe to reclaim? |
| Production source tour | [vLLM architecture overview](https://docs.vllm.ai/en/latest/design/arch_overview/) and the pinned source map | Which high-level responsibilities remain recognizable, and which source paths have changed? |
| Hybrid-state workshop | [vLLM hybrid cache manager](https://docs.vllm.ai/en/latest/design/hybrid_kv_cache_manager/) | Why is one dense-attention memory formula insufficient for every model? |

## Two concepts not to conflate

Paged KV storage and IO-aware attention tiling solve different parts of the problem. Paging manages persistent cache placement, sharing and allocation; IO-aware attention changes how an attention computation moves data between memory levels. The papers explain these different goals. Do not teach “PagedAttention versus FlashAttention” as though the names alone establish two mutually exclusive full serving architectures. A particular backend's supported layouts still need verification.

## Optional compact-code comparison

[Nano-vLLM](https://github.com/GeeeekExplorer/nano-vllm) is an independent compact implementation to examine after building the course engine. Compare its assumptions and abstractions rather than copying it wholesale. Its inclusion is not a claim of ROCm compatibility or that this course's toy has the same features.

## Reading note format

Record the problem, key idea, assumptions, one state invariant, one evaluation limitation, and one code question. Distinguish what the paper actually says from your proposed extension. Tie the note to a lesson and an immutable source revision when making implementation claims.
