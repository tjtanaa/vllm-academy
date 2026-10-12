# E28 · Cold starts are the new latency

**[English](#english) · [繁體中文](#繁體中文)** · Season 6 Frontier Watch · written 12 Oct 2026. Refresh monthly.

---

## English

### The one-line idea

Request latency is measured in milliseconds; **engine startup is measured in minutes**. For autoscaling, RL loops and model switching, startup *is* the latency.

### Where startup time goes

```text
vllm serve <model>
 ├─ 1. fetch weights        (HF Hub / object store / NFS → local disk; cached in ~/.cache/huggingface)
 ├─ 2. load + quantize      (disk → GPU, maybe on-the-fly FP8/FP4)
 ├─ 3. profile + compile    (a dummy forward measures peak memory and triggers torch.compile,
 │                           whose artifacts are cached in ~/.cache/vllm)
 ├─ 4. allocate KV cache    (whatever memory is left → blocks)
 └─ 5. CUDA-graph capture   (graphs per capture size; not cached across restarts)
      → "Application startup complete."
```

**Lab:** run Q1 twice, cold and then warm, and write down each stage's time from the log. Which stage shrank on the second run? (Answer: weight fetch, because the model now comes from the local Hugging Face cache instead of a download, and compile, from the torch.compile cache. Graph capture runs again.)

### What vLLM shipped in 2026

| Release | Feature | What it skips |
|---|---|---|
| older | **Sleep mode** (`--enable-sleep-mode`, `/sleep`, `/wake_up`) | Offload or discard weights and KV so the GPU can be lent out, then wake without a full restart. Popular in RL. |
| v0.30 (22 Sep 2026) | **Fast Start**: `--load-format ipc_cache` | Steps 1–2: map already-loaded weights over CUDA IPC |
| v0.31 (5 Oct 2026) | **`vllm preload`** daemon | Steps 1–2 across restarts: post-quantized weights stay resident; supports DP and MTP drafters |
| v0.31 | **`vllm snapshot`** (experimental, TP1) | Nearly all of it: CRIU freezes an *initialized* engine and restores it |

### The trade-off nobody tweets

Resident weights sit in GPU memory doing nothing between restarts. That memory could be KV cache for live users. The deal is worth it when:

- traffic is **bursty** (you scale often),
- weights change often (**RL rollouts**, frequent fine-tune pushes), or
- you **switch models** on shared hardware.

It isn't worth it for one long-lived replica serving one model all day.

### Cheap wins before the fancy stuff

- Pre-stage weights on **local NVMe**; don't download per pod.
- Persist the **torch.compile cache** across pods (mount it).
- If graph capture dominates, capture fewer batch sizes. `--enforce-eager` skips capture entirely but serves slower, and in v0.31 it also skips JIT kernel warm-up.
- Scale on **queue depth**, earlier, and keep one warm spare.

### 🎤 Interview angle

`iv-32` in `/interview`: "Scale-up takes 6 minutes." Strong answers time each stage before proposing fixes.

### Sources

- [vLLM v0.31.0 release notes](https://github.com/vllm-project/vllm/releases/tag/v0.31.0) · [v0.30.0](https://github.com/vllm-project/vllm/releases/tag/v0.30.0)
- [vLLM docs: sleep mode](https://docs.vllm.ai/en/latest/features/sleep_mode.html)
- Course background: [Backends and graphs](../../course/part3/12-backends-and-graphs.md)

---

## 繁體中文

### 一句話重點

請求延遲用毫秒計算；**引擎啟動用分鐘計算**。對自動擴展、RL 迴圈和切換模型來說，啟動時間*就是*延遲。

### 啟動時間花在哪裡

```text
vllm serve <model>
 ├─ 1. 取得權重          （HF Hub／物件儲存／NFS → 本機磁碟；快取在 ~/.cache/huggingface）
 ├─ 2. 載入 + 量化       （磁碟 → GPU，可能即時轉成 FP8/FP4）
 ├─ 3. 量測 + 編譯       （跑一次假的 forward 量測峰值記憶體，同時觸發 torch.compile，
 │                         編譯結果快取在 ~/.cache/vllm）
 ├─ 4. 配置 KV cache     （剩下的記憶體 → block）
 └─ 5. 擷取 CUDA graph   （每個 capture size 都有 graph；重啟後不會沿用）
      → "Application startup complete."
```

**實作：** 把 Q1 跑兩次，先冷啟動、再暖啟動，從日誌記下每個階段的時間。第二次是哪一個階段變短了？（答案：取得權重，因為模型改從本機的 Hugging Face 快取讀取、不用再下載；還有編譯，因為有 torch.compile 快取。Graph 擷取還是會再跑一次。）

### vLLM 在 2026 年推出了什麼

| 版本 | 功能 | 省掉哪些步驟 |
|---|---|---|
| 較早版本 | **Sleep mode**（`--enable-sleep-mode`、`/sleep`、`/wake_up`） | 卸載或丟棄權重與 KV，讓 GPU 可以先借出去，之後不用完整重啟就能喚醒。在 RL 中很常用。 |
| v0.30（2026/9/22） | **Fast Start**：`--load-format ipc_cache` | 步驟 1–2：透過 CUDA IPC 直接映射已載入的權重 |
| v0.31（2026/10/5） | **`vllm preload`** 常駐程式 | 跨重啟省掉步驟 1–2：量化後的權重保持常駐；支援 DP 與 MTP drafter |
| v0.31 | **`vllm snapshot`**（實驗性，TP1） | 幾乎全部：CRIU 凍結一個*已初始化*的引擎，之後再還原 |

### 推文不會告訴你的取捨

常駐的權重在兩次重啟之間佔著 GPU 記憶體，什麼事也沒做。那塊記憶體本來可以拿去當線上使用者的 KV cache。以下情況這筆交易才划算：

- 流量很**突發**（你常常要擴展），
- 權重常常換（**RL rollout**、頻繁推送 fine-tune 結果），或
- 你在共用硬體上**切換模型**。

如果只是一個長期運行、整天服務同一個模型的副本，就不划算。

### 在玩花招之前，先拿便宜的分數

- 把權重預先放到**本機 NVMe**，不要每個 pod 都下載一次。
- 讓 **torch.compile 快取**跨 pod 保留（掛載它）。
- 如果 graph 擷取最花時間，就減少擷取的 batch size 數量。`--enforce-eager` 完全跳過擷取，但服務會比較慢；在 v0.31 中它也會跳過 JIT kernel 暖機。
- 根據**佇列深度**更早擴展，並保留一個預熱好的備用副本。

### 🎤 面試角度

`/interview` 裡的 `iv-32`：「擴展一個副本要 6 分鐘。」好的回答會先把每個階段計時，再提出修正方案。

### 來源

- [vLLM v0.31.0 release notes](https://github.com/vllm-project/vllm/releases/tag/v0.31.0) · [v0.30.0](https://github.com/vllm-project/vllm/releases/tag/v0.30.0)
- [vLLM 文件：sleep mode](https://docs.vllm.ai/en/latest/features/sleep_mode.html)
- 課程背景：[Backends and graphs](../../course/part3/12-backends-and-graphs.md)
