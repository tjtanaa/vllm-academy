"""Embeds, persistent buttons and views. Everything user-facing is built here."""
from __future__ import annotations

import io
import random
import re
from typing import TYPE_CHECKING

import discord

from . import cards
from .content import Episode, Hunt, InterviewQ, Lab, Quiz
from .i18n import L, both, t
from .progress import XP, check_hunt, progress_bar

if TYPE_CHECKING:  # pragma: no cover
    from .bot import AcademyBot

LETTERS = ["A", "B", "C", "D", "E"]
AMBER = 0xFDBA34


def clip(text: str, n: int) -> str:
    text = text or ""
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def bot_of(interaction: discord.Interaction) -> "AcademyBot":
    return interaction.client  # type: ignore[return-value]


async def lang_of(interaction: discord.Interaction) -> str:
    return await bot_of(interaction).lang_for(interaction.user.id)


# =========================================================================== episodes
def season_label(bot: "AcademyBot", season_id: str, lang: str) -> str:
    s = bot.content.season(season_id)
    return f"{s.emoji} {season_id} · {L(s.title, lang)}" if s else season_id


def episode_cover_file(bot: "AcademyBot", ep: Episode) -> discord.File:
    path = bot.settings.assets_dir / "cards" / f"{ep.id}.png"
    if path.exists():
        data = path.read_bytes()
    else:
        data = bot.cover_cache.get(ep.id)
        if data is None:
            s = bot.content.season(ep.season)
            data = cards.episode_cover(ep_id=ep.id, title_en=ep.title["en"], title_zh=ep.title["zh"],
                                       season_label_en=f"{s.id} {s.title['en']}", season_label_zh=s.title["zh"],
                                       color=s.color, minutes=ep.minutes, xp=ep.xp)
            bot.cover_cache[ep.id] = data
    return discord.File(io.BytesIO(data), filename=f"{ep.id}.png")


def episode_embed(bot: "AcademyBot", ep: Episode, lang: str, *, done: bool = False) -> discord.Embed:
    c = bot.content
    s = c.season(ep.season)
    title = f"{'✅ ' if done else ''}{ep.id} · {L(ep.title, lang)}"
    desc = f"**{L(ep.hook, lang)}**\n\n{L(ep.aha, lang)}"
    e = discord.Embed(title=clip(title, 256), description=clip(desc, 4000), color=s.color if s else AMBER)
    e.add_field(name=t("ep_tldr", lang), value=clip("\n".join(f"• {x}" for x in L(ep.tldr, lang)), 1024), inline=False)
    lab_line = L(ep.lab_hint, lang)
    if ep.lab and (lab := c.lab(ep.lab)):
        lab_line += f"\n→ [{lab.id} · {L(lab.title, lang)}]({bot.settings.repo_link(L(lab.path, lang))})"
    e.add_field(name=t("ep_lab", lang), value=clip(lab_line, 1024), inline=False)
    e.add_field(name=t("ep_pro", lang), value=clip(L(ep.pro, lang), 1024), inline=False)
    e.add_field(name=t("ep_followup", lang), value=clip(f"*{L(ep.followup, lang)}*", 1024), inline=False)
    links = [f"[{ep.deep_dive.split('/')[-1]}]({bot.settings.repo_link(ep.deep_dive)})"]
    e.add_field(name=t("ep_deep", lang), value=" · ".join(links), inline=True)
    code_links = []
    for cid in ep.code[:4]:
        entry = c.code_entry(cid)
        if entry:
            code_links.append(f"[`{entry.path.split('/')[-1]}` · {clip(entry.symbol, 40)}]({c.permalink(entry)})")
    if code_links:
        e.add_field(name=t("ep_code", lang), value=clip("\n".join(code_links), 1024), inline=True)
    e.set_image(url=f"attachment://{ep.id}.png")
    e.set_footer(text=t("ep_footer", lang, season=season_label(bot, ep.season, lang),
                        minutes=t("minutes", lang, n=ep.minutes), xp=ep.xp))
    return e


