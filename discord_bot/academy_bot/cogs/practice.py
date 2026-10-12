"""/quiz /interview /mock /hunt — practice and interview prep."""
from __future__ import annotations

import random

import discord
from discord import app_commands
from discord.ext import commands

from ..content import InterviewQ, normalize_episode_id
from ..i18n import L, t
from ..progress import mock_xp, progress_bar
from ..ui import (LEVEL_COLORS, clip, hunt_embed, hunt_view, interview_embed, interview_view, lang_of, pick_quiz,
                  send_quiz)

LEVEL_CHOICES = [app_commands.Choice(name="Junior · 初階", value="junior"),
                 app_commands.Choice(name="Mid · 中階", value="mid"),
                 app_commands.Choice(name="Senior · 資深", value="senior")]
KIND_CHOICES = [app_commands.Choice(name=n, value=v) for n, v in [
    ("Concept · 觀念", "concept"), ("System design · 系統設計", "design"), ("Coding · 程式", "coding"),
    ("Debugging · 除錯", "debug"), ("Behavioral · 行為面試", "behavioral")]]


def pick_mock_set(pool: list[InterviewQ], level: str | None, n: int = 5, rng: random.Random | None = None) -> list[InterviewQ]:
    """A balanced mock: try to cover different kinds; prefer the requested level."""
    rng = rng or random.Random()
    cands = [q for q in pool if level is None or q.level == level] or list(pool)
    rng.shuffle(cands)
    chosen: list[InterviewQ] = []
    kinds_seen: set[str] = set()
    for q in cands:  # first pass: one per kind
        if q.kind not in kinds_seen:
            chosen.append(q)
            kinds_seen.add(q.kind)
        if len(chosen) == n:
            return chosen
    for q in cands:  # fill the rest
        if q not in chosen:
            chosen.append(q)
        if len(chosen) == n:
            break
    return chosen


class MockSession(discord.ui.View):
    SCORES = (2, 1, 0)

    def __init__(self, cog: "Practice", user_id: int, lang: str, questions: list[InterviewQ]):
        super().__init__(timeout=3600)
        self.cog, self.user_id, self.lang, self.qs = cog, user_id, lang, questions
        self.i, self.scores, self.revealed = 0, [], False
        self._build()

    # ---- rendering ----
    def embed(self) -> discord.Embed:
        q = self.qs[self.i]
        lang = self.lang
        e = discord.Embed(title=t("mock_title", lang, n=self.i + 1, total=len(self.qs)),
                          description=f"`{t(f'iv_level_{q.level}', lang)} · {q.kind}`\n### {L(q.q, lang)}\n\n{t('iv_prompt', lang)}",
                          color=LEVEL_COLORS.get(q.level, 0xFDBA34))
        if self.revealed:
            e.add_field(name=t("iv_points", lang), value=clip("\n".join(f"• {x}" for x in L(q.points, lang)), 1024),
                        inline=False)
            e.add_field(name=t("iv_followups", lang), value=clip("\n".join(f"• {x}" for x in L(q.followups, lang)), 1024),
                        inline=False)
            e.add_field(name=t("mock_rate", lang), value="🟢 2 · 🟡 1 · 🔴 0", inline=False)
        e.set_footer(text=progress_bar(self.i / len(self.qs), 10) + f"  {self.i}/{len(self.qs)}")
        return e

    def _build(self) -> None:
        self.clear_items()
        if not self.revealed:
            b = discord.ui.Button(label=t("mock_reveal", self.lang), emoji="🔑", style=discord.ButtonStyle.primary)
            b.callback = self._reveal
            self.add_item(b)
        else:
            for label_key, emoji, score, style in (("mock_nailed", "🟢", 2, discord.ButtonStyle.success),
                                                   ("mock_partial", "🟡", 1, discord.ButtonStyle.secondary),
                                                   ("mock_missed", "🔴", 0, discord.ButtonStyle.danger)):
                b = discord.ui.Button(label=t(label_key, self.lang), emoji=emoji, style=style)
                b.callback = self._rater(score)
                self.add_item(b)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def _reveal(self, interaction: discord.Interaction) -> None:
        self.revealed = True
        self._build()
        await interaction.response.edit_message(embed=self.embed(), view=self)

    def _rater(self, score: int):
        async def cb(interaction: discord.Interaction) -> None:
            self.scores.append(score)
            self.i += 1
            self.revealed = False
            if self.i >= len(self.qs):
                await self._finish(interaction)
            else:
                self._build()
                await interaction.response.edit_message(embed=self.embed(), view=self)
        return cb

    async def _finish(self, interaction: discord.Interaction) -> None:
        bot, lang = self.cog.bot, self.lang
        raw, mx = sum(self.scores), 2 * len(self.qs)
        pct = round(100 * raw / mx)
        xp = mock_xp(pct)
        await bot.store.set_best_mock(self.user_id, pct)
        lines = await bot.reward(interaction, xp, "mock")
        missed = [q for q, s in zip(self.qs, self.scores) if s < 2]
        e = discord.Embed(title=t("mock_done_title", lang),
                          description=t("mock_done", lang, score=pct, raw=raw, max=mx, xp=xp) + "\n\n" + "\n".join(lines),
                          color=0x34D399 if pct >= 80 else 0xFBBF24 if pct >= 50 else 0xF87171)
        e.add_field(name="📊", value=f"`{progress_bar(pct / 100, 20)}` {pct}%", inline=False)
        if missed:
            e.add_field(name="📚", value=clip("\n".join(f"• {L(q.q, lang)} → `{q.episode}`" for q in missed), 1024),
                        inline=False)
        self.clear_items()
        self.stop()
        self.cog.sessions.pop(self.user_id, None)
        await interaction.response.edit_message(embed=e, view=None)

    async def on_timeout(self) -> None:
        self.cog.sessions.pop(self.user_id, None)


