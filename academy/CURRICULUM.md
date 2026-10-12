# vLLM Academy Quest — From Zero to Inference Engineer

**[繁體中文版](CURRICULUM.zh-TW.md)** · [Academy Quest home](README.md) · [Discord bot](../discord_bot/README.md)

> The world is spending more on *running* LLMs than on training them. The people who know how to make
> inference fast and cheap are some of the most in-demand engineers in AI, and the open-source engine
> most of the industry runs on is vLLM. This course takes you from "what is a token?" to "my PR got
> merged and I can whiteboard a 70B serving design," one 20-minute episode at a time.

This is the **community-facing layer** on top of the rigorous Phase 1 course in this repository. The original lessons stay the source of truth for depth; Academy Quest repackages them into short, bilingual, hook-first episodes that the Discord bot delivers, quizzes and tracks. Every episode links back to the deep-dive lesson.

## What changed from the Phase 1 curriculum (and why)

| Phase 1 (deep, careful) | Academy Quest (refined for a community) | Why |
|---|---|---|
| 18 lessons, 90-minute sessions | 28 episodes of 15–30 minutes in 7 seasons (one of them a *living* season refreshed monthly) | People join Discord on phones, between classes. Short wins keep them coming back. |
| English lessons, zh-TW landing page | Every episode, quiz, lab, glossary entry and bot message in **English and 繁體中文** | Taiwan's community learns best in both; job interviews are often in English. |
| Theory → engine → source → contribution | Same spine, plus a **career track** (interview bank, mock interviews, system design, portfolio) | Students told us the goal: get hired, ace interviews. We teach to that honestly. |
| Labs need PyTorch or a GPU | Three new **zero-install labs** (stdlib Python only) before any GPU or PyTorch | Remove the "I don't have a GPU" excuse on day one. |
| Production topics end at the 2025 architecture | A **Pro Speed Tricks** season on what vLLM is shipping in 2026: speculative decoding (EAGLE-3, MTP, DFlash), NVFP4, disaggregated prefill/decode, tiered KV offload, RL rollout serving | That's what interviewers and maintainers talk about right now. |
| "Read the source" chapter | A **request-trace** walkthrough with permalinks into a pinned vLLM commit, plus a codebase treasure hunt the bot grades | Navigating more than a million lines of Python is a skill. We practice it like a game. |

### Refinement round 2 (12 Oct 2026)

| Added | Why |
|---|---|
| **S6 🔮 Frontier Watch**, a living season: E27 agentic inference, E28 cold starts | Agent traffic and elastic serving are what vLLM shipped and blogged about most in Sep–Oct 2026. A season that changes monthly gives people a reason to come back. |
| **Hot Take Court** (`/hottake`): 10 dated predictions with a confidence %, evidence and a "proves us wrong if" line. People vote; we grade ourselves on the date. | Speculation is the most shareable content, and labelling it honestly teaches people to tell evidence from hype. It also links up with the Friday vLLM Weekly newsletter's 🔮 section. |
| **⏱️ Interview Speedrun** route: 10 episodes in 7 days plus a daily `/mock` | "My interview is next week" is the most common DM. |
| Zero-install simulators: `paged_playground.py`, `batching_arena.py`, `kv_budget.py` | Every S1/S2 idea can be *seen* on a laptop with plain Python, no GPU or PyTorch. |
| Trend refresh and fact-check against sources (12 Oct 2026) | Corrected: Inferact's seed was co-led by a16z **and Lightspeed**. Added: `/v1/systemone`, vllm-metal, cold-start work, PyTorch Conference sessions. |

Nothing in Phase 1 was deleted. Its evidence rules still apply: CPU toy results are not GPU benchmarks; untested GPU recipes are labeled as such.

## The episode format

Every episode follows the same five beats, so learners always know what's next:

1. **🎣 Hook** — a provocative, true claim. ("Your GPU's compute units sit >90% idle while it writes your chat reply.")
2. **💡 Aha** — the one idea, in under 150 words, with a diagram card.
3. **🧪 Hands-on** — a lab of 10–20 minutes with copy-paste commands and an *expected output* to compare against.
4. **🎤 Say it like a pro** — the 30-second answer you'd give in an interview, plus the follow-up an interviewer will ask.
5. **🏁 Proof** — a 3-question quiz in Discord (XP) and a link to the deep-dive lesson.

## Seasons

