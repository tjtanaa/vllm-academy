# vLLM Academy Quest：從零到推論工程師

**[English](CURRICULUM.md)** · [Academy Quest 首頁](README.zh-TW.md) · [Discord 機器人](../discord_bot/README.md)

> 全世界花在「跑」大型語言模型的錢，已經比「訓練」它們還多。懂得讓推論又快又省的人，是 AI 領域最搶手的工程師之一；而業界大多數人用的開源推論引擎，就是 vLLM。
> 這門課帶你從「token 是什麼？」一路走到「我的 PR 被 merge 了，而且我能在白板上設計一套 70B 模型的服務架構」，每集只要 20 分鐘。

這是建立在本 repo 嚴謹的 Phase 1 課程之上的**社群版學習層**。原本的課程仍是深度內容的正式來源；Academy Quest 把它們重新包裝成短小、雙語、以「鉤子」開場的單集，由 Discord 機器人負責派送、出題與追蹤進度。每一集都會連回對應的深入課程。

## 和 Phase 1 課綱相比，改了什麼？為什麼？

| Phase 1（深入、嚴謹） | Academy Quest（為社群優化） | 原因 |
|---|---|---|
| 18 堂課、每堂 90 分鐘 | 7 季、28 集，每集 15–30 分鐘（其中一季是每月更新的*活季度*） | 大家是在手機上、在課堂之間打開 Discord。小小的成就感讓人一直回來。 |
| 英文課程 + 繁中入口頁 | 每一集、測驗、實作、名詞解釋與機器人訊息都有**英文與繁體中文** | 台灣社群用雙語學最有效；面試又常常是英文。 |
| 理論 → 引擎 → 原始碼 → 貢獻 | 主軸不變，另加**職涯路線**（面試題庫、模擬面試、系統設計、作品集） | 學生很明確：想找到工作、想把面試答好。我們就誠實地為這個目標而教。 |
| 實作需要 PyTorch 或 GPU | 新增三個**免安裝實作**（只用 Python 標準函式庫），先上手再碰 GPU | 第一天就拿掉「我沒有 GPU」這個藉口。 |
| 生產環境主題停在 2025 年的架構 | 新增 **高手加速祕技** 一季，涵蓋 vLLM 在 2026 年正在推出的東西：speculative decoding（EAGLE-3、MTP、DFlash）、NVFP4、prefill/decode 分離部署、分層 KV offload、RL rollout | 這正是現在面試官與維護者在聊的話題。 |
| 一章「閱讀原始碼」 | 一條**請求追蹤**導覽，附上固定版本 vLLM commit 的永久連結，再加上由機器人評分的原始碼尋寶遊戲 | 在超過一百萬行 Python 裡找路是一種技能，我們用遊戲的方式練習。 |

Phase 1 的內容一行都沒刪。它的證據規則依然適用：CPU 玩具引擎的結果不是 GPU 效能數據；沒實際跑過的 GPU 指令會清楚標示。

### 第二輪調整（2026 年 10 月 12 日）

| 新增 | 原因 |
|---|---|
| **S6 🔮 前沿觀測站**，一個活季度：E27 agent 推論、E28 冷啟動 | Agent 流量與彈性服務，是 vLLM 在 2026 年 9–10 月推出最多、寫最多文章的主題。每月更新的一季，讓大家有理由一直回來。 |
| **大膽預測法庭**（`/hottake`）：10 則有日期的預測，附信心百分比、證據，以及「什麼情況代表我們錯了」。大家投票，到期我們自己打分數。 | 推測是最容易被分享的內容；誠實標註它，能教大家分辨證據和炒作。它也和每週五 vLLM Weekly 電子報的 🔮 單元串在一起。 |
| **⏱️ 面試速通**路線：7 天 10 集，加上每天一場 `/mock` | 「我下週要面試」是最常收到的私訊。 |
| 免安裝模擬器：`paged_playground.py`、`batching_arena.py`、`kv_budget.py` | S1/S2 的每個概念都能在筆電上用純 Python *看見*，不需要 GPU 或 PyTorch。 |
| 依來源更新並查核趨勢內容（2026/10/12） | 更正：Inferact 的種子輪是 a16z **與 Lightspeed** 共同領投。新增：`/v1/systemone`、vllm-metal、冷啟動相關工作、PyTorch Conference 議程。 |

## 每一集的固定節奏

每一集都是同樣的五個步驟，學員永遠知道下一步是什麼：

