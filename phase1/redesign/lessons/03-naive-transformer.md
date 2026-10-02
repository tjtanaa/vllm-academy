# 03 — Build a naive Transformer decoder

**Status:** original lesson draft. **Pacing:** use the theory/lab/source cycle in the curriculum; exact timing is an instructor choice.

The first model should be small enough that a learner can follow every tensor. This lesson implements a decoder-only teaching model, not a bit-for-bit reconstruction of the original 2017 encoder-decoder Transformer and not a Llama/Qwen checkpoint loader. [R03](../REFERENCES.md)

## The forward computation

Start with IDs of shape `[B,T]`, an embedding width `D`, `H` attention heads and vocabulary size `V`. The lab obtains `[B,T,D]` token embeddings and adds learned positional embeddings. Within a block, projections form Q, K and V. In this particular ordinary-MHA lab, each head has width `D/H`.

Attention computes `softmax(Q Kᵀ / sqrt(d_head) + mask) V`. The causal mask removes access to future key positions. The attention output passes through a projection and a residual connection. A token-wise feed-forward network follows normalization and another residual. Finally the vocabulary projection gives `[B,T,V]` logits.

The softmax over keys belongs to attention; the later distribution over vocabulary belongs to token selection. They normalize different axes for different purposes. The feed-forward network transforms a position's features; attention mixes information across allowed positions.

## What the lab simplifies

| Choice in this lab | Why it is useful now | What comes later |
|---|---|---|
| Learned absolute positions | Position information is easy to locate. | Model-specific RoPE. |
| Ordinary MHA | One head-count relation is easy to inspect. | GQA and explicit projected head dimensions. |
| LayerNorm + GELU | Compact familiar building blocks. | RMSNorm and gated FFNs. |
| Pre-norm decoder blocks | Small readable modern-style scaffold. | Understand original post-norm encoder-decoder separately. |
| Dense attention matrix | Every mask entry can be inspected. | IO-efficient and paged attention implementations. |

The original Transformer also contains an encoder stack and decoder cross-attention. A causal-only decoder should not be described as that entire original architecture. The Annotated and Illustrated Transformer are useful comparative readings, not code to paste indiscriminately into this model. [R08–R09](../REFERENCES.md)

## Run and break it

```bash
python -m labs.naive_transformer
python -m pytest -q tests/test_mechanisms.py -k 'future_tokens'
```

For the default lab, `[1,6]` IDs become `[1,6,24]` embeddings. Q has shape `[1,3,6,8]`, and attention scores have shape `[1,3,6,6]`. Predict the final logit shape using the vocabulary size in `Config` before reading output.

Temporarily remove the mask and rerun the future-mutation tests. A change to later input tokens must not alter earlier causal logits. Restore the mask after explaining why the failing result exposes information leakage.

## Source detour and exit ticket

Read only `Block.forward` and annotate the axes of three operations. Then read `NaiveDecoder.forward` to locate model-level embedding and output projection. Keep model mathematics separate from an engine schedule.

A passing submission includes the tensor ledger, a mask for four positions, and a test proving future-token invariance. A diagram alone is not the correctness evidence.
