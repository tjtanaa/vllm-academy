# Q4 · KV Budget: the memory math that sinks most candidates

**Needs:** Python 3.10+ only · **Time:** 10 min · **Episodes:** E07, E18 · **XP:** +75
**[繁體中文](Q4-kv-budget.zh-TW.md)**

"How much memory does a 128k-context request on Llama-3.1-70B need?" Interviewers ask this because it shows whether you understand what's actually in GPU memory during inference. After this lab you'll answer it in 30 seconds and know where the answer goes wrong in real life.

## 1. List the presets

The presets come from public Hugging Face `config.json` files. What matters for KV is `num_hidden_layers`, `num_key_value_heads` and `head_dim`.

```bash
python academy/labs/kv_budget.py --list
```

> ✅ **Checkpoint:** you see `llama-3.1-70b` with 80 layers, 8 KV heads, head_dim 128 and **320 KiB** of KV per token.

## 2. Answer the E07 question

Llama-3.1-70B, 131,072 tokens, 4× 80 GB GPUs:

```bash
python academy/labs/kv_budget.py --model llama-3.1-70b --context 131072 --gpus 4 --gpu-mem 80
```

> ✅ **Checkpoint:** one 128k sequence needs **40.0 GiB** of KV. The BF16 weights are about 132 GiB, and 4 GPUs hold about **4** full-length sequences at once.

## 3. Say it like a pro

Memorize the shape of the formula, not the numbers: `2 (K and V) × layers × kv_heads × head_dim × bytes`. For the 70B model that's `2 × 80 × 8 × 128 × 2 B = 320 KiB` per token. Then per sequence, then weights, then what's left, then how many fit.

```text
2 × 80 layers × 8 KV heads × 128 head_dim × 2 B = 320 KiB per token
320 KiB × 131,072 tokens = 40.0 GiB
```

> ✅ **Checkpoint:** close the terminal and do the 70B math on paper in under a minute.

## 4. Shrink the KV (E18)

Quantizing the KV cache to FP8 or FP4 halves or quarters its bytes, so more requests fit on the same hardware.

```bash
python academy/labs/kv_budget.py --model llama-3.1-8b --context 8192 --gpu H100 --compare
```

> ✅ **Checkpoint:** on one H100, 8k-context Llama-3.1-8B fits about **58** sequences with BF16 KV, **116** with FP8 and **233** with FP4. Real NVFP4 also stores per-block scales (about 4.5 bits per value), so expect closer to 3.5× than 4×.

## 5. Meet MLA

DeepSeek-style Multi-head Latent Attention stores one compressed latent per layer instead of full K and V for each head. Compare its per-token KV with the 70B GQA model.

```bash
python academy/labs/kv_budget.py --model deepseek-v3 --context 131072 --gpus 8 --gpu H200 --weight-dtype fp8
```

> ✅ **Checkpoint:** DeepSeek-V3 needs about **68.6 KiB** per token, less than a quarter of Llama-70B's 320 KiB, despite being a 671B model. You can say in one sentence why MLA exists. DeepSeek-V3 ships FP8 weights, hence `--weight-dtype fp8`. Bonus: under tensor parallelism the MLA latent is replicated on every rank rather than split, so extra GPUs add less KV room than the calculator assumes.

## 6. Bring your own model

Open any model's `config.json` on Hugging Face and plug in its numbers. If `head_dim` isn't listed, it's usually `hidden_size / num_attention_heads`.

```bash
python academy/labs/kv_budget.py --layers 40 --kv-heads 8 --head-dim 128 --params 14 --context 32768 --gpu RTX-4090
```

> ✅ **Checkpoint:** you can tell whether that 14B model fits on a 24 GB card in BF16, and what you'd change if it doesn't (FP8 weights, FP8 KV, shorter context, or a second GPU).

## 7. Check against reality

If you did Q1, compare with the real log. Qwen3-0.6B has 28 layers, 8 KV heads and head_dim 128, so `2 × 28 × 8 × 128 × 2 B = 112 KiB` per token. Divide the KV memory vLLM reported by that and you should get close to the token count it printed. In Discord, `/kvcalc` uses the same formulas.

```text
/kvcalc model:qwen3-0.6b context:4096 gpu:T4
```

> ✅ **Checkpoint:** your hand-calculated token capacity is within about 10% of the `GPU KV cache size` line in your Q1 log. If not, list what the calculator ignores: activations, CUDA graphs, the `--gpu-memory-utilization` setting and fragmentation.

## What you learned

- KV per token = `2 × layers × kv_heads × head_dim × bytes`. GQA and MLA exist to shrink it.
- Long contexts are a memory problem before they're a compute problem.
- Quantizing the KV cache trades a little accuracy risk for a lot of concurrency.
- Always check the calculator against the engine's own startup log.