1. **🎣 鉤子**：一句挑釁但正確的話。（「GPU 在幫你寫回覆的時候，運算單元有超過 90% 在發呆。」）
2. **💡 頓悟**：一個核心觀念，150 字以內，搭配一張圖卡。
3. **🧪 動手做**：10–20 分鐘的實作，指令可以直接複製貼上，並附上可以對照的**預期輸出**。
4. **🎤 用專業的方式說出來**：面試時 30 秒的標準回答，加上面試官一定會追問的那一題。
5. **🏁 證明**：在 Discord 回答 3 題小測驗（拿 XP），以及深入課程的連結。

## 六季內容

| 季 | 主題 | 集數 | 硬體 | 學完你能… |
|---|---|---|---|---|
| **S0 你好，Token** | LLM 到底是怎麼產生文字的 | E01–E04 | 任何筆電 | 解釋自迴歸生成、token、attention，以及為什麼推論不等於訓練 |
| **S1 記憶體之牆** | 推論為什麼這麼難 | E05–E08 | 任何筆電 | 心算 KV cache 大小，並講清楚 PagedAttention |
| **S2 親手打造 mini-vLLM** | 自己實作核心概念 | E09–E12 | CPU + PyTorch | 實作 continuous batching、prefix caching、chunked prefill，並通過 30 個測試 |
| **S3 vLLM 原始碼探險** | 在真正的程式碼裡找路 | E13–E16 | 不需要 GPU | 追蹤一個請求從 HTTP 到 GPU 再回來；知道一個修改該放在哪裡 |
| **S4 高手加速祕技** | 2026 年的前沿技術 | E17–E22 | GPU 可有可無 | 討論 speculative decoding、量化、平行化、分離部署、KV offload 與 RL rollout |
| **S5 上 PR、拿 Offer** | 把能力變成證明 | E23–E26 | 有 GPU 更好 | 送出有價值的 PR、正確做 benchmark、通過系統設計面試 |
| **S6 🔮 前沿觀測站** | 每月更新的活季度 | E27–E28（持續增加） | GPU 可有可無 | 說明這個月推出了什麼、它如何改變服務方式，並且辯論它會走向哪裡 |

### S0 — 你好，Token

| # | 單集 | 鉤子 | 實作 | 深入課程 |
|---|---|---|---|---|
| E01 | **ChatGPT 其實只是一個 for 迴圈** | 你用過的每個聊天機器人，都是一個 `for` 迴圈不斷呼叫同一個函式。 | [Q1 第一個 Token](labs/Q1-first-token.zh-TW.md) | [Lesson 00](../phase1/redesign/lessons/00-first-request.md) |
| E02 | **Token：為什麼「strawberry」會讓模型出錯，也讓你的帳單變貴** | 模型從來看不到字母。你是按照它「看得到的碎片」付費的。 | Q1 裡的 tokenizer 遊樂場 | [Lesson 02](../phase1/redesign/lessons/02-tokens.md) |
| E03 | **130 行打造一個 Transformer** | GPT、Llama、Qwen 背後的架構，兩個螢幕就裝得下。 | `python -m labs.naive_transformer` | [Lesson 03](../phase1/redesign/lessons/03-naive-transformer.md) |
| E04 | **訓練 ≠ 推論：兆元等級的分水嶺** | 訓練只做一次。推論是每個人每按一次 Enter 就要做一次。 | `python -m labs.train_tiny` | [Lesson 04](../phase1/redesign/lessons/04-training-inference.md) |

### S1 — 記憶體之牆

| # | 單集 | 鉤子 | 實作 | 深入課程 |
|---|---|---|---|---|
| E05 | **GPU 跟你聊天時，有超過 90% 的時間在發呆** | Decode 是一個披著運算外衣的記憶體頻寬問題。 | [Q3 批次競技場](labs/Q3-batching-arena.zh-TW.md)（roofline 模式） | [硬體](../course/part1/03-hardware.md) |
| E06 | **KV cache：每個 LLM 都在用的作弊碼** | 沒有它，生成第 1,000 個 token 時，要把前 999 個 token 的工作全部重做一遍。 | `python -m labs.naive_transformer` | [Lesson 06](../phase1/redesign/lessons/06-kv-cache.md) |
| E07 | **讓多數面試者陣亡的那一題** | 「一個 128k context 的 Llama-70B 請求，需要多少記憶體？」 | [Q4 KV 預算](labs/Q4-kv-budget.zh-TW.md) + `/kvcalc` | [KV 記憶體](../course/part1/04-kv-memory.md) |
| E08 | **PagedAttention：讓 vLLM 快 24 倍的 1960 年代作業系統老招** | 在 vLLM 之前，伺服器浪費了 60–80% 的 KV 記憶體。虛擬記憶體解決了這件事。 | [Q2 分頁遊樂場](labs/Q2-paged-playground.zh-TW.md) | [Lesson 08](../phase1/redesign/lessons/08-pages-prefix.md) |