def episode_view(bot: "AcademyBot", ep: Episode, lang: str) -> discord.ui.View:
    v = discord.ui.View(timeout=None)
    v.add_item(CompleteButton(ep.id, label=t("btn_complete", lang)))
    if bot.content.quizzes_for(ep.id):
        v.add_item(EpisodeQuizButton(ep.id, label=t("btn_quiz", lang)))
    nxt = bot.content.next_episode(ep.id)
    if nxt:
        v.add_item(OpenEpisodeButton(nxt.id, label=f"{t('btn_next', lang)} · {nxt.id}"))
    if ep.lab and (lab := bot.content.lab(ep.lab)):
        v.add_item(discord.ui.Button(label=f"{t('btn_lab', lang)} {lab.id}", emoji="🧪",
                                     url=bot.settings.repo_link(L(lab.path, lang))))
    return v


async def send_episode(interaction: discord.Interaction, ep: Episode, *, ephemeral: bool) -> None:
    bot = bot_of(interaction)
    lang = await lang_of(interaction)
    done = await bot.store.has(interaction.user.id, "episode", ep.id)
    kwargs = dict(embed=episode_embed(bot, ep, lang, done=done), view=episode_view(bot, ep, lang),
                  file=episode_cover_file(bot, ep), ephemeral=ephemeral)
    if interaction.response.is_done():
        await interaction.followup.send(**kwargs)
    else:
        await interaction.response.send_message(**kwargs)


class OpenEpisodeButton(discord.ui.DynamicItem[discord.ui.Button], template=r"ep:(?P<ep>E\d{2})"):
    def __init__(self, ep_id: str, label: str | None = None):
        super().__init__(discord.ui.Button(label=label or ep_id, style=discord.ButtonStyle.primary, emoji="▶️",
                                           custom_id=f"ep:{ep_id}"))
        self.ep_id = ep_id

    @classmethod
    async def from_custom_id(cls, interaction, item, match):  # noqa: D401
        return cls(match["ep"])

    async def callback(self, interaction: discord.Interaction) -> None:
        ep = bot_of(interaction).content.episode(self.ep_id)
        if ep:
            await send_episode(interaction, ep, ephemeral=True)


class CompleteButton(discord.ui.DynamicItem[discord.ui.Button], template=r"done:(?P<ep>E\d{2})"):
    def __init__(self, ep_id: str, label: str | None = None):
        super().__init__(discord.ui.Button(label=label or "Done", style=discord.ButtonStyle.success, emoji="✅",
                                           custom_id=f"done:{ep_id}"))
        self.ep_id = ep_id

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["ep"])

    async def callback(self, interaction: discord.Interaction) -> None:
        bot = bot_of(interaction)
        lang = await lang_of(interaction)
        ep = bot.content.episode(self.ep_id)
        if ep is None:
            return await interaction.response.send_message(t("not_found", lang, what=self.ep_id), ephemeral=True)
        nxt = bot.content.next_episode(ep.id)
        first = await bot.store.mark(interaction.user.id, "episode", ep.id)
        if not first:
            msg = t("already_done", lang, ep=ep.id, next=nxt.id if nxt else ep.id)
            return await interaction.response.send_message(msg, ephemeral=True)
        lines = [t("completed", lang, ep=f"{ep.id} · {L(ep.title, lang)}", xp=ep.xp)]
        lines += await bot.reward(interaction, ep.xp, f"episode:{ep.id}")
        view = discord.ui.View(timeout=None)
        if nxt:
            lines.append(f"▶ **{nxt.id} · {L(nxt.title, lang)}**")
            view.add_item(OpenEpisodeButton(nxt.id, label=f"{t('btn_next', lang)} · {nxt.id}"))
        else:
            lines.append(t("last_episode", lang))
        if bot.content.quizzes_for(ep.id):
            view.add_item(EpisodeQuizButton(ep.id, label=t("btn_quiz", lang)))
        await interaction.response.send_message("\n".join(lines), view=view, ephemeral=True)