class Practice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sessions: dict[int, MockSession] = {}

    async def episode_ac(self, interaction: discord.Interaction, current: str):
        lang = await lang_of(interaction)
        cur = current.lower()
        return [app_commands.Choice(name=clip(f"{e.id} · {L(e.title, lang)}", 100), value=e.id)
                for e in self.bot.content.episodes if cur in f"{e.id} {L(e.title, lang)}".lower()][:25]

    async def hunt_ac(self, interaction: discord.Interaction, current: str):
        lang = await lang_of(interaction)
        cur = current.lower()
        return [app_commands.Choice(name=clip(f"{h.id} · {L(h.q, lang)}", 100), value=h.id)
                for h in self.bot.content.hunts if cur in f"{h.id} {L(h.q, lang)}".lower()][:25]

    @app_commands.command(name="quiz", description="A quick multiple-choice question (+XP) · 隨堂測驗")
    @app_commands.describe(episode="Limit to one episode", private="Only you can see it · 只有你看得到")
    @app_commands.autocomplete(episode=episode_ac)
    async def quiz(self, interaction: discord.Interaction, episode: str | None = None, private: bool = False) -> None:
        q = await pick_quiz(self.bot, interaction.user.id, normalize_episode_id(episode) if episode else None)
        if q is None:
            return await interaction.response.send_message(t("quiz_none", await lang_of(interaction)), ephemeral=True)
        await send_quiz(interaction, q, ephemeral=private)

    @app_commands.command(name="interview", description="A real inference-engineer interview question · 面試題")
    @app_commands.describe(level="Junior / Mid / Senior", kind="Question type", private="Only you can see it")
    @app_commands.choices(level=LEVEL_CHOICES, kind=KIND_CHOICES)
    async def interview(self, interaction: discord.Interaction, level: app_commands.Choice[str] | None = None,
                        kind: app_commands.Choice[str] | None = None, private: bool = False) -> None:
        lang = await lang_of(interaction)
        pool = [q for q in self.bot.content.interview
                if (level is None or q.level == level.value) and (kind is None or q.kind == kind.value)]
        if not pool:
            return await interaction.response.send_message(t("quiz_none", lang), ephemeral=True)
        iv = random.choice(pool)
        await interaction.response.send_message(embed=interview_embed(self.bot, iv, lang),
                                                view=interview_view(iv, lang), ephemeral=private)

    @app_commands.command(name="mock", description="5-question mock interview, scored (+XP) · 模擬面試")
    @app_commands.describe(level="Junior / Mid / Senior (mixed if empty)")
    @app_commands.choices(level=LEVEL_CHOICES)
    async def mock(self, interaction: discord.Interaction, level: app_commands.Choice[str] | None = None) -> None:
        lang = await lang_of(interaction)
        if interaction.user.id in self.sessions:
            return await interaction.response.send_message(t("mock_busy", lang), ephemeral=True)
        qs = pick_mock_set(self.bot.content.interview, level.value if level else None)
        session = MockSession(self, interaction.user.id, lang, qs)
        self.sessions[interaction.user.id] = session
        await interaction.response.send_message(embed=session.embed(), view=session, ephemeral=True)

    @app_commands.command(name="hunt", description="Codebase treasure hunt in real vLLM source (+XP) · 原始碼尋寶")
    @app_commands.describe(hunt="H1–H14 (next unsolved if empty)", private="Only you can see it")
    @app_commands.autocomplete(hunt=hunt_ac)
    async def hunt(self, interaction: discord.Interaction, hunt: str | None = None, private: bool = False) -> None:
        lang = await lang_of(interaction)
        solved = await self.bot.store.items(interaction.user.id, "hunt")
        if hunt:
            h = self.bot.content.hunt(hunt)
        else:
            h = next((x for x in self.bot.content.hunts if x.id not in solved), self.bot.content.hunts[0])
        if h is None:
            return await interaction.response.send_message(t("not_found", lang, what=hunt), ephemeral=True)
        emb = hunt_embed(self.bot, h, lang, solved=h.id in solved)
        emb.set_footer(text=t("hunt_progress", lang, n=len(solved), total=len(self.bot.content.hunts)))
        await interaction.response.send_message(embed=emb, view=hunt_view(h, lang), ephemeral=private)


async def setup(bot) -> None:
    await bot.add_cog(Practice(bot))
