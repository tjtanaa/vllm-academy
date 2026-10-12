# Q6 · Codebase Treasure Hunt: navigate a million lines like you wrote them

**Needs:** git and ~1 GB of disk (no GPU) · **Time:** 45 min · **Episodes:** E13, E14, E15, E16 · **XP:** +75 (plus +40 per hunt)
**[繁體中文](Q6-codebase-hunt.zh-TW.md)**

Navigating a huge codebase is a skill you can practice. In this lab you check out vLLM at the course's pinned commit, learn four search moves, and solve the bot's graded hunts (H1–H14). The bot checks your answers against that exact commit.

## 1. Check out the pinned commit

Line numbers drift on `main`, so the course pins one commit (12 Oct 2026, after v0.31.0). A shallow fetch keeps the download small.

```bash
git clone --filter=blob:none https://github.com/vllm-project/vllm.git && cd vllm
git checkout 74f4404f58c0fb16821b34c16343486eeaf164a5
git log -1 --format='%h %cd %s'
```

> ✅ **Checkpoint:** `git log` shows commit `74f4404f`. Every `/code` and `/trace` permalink in Discord points here.

## 2. Get the lay of the land

Before searching, look at the map. Most of what this course teaches lives under `vllm/v1/`.

```bash
ls vllm/ && ls vllm/v1/ && ls vllm/v1/core vllm/v1/engine vllm/v1/worker
```

> ✅ **Checkpoint:** you can say which directory holds the scheduler (`vllm/v1/core/sched/`), the engine core and client (`vllm/v1/engine/`) and the GPU model runner (`vllm/v1/worker/`).

## 3. Learn four search moves

`git grep` works everywhere and is fast. Find a definition with `class Name` or `def name`, find callers by searching the name followed by `(`, and narrow with a path.

```bash
git grep -n "^class Scheduler" -- vllm/v1
git grep -n "def schedule(" -- vllm/v1/core
git grep -n "token_budget" -- vllm/v1/core/sched | head
git grep -ln "PagedAttention\|block_table" -- vllm/v1 | head
```

> ✅ **Checkpoint:** you found the file that defines the V1 `Scheduler`. That's the answer to hunt **H1**: submit it with `/hunt hunt:H1`.

## 4. Follow one request

In Discord, run `/trace` and click through all 12 stops, from `vllm serve` to the HTTP route, AsyncLLM, EngineCore, scheduler, model runner, sampler and back out as a streamed token. Open each permalink in your checkout.

```text
/trace
```

> ✅ **Checkpoint:** you can draw the request path on paper with the two process boundaries (API server ↔ engine core over ZMQ, engine core ↔ workers).

## 5. Solve the scheduler hunts (E14)

Open `Scheduler.schedule()` and read it top to bottom once without stopping. Then solve H2 (the token-budget variable), H9 (the method that processes model outputs) and H14 (who gets preempted under FCFS).

```bash
git grep -n "def update_from_output\|def _preempt\|self.running" -- vllm/v1/core/sched/scheduler.py | head -20
```

> ✅ **Checkpoint:** H2, H9 and H14 are solved in Discord. You can explain in one sentence what happens to a request's KV blocks when it's preempted.

## 6. Solve the memory hunts (E08, E10)

The KV cache manager, block pool and free queue are Q2's playground in production form. Solve H3 (block allocation), H4 (block hashing) and H5 (the LRU free list), then H6–H7 (defaults that matter).

```bash
git grep -n "^class \|^def " -- vllm/v1/core/kv_cache_manager.py vllm/v1/core/block_pool.py vllm/v1/core/kv_cache_utils.py | head -40
```

> ✅ **Checkpoint:** five hunts solved earns you the 🧭 **Navigator** badge. Check it with `/profile`.

## 7. Solve the hardware and model hunts (E15, E16)

Find where vLLM picks an attention backend (H8), where the EAGLE proposer lives (H10), which module serves DeepSeek-V3 (H11), the KV-connector base class (H12) and Model Runner V2's directory (H13).

```bash
git grep -n "def get_attn_backend" -- vllm
git grep -n "DeepseekV3ForCausalLM" -- vllm/model_executor/models/registry.py
```

> ✅ **Checkpoint:** all 14 hunts are solved, or you've posted in `#labs-help` with the one that beat you and what you tried.

## 8. Make your own hunt

The best way to lock in a codebase is to teach it. Write one new hunt in the same format as `academy/content/hunts.yaml`: a question, a hint, accepted answers and a code-map entry. Open a PR to vllm-academy.

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

> ✅ **Checkpoint:** your hunt PR is open. That counts as a real contribution to an open-source learning project, and it's good practice for Q8.

## What you learned

- Pin a commit before you read, and permalink everything you cite.
- `git grep` for definitions, callers and paths beats scrolling.
- The V1 engine splits into API server, engine core, scheduler, KV manager and workers, and each hunt taught you where one of them lives.