| Season | Theme | Episodes | Hardware | You walk away able to… |
|---|---|---|---|---|
| **S0 Hello, Token** | How an LLM actually produces text | E01–E04 | Any laptop | Explain autoregression, tokens, attention and why inference ≠ training |
| **S1 The Memory Wall** | Why inference is hard | E05–E08 | Any laptop | Do KV-cache math in your head and explain PagedAttention |
| **S2 Build mini-vLLM** | Construct the core ideas yourself | E09–E12 | CPU + PyTorch | Build continuous batching, prefix caching and chunked prefill, and pass 30 tests |
| **S3 Inside vLLM** | Navigate the real codebase | E13–E16 | No GPU needed | Trace a request from HTTP to GPU and back; know where a change belongs |
| **S4 Pro Speed Tricks** | The 2026 frontier | E17–E22 | GPU optional | Discuss speculative decoding, quantization, parallelism, disaggregation, KV offload and RL rollouts |
| **S5 Get Merged, Get Hired** | Turn skill into proof | E23–E26 | GPU helpful | Ship a useful PR, benchmark properly, pass a system-design interview |
| **S6 🔮 Frontier Watch** | Living season, refreshed monthly | E27–E28 (growing) | GPU optional | Explain what shipped this month and what it changes for serving, and argue about where it's going |

### S0 — Hello, Token

| # | Episode | Hook | Lab | Deep dive |
|---|---|---|---|---|
| E01 | **ChatGPT is just a for-loop** | Every chatbot you've used is one `for` loop calling the same function. | [Q1 First Token](labs/Q1-first-token.md) | [Lesson 00](../phase1/redesign/lessons/00-first-request.md) |
| E02 | **Tokens: why "strawberry" breaks models and your bill** | Models never see letters. You pay per piece they *do* see. | Tokenizer playground in Q1 | [Lesson 02](../phase1/redesign/lessons/02-tokens.md) |
| E03 | **Build a Transformer in 130 lines** | The architecture behind GPT, Llama and Qwen fits on two screens. | `python -m labs.naive_transformer` | [Lesson 03](../phase1/redesign/lessons/03-naive-transformer.md) |
| E04 | **Training ≠ inference: the trillion-dollar split** | Training happens once. Inference happens every time anyone hits Enter. | `python -m labs.train_tiny` | [Lesson 04](../phase1/redesign/lessons/04-training-inference.md) |

### S1 — The Memory Wall

| # | Episode | Hook | Lab | Deep dive |
|---|---|---|---|---|
| E05 | **Your GPU is >90% idle while it talks to you** | Decode is a memory-bandwidth problem wearing a compute costume. | [Q3 Batching Arena](labs/Q3-batching-arena.md) (roofline mode) | [Hardware](../course/part1/03-hardware.md) |
| E06 | **The KV cache: the cheat code every LLM uses** | Without it, writing token 1,000 would redo the work of tokens 1–999. | `python -m labs.naive_transformer` | [Lesson 06](../phase1/redesign/lessons/06-kv-cache.md) |
| E07 | **The interview question that sinks most candidates** | "How much memory does a 128k-context Llama-70B request need?" | [Q4 KV Budget](labs/Q4-kv-budget.md) + `/kvcalc` | [KV memory](../course/part1/04-kv-memory.md) |
| E08 | **PagedAttention: the 1960s OS trick behind vLLM's 24× speedup** | Before vLLM, servers wasted 60–80% of KV memory. Virtual memory fixed it. | [Q2 Paged Playground](labs/Q2-paged-playground.md) | [Lesson 08](../phase1/redesign/lessons/08-pages-prefix.md) |

### S2 — Build mini-vLLM

| # | Episode | Hook | Lab | Deep dive |
|---|---|---|---|---|
| E09 | **Continuous batching: how one GPU serves a thousand users** | Static batching makes everyone wait for the slowest request. | [Q3 Batching Arena](labs/Q3-batching-arena.md) | [Lesson 07](../phase1/redesign/lessons/07-scheduling.md) |
| E10 | **Prefix caching: free speed you're probably ignoring** | Your system prompt is computed once, then reused for every user. | [Q2](labs/Q2-paged-playground.md) `--scenario prefix` | [Prefix cache](../course/part2/09-prefix-cache.md) |
| E11 | **Chunked prefill: stop one giant prompt from freezing everyone** | One 100k-token paste can stall every chat on the server. Unless... | [Q3](labs/Q3-batching-arena.md) `--chunk` | [Scheduling](../course/part2/08-scheduling.md) |
| E12 | **Boss fight: your mini-vLLM passes 30 tests** | You build the engine. The tests decide if it's real. | [Q5 Build mini-vLLM](labs/Q5-build-mini-vllm.md) | [Milestones](../labs/MILESTONES.md) |

### S3 — Inside vLLM

