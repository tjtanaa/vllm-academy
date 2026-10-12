# vLLM Academy Discord Bot

The bot that runs [vLLM Academy Quest](../academy/README.md) inside your Discord server: bilingual (EN / 繁體中文) episodes, step-by-step labs, quizzes, interview drills, codebase treasure hunts, a KV-cache calculator, the 🔮 Hot Take Court, a Daily Drop and a vLLM Release Radar, with XP, levels, rank roles and badges.

- **Slash commands only.** No privileged intents, so it never reads your members' messages.
- **One SQLite file** for progress. No database server to run.
- **Content is YAML + Markdown** in `academy/`. Edit, then run `/academy reload`; no redeploy needed.
- **Offline-tested:** CI boots the bot without a token and checks every embed against Discord's limits.

## 10-minute setup

### 1. Create the Discord application

1. Go to https://discord.com/developers/applications → **New Application** → name it, e.g. "vLLM Academy".
2. **Bot** tab → **Reset Token** → copy the token (that's `DISCORD_TOKEN`). Leave every privileged intent **off**.
3. **OAuth2 → URL Generator**: scopes `bot` + `applications.commands`. Or use this invite URL with your app's client ID. The permissions are View Channels, Send Messages, Embed Links, Attach Files, Read Message History, plus Manage Channels and Manage Roles so `/academy setup` can build the channels and rank roles:

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=268553232
```

4. After inviting, drag the bot's role **above** the rank roles in Server Settings → Roles. Otherwise it can't assign levels.

### 2. Configure

```bash
cd discord_bot
cp .env.example .env
# edit .env: DISCORD_TOKEN, and DISCORD_GUILD_IDS=<your server id> so commands appear instantly
```

Get the server ID by enabling Developer Mode (User Settings → Advanced), then right-click the server → Copy Server ID.

### 3. Run it

**Python (3.10+):**

```bash
cd discord_bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m academy_bot --check        # validates all content: should print OK
python -m academy_bot                # starts the bot
```

The image cards need a CJK font for Chinese text. On Ubuntu/Debian: `sudo apt install fonts-noto-cjk`. On macOS and Windows, the system fonts are found automatically. You can also point `ACADEMY_FONT_DIR` at a folder of Noto Sans TC files.

**Docker (recommended for a server):**

```bash
# from the repo root
docker compose -f discord_bot/docker-compose.yml up -d --build
docker compose -f discord_bot/docker-compose.yml logs -f
```

Progress lives in the `academy-data` volume. Any small VM, a home server or a Raspberry Pi is plenty: the bot idles at a few tens of MB of RAM.

### 4. Set up the server (in Discord)

```
/academy setup               ← shows the plan
/academy setup confirm:True  ← creates the 🎓 vLLM Academy category, 7 channels and 6 rank roles,
                               posts the welcome panel in #start-here
```

Channels: `#start-here` · `#daily-drop` · `#hot-takes` · `#release-radar` · `#show-your-work` · `#labs-help` · `#mock-interviews`. The Daily Drop and Release Radar automatically post to the channels setup created.

## Commands

| Command | What it does |
|---|---|
| `/start` | Welcome panel: pick a route (Curious, Get hired, Contributor, Serving engineer, Interview Speedrun) and a language |
| `/path` | Your learning map with ✅ per episode, by season |
| `/episode E08` | An episode card: hook, aha, TL;DR, lab, interview answer, follow-up, deep dive, code permalinks |
| `/lab Q2` | Step-by-step lab with checkpoints, ◀ ▶ navigation and a "finished" button |
| `/quiz` | A multiple-choice question (+15 XP on a first-try correct answer); shows how many people solved it |
| `/interview level kind` | A real interview question; reveal key points, follow-ups and red flags |
| `/mock level` | A 5-question scored mock interview (up to +100 XP; 80%+ earns 🎤 Interview Ready) |
| `/hunt H5` | Codebase treasure hunt in real vLLM source at a pinned commit (+40 XP each) |
| `/kvcalc model context users gpu gpus kv_dtype` | Will it fit? Memory math with the formula and an image card |
| `/trace` | Follow one request through vLLM in 12 stops, with permalinks |
| `/code` | Browse the vLLM code map by area |
| `/glossary term` | Bilingual definitions with autocomplete |
| `/trends` | What's happening in vLLM right now, dated and sourced |
| `/hottake` | 🔮 Hot Take Court: vote 🔥/🧊 on dated predictions (5 votes earns 🔮 Oracle) |
| `/profile` · `/leaderboard` | Your level card, and the weekly or all-time ranking |
| `/career` · `/community` · `/events` · `/gfi` | Career paths, links, Taiwan events, live good first issues from GitHub |

**Moderators** (Manage Server): `/academy setup`, `/academy post-start`, `/academy daily-now`, `/academy award member badge` (e.g. grant 🏅 Merged when someone's upstream PR lands), `/academy verdict take verdict note` (grade a hot take on its judge date), `/academy reload`.

## Scheduled posts

| Post | When | Content |
|---|---|---|
| **Daily Drop** | Every day at `ACADEMY_DAILY_HOUR` (default 20:00 Asia/Taipei) | Mon quiz · Tue interview question · Wed term · Thu code hunt · **Fri hot take** (same day as the vLLM Weekly newsletter) · Sat trend · Sun episode. Bilingual and deterministic per date. |
| **Release Radar** | Checks GitHub every 3 h | New vLLM release → top highlights + the episodes that explain them. The first run only records the current release. |

## Editing content

Everything learners see lives in `academy/`:

```
academy/content/seasons.yaml     seasons, routes, ranks, badges
academy/content/episodes/S*.yaml 28 episodes (EN + zh)
academy/content/quizzes.yaml     84 quiz questions
academy/content/interview.yaml   interview bank
academy/content/hunts.yaml       codebase hunts (answers checked against codemap.yaml's pinned commit)
academy/content/codemap.yaml     vLLM code map + pinned commit; trace.yaml is the 12-stop tour
academy/content/trends.yaml      dated, sourced trend cards — refresh monthly
academy/content/hottakes.yaml    🔮 predictions: claim, evidence, wrong_if, confidence, judge_on, verdict
academy/content/glossary.yaml, careers.yaml, community.yaml
academy/labs/Q*-*.md (+ .zh-TW.md) labs: `## 1. Step` headings, one code block, `> ✅ **Checkpoint:**`
academy/frontier/                S6 deep dives
```

After editing, run `python -m academy_bot --check` and `python -m pytest -q`, then `/academy reload` in Discord. The validator catches missing translations, unknown IDs, broken deep-dive paths, oversized embeds and labs whose EN/zh step counts differ.

When you re-pin the code map to a newer vLLM commit, update `pin.commit` in `codemap.yaml`, re-check every path, symbol and line, and update the hunt answers that depend on them.

## Development

```bash
cd discord_bot
pip install -r requirements-dev.txt
python -m pytest -q                       # offline: content, sims, logic, storage, cards, bot boot + embed limits
python -m academy_bot --render-cards      # pre-render covers into academy/assets/cards (optional cache)
```

Layout: `bot.py` (wiring, XP and level roles) · `cogs/` (learn, practice, explore, community, profile, daily, admin) · `ui.py` (embeds and persistent buttons) · `cards.py` (Pillow image cards) · `content.py` (loader and validator) · `store.py` (SQLite) · `progress.py` (XP, levels, badges) · `drops.py` (daily rotation and release study links) · `kvcalc.py` (memory math shared with `academy/labs/kv_budget.py`).

Buttons are persistent (`DynamicItem`), so quiz and vote buttons on old messages keep working after a restart.
