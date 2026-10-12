# Q3 · Batching Arena：為什麼一張 GPU 能服務上千位使用者

**需要：** 只要 Python 3.10+（不需要 GPU、PyTorch） · **時間：** 15 分鐘 · **單元：** E05、E09、E11 · **XP：** +75
**[English](Q3-batching-arena.md)**

LLM 服務的大部分設計，都是由兩個問題決定的：為什麼 decode 是受記憶體頻寬限制（memory-bound）的？排程器下一步該跑什麼？這個實驗用一個 roofline 成本模型，再讓三種排程器在同一份工作負載上賽跑，來回答這兩個問題。

> 這個 arena 模擬的是在 H100 等級 GPU 上跑 8B 的 BF16 模型。每一步的成本是 `overhead + max(bytes / bandwidth, FLOPs / peak)`。絕對數字只是示意；真正會延續到實際 vLLM 的是結果的「形狀」（Q7 會去量測真實的數據）。預設的執行結果是確定性的，所以你的數字應該會一模一樣。

## 1. 畫出 roofline（E05）

不管 batch 裡有幾位使用者，decode 每一步都要把全部 16 GB 的權重讀一遍。

```bash
python academy/labs/batching_arena.py --roofline
```

> ✅ **檢查點：** batch 1 每一步大約花 **7.5 ms**（約 133 tokens/s）。batch 8 大約花 **7.9 ms**，卻產出 8 倍的 token。每一列的結果都寫著 `memory`。

## 2. 讀懂這個取捨

看看 `per-user tok/s` 這一欄隨著 batch 變大的變化：總吞吐量一路攀升，但每位使用者的速度卻變慢了，因為 KV 的讀取量會隨著 batch × context 一起增加。到了 512 條序列時，KV 甚至連 80 GB 都放不下。

```text
batch  step ms  total tok/s  per-user tok/s
   64     10.7        5,983            93.5
  256     20.3       12,603            49.2
```

> ✅ **檢查點：** 你能用兩句話回答面試經典題「為什麼 batching 對 decode 幫助這麼大？」，而且要用到 *頻寬（bandwidth）* 和 *權重（weights）* 這兩個詞。

## 3. 開始賽跑（E09）

同一份工作負載會在三種排程器下各跑一次：24 個聊天請求，再加上一個在 0.8 秒時貼進來的 🐋 16,000 token 長文。

```bash
python academy/labs/batching_arena.py
```

> ✅ **檢查點：** 計分板顯示，同一張 GPU 上 static batching 約為 **468 tok/s**，continuous batching 約為 **1,192 tok/s**。Static 的 TTFT p50 約 **4.9 s**；continuous 只有約 **0.15 s**。

## 4. 讀懂時間軸

`·` 代表等待中，`▒` 代表 prefill，`█` 代表正在 decode。在 static batching 裡，先完成的請求會留下空位閒置，一直到 batch 裡最慢的那個也做完為止，後來的新請求則得在整個 batch 後面排隊。Continuous batching 每一步都會讓請求進場和離場（這就是 iteration-level scheduling，出自 Orca 論文）。

```text
Legend: · waiting   ▒ prefill   █ decoding   🐋 = the 16k-token paste
```

> ✅ **檢查點：** 你能在 static 的時間軸上指出某一列：明明 GPU 還有空間，那個請求卻等了很久。

## 5. 抓出鯨魚造成的停頓（E11）

看看 continuous batching 底下的 `decode gap` 那一行：有一個高達約 **401 ms** 的巨大尖峰。那是鯨魚整段 16k token 的 prefill 被當成單一一步執行，期間所有正在聊天的使用者都被凍住了。現在明確把 chunking 關掉來比較：

```bash
python academy/labs/batching_arena.py --chunk 0
```

> ✅ **檢查點：** 用 `--chunk 0` 時，第三列的結果會跟 continuous 一樣（最糟的間隔約 401 ms）。用預設的 `--chunk 512` 時，最糟的間隔只有約 **14 ms**。Chunked prefill 要付出一點 TTFT 的代價（p50 從 0.15 s 變成 0.25 s）。

## 6. 自己動手調調看

試試不同的預算和工作負載，並記下有什麼變化。chunk 越小，對 decode 的保護越好，但步數會變多；沒有鯨魚的話，chunking 幾乎沒什麼影響。

```bash
python academy/labs/batching_arena.py --chunk 2048
python academy/labs/batching_arena.py --chunk 128
python academy/labs/batching_arena.py --no-whale
python academy/labs/batching_arena.py --batch 32
```

> ✅ **檢查點：** 你找到了一個 chunk 大小，讓最糟的間隔和 TTFT p99 你都能接受，而且能說明自己為什麼這樣選。

## 7. 對應到真正的 vLLM 參數

Arena 裡的每個旋鈕，在真正的 vLLM 都有對應的名字。在 vLLM 裡，chunked prefill 預設就是開啟的，`--max-num-batched-tokens` 是每一步的 token 預算（也就是 arena 的 `--chunk`），而 `--max-num-seqs` 則限制同時最多能執行多少個請求。

```bash
vllm serve Qwen/Qwen3-8B --max-num-batched-tokens 2048 --max-num-seqs 128
```

> ✅ **檢查點：** 你能向隊友說明，調高 `--max-num-batched-tokens` 會對 TTFT 和 inter-token latency 造成什麼影響。請把你的說明貼到 `#show-your-work`。

## 學到了什麼

- Decode 受記憶體頻寬限制：batching 讓許多使用者共用同一次權重讀取。
- Continuous batching 以每一步為單位來排程，所以沒有人需要等最慢的那個請求。
- 巨大的 prefill 會讓 decode 停擺；每一步的 token 預算（chunked prefill）能把一次漫長的凍結，變成幾個稍微慢一點的步驟。
- 每個旋鈕都是在 TTFT、inter-token latency 和吞吐量之間互相取捨。天下沒有白吃的午餐，只有經過評估的選擇。