| # | Episode | Hook | Lab | Deep dive |
|---|---|---|---|---|
| E13 | **Follow one request through a million lines of vLLM** | Twelve stops from `curl` to GPU and back. Learn them and the codebase gets small. | `/trace` in Discord | [Lesson 09](../phase1/redesign/lessons/09-system-map.md) |
| E14 | **The whole scheduler is one function. Read it.** | `Scheduler.schedule()` decides who runs, every step, for every user. | [Q6 Treasure Hunt](labs/Q6-codebase-hunt.md) | [Source walkthrough](../course/part3/11-source-walkthrough.md) |
| E15 | **Where the GPU actually works: runners, graphs and attention backends** | The same model runs different kernels on NVIDIA, AMD, Intel, TPU and CPU. | Q6 hunts 6–10 | [Backends and graphs](../course/part3/12-backends-and-graphs.md) |
| E16 | **Add a model to vLLM: the classic first big PR** | New models drop weekly. Someone has to wire them in. That can be you. | Read `llama.py` with the bot's code map | [Lesson 05](../phase1/redesign/lessons/05-real-models.md) |

### S4 — Pro Speed Tricks (2026 edition)

| # | Episode | Hook | Lab | Deep dive |
|---|---|---|---|---|
| E17 | **Speculative decoding: guess fast, verify once** | Get 2–3 tokens for the price of one forward pass, with identical output. | [Q7](labs/Q7-benchmark-like-a-pro.md) spec-decode variant | [Quantization and speculation](../course/part3/13-quantization-and-speculation.md) |
| E18 | **4 bits is enough? FP8, NVFP4 and the quantization zoo** | Half the memory, nearly the same answers, if you know what to measure. | `/kvcalc dtype:fp8` | Same |
| E19 | **TP, PP, DP, EP: four ways to split a giant model** | A 1T-parameter MoE doesn't fit on one GPU. How you cut it decides your latency. | Rank-diagram exercise | [Parallelism](../course/part3/14-parallelism.md) |
| E20 | **Disaggregated serving: split prefill and decode like the big labs** | Prefill wants compute, decode wants bandwidth. So run them on different GPUs. | Sequence-diagram exercise | [KV transfer](../course/part3/15-kv-transfer.md) |
| E21 | **When 80 GB isn't enough: tiered KV offloading** | Spill KV to CPU RAM, SSD or a remote store instead of throwing it away. | Q2 `--scenario offload` | [Placement](../phase1/redesign/lessons/15-placement.md) |
| E22 | **vLLM is secretly the engine behind RL post-training** | Reasoning models learn by generating millions of attempts. vLLM writes them. | Read the weight-transfer code map entry | [Contribution routes](../phase1/redesign/lessons/17-contribution.md) |

### S5 — Get Merged, Get Hired

| # | Episode | Hook | Lab | Deep dive |
|---|---|---|---|---|
| E23 | **Your first vLLM PR in 7 steps (without being "that" contributor)** | Maintainers love some first PRs and close others in minutes. Here's the difference. | [Q8 First PR Quest](labs/Q8-first-pr-quest.md) | [Contributing](../course/part4/17-contributing.md) |
| E24 | **Benchmark like a pro: TTFT, ITL and the lie of averages** | "It's 2× faster" means nothing without p99 and a workload. | [Q7](labs/Q7-benchmark-like-a-pro.md) | [Measurement](../course/part1/05-measurement.md) |
| E25 | **The inference-engineer interview, decoded** | The same five system-design questions keep coming up. Practise them here. | [Q9 Mock Interview](labs/Q9-mock-interview.md) | [Lesson 16](../phase1/redesign/lessons/16-measurement.md) |
| E26 | **Public proof beats a perfect CV** | A merged PR, a benchmark write-up and a blog post get noticed faster than a certificate. | Portfolio checklist | [Roadmap](../ROADMAP.md) |

### S6 — Frontier Watch (living season · refreshed monthly)

| # | Episode | Hook | Lab | Deep dive |
|---|---|---|---|---|
| E27 | **Agents broke your benchmark** | Your engine tops the tokens/sec chart and still feels slow to an agent. | Q2 `--scenario agent` | [E27 deep dive](frontier/E27-agentic-inference.md) |
| E28 | **Cold starts are the new latency** | Your p99 latency is 400 ms. Your autoscaler's p99 is four minutes. | Q1 cold vs warm timing | [E28 deep dive](frontier/E28-cold-starts.md) |

Frontier episodes follow the same five beats, plus a "written on" date and a source for every number. When a frontier topic stabilizes, it graduates into S4.

## Routes

Pick one in Discord with `/start`. Routes only change the *order* and what the bot recommends next.

| Route | For | Path |
|---|---|---|
| 🌱 **Curious** | Anyone who uses ChatGPT and wants to know how it works | S0 → S1 → E09, E10, E17 → E25 |
| 🎓 **Get hired** | Students and career switchers aiming at ML infra or inference roles | S0 → S1 → S2 → E13 → S4 → S5 with weekly `/mock` |
| 🛠 **Contributor** | People who want their name in the vLLM commit log | S1 → S2 → S3 → E23 → E24 → one S4 topic deep dive |
| ⚡ **Serving engineer** | Practitioners running models in production | E05–E11 → E17–E21 → E27, E28 → E24 → E25 |
| ⏱️ **Interview Speedrun** | Interview in a week | E05, E07, E08, E09, E10, E17, E20, E27, E24, E25 (10 episodes in 7 days) + `/mock` every day |