### S2 — 親手打造 mini-vLLM

| # | 單集 | 鉤子 | 實作 | 深入課程 |
|---|---|---|---|---|
| E09 | **Continuous batching：一張 GPU 如何服務一千個使用者** | Static batching 讓所有人都要等最慢的那個請求。 | [Q3 批次競技場](labs/Q3-batching-arena.zh-TW.md) | [Lesson 07](../phase1/redesign/lessons/07-scheduling.md) |
| E10 | **Prefix caching：你可能一直沒用到的免費加速** | 你的 system prompt 只算一次，之後每個使用者都能重複使用。 | [Q2](labs/Q2-paged-playground.zh-TW.md) `--scenario prefix` | [Prefix cache](../course/part2/09-prefix-cache.md) |
| E11 | **Chunked prefill：別讓一個巨大的 prompt 卡住所有人** | 有人貼上 10 萬個 token，伺服器上每個聊天都可能跟著卡住。除非… | [Q3](labs/Q3-batching-arena.zh-TW.md) `--chunk` | [排程](../course/part2/08-scheduling.md) |
| E12 | **魔王關：你的 mini-vLLM 通過 30 個測試** | 引擎你自己寫。是不是真的能用，由測試決定。 | [Q5 打造 mini-vLLM](labs/Q5-build-mini-vllm.zh-TW.md) | [里程碑](../labs/MILESTONES.md) |

### S3 — vLLM 原始碼探險

| # | 單集 | 鉤子 | 實作 | 深入課程 |
|---|---|---|---|---|
| E13 | **跟著一個請求，穿越一百萬行 vLLM 程式碼** | 從 `curl` 到 GPU 再回來，一共 12 站。記住這 12 站，整個程式碼庫就變小了。 | Discord 裡的 `/trace` | [Lesson 09](../phase1/redesign/lessons/09-system-map.md) |
| E14 | **整個排程器就是一個函式，讀它就對了** | `Scheduler.schedule()` 在每一步替每個使用者決定誰能執行。 | [Q6 原始碼尋寶](labs/Q6-codebase-hunt.zh-TW.md) | [原始碼導覽](../course/part3/11-source-walkthrough.md) |
| E15 | **GPU 真正在工作的地方：runner、graph 與 attention backend** | 同一個模型，在 NVIDIA、AMD、Intel、TPU、CPU 上跑的是不同的 kernel。 | Q6 第 6–10 題 | [Backend 與 graph](../course/part3/12-backends-and-graphs.md) |
| E16 | **幫 vLLM 加一個新模型：經典的第一個大 PR** | 每週都有新模型發布，總要有人把它接進來。那個人可以是你。 | 用機器人的 code map 讀 `llama.py` | [Lesson 05](../phase1/redesign/lessons/05-real-models.md) |

### S4 — 高手加速祕技（2026 版）

| # | 單集 | 鉤子 | 實作 | 深入課程 |
|---|---|---|---|---|
| E17 | **Speculative decoding：快速猜、一次驗** | 一次 forward 換到 2–3 個 token，輸出還完全一樣。 | [Q7](labs/Q7-benchmark-like-a-pro.zh-TW.md) speculative decoding 版本 | [量化與推測解碼](../course/part3/13-quantization-and-speculation.md) |
| E18 | **4 bit 就夠了？FP8、NVFP4 與量化動物園** | 記憶體砍半、答案幾乎一樣，前提是你知道要量什麼。 | `/kvcalc dtype:fp8` | 同上 |
| E19 | **TP、PP、DP、EP：切開巨型模型的四種刀法** | 1T 參數的 MoE 一張 GPU 放不下。怎麼切，決定你的延遲。 | Rank 圖練習 | [平行化](../course/part3/14-parallelism.md) |
| E20 | **分離部署：像大型實驗室一樣把 prefill 和 decode 拆開** | Prefill 要算力、decode 要頻寬，那就放在不同的 GPU 上跑。 | 時序圖練習 | [KV 傳輸](../course/part3/15-kv-transfer.md) |
| E21 | **80 GB 不夠用時：分層 KV offload** | 把 KV 溢出到 CPU 記憶體、SSD 或遠端儲存，而不是直接丟掉。 | Q2 `--scenario offload` | [配置](../phase1/redesign/lessons/15-placement.md) |
| E22 | **vLLM 其實是 RL 後訓練背後的引擎** | 推理模型是靠生成數百萬次嘗試學會的，而這些嘗試是 vLLM 寫出來的。 | 閱讀 code map 裡的權重傳輸條目 | [貢獻路線](../phase1/redesign/lessons/17-contribution.md) |