# =========================================================================== quizzes
def quiz_embed(bot: "AcademyBot", q: Quiz, lang: str, solved: int, *, bilingual: bool = False) -> discord.Embed:
    ep = bot.content.episode(q.episode)
    s = bot.content.season(ep.season) if ep else None
    if bilingual:
        body = both(q.q, "\n") + "\n\n" + "\n".join(
            f"**{LETTERS[i]}.** {q.options['zh'][i]}　/　{q.options['en'][i]}" for i in range(len(q.options["en"])))
    else:
        body = L(q.q, lang) + "\n\n" + "\n".join(f"**{LETTERS[i]}.** {o}" for i, o in enumerate(L(q.options, lang)))
    e = discord.Embed(title=t("quiz_title", lang, ep=f"{q.episode} · {clip(L(ep.title, lang), 80) if ep else ''}"),
                      description=clip(body, 4000), color=s.color if s else AMBER)
    e.set_footer(text=t("quiz_footer", lang, solved=solved))
    return e


def quiz_view(q: Quiz) -> discord.ui.View:
    v = discord.ui.View(timeout=None)
    for i in range(len(q.options["en"])):
        v.add_item(QuizButton(q.id, i))
    return v


async def send_quiz(interaction: discord.Interaction, q: Quiz, *, ephemeral: bool) -> None:
    bot = bot_of(interaction)
    lang = await lang_of(interaction)
    solved = await bot.store.quiz_solvers(q.id)
    kwargs = dict(embed=quiz_embed(bot, q, lang, solved), view=quiz_view(q), ephemeral=ephemeral)
    if interaction.response.is_done():
        await interaction.followup.send(**kwargs)
    else:
        await interaction.response.send_message(**kwargs)


async def pick_quiz(bot: "AcademyBot", user_id: int, episode: str | None = None) -> Quiz | None:
    pool = bot.content.quizzes_for(episode) if episode else bot.content.quizzes
    if not pool:
        return None
    fresh = await bot.store.unanswered_quizzes(user_id, [q.id for q in pool])
    choices = [q for q in pool if q.id in fresh] or pool
    return random.choice(choices)


class QuizButton(discord.ui.DynamicItem[discord.ui.Button], template=r"quiz:(?P<qid>[\w.-]+):(?P<opt>\d)"):
    def __init__(self, quiz_id: str, option: int):
        super().__init__(discord.ui.Button(label=LETTERS[option], style=discord.ButtonStyle.secondary,
                                           custom_id=f"quiz:{quiz_id}:{option}"))
        self.quiz_id, self.option = quiz_id, option

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["qid"], int(match["opt"]))

    async def callback(self, interaction: discord.Interaction) -> None:
        bot = bot_of(interaction)
        lang = await lang_of(interaction)
        q = bot.content.quiz(self.quiz_id)
        if q is None:
            return await interaction.response.send_message(t("not_found", lang, what=self.quiz_id), ephemeral=True)
        correct = self.option == q.answer
        first = await bot.store.record_quiz(interaction.user.id, q.id, correct)
        your = f"**{LETTERS[self.option]}.** {L(q.options, lang)[self.option]}"
        if correct:
            xp = XP["quiz_first_try"] if first else 0
            head = t("quiz_right", lang, xp=xp) if first else t("quiz_right_again", lang)
            lines = [head, your, "", L(q.explain, lang)]
            lines += await bot.reward(interaction, xp, f"quiz:{q.id}")
        else:
            right = f"**{LETTERS[q.answer]}.** {L(q.options, lang)[q.answer]}"
            lines = [t("quiz_wrong", lang, letter=LETTERS[q.answer]), right, "", L(q.explain, lang)]
            await bot.reward(interaction, 0, f"quiz-miss:{q.id}")
        more = discord.ui.View(timeout=None)
        more.add_item(EpisodeQuizButton(q.episode, label=t("btn_quiz", lang)))
        more.add_item(OpenEpisodeButton(q.episode, label=q.episode))
        await interaction.response.send_message("\n".join(lines), view=more, ephemeral=True)
        # refresh the public "solved" counter on the original message
        try:
            if interaction.message and interaction.message.embeds:
                emb = interaction.message.embeds[0]
                footer_lang = "zh" if emb.footer and emb.footer.text and "答對" in emb.footer.text else "en"
                emb.set_footer(text=t("quiz_footer", footer_lang, solved=await bot.store.quiz_solvers(q.id)))
                await interaction.message.edit(embed=emb)
        except discord.HTTPException:
            pass


