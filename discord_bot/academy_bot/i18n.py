"""Bilingual UI strings. Content strings live in academy/content/*.yaml."""
from __future__ import annotations

from typing import Any, Mapping

LANGS = ("en", "zh")

STRINGS: dict[str, dict[str, str]] = {
    # ---- general ----
    "brand": {"en": "vLLM Academy", "zh": "vLLM Academy"},
    "tagline": {
        "en": "From zero to inference engineer, one episode at a time.",
        "zh": "從零到推論工程師，一集一集來。",
    },
    "lang_set": {"en": "Language set to **English**.", "zh": "語言已切換為 **繁體中文**。"},
    "lang_button": {"en": "中文", "zh": "English"},
    "not_found": {"en": "I couldn't find `{what}`.", "zh": "找不到 `{what}`。"},
    "admin_only": {"en": "Moderators only.", "zh": "只有管理員可以使用。"},
    "error": {"en": "Something went wrong: {err}", "zh": "發生錯誤：{err}"},
    "minutes": {"en": "{n} min", "zh": "{n} 分鐘"},
    "open_github": {"en": "Open on GitHub", "zh": "在 GitHub 開啟"},
    "source": {"en": "Source", "zh": "來源"},
    # ---- start ----
    "start_title": {"en": "Welcome to vLLM Academy 🎓", "zh": "歡迎來到 vLLM Academy 🎓"},
    "start_body": {
        "en": (
            "The world now spends more on **running** LLMs than training them. The engine most of the industry runs on is "
            "**vLLM**, and the people who understand it get hired.\n\n"
            "**28 bite-size episodes · 9 hands-on labs · interview prep · hot takes · real PRs.**\n"
            "Pick a route below. You can change it any time."
        ),
        "zh": (
            "全世界花在**運行** LLM 的錢，已經比訓練它們還多。業界大多數人用的引擎就是 **vLLM**，"
            "懂它的人，就是被搶著要的人。\n\n"
            "**28 集短課程 · 9 個實作關卡 · 面試準備 · 大膽預測 · 真正的 PR。**\n"
            "在下面選一條路線，之後隨時可以更換。"
        ),
    },
    "start_route_placeholder": {"en": "Choose your route…", "zh": "選擇你的路線…"},
    "start_route_set": {"en": "Route set: **{route}**. Your first stop is **{ep}**.", "zh": "路線已設定：**{route}**。你的第一站是 **{ep}**。"},
    "start_go": {"en": "▶ Start / continue", "zh": "▶ 開始／繼續"},
    "start_howto": {
        "en": "Commands: `/episode` `/path` `/quiz` `/lab` `/kvcalc` `/trace` `/hunt` `/interview` `/mock` `/hottake` `/profile`",
        "zh": "指令：`/episode` `/path` `/quiz` `/lab` `/kvcalc` `/trace` `/hunt` `/interview` `/mock` `/hottake` `/profile`",
    },
    # ---- path ----
    "path_title": {"en": "🗺️ Your learning map", "zh": "🗺️ 你的學習地圖"},
    "path_route": {"en": "Route: {route} · Next up: **{ep}**", "zh": "路線：{route} · 下一集：**{ep}**"},
    "path_select_season": {"en": "Open a season…", "zh": "打開一季…"},
    "path_select_episode": {"en": "Open an episode…", "zh": "打開一集…"},
    "no_route": {"en": "No route yet: use `/start`.", "zh": "還沒選路線：請用 `/start`。"},
    # ---- episode ----
    "ep_tldr": {"en": "⚡ TL;DR", "zh": "⚡ 重點整理"},
    "ep_lab": {"en": "🧪 Hands-on", "zh": "🧪 動手做"},
    "ep_pro": {"en": "🎤 Say it like a pro", "zh": "🎤 用專業的方式說出來"},
    "ep_followup": {"en": "🤔 The interviewer then asks…", "zh": "🤔 面試官接著會問…"},
    "ep_deep": {"en": "📖 Deep dive", "zh": "📖 深入閱讀"},
    "ep_code": {"en": "🧭 In the vLLM codebase", "zh": "🧭 在 vLLM 原始碼中"},
    "ep_footer": {"en": "{season} · {minutes} · +{xp} XP when complete", "zh": "{season} · {minutes} · 完成可得 +{xp} XP"},
    "btn_complete": {"en": "Mark complete", "zh": "標記完成"},
    "btn_quiz": {"en": "Quiz me", "zh": "考考我"},
    "btn_next": {"en": "Next episode", "zh": "下一集"},
    "btn_lab": {"en": "Open lab", "zh": "打開實作"},
    "already_done": {"en": "You already completed {ep}. Onward! ▶ `/episode {next}`", "zh": "你已經完成 {ep} 了，繼續前進！▶ `/episode {next}`"},
    "completed": {"en": "✅ **{ep} complete!** +{xp} XP", "zh": "✅ **{ep} 完成！** +{xp} XP"},
    "last_episode": {"en": "That was the final episode. Legend. 👑", "zh": "這是最後一集了。傳奇。👑"},
    # ---- xp / level ----
    "level_up": {
        "en": "🎉 {user} reached **Level {level} · {rank}**! ({xp} XP)",
        "zh": "🎉 {user} 升到 **Level {level} · {rank}**！（{xp} XP）",
    },
    "badge_earned": {"en": "🏅 New badge: **{badge}**", "zh": "🏅 獲得新徽章：**{badge}**"},
    "streak": {"en": "🔥 {n}-day streak", "zh": "🔥 連續 {n} 天"},
    # ---- quiz ----
    "quiz_title": {"en": "🧠 Quiz · {ep}", "zh": "🧠 小測驗 · {ep}"},
    "quiz_footer": {"en": "Tap an answer. Only you see the result. · {solved} solved so far", "zh": "點選答案，只有你看得到結果。· 目前 {solved} 人答對"},
    "quiz_right": {"en": "✅ **Correct!** +{xp} XP", "zh": "✅ **答對了！** +{xp} XP"},
    "quiz_right_again": {"en": "✅ **Correct!** (XP is only awarded on your first attempt)", "zh": "✅ **答對了！**（XP 只在第一次作答時給）"},
    "quiz_wrong": {"en": "❌ **Not quite.** The answer is **{letter}**.", "zh": "❌ **差一點。** 正確答案是 **{letter}**。"},
    "quiz_none": {"en": "No quiz questions found for that.", "zh": "找不到相關的測驗題目。"},
    # ---- interview ----
    "iv_title": {"en": "🎤 Interview question · {level}", "zh": "🎤 面試題 · {level}"},
    "iv_level_junior": {"en": "Junior", "zh": "初階"},
    "iv_level_mid": {"en": "Mid", "zh": "中階"},
    "iv_level_senior": {"en": "Senior", "zh": "資深"},
    "iv_prompt": {
        "en": "Answer out loud (or type it to yourself) **before** you reveal. Two minutes. Go. ⏱️",
        "zh": "先大聲回答（或寫給自己看），**再**打開答案。兩分鐘，開始。⏱️",
    },
    "btn_points": {"en": "Key points", "zh": "答題重點"},
    "btn_followups": {"en": "Follow-ups", "zh": "追問"},
    "btn_redflags": {"en": "Red flags", "zh": "地雷"},
    "iv_points": {"en": "🔑 A strong answer covers", "zh": "🔑 好答案應該涵蓋"},
    "iv_followups": {"en": "➡️ Expect these follow-ups", "zh": "➡️ 預期會被追問"},
    "iv_redflags": {"en": "🚩 Red flags interviewers notice", "zh": "🚩 面試官會注意的地雷"},
    "iv_related": {"en": "Related episode: {ep}", "zh": "相關單集：{ep}"},
    # ---- mock ----
    "mock_title": {"en": "🎯 Mock interview · Q{n}/{total}", "zh": "🎯 模擬面試 · 第 {n}/{total} 題"},
    "mock_reveal": {"en": "Reveal key points", "zh": "顯示答題重點"},
    "mock_rate": {"en": "How did you do?", "zh": "你答得如何？"},
    "mock_nailed": {"en": "Nailed it", "zh": "完全答出"},
    "mock_partial": {"en": "Partial", "zh": "部分答出"},
    "mock_missed": {"en": "Missed it", "zh": "沒答出"},
    "mock_done_title": {"en": "🎯 Mock interview complete", "zh": "🎯 模擬面試完成"},
    "mock_done": {
        "en": "Score: **{score}%** ({raw}/{max}) · +{xp} XP\nReview the ones you missed, then run `/mock` again next week.",
        "zh": "分數：**{score}%**（{raw}/{max}）· +{xp} XP\n複習沒答好的題目，下週再跑一次 `/mock`。",
    },
    "mock_busy": {"en": "You already have a mock running. Finish it first!", "zh": "你已經有一場模擬面試在進行，先完成它！"},
    # ---- hunt ----
    "hunt_title": {"en": "🗺️ Codebase hunt {id}", "zh": "🗺️ 原始碼尋寶 {id}"},
    "hunt_how": {
        "en": "Clone vLLM, find the answer in the source, then submit it here. Pinned commit: `{commit}`",
        "zh": "Clone vLLM，在原始碼中找到答案，然後在這裡送出。固定 commit：`{commit}`",
    },
    "btn_submit": {"en": "Submit answer", "zh": "送出答案"},
    "btn_hint": {"en": "Hint", "zh": "提示"},
    "hunt_modal": {"en": "Hunt {id}", "zh": "尋寶 {id}"},
    "hunt_label": {"en": "Your answer", "zh": "你的答案"},
    "hunt_right": {"en": "🎯 **Found it!** +{xp} XP", "zh": "🎯 **找到了！** +{xp} XP"},
    "hunt_right_again": {"en": "🎯 Correct again! (already solved)", "zh": "🎯 又答對了！（已經解開過）"},
    "hunt_wrong": {"en": "🔍 Not it. Keep digging (try the hint).", "zh": "🔍 不是這個。繼續挖（試試提示）。"},
    "hunt_progress": {"en": "Solved {n}/{total} hunts", "zh": "已解開 {n}/{total} 題尋寶"},
    # ---- kvcalc ----
    "kv_title": {"en": "🧮 KV-cache budget · {model}", "zh": "🧮 KV cache 預算 · {model}"},
    "kv_per_token": {"en": "KV per token", "zh": "每個 token 的 KV"},
    "kv_per_seq": {"en": "KV per sequence ({ctx} tokens)", "zh": "每個序列的 KV（{ctx} tokens）"},
    "kv_total": {"en": "KV for {users} sequences", "zh": "{users} 個序列的 KV"},
    "kv_weights": {"en": "Weights", "zh": "權重"},
    "kv_capacity": {"en": "Fits on {gpus}× {gpu}", "zh": "可放進 {gpus}× {gpu}"},
    "kv_fits": {"en": "✅ Fits. Max ~**{maxseq}** full-length sequences concurrently.", "zh": "✅ 放得下。最多約 **{maxseq}** 個滿長度序列同時執行。"},
    "kv_nofit": {"en": "❌ Doesn't fit. You can hold ~**{maxseq}** full-length sequences. Try FP8 KV, more GPUs or a shorter context.", "zh": "❌ 放不下。只能放約 **{maxseq}** 個滿長度序列。試試 FP8 KV、更多 GPU 或更短的 context。"},
    "kv_noweights": {"en": "❌ The weights alone don't fit. Add GPUs or quantize.", "zh": "❌ 光是權重就放不下。增加 GPU 或做量化。"},
    "kv_formula": {"en": "Formula", "zh": "公式"},
    "kv_assumptions": {
        "en": "Assumes {util:.0%} of GPU memory for weights+KV, no activation/graph overhead, and KV sharded evenly across TP ranks. Real capacity is lower: read the engine's startup log.",
        "zh": "假設 GPU 記憶體的 {util:.0%} 用於權重 + KV，不計激活值與 graph 開銷，KV 平均分散在各 TP rank。實際容量會更低：請看引擎啟動日誌。",
    },
    "kv_custom_needed": {"en": "For a custom model give layers, kv_heads and head_dim.", "zh": "自訂模型請提供 layers、kv_heads 與 head_dim。"},
    # ---- codemap / trace ----
    "code_title": {"en": "🧭 vLLM code map", "zh": "🧭 vLLM 程式碼地圖"},
    "code_pick_area": {"en": "Pick an area…", "zh": "選一個區域…"},
    "code_pick_entry": {"en": "Pick a component…", "zh": "選一個元件…"},
    "code_owns": {"en": "What it owns", "zh": "它負責什麼"},
    "code_try": {"en": "🔎 Try this", "zh": "🔎 試試看"},
    "code_where": {"en": "Where", "zh": "位置"},
    "code_pin": {"en": "Pinned at `{short}` ({date})", "zh": "固定於 `{short}`（{date}）"},
    "trace_footer": {"en": "Stop {n}/{total} · {process}", "zh": "第 {n}/{total} 站 · {process}"},
    "trace_carries": {"en": "📦 What crosses this stop", "zh": "📦 經過這一站的資料"},
    "btn_prev": {"en": "Back", "zh": "上一站"},
    "btn_fwd": {"en": "Next", "zh": "下一站"},
    "btn_code": {"en": "Open the code", "zh": "打開程式碼"},
    # ---- labs ----
    "lab_title": {"en": "🧪 Lab {id} · {title}", "zh": "🧪 實作 {id} · {title}"},
    "lab_step": {"en": "Step {n}/{total}", "zh": "步驟 {n}/{total}"},
    "lab_checkpoint": {"en": "✅ Checkpoint", "zh": "✅ 檢查點"},
    "lab_done_btn": {"en": "I finished this lab", "zh": "我完成這個實作了"},
    "lab_done": {"en": "🧪 **Lab {id} complete!** +{xp} XP. Post your output in #show-your-work.", "zh": "🧪 **實作 {id} 完成！** +{xp} XP。把你的輸出貼到 #show-your-work。"},
    "lab_already": {"en": "Already logged. Nice work.", "zh": "已經記錄過了，做得好。"},
    "lab_list": {"en": "🧪 Labs", "zh": "🧪 實作關卡"},
    # ---- profile / leaderboard ----
    "profile_title": {"en": "{user}'s Academy card", "zh": "{user} 的 Academy 卡片"},
    "lb_title": {"en": "🏆 Leaderboard", "zh": "🏆 排行榜"},
    "lb_empty": {"en": "No XP yet. Be the first: `/episode E01`", "zh": "還沒有人拿到 XP。成為第一個吧：`/episode E01`"},
    "award_done": {"en": "Awarded **{badge}** to {user} (+{xp} XP).", "zh": "已頒發 **{badge}** 給 {user}（+{xp} XP）。"},
    # ---- github ----
    "gfi_title": {"en": "🌱 Good first issues in vLLM", "zh": "🌱 vLLM 的 Good first issues"},
    "gfi_tip": {
        "en": "Before you start: read the comments, search open PRs for the issue number, and say you're working on it. (E23)",
        "zh": "開始之前：讀完留言、用 issue 編號搜尋開著的 PR，並留言說你要處理。（E23）",
    },
    "gfi_none": {"en": "No open good-first-issues right now. Try the onboarding board or `/hunt`.", "zh": "目前沒有開著的 good first issue。試試新手看板或 `/hunt`。"},
    "release_title": {"en": "📦 vLLM {tag} is out", "zh": "📦 vLLM {tag} 發布了"},
    "release_learn": {"en": "🎓 Study links for this release", "zh": "🎓 這個版本的學習連結"},
    "github_down": {"en": "GitHub didn't answer. Try again in a minute.", "zh": "GitHub 沒有回應，請稍後再試。"},
    # ---- daily ----
    "daily_title": {"en": "🔥 Daily vLLM Drop · {date}", "zh": "🔥 每日 vLLM 一練 · {date}"},
    "daily_quiz": {"en": "Quiz of the day", "zh": "今日測驗"},
    "daily_interview": {"en": "Interview question of the day", "zh": "今日面試題"},
    "daily_term": {"en": "Term of the day", "zh": "今日名詞"},
    "daily_hunt": {"en": "Code hunt of the day", "zh": "今日原始碼尋寶"},
    "daily_trend": {"en": "What's happening in vLLM", "zh": "vLLM 最新動態"},
    "daily_episode": {"en": "Weekend binge", "zh": "週末追劇"},
    # ---- trends / career / community ----
    "trend_title": {"en": "📈 vLLM trends · as of {date}", "zh": "📈 vLLM 趨勢 · 截至 {date}"},
    "trend_why": {"en": "Why it matters for you", "zh": "這對你的意義"},
    "career_title": {"en": "💼 Career paths", "zh": "💼 職涯路線"},
    "career_skills": {"en": "Skills", "zh": "技能"},
    "career_eps": {"en": "Episodes", "zh": "相關單集"},
    "career_proof": {"en": "🏗️ Proof projects that get interviews", "zh": "🏗️ 能拿到面試的作品"},
    "community_title": {"en": "🤝 vLLM community", "zh": "🤝 vLLM 社群"},
    "community_events": {"en": "📅 Taiwan events", "zh": "📅 台灣活動"},
    "glossary_title": {"en": "📚 {term}", "zh": "📚 {term}"},
    # ---- hot takes ----
    "ht_title": {"en": "🔮 Hot Take Court · {id}", "zh": "🔮 大膽預測法庭 · {id}"},
    "ht_evidence": {"en": "📎 What we're betting on", "zh": "📎 我們押注的依據"},
    "ht_wrong_if": {"en": "❌ We're wrong if…", "zh": "❌ 以下情況代表我們錯了…"},
    "ht_meta": {"en": "Our confidence: **{conf}%** · Judged on **{date}** · Related: {ep}",
                "zh": "我們的信心：**{conf}%** · 判決日：**{date}** · 相關單集：{ep}"},
    "ht_agree": {"en": "Agree", "zh": "同意"},
    "ht_disagree": {"en": "Disagree", "zh": "不同意"},
    "ht_voted": {"en": "🗳️ Vote counted: **{choice}**. The room so far: 🔥 {agree} · 🧊 {disagree}",
                 "zh": "🗳️ 已計票：**{choice}**。目前大家：🔥 {agree} · 🧊 {disagree}"},
    "ht_changed": {"en": "🗳️ Vote changed to **{choice}**. The room so far: 🔥 {agree} · 🧊 {disagree}",
                   "zh": "🗳️ 已改投 **{choice}**。目前大家：🔥 {agree} · 🧊 {disagree}"},
    "ht_verdict": {"en": "⚖️ Verdict: **{verdict}**. {note}", "zh": "⚖️ 判決：**{verdict}**。{note}"},
    "ht_pending": {"en": "⏳ Not judged yet.", "zh": "⏳ 尚未判決。"},
    "ht_list": {"en": "🔮 All hot takes · vote on 5 to earn the Oracle badge", "zh": "🔮 所有大膽預測 · 投滿 5 則可得「先知」徽章"},
    "ht_pick": {"en": "Open a hot take…", "zh": "打開一則預測…"},
    "verdict_right": {"en": "Called it ✅", "zh": "猜中了 ✅"},
    "verdict_wrong": {"en": "We were wrong ❌", "zh": "我們猜錯了 ❌"},
    "verdict_partly": {"en": "Partly right 🟡", "zh": "對一半 🟡"},
    "daily_hottake": {"en": "Hot take of the day: vote!", "zh": "今日大膽預測：來投票！"},
    "trend_more": {"en": "More with `/trends` · Related episode: {ep}", "zh": "更多請用 `/trends` · 相關單集：{ep}"},
    "events_none": {"en": "No upcoming events listed. Know one? Open a PR to community.yaml.",
                    "zh": "目前沒有列出即將舉行的活動。知道有活動？歡迎對 community.yaml 開 PR。"},
    "event_past": {"en": "past", "zh": "已結束"},
    "event_upcoming": {"en": "upcoming", "zh": "即將舉行"},
    "event_announced": {"en": "announced", "zh": "已宣布"},
    "trace_title": {"en": "🛰️ {title}", "zh": "🛰️ {title}"},
    "code_pick_hint": {"en": "Pick an area, then a component. Every link is a permalink at the pinned commit.",
                       "zh": "先選區域，再選元件。每個連結都是固定 commit 的永久連結。"},
    "kv_card_sub": {"en": "{ctx} tokens · {users} seq · {gpus}× {gpu} · KV {kvd} · weights {wd}",
                    "zh": "{ctx} tokens · {users} 序列 · {gpus}× {gpu} · KV {kvd} · 權重 {wd}"},
    "kv_unknown_model": {"en": "Unknown model `{m}`. Presets: {list}", "zh": "未知的模型 `{m}`。預設選項：{list}"},
    "kv_unknown_gpu": {"en": "Unknown GPU `{g}`. Presets: {list}", "zh": "未知的 GPU `{g}`。預設選項：{list}"},
    "lb_week": {"en": "this week", "zh": "本週"},
    "lb_all": {"en": "all time", "zh": "總榜"},
    "lb_you": {"en": "You: #{rank} · {xp} XP", "zh": "你：第 {rank} 名 · {xp} XP"},
    "award_badge_unknown": {"en": "Unknown badge `{b}`.", "zh": "未知的徽章 `{b}`。"},
    "verdict_set": {"en": "Verdict for {id} recorded: {verdict}", "zh": "已記錄 {id} 的判決：{verdict}"},
    "daily_posted": {"en": "Daily drop posted.", "zh": "每日一練已發布。"},
    "start_posted": {"en": "Welcome panel posted.", "zh": "歡迎面板已發布。"},
    # ---- setup ----
    "setup_plan": {"en": "**Plan** (run again with `confirm:True` to apply):\n{plan}", "zh": "**計畫**（加上 `confirm:True` 再執行一次即可套用）：\n{plan}"},
    "setup_done": {"en": "Server setup complete:\n{plan}", "zh": "伺服器設定完成：\n{plan}"},
    "reloaded": {"en": "Content reloaded: {summary}", "zh": "內容已重新載入：{summary}"},
}


def t(key: str, lang: str, **kwargs: Any) -> str:
    entry = STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(lang) or entry.get("en") or key
    return text.format(**kwargs) if kwargs else text


def L(value: Any, lang: str) -> Any:
    """Pick a language from a {en, zh} mapping; pass other values through."""
    if isinstance(value, Mapping) and ("en" in value or "zh" in value):
        return value.get(lang) or value.get("en") or value.get("zh")
    return value


def both(value: Mapping[str, Any], sep: str = "\n") -> str:
    """Render both languages, Chinese first (for public bilingual posts)."""
    zh, en = value.get("zh"), value.get("en")
    if zh and en and zh != en:
        return f"{zh}{sep}{en}"
    return zh or en or ""