### S5 — 上 PR、拿 Offer

| # | 單集 | 鉤子 | 實作 | 深入課程 |
|---|---|---|---|---|
| E23 | **7 步送出你的第一個 vLLM PR（而且不當「那種」貢獻者）** | 有些第一次的 PR 讓維護者很開心，有些幾分鐘就被關掉。差別在這裡。 | [Q8 第一個 PR 任務](labs/Q8-first-pr-quest.zh-TW.md) | [貢獻指南](../course/part4/17-contributing.md) |
| E24 | **像專家一樣做 benchmark：TTFT、ITL 與平均值的謊言** | 「快了 2 倍」如果沒有 p99 和工作負載描述，就等於什麼都沒說。 | [Q7](labs/Q7-benchmark-like-a-pro.zh-TW.md) | [量測](../course/part1/05-measurement.md) |
| E25 | **推論工程師面試，一次拆解** | 同樣五題系統設計題反覆出現。在這裡練熟它們。 | [Q9 模擬面試](labs/Q9-mock-interview.zh-TW.md) | [Lesson 16](../phase1/redesign/lessons/16-measurement.md) |
| E26 | **公開的證明，勝過完美的履歷** | 一個被 merge 的 PR、一篇 benchmark 分析、一篇部落格文章，比一張證書更快被看見。 | 作品集檢查表 | [路線圖](../ROADMAP.md) |

### S6 — 前沿觀測站（活季度・每月更新）