class EpisodeQuizButton(discord.ui.DynamicItem[discord.ui.Button], template=r"epquiz:(?P<ep>E\d{2})"):
    def __init__(self, ep_id: str, label: str | None = None):
        super().__init__(discord.ui.Button(label=label or "Quiz", style=discord.ButtonStyle.secondary, emoji="🧠",
                                           custom_id=f"epquiz:{ep_id}"))
        self.ep_id = ep_id

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["ep"])

    async def callback(self, interaction: discord.Interaction) -> None:
        bot = bot_of(interaction)
        q = await pick_quiz(bot, interaction.user.id, self.ep_id)
        if q is None:
            return await interaction.response.send_message(t("quiz_none", await lang_of(interaction)), ephemeral=True)
        await send_quiz(interaction, q, ephemeral=True)


# =========================================================================== interview
LEVEL_COLORS = {"junior": 0x34D399, "mid": 0xFBBF24, "senior": 0xF87171}


def interview_embed(bot: "AcademyBot", iv: InterviewQ, lang: str) -> discord.Embed:
    level = t(f"iv_level_{iv.level}", lang)
    e = discord.Embed(title=t("iv_title", lang, level=f"{level} · {iv.kind}"),
                      description=f"### {L(iv.q, lang)}\n\n{t('iv_prompt', lang)}",
                      color=LEVEL_COLORS.get(iv.level, AMBER))
    ep = bot.content.episode(iv.episode)
    if ep:
        e.set_footer(text=t("iv_related", lang, ep=f"{ep.id} · {L(ep.title, lang)}"))
    return e


def interview_view(iv: InterviewQ, lang: str) -> discord.ui.View:
    v = discord.ui.View(timeout=None)
    v.add_item(InterviewRevealButton(iv.id, "points", label=t("btn_points", lang)))
    v.add_item(InterviewRevealButton(iv.id, "follow", label=t("btn_followups", lang)))
    v.add_item(InterviewRevealButton(iv.id, "flags", label=t("btn_redflags", lang)))
    return v


class InterviewRevealButton(discord.ui.DynamicItem[discord.ui.Button],
                            template=r"iv:(?P<id>[\w.-]+):(?P<part>points|follow|flags)"):
    EMOJI = {"points": "🔑", "follow": "➡️", "flags": "🚩"}

    def __init__(self, iv_id: str, part: str, label: str | None = None):
        super().__init__(discord.ui.Button(label=label or part, emoji=self.EMOJI[part],
                                           style=discord.ButtonStyle.secondary, custom_id=f"iv:{iv_id}:{part}"))
        self.iv_id, self.part = iv_id, part

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["id"], match["part"])

    async def callback(self, interaction: discord.Interaction) -> None:
        bot = bot_of(interaction)
        lang = await lang_of(interaction)
        iv = bot.content.interview_q(self.iv_id)
        if iv is None:
            return await interaction.response.send_message(t("not_found", lang, what=self.iv_id), ephemeral=True)
        key, items = {"points": ("iv_points", iv.points), "follow": ("iv_followups", iv.followups),
                      "flags": ("iv_redflags", iv.red_flags)}[self.part]
        body = f"**{t(key, lang)}**\n" + "\n".join(f"• {x}" for x in L(items, lang))
        await bot.reward(interaction, 0, f"interview:{iv.id}")
        await interaction.response.send_message(clip(body, 1900), ephemeral=True)


