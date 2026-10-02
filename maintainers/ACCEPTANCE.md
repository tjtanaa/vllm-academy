# Acceptance and validation gates

## Included and locally testable

Original random-weight decoder; dense and incremental logits; physical K/V pages and logical tables; retain/release; full-block chained prefix identity and LRU index eviction; dynamic request admission; token-budget scheduling; greedy generation; cancellation and deterministic cleanup. The reference tests also cover unsharded KV arithmetic.

The code is CPU-friendly and uses ordinary PyTorch operations. It gathers page contents and executes requests serially. A passing test means the recorded inputs passed in the recorded CPU environment; it does not imply a fused kernel, physical GPU batching, model-family compatibility or a production service.

## Intentionally absent

Pretrained weights/tokenizer, RoPE/GQA/MoE implementation, fused paged attention, vectorized prefill, HTTP transport in the toy, actual parallel GPU execution, graph capture, quantization, speculative decoding, preemption, external transfers and hybrid/multimodal state. The corresponding lessons are source exercises or workshop briefs. The real server is vLLM itself, launched separately by the provided recipes.

## Publication gates

| Gate | Requirement | Starter status |
|---|---|---|
| CPU reference | Full tests and saved environment | See `results/validation.json` |
| Script syntax | Python compilation and Bash syntax | See validation evidence |
| Pedagogical review | Human review of explanations, progression and exercises | Pending |
| Source review | Six immutable excerpts inspected | Source-checked; not a runtime trace |
| Source checker | Run against a matching full checkout | Not executed in this environment |
| CUDA service | Pinned image/model, smoke, correctness, benchmark | Not run |
| ROCm service | Pinned image/model, HIP/backend evidence, smoke, correctness, benchmark | Not run |
| Advanced workshops | Version-specific implementations and measurements where advertised | Briefs only |
| Hosted CI | Workflow runs in the intended GitHub repository | Not run here |
| Public release | Owner/reviewer, license/attribution, links, accessibility | Final maintainer review required |

## Evidence discipline

Do not replace failures with inferred compatibility. Preserve raw logs and model/input identity. Report limitations beside a result, not only in a footnote. Never advertise synthetic numbers as measured GPU throughput. Re-run checks whenever code or dependencies change.
