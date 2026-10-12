<p align="center"><img src="assets/showcase/banner.png" alt="vLLM Academy: Zero to Inference Engineer" width="820"></p>

<h1 align="center">vLLM Academy Quest</h1>
<p align="center"><b>Learn how ChatGPT-style models actually run. Build the engine. Get merged. Get hired.</b><br>
28 bite-size episodes · 9 hands-on labs · a Discord bot that quizzes, grades and levels you up · English + 繁體中文</p>
<p align="center"><a href="README.zh-TW.md">繁體中文</a> · <a href="CURRICULUM.md">Curriculum</a> · <a href="../discord_bot/README.md">Run the Discord bot</a> · <a href="labs/">Labs</a></p>

---

## Why this, why now

- **Running models now costs more than training them.** Training happens once; inference runs every time anyone hits Enter. The people who make it fast and cheap are some of the most sought-after engineers in AI.
- **vLLM is the engine most of the industry runs on.** 300+ contributors ship a release roughly every two weeks (v0.31.0 landed on 5 Oct 2026 with 717 commits from 307 people). Its creators raised a $150M seed for Inferact in January 2026, co-led by a16z and Lightspeed. [source](https://techcrunch.com/2026/01/22/inference-startup-inferact-lands-150m-to-commercialize-vllm/)
- **Taiwan builds the racks. Who's going to serve the models on them?** A lot of the world's AI servers come off Taiwanese production lines. People who can make models fly on that hardware are much rarer than the hardware itself. TAIONE and Embedded LLM launched a vLLM Fellowship Track in Aug 2026. [source](https://macaubusiness.com/taione-open-source-foundation-and-embedded-llm-collaborate-to-build-taiwans-vllm-ecosystem/)

## Try it in 60 seconds (no GPU, no install)

```bash
git clone https://github.com/tjtanaa/vllm-academy.git && cd vllm-academy
python academy/labs/paged_playground.py --scenario prefix   # watch two chats share KV blocks
python academy/labs/batching_arena.py                       # static vs continuous batching, head to head
python academy/labs/kv_budget.py --model llama-3.1-70b --context 131072 --gpus 4   # the interview classic
```

Plain Python 3.10+, standard library only. Every number in the lab checkpoints is deterministic, so you know immediately whether you got it right.

## The seasons

<table>
<tr>
<td width="50%"><img src="assets/showcase/E05.png" alt="E05"></td>
<td width="50%"><img src="assets/showcase/E08.png" alt="E08"></td>
</tr>
<tr>
<td><img src="assets/showcase/E17.png" alt="E17"></td>
<td><img src="assets/showcase/E27.png" alt="E27"></td>
</tr>
</table>

| | Season | You walk away able to… |
|---|---|---|
| 🔤 | **S0 Hello, Token** · E01–E04 | Explain tokens, attention and why inference ≠ training |
| 🧱 | **S1 The Memory Wall** · E05–E08 | Do KV-cache math in your head and explain PagedAttention |
| 🛠️ | **S2 Build mini-vLLM** · E09–E12 | Build continuous batching, prefix caching and chunked prefill, and pass 30 tests |
| 🧭 | **S3 Inside vLLM** · E13–E16 | Trace a request from HTTP to GPU and back in the real codebase |
| 🚀 | **S4 Pro Speed Tricks** · E17–E22 | Talk speculative decoding, FP8/FP4, TP/PP/EP, P/D disaggregation, KV offload and RL |
| 🏆 | **S5 Get Merged, Get Hired** · E23–E26 | Ship a PR, benchmark honestly, own a system-design interview |
| 🔮 | **S6 Frontier Watch** · E27–E28+ | *Living season, refreshed monthly:* agentic inference, cold starts, and whatever ships next |

Every episode has the same five beats: **🎣 Hook → 💡 Aha → 🧪 Hands-on → 🎤 Say it like a pro → 🏁 Quiz.** Full details are in the [curriculum](CURRICULUM.md).

## Labs

| Lab | Needs | Time |
|---|---|---|
| [Q1 First Token](labs/Q1-first-token.md): your own vLLM server and streamed tokens | Free Colab GPU | 15 min |
| [Q2 Paged Playground](labs/Q2-paged-playground.md): pages, sharing, offload, agents | Python only | 15 min |
| [Q3 Batching Arena](labs/Q3-batching-arena.md): roofline + scheduler race | Python only | 15 min |
| [Q4 KV Budget](labs/Q4-kv-budget.md): the memory math that sinks candidates | Python only | 10 min |
| [Q5 Build mini-vLLM](labs/Q5-build-mini-vllm.md): the boss fight, 30 tests | CPU + PyTorch | 4–8 h |
| [Q6 Codebase Treasure Hunt](labs/Q6-codebase-hunt.md): 14 graded hunts in real vLLM | git | 45 min |
| [Q7 Benchmark Like a Pro](labs/Q7-benchmark-like-a-pro.md): an honest A/B write-up | 1 GPU | 45 min |
| [Q8 First PR Quest](labs/Q8-first-pr-quest.md): fork → merged | Linux/macOS | 2 h + review |
| [Q9 Mock Interview](labs/Q9-mock-interview.md): weekly reps | Discord | 30 min |

Each lab has a 繁體中文 version next to it (`*.zh-TW.md`), and the bot walks you through it step by step with `/lab`.

## The Discord bot

<table>
<tr>
<td width="50%"><img src="assets/showcase/hottake.png" alt="Hot Take Court card"><br><b>🔮 Hot Take Court</b>: dated predictions with our confidence, the evidence and what would prove us wrong. Vote 🔥/🧊; we grade ourselves in public on the judge date.</td>
<td width="50%"><img src="assets/showcase/kvcalc.png" alt="KV calculator card"><br><b>🧮 /kvcalc</b>: "Will it fit?" for any model and GPU, with the formula shown, so you learn the math instead of copying an answer.</td>
</tr>
<tr>
<td colspan="2"><img src="assets/showcase/profile.png" alt="Profile card" width="70%"><br><b>🏅 /profile</b>: levels from <i>Token Rookie</i> to <i>Maintainer Material</i>, season progress, streaks and badges (including <b>Merged</b>, granted when your upstream PR lands).</td>
</tr>
</table>

| Learn | Practice | Explore | Community |
|---|---|---|---|
| `/start` `/path` `/episode` `/lab` `/lang` | `/quiz` `/interview` `/mock` `/hunt` `/kvcalc` | `/trace` `/code` `/glossary` `/trends` `/hottake` | `/profile` `/leaderboard` `/career` `/community` `/events` `/gfi` |

Plus a bilingual **Daily Drop** at 20:00 Taipei (Friday is hot-take day, the same day as the vLLM Weekly newsletter) and a **Release Radar** that maps each new vLLM release to the episodes that explain it. [Set it up in 10 minutes →](../discord_bot/README.md)

## Pick your route

🌱 **Curious**: how does ChatGPT work? · 🎓 **Get hired**: the full path with weekly mocks · 🛠️ **Contributor**: straight to the codebase and a PR · ⚡ **Serving engineer**: production speed tricks · ⏱️ **Interview Speedrun**: 10 episodes in 7 days

## Honesty rules

Bold hooks, honest bodies. Every speed claim says *compared to what, on which workload*. GPU recipes not yet run by a maintainer are labelled as such. Trend cards carry a date and a source. Hot takes are labelled **speculation**, carry a confidence and a judge date, and get graded publicly. The deep, careful version of everything here lives in [Phase 1](../phase1/README.md).

## Contribute

Found a wrong number? Have a better hook? Want to add a hunt, a quiz or a frontier episode? Content is plain YAML in [`content/`](content/) and Markdown in [`labs/`](labs/) and [`frontier/`](frontier/), validated by `python -m academy_bot --check` (run it from `discord_bot/`). PRs welcome. See [CONTRIBUTING](../CONTRIBUTING.md).

<sub>An independent community project, not an official vLLM course. vLLM is a project of the vLLM team and its contributors.</sub>