# =========================================================================== hunts
def hunt_embed(bot: "AcademyBot", h: Hunt, lang: str, solved: bool = False) -> discord.Embed:
    pin = bot.content.code_pin
    stars = "★" * h.difficulty + "☆" * (3 - h.difficulty)
    e = discord.Embed(title=f"{'✅ ' if solved else ''}{t('hunt_title', lang, id=h.id)} · {stars} · +{h.xp} XP",
                      description=f"### {L(h.q, lang)}\n\n{t('hunt_how', lang, commit=pin['commit'][:12])}",
                      color=0x10B981)
    e.add_field(name="git", value=f"```bash\ngit clone https://github.com/{pin['repo']}.git && cd vllm\n"
                                  f"git checkout {pin['commit'][:12]}\n```", inline=False)
    return e


def hunt_view(h: Hunt, lang: str) -> discord.ui.View:
    v = discord.ui.View(timeout=None)
    v.add_item(HuntButton(h.id, "answer", label=t("btn_submit", lang)))
    v.add_item(HuntButton(h.id, "hint", label=t("btn_hint", lang)))
    return v


class HuntModal(discord.ui.Modal):
    def __init__(self, hunt: Hunt, lang: str):
        super().__init__(title=t("hunt_modal", lang, id=hunt.id))
        self.hunt, self.lang = hunt, lang
        self.answer = discord.ui.TextInput(label=t("hunt_label", lang), max_length=200)
        self.add_item(self.answer)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        bot = bot_of(interaction)
        h, lang = self.hunt, self.lang
        if check_hunt(str(self.answer.value), h.answers):
            first = await bot.store.mark(interaction.user.id, "hunt", h.id)
            lines = [t("hunt_right", lang, xp=h.xp) if first else t("hunt_right_again", lang), L(h.explain, lang)]
            entry = bot.content.code_entry(h.code)
            if entry:
                lines.append(f"🔗 {bot.content.permalink(entry)}")
            if first:
                lines += await bot.reward(interaction, h.xp, f"hunt:{h.id}")
            solved = len(await bot.store.items(interaction.user.id, "hunt"))
            lines.append(t("hunt_progress", lang, n=solved, total=len(bot.content.hunts)))
        else:
            lines = [t("hunt_wrong", lang)]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)


class HuntButton(discord.ui.DynamicItem[discord.ui.Button], template=r"hunt:(?P<id>H\d+):(?P<act>answer|hint)"):
    def __init__(self, hunt_id: str, act: str, label: str | None = None):
        style = discord.ButtonStyle.success if act == "answer" else discord.ButtonStyle.secondary
        super().__init__(discord.ui.Button(label=label or act, emoji="✍️" if act == "answer" else "💡", style=style,
                                           custom_id=f"hunt:{hunt_id}:{act}"))
        self.hunt_id, self.act = hunt_id, act

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["id"], match["act"])

    async def callback(self, interaction: discord.Interaction) -> None:
        bot = bot_of(interaction)
        lang = await lang_of(interaction)
        h = bot.content.hunt(self.hunt_id)
        if h is None:
            return await interaction.response.send_message(t("not_found", lang, what=self.hunt_id), ephemeral=True)
        if self.act == "hint":
            return await interaction.response.send_message(f"💡 {L(h.hint, lang)}", ephemeral=True)
        await interaction.response.send_modal(HuntModal(h, lang))


# =========================================================================== labs
def lab_step_embed(bot: "AcademyBot", lab: Lab, lang: str, index: int) -> discord.Embed:
    steps = lab.steps[lang] or lab.steps["en"]
    step = steps[index]
    desc = step.body
    if step.code:
        desc += f"\n```bash\n{clip(step.code, 1500)}\n```"
    e = discord.Embed(title=clip(t("lab_title", lang, id=lab.id, title=L(lab.title, lang)), 256),
                      description=clip(f"### {index + 1}. {step.title}\n{desc}", 4000), color=0x8B5CF6)
    if step.checkpoint:
        e.add_field(name=t("lab_checkpoint", lang), value=clip(step.checkpoint, 1024), inline=False)
    e.set_footer(text=f"{t('lab_step', lang, n=index + 1, total=len(steps))}  {progress_bar((index + 1) / len(steps), 12)}")
    return e