| # | 單集 | 鉤子 | 實作 | 深入閱讀 |
|---|---|---|---|---|
| E27 | **Agent 把你的 benchmark 打爆了** | 你的引擎在 tokens/sec 排行榜第一名，agent 用起來卻還是很慢。 | Q2 `--scenario agent` | [E27 深入閱讀](frontier/E27-agentic-inference.md#繁體中文) |
| E28 | **冷啟動是新的延遲** | 你的 p99 延遲是 400 毫秒，你的自動擴展 p99 卻是 4 分鐘。 | Q1 冷／暖啟動計時 | [E28 深入閱讀](frontier/E28-cold-starts.md#繁體中文) |

前沿單集一樣是五個節拍，另外每個數字都附「撰寫日期」與來源。當某個前沿主題穩定下來，就會畢業併入 S4。

## 學習路線

在 Discord 用 `/start` 選一條。路線只會改變**順序**和機器人推薦的下一步。

| 路線 | 適合誰 | 路徑 |
|---|---|---|
| 🌱 **好奇寶寶** | 用過 ChatGPT、想知道它怎麼運作的任何人 | S0 → S1 → E09、E10、E17 → E25 |
| 🎓 **求職衝刺** | 想進 ML infra 或推論相關職位的學生與轉職者 | S0 → S1 → S2 → E13 → S4 → S5，每週一次 `/mock` |
| 🛠 **貢獻者** | 想讓自己的名字出現在 vLLM commit 紀錄裡的人 | S1 → S2 → S3 → E23 → E24 → 深入一個 S4 主題 |
| ⚡ **服務工程師** | 在生產環境跑模型的實務工作者 | E05–E11 → E17–E21 → E27、E28 → E24 → E25 |
| ⏱️ **面試速通** | 一週後要面試 | E05、E07、E08、E09、E10、E17、E20、E27、E24、E25（7 天 10 集）+ 每天 `/mock` |

## 實作關卡

| 關卡 | 需要什麼 | 時間 | 你會得到 |
|---|---|---|---|
| [Q1 第一個 Token](labs/Q1-first-token.zh-TW.md) | 免費的 Colab GPU，或任何 NVIDIA/AMD GPU | 15 分鐘 | 一個運作中、相容 OpenAI 的 vLLM 伺服器，以及你的第一串串流 token |
| [Q2 分頁遊樂場](labs/Q2-paged-playground.zh-TW.md) | 只要 Python 3.10+ | 15 分鐘 | 用彩色畫面一步步看懂分頁、block table、前綴共享與淘汰 |
| [Q3 批次競技場](labs/Q3-batching-arena.zh-TW.md) | 只要 Python 3.10+ | 15 分鐘 | Static batching vs continuous batching vs chunked prefill，模擬對決 |
| [Q4 KV 預算](labs/Q4-kv-budget.zh-TW.md) | 只要 Python 3.10+ | 10 分鐘 | 真實模型的記憶體計算（MHA、GQA、MLA），以及 E07 的答案 |
| [Q5 打造 mini-vLLM](labs/Q5-build-mini-vllm.zh-TW.md) | CPU 版 PyTorch | 一週內 4–8 小時 | 你自己的引擎與全綠的測試 |
| [Q6 原始碼尋寶](labs/Q6-codebase-hunt.zh-TW.md) | 一份 vLLM 原始碼 | 45 分鐘 | 12 題在真實原始碼裡的計分尋寶 |
| [Q7 像專家一樣做 Benchmark](labs/Q7-benchmark-like-a-pro.zh-TW.md) | 一張 GPU | 45 分鐘 | 一份可重現的 TTFT/ITL/吞吐量報告：開與不開 prefix caching |
| [Q8 第一個 PR 任務](labs/Q8-first-pr-quest.zh-TW.md) | Linux 機器，GPU 可有可無 | 2 小時 + 審查時間 | 開發環境、通過的測試，以及格式正確的 PR |
| [Q9 模擬面試](labs/Q9-mock-interview.zh-TW.md) | Discord | 30 分鐘 | 有計分的五題模擬面試，附參考答案 |

## 遊戲化設計（讓大家真的會學完）

- **XP**：完成一集 +50、答對測驗 +10（第一次就答對 +15）、實作檢查點 +25、解開尋寶 +40、模擬面試最多 +100。
- **等級**（可選擇對應 Discord 身分組）：`Token Rookie 新手` → `KV Cadet 見習生` → `Page Master 分頁大師` → `Scheduler Sage 排程賢者` → `Kernel Ninja 核心忍者` → `Maintainer Material 準維護者`。
- **徽章**：First Token、KV Accountant、Pager、Engine Builder、Navigator、Interview Ready、連續 7 天、Merged（當你真的有 PR 被上游 merge，由管理員頒發）。
- **每日一練**：台北時間每晚 20:00，在 `#daily-drop` 發布一題測驗、一題面試題、一個名詞或一則趨勢，雙語呈現。
- **版本雷達**：vLLM 發布新版本時，機器人會公告，並附上「這對學習者代表什麼」。
- **🔮 大膽預測法庭**：`/hottake` 顯示一則有日期的預測，附上我們的信心、證據，以及什麼情況代表我們錯了。投 🔥 同意或 🧊 不同意，看看大家怎麼分。到了判決日，管理員記錄結果，機器人公開幫我們打分數。投滿 5 則可得 **先知** 徽章。

## Discord 指令

| 學習 | 練習 | 探索 | 社群 |
|---|---|---|---|
| `/start` 選路線 · `/path` 學習地圖 · `/episode` · `/lab` · `/lang` | `/quiz` · `/interview` · `/mock` · `/hunt` · `/kvcalc` | `/trace` 12 站請求之旅 · `/code` 程式碼地圖 · `/glossary` · `/trends` · `/hottake` | `/profile` 卡片 · `/leaderboard` · `/career` · `/community` · `/events` · `/gfi` good first issue |

管理員：`/academy setup` 建立頻道與等級身分組、`/academy post-start` 發布歡迎面板、`/academy daily-now`、`/academy award`、`/academy verdict`、`/academy reload`。

## 讀書會模式（8 週）

| 週 | 線上直播（60 分鐘） | Discord 非同步 |
|---|---|---|
| 1 | 開訓 + 一起完成 Q1 第一個 Token | S0 各集 + 測驗 |
| 2 | KV 數學 jam（E07） | S1 + Q2、Q4 |
| 3 | 批次競技場大賽（E09、E11） | Q3 + 開始 Q5 M1–M2 |
| 4 | 結對除錯 mini-vLLM | Q5 M3–M6 |
| 5 | 和貢獻者一起現場追蹤請求 | S3 + Q6 尋寶 |
| 6 | 加速祕技 AMA | S4，選一個主題準備 5 分鐘閃電講 |
| 7 | Benchmark 診所 | Q7 + Q8 環境建置 |
| 8 | Demo Day：閃電講、模擬面試、PR 互審 | S5 + `/mock` |

## 誠實原則（沿用 Phase 1）

標題可以大膽，內容必須誠實。鉤子可以挑釁，但內文必須正確，並且寫清楚前提假設。任何速度數字都要說清楚**和什麼比、在什麼工作負載下**。維護者還沒實際執行過的 GPU 指令，會標註「尚未驗證」。趨勢內容會註明撰寫時間（2026 年 10 月）並附上來源。
