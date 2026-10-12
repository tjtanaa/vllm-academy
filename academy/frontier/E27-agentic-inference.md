# E27 · Agents broke your benchmark

**[English](#english) · [繁體中文](#繁體中文)** · Season 6 Frontier Watch · written 12 Oct 2026. Refresh monthly.

---

## English

### The one-line idea

An agent turn is a **huge repeated prefix + a tiny output + a pause**. Engines tuned for "short prompt, long answer" chat leave most of the win on the table.

### What an agent session looks like

```text
turn 1  [system 3k][tools 6k][user 1k]                          → tool_call (40 tok)  ⏸ tool runs 2–30 s
turn 2  [system 3k][tools 6k][user 1k][call+result 4k]          → tool_call (60 tok)  ⏸
turn 3  [system 3k][tools 6k][user 1k][...........  9k]         → tool_call (30 tok)  ⏸
  ...
turn 30 [system 3k][tools 6k][user 1k][................ 70k]    → final answer (800 tok)
```

Each turn re-sends everything before it. If the engine still holds those KV blocks, turn *n* only prefills its **new** tokens. If not, it recomputes the whole context, and on a 70k context that is seconds of GPU time per turn.

### Back-of-envelope: what a cache miss costs

For Llama-3.1-70B in BF16, KV is `2 × 80 × 8 × 128 × 2 B = 320 KiB/token` (E07). A 70k-token context is **about 21 GiB of KV**.

| Option on the returning turn | What it costs |
|---|---|
| Blocks still in HBM (hit) | Prefill only the ~500 new tokens |
| Blocks offloaded to host DRAM | Copy ~21 GiB back over PCIe/NVLink-C2C, often much faster than recomputing |
| Blocks gone (miss) | Recompute 70k tokens of prefill, which slows every other user's decode steps while it runs (E11) |

This is why **tiered KV offload** (E21) and **cache-aware routing** stopped being nice-to-haves.

### The metrics that matter now

- **Prefix-cache hit rate**, by token and by request. vLLM exposes prefix-cache metrics on `/metrics`.
- **TTFT on returning turns**, not just first turns.
- **Re-prefill tokens per session**: the tokens you computed twice.
- **Throughput under a per-user floor.** SemiAnalysis AgentX reports capacity while each user still gets, say, 150 tokens/s. vLLM's DeepSeek-V4.1-Flash post (7 Oct 2026) reports about 5x on that benchmark three weeks after day 0.

### Levers, in the order to try them

1. Check prefix caching is on (it is by default in vLLM V1) and **put stable content first**: system prompt, then tools, then history. A timestamp at the top of the system prompt wipes out your hit rate.
2. **Session affinity / prefix-aware routing** across replicas, so turn 2 lands where turn 1's blocks live.
3. **Tiered KV offload** for sessions paused on tools.
4. Tune the per-step token budget (`--max-num-batched-tokens`; chunked prefill is on by default) so a returning 70k miss doesn't drag down everyone's decode.
5. Only then: speculative decoding for the short outputs, and P/D disaggregation at scale (E20).

### 🎤 Interview angle

"How would you serve a coding agent?" is the 2026 version of "design a chat service". Lead with the trace shape, then KV math, then routing and cache tiers. Try `iv-31` with `/interview`.

### Sources

- [vLLM blog: DeepSeek-V4.1-Flash, 5x agentic throughput (7 Oct 2026)](https://vllm.ai/blog/2026-10-07-deepseek-v41-flash)
- [vLLM blog: vLLM × AgentX (8 Sep 2026)](https://vllm.ai/blog/2026-09-08-vllm-agentx)
- [vLLM blog: Tiered KV cache offloading (10 Sep 2026)](https://vllm.ai/blog/2026-09-10-tiered-kv-offloading)
- Course background: [Lesson 08 pages and prefixes](../../phase1/redesign/lessons/08-pages-prefix.md) · [Prefix cache](../../course/part2/09-prefix-cache.md)

---

## 繁體中文

### 一句話重點

Agent 的每一回合 = **超大的重複前綴 + 很短的輸出 + 一段暫停**。為「短 prompt、長回答」的聊天調校的引擎，會把大部分的好處留在桌上。

### Agent session 長什麼樣子

```text
第 1 回合  [system 3k][工具 6k][使用者 1k]                        → 工具呼叫（40 tok）  ⏸ 工具執行 2–30 秒
第 2 回合  [system 3k][工具 6k][使用者 1k][呼叫+結果 4k]           → 工具呼叫（60 tok）  ⏸
第 3 回合  [system 3k][工具 6k][使用者 1k][...........  9k]       → 工具呼叫（30 tok）  ⏸
  ...
第 30 回合 [system 3k][工具 6k][使用者 1k][................ 70k]  → 最終回答（800 tok）
```

每一回合都會把前面所有內容再送一次。如果引擎還保有那些 KV block，第 *n* 回合只需要 prefill **新的** token；如果沒有，就要把整段 context 重新算一遍。7 萬 token 的 context，每回合就是好幾秒的 GPU 時間。

### 粗算：一次 cache miss 的代價

以 BF16 的 Llama-3.1-70B 為例，KV 是 `2 × 80 × 8 × 128 × 2 B = 每 token 320 KiB`（E07）。7 萬 token 的 context 大約是 **21 GiB 的 KV**。

| 回訪回合的情況 | 代價 |
|---|---|
| Block 還在 HBM（命中） | 只 prefill 約 500 個新 token |
| Block 被 offload 到主機 DRAM | 透過 PCIe/NVLink-C2C 把約 21 GiB 搬回來，通常比重算快很多 |
| Block 不見了（未命中） | 重新 prefill 7 萬個 token，這段期間其他所有使用者的 decode 都會被拖慢（E11） |

這就是為什麼**分層 KV offload**（E21）和**感知快取的路由**，不再只是加分項。

### 現在真正重要的指標

- **Prefix cache 命中率**：以 token 計、以請求計都要看。vLLM 在 `/metrics` 上有 prefix cache 指標。
- **回訪回合的 TTFT**，不只是第一回合。
- **每個 session 重新 prefill 的 token 數**：你算了兩次的 token。
- **在每位使用者速度下限之下的吞吐量**。SemiAnalysis AgentX 量的是每位使用者仍保有例如 150 tokens/s 時的容量。vLLM 的 DeepSeek-V4.1-Flash 文章（2026 年 10 月 7 日）回報，首日支援三週後在這個 benchmark 上快了約 5 倍。

### 槓桿，照這個順序試

1. 確認 prefix caching 有開（vLLM V1 預設就是開的），並且**把穩定的內容放前面**：先 system prompt，再工具，最後歷史。在 system prompt 開頭放時間戳，會把命中率整個毀掉。
2. 跨副本做 **session 親和性／感知前綴的路由**，讓第 2 回合落在第 1 回合 block 所在的地方。
3. 對正在等工具的 session 做**分層 KV offload**。
4. 調整每一步的 token 預算（`--max-num-batched-tokens`；chunked prefill 預設已開啟），避免一個 7 萬 token 的回訪未命中拖慢所有人的 decode。
5. 最後才是：針對短輸出做推測解碼，以及大規模時做 P/D 分離（E20）。

### 🎤 面試角度

「你會怎麼服務一個 coding agent？」是 2026 年版的「設計一個聊天服務」。先講 trace 的形狀，再講 KV 計算，然後是路由與快取分層。用 `/interview` 試試 `iv-31`。

### 來源

- [vLLM 部落格：DeepSeek-V4.1-Flash，agent 吞吐量 5 倍（2026/10/7）](https://vllm.ai/blog/2026-10-07-deepseek-v41-flash)
- [vLLM 部落格：vLLM × AgentX（2026/9/8）](https://vllm.ai/blog/2026-09-08-vllm-agentx)
- [vLLM 部落格：分層 KV cache offload（2026/9/10）](https://vllm.ai/blog/2026-09-10-tiered-kv-offloading)
- 課程背景：[Lesson 08 pages 與 prefix](../../phase1/redesign/lessons/08-pages-prefix.md) · [Prefix cache](../../course/part2/09-prefix-cache.md)
