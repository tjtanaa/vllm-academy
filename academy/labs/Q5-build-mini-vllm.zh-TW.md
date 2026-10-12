# Q5 · 打造 mini-vLLM：最終 Boss 戰

**需求：** CPU + PyTorch（不需要 GPU） · **時間：** 一週內分段完成，共 4–8 小時 · **集數：** E06, E08, E09, E10, E12 · **XP：** +75
**[English](Q5-build-mini-vllm.md)**

你要從頭重建一個小型推論引擎（incremental KV、paged blocks、有 token budget 的 scheduler、prefix 重用、取消請求），並讓 30 個測試來判定它是不是真的能用。repo 裡的 `mini_vllm/` 是參考解答。規則只有兩條：**先預測再偷看**，以及絕對不能為了讓測試變綠就刪掉測試。

> mini_vllm 使用隨機權重，而且在 CPU 上循序執行。它教的是 vLLM 背後的*機制*，不是速度。詳細的里程碑表請看 [labs/MILESTONES.md](../../labs/MILESTONES.md)。

## 1. 建立環境並執行參考解答

建立獨立的環境、安裝 CPU 版 PyTorch，並在動手修改之前，先確認參考引擎能通過所有測試。

```bash
git clone https://github.com/tjtanaa/vllm-academy.git && cd vllm-academy
python3 -m venv .venv && source .venv/bin/activate
python -m pip install 'torch==2.10.0' --index-url https://download.pytorch.org/whl/cpu
python -m pip install 'pytest>=8,<10'
python -m pytest -q && python -m mini_vllm.demo
```

> ✅ **檢查點：** 所有測試通過，而且 demo 會印出請求被排程的 trace。接著開一個練習用的 branch：`git switch -c my-mini-vllm`。

## 2. M1–M2：decoder 與 incremental KV

在讀 `model.py` 之前，先寫下長度為 T 的 prompt 其 Q、K、V 的 shape，以及 KV cache 必須存什麼，才能讓第 T+1 步不用重算第 1 到第 T 步。然後在你的 branch 裡實作（或重寫）`DecoderLayer.step` 和 `TinyDecoder.cached`。

```bash
python -m pytest -q tests/test_engine.py -k 'dense or chunking'
```

> ✅ **檢查點：** 對每個測試用的 prompt 長度，cached 和 dense 的 logits 都在容許誤差內一致。你能解釋為什麼 chunked prefill 跟一次做完的 prefill 會得到相同的答案。

## 3. M3：實體分頁與 block tables

現在把每個請求私有的 cache 換成共用的 `BlockPool`，並為每個請求建立 block table。這就是把 Q2 的 playground 變成真的東西。動手前先寫下不變條件：一個 page 除非被共用，否則只有一個擁有者；而且只要還有人參照，page 就不能被釋放。

```bash
python -m pytest -q tests/test_engine.py -k 'noncontiguous or commit or pool_lifetime'
```

> ✅ **檢查點：** 不連續的 pages 產生完全相同的 logits，而且每個請求結束後，pool 都會回到全部空閒的狀態。

## 4. M4：scheduler

在 `Engine.step` 裡實作 waiting／running 佇列，以及每一步的 token budget。請求必須能在執行途中加入，也能在任何時候被取消。這就是 Q3 的 continuous batching。

```bash
python -m pytest -q tests/test_engine.py -k 'cancel or dynamic'
```

> ✅ **檢查點：** 有一份 trace 顯示晚到的請求加入了正在跑的 batch，而且取消一個執行中的請求會立刻釋放它的 pages。

## 5. M5：prefix 重用

為每個完整的 block 產生一個串鏈式的 key（parent key + tokens + namespace），並在不同請求之間重用相符的 blocks。只有完整的 block 才能共用。絕對不要寫入共用的 block。

```bash
python -m pytest -q tests/test_engine.py -k 'prefix'
```

> ✅ **檢查點：** 同一個 prompt 的冷啟動與暖啟動（cold／warm）輸出完全相同，而且*第一個* token 就不同的兩個 prompt 什麼都不會共用。

## 6. M6：撐過壓力測試

把整個生命週期補完整：finish、cancel、close、eviction 以及 block 用完的情況。被驅逐的 page 絕對不能是仍有活躍請求在使用的那一個。

```bash
python -m pytest -q
```

> ✅ **檢查點：** 你的 branch 上整套測試全綠，而且 `close()` 之後沒有遺漏的參照。在 `#show-your-work` 貼上截圖就能領取 ⚙️ Engine Builder 徽章（也記得在 Discord 完成 S2）。

## 7. 突變挑戰

故意破壞一條不變條件，先預測哪個測試會失敗，再執行測試。可以試試這些：重用一個已釋放的活躍 page；漏掉 parent hash；覆寫共用的完整 block；取消時忘記釋放。

```bash
python -m pytest -q -x
```

> ✅ **檢查點：** 每個突變都讓你預測的那個測試失敗。如果有突變存活下來，代表你找到了測試的覆蓋缺口。補上一個針對性的測試，這個測試就是送給這個 repo 一份很棒的第一個 PR。

## 學到了什麼

- Incremental KV 把 O(T²) 的重複計算，變成每條序列 O(T) 的工作量。
- Paging、reference count 和串鏈式 prefix key 各自只要幾十行程式碼，而測試會告訴你每一行為什麼存在。
- scheduler 就是在 budget 限制下跑迴圈處理佇列；真正困難的是出錯時的清理。
- 現在你知道，在 S3 打開 vLLM 真正的 `scheduler.py` 和 `kv_cache_manager.py` 時，該問哪些問題了。