class LabView(discord.ui.View):
    def __init__(self, bot: "AcademyBot", lab: Lab, lang: str, owner_id: int, index: int = 0):
        super().__init__(timeout=1800)
        self.bot, self.lab, self.lang, self.owner_id, self.index = bot, lab, lang, owner_id, index
        self.total = len(lab.steps[lang] or lab.steps["en"])
        self.prev_btn = discord.ui.Button(label=t("btn_prev", lang), emoji="◀️", style=discord.ButtonStyle.secondary)
        self.next_btn = discord.ui.Button(label=t("btn_fwd", lang), emoji="▶️", style=discord.ButtonStyle.primary)
        self.prev_btn.callback = self._prev
        self.next_btn.callback = self._next
        self.add_item(self.prev_btn)
        self.add_item(self.next_btn)
        self.add_item(LabDoneButton(lab.id, label=t("lab_done_btn", lang)))
        self.add_item(discord.ui.Button(label=t("open_github", lang), emoji="📄",
                                        url=bot.settings.repo_link(L(lab.path, lang))))
        self._sync()

    def _sync(self) -> None:
        self.prev_btn.disabled = self.index == 0
        self.next_btn.disabled = self.index >= self.total - 1

    async def _move(self, interaction: discord.Interaction, delta: int) -> None:
        self.index = max(0, min(self.total - 1, self.index + delta))
        self._sync()
        await interaction.response.edit_message(embed=lab_step_embed(self.bot, self.lab, self.lang, self.index), view=self)

    async def _prev(self, interaction: discord.Interaction) -> None:
        await self._move(interaction, -1)

    async def _next(self, interaction: discord.Interaction) -> None:
        await self._move(interaction, +1)


class LabDoneButton(discord.ui.DynamicItem[discord.ui.Button], template=r"labdone:(?P<id>Q\d+)"):
    def __init__(self, lab_id: str, label: str | None = None):
        super().__init__(discord.ui.Button(label=label or "Done", emoji="🏁", style=discord.ButtonStyle.success,
                                           custom_id=f"labdone:{lab_id}"))
        self.lab_id = lab_id

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["id"])

    async def callback(self, interaction: discord.Interaction) -> None:
        bot = bot_of(interaction)
        lang = await lang_of(interaction)
        lab = bot.content.lab(self.lab_id)
        if lab is None:
            return await interaction.response.send_message(t("not_found", lang, what=self.lab_id), ephemeral=True)
        if not await bot.store.mark(interaction.user.id, "lab", lab.id):
            return await interaction.response.send_message(t("lab_already", lang), ephemeral=True)
        lines = [t("lab_done", lang, id=lab.id, xp=lab.xp)] + await bot.reward(interaction, lab.xp, f"lab:{lab.id}")
        await interaction.response.send_message("\n".join(lines), ephemeral=True)


# =========================================================================== start / language
class LangButton(discord.ui.DynamicItem[discord.ui.Button], template=r"setlang:(?P<lang>en|zh)"):
    def __init__(self, lang: str):
        super().__init__(discord.ui.Button(label="English" if lang == "en" else "繁體中文",
                                           emoji="🇬🇧" if lang == "en" else "🇹🇼",
                                           style=discord.ButtonStyle.secondary, custom_id=f"setlang:{lang}"))
        self.lang = lang

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["lang"])

    async def callback(self, interaction: discord.Interaction) -> None:
        await bot_of(interaction).set_lang(interaction.user.id, self.lang)
        await interaction.response.send_message(t("lang_set", self.lang) + "\n" + t("start_howto", self.lang),
                                                ephemeral=True)