## Labs

| Lab | Needs | Time | What you get |
|---|---|---|---|
| [Q1 First Token](labs/Q1-first-token.md) | A free Colab GPU or any NVIDIA/AMD GPU | 15 min | A live OpenAI-compatible vLLM server and your first streamed tokens |
| [Q2 Paged Playground](labs/Q2-paged-playground.md) | Python 3.10+ only | 15 min | A colored, step-by-step view of pages, block tables, prefix sharing and eviction |
| [Q3 Batching Arena](labs/Q3-batching-arena.md) | Python 3.10+ only | 15 min | Static vs continuous batching vs chunked prefill, simulated head-to-head |
| [Q4 KV Budget](labs/Q4-kv-budget.md) | Python 3.10+ only | 10 min | Memory math for real models (MHA, GQA and MLA) and the answer to E07 |
| [Q5 Build mini-vLLM](labs/Q5-build-mini-vllm.md) | CPU PyTorch | 4–8 h over a week | Your own engine and a green test suite |
| [Q6 Codebase Treasure Hunt](labs/Q6-codebase-hunt.md) | A vLLM checkout | 45 min | 12 graded hunts through the real source |
| [Q7 Benchmark Like a Pro](labs/Q7-benchmark-like-a-pro.md) | One GPU | 45 min | A reproducible TTFT/ITL/throughput report: prefix caching on vs off |
| [Q8 First PR Quest](labs/Q8-first-pr-quest.md) | Linux machine, GPU optional | 2 h + review time | A dev environment, a passing test and a well-formed PR |
| [Q9 Mock Interview](labs/Q9-mock-interview.md) | Discord | 30 min | A scored five-question mock interview with model answers |

## Gamification (so people actually finish)

- **XP**: episode complete +50, quiz correct +10 (first try +15), lab checkpoint +25, hunt solved +40, mock interview up to +100.
- **Ranks** (Discord roles, optional): `Token Rookie 新手` → `KV Cadet 見習生` → `Page Master 分頁大師` → `Scheduler Sage 排程賢者` → `Kernel Ninja 核心忍者` → `Maintainer Material 準維護者`.
- **Badges**: First Token, KV Accountant, Pager, Engine Builder, Navigator, Interview Ready, 7-Day Streak, Merged (granted by moderators when a real upstream PR merges).
- **Daily Drop** at 20:00 Taipei: one quiz, one interview question, one term or one trend, bilingual, in `#daily-drop`.
- **Release radar**: the bot announces new vLLM releases with "what this means for learners."
- **🔮 Hot Take Court**: `/hottake` shows a dated prediction with our confidence, the evidence and what would prove it wrong. Vote 🔥 agree or 🧊 disagree and see the room's split. On the judge date a moderator records the verdict, and the bot grades us in public. Vote on 5 to earn the **Oracle** badge.

## Discord commands

| Learn | Practice | Explore | Community |
|---|---|---|---|
| `/start` pick a route · `/path` your map · `/episode` · `/lab` · `/lang` | `/quiz` · `/interview` · `/mock` · `/hunt` · `/kvcalc` | `/trace` 12-stop request tour · `/code` code map · `/glossary` · `/trends` · `/hottake` | `/profile` card · `/leaderboard` · `/career` · `/community` · `/events` · `/gfi` good first issues |

Moderators: `/academy setup` creates channels and rank roles, `/academy post-start` posts the welcome panel, `/academy daily-now`, `/academy award`, `/academy verdict`, `/academy reload`.

## Cohort mode (8 weeks)

| Week | Live session (60 min) | Async in Discord |
|---|---|---|
| 1 | Kickoff + Q1 First Token together | S0 episodes + quizzes |
| 2 | KV math jam (E07) | S1 + Q2, Q4 |
| 3 | Batching arena race (E09, E11) | Q3 + start Q5 M1–M2 |
| 4 | Pair-debug mini-vLLM | Q5 M3–M6 |
| 5 | Request trace live-read with a contributor | S3 + Q6 hunts |
| 6 | Speed tricks AMA | S4, pick one topic for a 5-minute lightning talk |
| 7 | Benchmark clinic | Q7 + Q8 setup |
| 8 | Demo day: lightning talks, mock interviews, PR reviews | S5 + `/mock` |

## Honesty rules (inherited from Phase 1)

Bold hooks, honest bodies. A hook may be provocative; the body must be correct and must name its assumptions. Speed numbers always say *compared to what, on which workload*. GPU recipes that have not been executed by a maintainer carry a "not yet validated" note. Trend content says when it was written (October 2026) and links its source.
