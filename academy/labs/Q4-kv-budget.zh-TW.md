# Q4 · KV Budget：讓大多數面試者翻車的記憶體算術

**需求：** 只要 Python 3.10+ · **時間：** 10 分鐘 · **集數：** E07, E18 · **XP：** +75
**[English](Q4-kv-budget.md)**

「Llama-3.1-70B 跑一個 128k context 的請求，需要多少記憶體？」面試官愛問這題，因為它能看出你到底懂不懂推論時 GPU 記憶體裡裝了什麼。做完這個 lab，你可以在 30 秒內答出來，還會知道這個答案在真實世界哪裡會失準。

## 1. 列出預設模型

這些預設模型的參數都來自 Hugging Face 上公開的 `config.json`。跟 KV 有關的只有三個欄位：`num_hidden_layers`、`num_key_value_heads` 和 `head_dim`。

```bash
python academy/labs/kv_budget.py --list
```

> ✅ **檢查點：** 你看到 `llama-3.1-70b`：80 層、8 個 KV heads、head_dim 128，每個 token 的 KV 是 **320 KiB**。

## 2. 回答 E07 的那一題

Llama-3.1-70B、131,072 個 token、4 張 80 GB 的 GPU：

```bash
python academy/labs/kv_budget.py --model llama-3.1-70b --context 131072 --gpus 4 --gpu-mem 80
```

> ✅ **檢查點：** 一條 128k 的序列需要 **40.0 GiB** 的 KV。BF16 權重大約 132 GiB，4 張 GPU 同時大約能放下 **4** 條滿長度的序列。

## 3. 像高手一樣說出來

要背的是公式的「形狀」，不是數字：`2 (K and V) × layers × kv_heads × head_dim × bytes`。以 70B 模型來說就是 `2 × 80 × 8 × 128 × 2 B = 320 KiB`（每個 token）。接著算每條序列、再扣掉權重、看剩多少、最後算出能放幾條。

```text
2 × 80 layers × 8 KV heads × 128 head_dim × 2 B = 320 KiB per token
320 KiB × 131,072 tokens = 40.0 GiB
```

> ✅ **檢查點：** 關掉終端機，在紙上一分鐘內算完 70B 這題。

## 4. 把 KV 縮小（E18）

把 KV cache 量化成 FP8 或 FP4，位元組數會減半或剩四分之一，同樣的硬體就能塞進更多請求。

```bash
python academy/labs/kv_budget.py --model llama-3.1-8b --context 8192 --gpu H100 --compare
```

> ✅ **檢查點：** 在單張 H100 上，8k context 的 Llama-3.1-8B 用 BF16 KV 大約能放 **58** 條序列，FP8 是 **116** 條，FP4 是 **233** 條。實際的 NVFP4 還要存每個 block 的 scale（每個值約 4.5 bit），所以比較接近 3.5 倍，而不是 4 倍。

## 5. 認識 MLA

DeepSeek 系列的 Multi-head Latent Attention 每層只存一份壓縮過的 latent，而不是每個 head 都存完整的 K 和 V。來比較一下它和 70B GQA 模型每個 token 的 KV 差多少。

```bash
python academy/labs/kv_budget.py --model deepseek-v3 --context 131072 --gpus 8 --gpu H200 --weight-dtype fp8
```

> ✅ **檢查點：** DeepSeek-V3 每個 token 大約只要 **68.6 KiB**，不到 Llama-70B（320 KiB）的四分之一，儘管它是 671B 的大模型。你能用一句話說明 MLA 為什麼存在。DeepSeek-V3 發布的就是 FP8 權重，所以要加 `--weight-dtype fp8`。加分題：在 tensor parallel 下，MLA 的 latent 會複製到每個 rank 上而不是被切開，所以多加 GPU 增加的 KV 空間會比計算機假設的少。

## 6. 換成你自己的模型

打開任何一個模型在 Hugging Face 上的 `config.json`，把它的數字填進去。如果沒有列出 `head_dim`，通常就是 `hidden_size / num_attention_heads`。

```bash
python academy/labs/kv_budget.py --layers 40 --kv-heads 8 --head-dim 128 --params 14 --context 32768 --gpu RTX-4090
```

> ✅ **檢查點：** 你能判斷那個 14B 模型用 BF16 放不放得進 24 GB 的顯示卡；放不下的話，你知道可以怎麼調整（FP8 權重、FP8 KV、縮短 context，或再加一張 GPU）。

## 7. 對照真實世界

如果你做過 Q1，就拿真實的 log 來比對。Qwen3-0.6B 有 28 層、8 個 KV heads、head_dim 128，所以每個 token 是 `2 × 28 × 8 × 128 × 2 B = 112 KiB`。把 vLLM 回報的 KV 記憶體除以這個數字，結果應該很接近它印出來的 token 數。在 Discord 裡，`/kvcalc` 用的是同一套公式。

```text
/kvcalc model:qwen3-0.6b context:4096 gpu:T4
```

> ✅ **檢查點：** 你手算出的 token 容量，和 Q1 log 裡 `GPU KV cache size` 那一行的誤差在 10% 左右以內。如果差很多，請列出計算器沒算進去的東西：activations、CUDA graphs、`--gpu-memory-utilization` 設定，以及記憶體碎片。

## 學到了什麼

- 每個 token 的 KV = `2 × layers × kv_heads × head_dim × bytes`。GQA 和 MLA 就是為了把它變小而生的。
- 長 context 首先是記憶體問題，其次才是運算問題。
- 量化 KV cache 是拿一點點精度風險，換來大幅提升的並行量。
- 計算器的結果，一定要拿引擎自己的啟動 log 來對照。