class RouteSelect(discord.ui.DynamicItem[discord.ui.Select], template=r"route:select"):
    def __init__(self, routes: list[dict] | None = None, lang: str = "en"):
        options = [discord.SelectOption(label=f"{r['title']['en']} · {r['title']['zh']}", value=r["id"], emoji=r["emoji"],
                                        description=clip(L(r["blurb"], lang), 100)) for r in (routes or [])]
        super().__init__(discord.ui.Select(placeholder=f"{t('start_route_placeholder', 'en')} / {t('start_route_placeholder', 'zh')}",
                                           options=options or [discord.SelectOption(label="-", value="-")],
                                           custom_id="route:select"))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        inst = cls()
        inst.item = item
        return inst

    async def callback(self, interaction: discord.Interaction) -> None:
        bot = bot_of(interaction)
        lang = await lang_of(interaction)
        route_id = self.item.values[0]
        route = bot.content.route(route_id)
        if route is None:
            return await interaction.response.send_message(t("not_found", lang, what=route_id), ephemeral=True)
        await bot.store.set_route(interaction.user.id, route_id)
        done = await bot.store.items(interaction.user.id, "episode")
        nxt = next((e for e in route["path"] if e not in done), route["path"][0])
        ep = bot.content.episode(nxt)
        path = " → ".join(f"~~{e}~~" if e in done else e for e in route["path"])
        msg = t("start_route_set", lang, route=f"{route['emoji']} {L(route['title'], lang)}",
                ep=f"{ep.id} · {L(ep.title, lang)}") + f"\n{path}"
        view = discord.ui.View(timeout=None)
        view.add_item(OpenEpisodeButton(ep.id, label=t("start_go", lang)))
        await interaction.response.send_message(msg, view=view, ephemeral=True)


def start_embed(bot: "AcademyBot") -> discord.Embed:
    e = discord.Embed(title=f"{t('start_title', 'zh')}  ·  {t('start_title', 'en')}",
                      description=f"{t('start_body', 'zh')}\n\n{t('start_body', 'en')}", color=AMBER)
    for s in bot.content.seasons:
        eps = bot.content.season_episodes(s.id)
        e.add_field(name=f"{s.emoji} {s.id} · {s.title['zh']} / {s.title['en']}",
                    value=f"{eps[0].id}–{eps[-1].id} · {clip(s.tagline['zh'], 60)}", inline=False)
    e.set_image(url="attachment://banner.png")
    e.set_footer(text=f"{t('start_howto', 'en')}")
    return e


def start_view(bot: "AcademyBot") -> discord.ui.View:
    v = discord.ui.View(timeout=None)
    v.add_item(RouteSelect(bot.content.routes, "en"))
    v.add_item(LangButton("zh"))
    v.add_item(LangButton("en"))
    v.add_item(OpenEpisodeButton("E01", label="E01"))
    return v


def banner_file(bot: "AcademyBot") -> discord.File:
    path = bot.settings.assets_dir / "cards" / "banner.png"
    data = path.read_bytes() if path.exists() else bot.cover_cache.setdefault("banner", cards.banner())
    return discord.File(io.BytesIO(data), filename="banner.png")


# =========================================================================== hot takes
HOT = 0xEF4444


async def take_state(bot: "AcademyBot", take: dict) -> tuple[int, int, str | None, str]:
    from .drops import take_verdict
    agree, disagree = await bot.store.tally(take["id"])
    override = await bot.store.setting(0, f"verdict:{take['id']}")
    verdict, note = take_verdict(take, override)
    return agree, disagree, verdict, note


def hottake_embed(bot: "AcademyBot", take: dict, lang: str, *, verdict: str | None = None, note: str = "") -> discord.Embed:
    ep = bot.content.episode(take.get("episode", ""))
    disclaimer = L(bot.content.hottakes.get("disclaimer", {}), lang) or ""
    desc = (f"## {take['emoji']} {L(take['claim'], lang)}\n*{disclaimer}*\n\n"
            f"**{t('ht_evidence', lang)}**\n{L(take['evidence'], lang)}\n\n"
            f"**{t('ht_wrong_if', lang)}**\n{L(take['wrong_if'], lang)}\n\n"
            + t("ht_meta", lang, conf=take["confidence"], date=take["judge_on"],
                ep=f"{ep.id} · {L(ep.title, lang)}" if ep else "-"))
    if verdict:
        desc += "\n\n" + t("ht_verdict", lang, verdict=t(f"verdict_{verdict}", lang), note=note)
    else:
        desc += "\n" + t("ht_pending", lang)
    e = discord.Embed(title=t("ht_title", lang, id=take["id"]), description=clip(desc, 4000), color=HOT,
                      url=take.get("source"))
    e.set_image(url=f"attachment://{take['id']}.png")
    e.set_footer(text=f"{t('source', lang)}: {clip(take.get('source', ''), 120)}")
    return e


