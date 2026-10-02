# 06 · Build a decoder with a trustworthy reference

**Material status:** Core lesson draft. **Source-check date:** 2026-09-22.

The most useful first model is small enough that you can inspect every tensor and execute every correctness test without a GPU. The supplied `TinyDecoder` has random weights: it generates token IDs, not meaningful language. Its job is to expose causal computation and cache correctness without checkpoint loading, tokenizer behavior, or a fused kernel obscuring the mechanism.

## Learning objectives

Derive the shapes of Q, K, V and logits. Explain which operations are recomputed in dense generation. Build an independent numerical comparison before changing execution order.

## The mathematical path

For a sequence of length T, the hidden states have shape `[T, D]`. The teaching model projects normalized states into Q, K and V, then reshapes each to `[H, T, d]`, where `D = H × d`. Attention uses

```text
scores[h, i, j] = dot(Q[h, i], K[h, j]) / sqrt(d)
scores[h, i, j] = -infinity when j > i
attention_output = softmax(scores, dim=keys) @ V
```

The causal mask prevents the query at position i from reading future positions. A residual connection, another normalization, and a feed-forward network complete the layer. A final normalization and vocabulary projection produce `[T, vocabulary_size]` logits. Sampling from the last row produces the next token. During ordinary autoregressive generation, that sampled token is an input to the *next* forward operation.

This is a decoder-only Transformer teaching model, not a reproduction of a particular pretrained model. It uses learned position embeddings, ordinary multi-head attention, LayerNorm and GELU. It deliberately does not implement RoPE, GQA, MoE, a tokenizer, or checkpoint loading. Those differences matter when reading a real model implementation.

## Implement in this order

Read `ModelConfig`, `DecoderLayer.dense`, `TinyDecoder.forward`, then `generate_dense` in `mini_vllm/model.py`. Reimplement the dense method in a scratch branch before reading the cached method. Start with shape assertions and a two-token causal-mask test. Then generate a few tokens by repeatedly evaluating the entire growing sequence.

Next read `DecoderLayer.step`. It computes only the new token's Q, K and V, writes K and V into the request's page, reads the existing history, and evaluates the new query against that history. In this teaching implementation the reads gather page contents into a dense temporary tensor. That is useful for correctness; it is not an efficient PagedAttention kernel.

The cached method processes even a prefill chunk token by token. A production engine has stronger reasons to process known prompt tokens together. Keep the teaching tradeoff explicit: simpler intermediate states and tests, not an optimization claim.

## Lab

```bash
python -m pytest -q tests/test_engine.py -k 'dense or cached or chunk'
python -m mini_vllm.demo
```

Use prompt lengths immediately below, at, and above a block boundary. Compare logits, not only decoded text. Greedy tokens can match even when probabilities differ, and a tiny numerical change near a tie can change a greedy token despite otherwise close logits. Use an explicit floating-point tolerance and record the dtype and device. Do not demand bitwise equality across hardware as a universal guarantee.

## Exercises and acceptance

Explain why the final sampled token is not necessarily represented in the cache yet. Remove the causal mask in a scratch branch and describe which assertion should fail. Explain how an incorrect position offset could pass a one-token test but fail a longer continuation.

Submit a shape table, dense-versus-cached numerical comparison, and an account of one deliberately introduced bug. Passing the reference tests establishes the tested tiny model's behavior; it does not validate a new architecture or GPU backend.

## References

- [S2] [vLLM quickstart](https://docs.vllm.ai/en/latest/getting_started/quickstart/)
- [S5] [vLLM architecture overview (background; verify against pinned source)](https://docs.vllm.ai/en/latest/design/arch_overview/)
