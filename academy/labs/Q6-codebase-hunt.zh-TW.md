# Q6 · 程式碼尋寶：像是你自己寫的一樣，在百萬行程式碼裡來去自如

**需求：** git 與約 1 GB 的磁碟空間（不需要 GPU） · **時間：** 45 分鐘 · **集數：** E13, E14, E15, E16 · **XP：** +75（每個 hunt 另外 +40）
**[English](Q6-codebase-hunt.md)**

在巨大的程式碼庫裡找路，是可以練出來的技能。這個 lab 會讓你 checkout 課程固定的那個 vLLM commit，學會四招搜尋手法，然後挑戰 bot 出的計分 hunts（H1–H14）。bot 會用那個確切的 commit 來檢查你的答案。

## 1. Checkout 固定的 commit

`main` 上的行號會一直漂移，所以課程固定使用一個 commit（2026 年 10 月 12 日，v0.31.0 之後）。用 shallow 的方式抓取可以讓下載量小一點。

```bash
git clone --filter=blob:none https://github.com/vllm-project/vllm.git && cd vllm
git checkout 74f4404f58c0fb16821b34c16343486eeaf164a5
git log -1 --format='%h %cd %s'
```

> ✅ **檢查點：** `git log` 顯示 commit `74f4404f`。Discord 裡每個 `/code` 和 `/trace` 的 permalink 都指向這裡。

## 2. 先看清楚全貌

搜尋之前，先看一下地圖。這門課教的內容，大部分都在 `vllm/v1/` 底下。

```bash
ls vllm/ && ls vllm/v1/ && ls vllm/v1/core vllm/v1/engine vllm/v1/worker
```

> ✅ **檢查點：** 你能說出 scheduler 在哪個目錄（`vllm/v1/core/sched/`）、engine core 與 client 在哪裡（`vllm/v1/engine/`），以及 GPU model runner 在哪裡（`vllm/v1/worker/`）。

## 3. 學會四招搜尋手法

`git grep` 到哪都能用，而且很快。找定義就搜 `class Name` 或 `def name`，找呼叫者就搜名稱後面接 `(`，再用路徑來縮小範圍。

```bash
git grep -n "^class Scheduler" -- vllm/v1
git grep -n "def schedule(" -- vllm/v1/core
git grep -n "token_budget" -- vllm/v1/core/sched | head
git grep -ln "PagedAttention\|block_table" -- vllm/v1 | head
```

> ✅ **檢查點：** 你找到了定義 V1 `Scheduler` 的檔案。這就是 hunt **H1** 的答案：用 `/hunt hunt:H1` 提交。

## 4. 跟著一個請求走一遍

在 Discord 執行 `/trace`，從 `vllm serve` 開始，依序點過全部 12 站：HTTP route、AsyncLLM、EngineCore、scheduler、model runner、sampler，最後以串流 token 的形式回傳出去。每一站的 permalink 都在你的 checkout 裡打開來看。

```text
/trace
```

> ✅ **檢查點：** 你能在紙上畫出請求的路徑，並標出兩個 process 邊界（API server ↔ engine core 之間透過 ZMQ，engine core ↔ workers 之間）。

## 5. 解開 scheduler 的 hunts（E14）

打開 `Scheduler.schedule()`，不要中斷、從頭到尾讀過一遍。然後解 H2（token budget 的變數）、H9（處理模型輸出的方法）和 H14（FCFS 下誰會被 preempt）。

```bash
git grep -n "def update_from_output\|def _preempt\|self.running" -- vllm/v1/core/sched/scheduler.py | head -20
```

> ✅ **檢查點：** H2、H9 和 H14 都已在 Discord 解開。你能用一句話說明，一個請求被 preempt 時，它的 KV blocks 會怎麼處理。

## 6. 解開記憶體的 hunts（E08, E10）

KV cache manager、block pool 和 free queue，就是 Q2 playground 的正式上線版。請解 H3（block 配置）、H4（block hashing）和 H5（LRU free list），再解 H6–H7（影響重大的預設值）。

```bash
git grep -n "^class \|^def " -- vllm/v1/core/kv_cache_manager.py vllm/v1/core/block_pool.py vllm/v1/core/kv_cache_utils.py | head -40
```

> ✅ **檢查點：** 解開五個 hunts 就能拿到 🧭 **Navigator** 徽章。用 `/profile` 確認一下。

## 7. 解開硬體與模型的 hunts（E15, E16）

找出 vLLM 在哪裡挑選 attention backend（H8）、EAGLE proposer 在哪裡（H10）、哪個模組負責 serve DeepSeek-V3（H11）、KV-connector 的 base class（H12），以及 Model Runner V2 的目錄（H13）。

```bash
git grep -n "def get_attn_backend" -- vllm
git grep -n "DeepseekV3ForCausalLM" -- vllm/model_executor/models/registry.py
```

> ✅ **檢查點：** 14 個 hunts 全部解開，或者你已經在 `#labs-help` 發文，說明是哪一題難倒了你，以及你試過什麼。

## 8. 自己出一個 hunt

把程式碼庫記牢的最好方法，就是教別人。照著 `academy/content/hunts.yaml` 的格式寫一個新的 hunt：包含問題、提示、可接受的答案，以及一筆 code-map 條目。然後對 vllm-academy 開一個 PR。

```yaml
- id: H15
  xp: 40
  difficulty: 2
  q: {en: "...", zh: "..."}
  hint: {en: "...", zh: "..."}
  answers: ["..."]
  explain: {en: "...", zh: "..."}
  code: scheduler
```

> ✅ **檢查點：** 你的 hunt PR 已經開出去了。這算是對開源學習專案的一份真實貢獻，也是練習 Q8 的好暖身。

## 學到了什麼

- 讀程式碼之前先固定 commit，引用的所有東西都附上 permalink。
- 找定義、找呼叫者、找路徑，`git grep` 都比滾動畫面快得多。
- V1 引擎分成 API server、engine core、scheduler、KV manager 和 workers，而每個 hunt 都帶你認識了其中一塊在哪裡。