def hottake_file(take: dict, agree: int, disagree: int, verdict: str | None) -> discord.File:
    data = cards.hottake_card(take_id=take["id"], claim_en=take["claim"]["en"], claim_zh=take["claim"]["zh"],
                              confidence=int(take["confidence"]), judge_on=str(take["judge_on"]),
                              agree=agree, disagree=disagree, verdict=verdict)
    return discord.File(io.BytesIO(data), filename=f"{take['id']}.png")


def hottake_view(take: dict, lang: str) -> discord.ui.View:
    v = discord.ui.View(timeout=None)
    v.add_item(HotTakeVoteButton(take["id"], "y", label=f"{t('ht_agree', 'zh')} · {t('ht_agree', 'en')}"))
    v.add_item(HotTakeVoteButton(take["id"], "n", label=f"{t('ht_disagree', 'zh')} · {t('ht_disagree', 'en')}"))
    if take.get("source"):
        v.add_item(discord.ui.Button(label=t("source", lang), emoji="📎", url=take["source"]))
    return v


async def send_hottake(interaction: discord.Interaction, take: dict, *, ephemeral: bool) -> None:
    bot = bot_of(interaction)
    lang = await lang_of(interaction)
    agree, disagree, verdict, note = await take_state(bot, take)
    kwargs = dict(embed=hottake_embed(bot, take, lang, verdict=verdict, note=note), view=hottake_view(take, lang),
                  file=hottake_file(take, agree, disagree, verdict), ephemeral=ephemeral)
    if interaction.response.is_done():
        await interaction.followup.send(**kwargs)
    else:
        await interaction.response.send_message(**kwargs)


class HotTakeVoteButton(discord.ui.DynamicItem[discord.ui.Button], template=r"ht:(?P<id>ht-\d+):(?P<v>[yn])"):
    def __init__(self, take_id: str, v: str, label: str | None = None):
        super().__init__(discord.ui.Button(label=label or v, emoji="🔥" if v == "y" else "🧊",
                                           style=discord.ButtonStyle.danger if v == "y" else discord.ButtonStyle.primary,
                                           custom_id=f"ht:{take_id}:{v}"))
        self.take_id, self.v = take_id, v

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["id"], match["v"])

    async def callback(self, interaction: discord.Interaction) -> None:
        bot = bot_of(interaction)
        lang = await lang_of(interaction)
        take = bot.content.hottake(self.take_id)
        if take is None:
            return await interaction.response.send_message(t("not_found", lang, what=self.take_id), ephemeral=True)
        first = await bot.store.vote(interaction.user.id, take["id"], self.v == "y")
        agree, disagree = await bot.store.tally(take["id"])
        choice = t("ht_agree" if self.v == "y" else "ht_disagree", lang)
        lines = [t("ht_voted" if first else "ht_changed", lang, choice=choice, agree=agree, disagree=disagree)]
        if first:
            lines += await bot.reward(interaction, XP["hottake_vote"], f"hottake:{take['id']}")
        await interaction.response.send_message("\n".join(lines), ephemeral=True)


DYNAMIC_ITEMS = (OpenEpisodeButton, CompleteButton, QuizButton, EpisodeQuizButton, InterviewRevealButton,
                 HuntButton, LabDoneButton, LangButton, RouteSelect, HotTakeVoteButton)


def strip_md_links(text: str) -> str:
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
