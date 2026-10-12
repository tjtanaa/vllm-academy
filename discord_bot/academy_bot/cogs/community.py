"""/community /events /career /gfi — the people, the events and the jobs."""
from __future__ import annotations

import logging

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from ..i18n import L, t
from ..ui import OpenEpisodeButton, clip, lang_of

log = logging.getLogger("academy")
COMMUNITY = 0xF59E0B
STATUS_EMOJI = {"past": "✅", "upcoming": "🗓️", "announced": "📣"}


def community_embed(bot, lang: str) -> discord.Embed:
    com = bot.content.community
    e = discord.Embed(title=t("community_title", lang), color=COMMUNITY,
                      description="\n".join(f"{x['emoji']} [{L(x['name'], lang)}]({x['url']})" for x in com["links"]))
    upcoming = [ev for ev in com.get("events", []) if ev.get("status") != "past"]
    if upcoming:
        e.add_field(name=t("community_events", lang), value=clip("\n".join(
            f"{STATUS_EMOJI.get(ev['status'], '📅')} **{ev['date']}** · [{L(ev['title'], lang)}]({ev['url']})"
            for ev in upcoming), 1024), inline=False)
    return e


def events_embed(bot, lang: str) -> discord.Embed:
    events = sorted(bot.content.community.get("events", []), key=lambda ev: ev["date"], reverse=True)
    e = discord.Embed(title=t("community_events", lang), color=COMMUNITY)
    if not events:
        e.description = t("events_none", lang)
    for ev in events[:10]:
        status = t(f"event_{ev['status']}", lang) if ev.get("status") in ("past", "upcoming", "announced") else ""
        e.add_field(name=clip(f"{STATUS_EMOJI.get(ev.get('status'), '📅')} {ev['date']} · {L(ev['title'], lang)}", 256),
                    value=clip(f"*{status}* · {L(ev['where'], lang)}\n{L(ev['blurb'], lang)}\n[link]({ev['url']})", 1024),
                    inline=False)
    return e


def career_embed(bot, cr: dict, lang: str) -> discord.Embed:
    e = discord.Embed(title=f"{cr['emoji']} {L(cr['title'], lang)}", description=f"*{L(cr['pitch'], lang)}*",
                      color=0x22C55E)
    e.add_field(name=t("career_skills", lang), value=clip("\n".join(f"• {s}" for s in L(cr["skills"], lang)), 1024),
                inline=True)
    eps = [bot.content.episode(x) for x in cr["episodes"]]
    e.add_field(name=t("career_eps", lang),
                value=clip("\n".join(f"`{ep.id}` {L(ep.title, lang)}" for ep in eps if ep), 1024), inline=True)
    e.add_field(name=t("career_proof", lang), value=clip("\n".join(f"🏗️ {p}" for p in L(cr["proof"], lang)), 1024),
                inline=False)
    return e


class CareerView(discord.ui.View):
    def __init__(self, bot, lang: str):
        super().__init__(timeout=900)
        self.bot, self.lang = bot, lang
        self.sel = discord.ui.Select(placeholder=t("career_title", lang), options=[
            discord.SelectOption(label=clip(L(cr["title"], lang), 100), value=cr["id"], emoji=cr["emoji"],
                                 description=clip(L(cr["pitch"], lang), 100)) for cr in bot.content.careers])
        self.sel.callback = self._pick
        self.add_item(self.sel)

    async def _pick(self, interaction: discord.Interaction) -> None:
        cr = next(c for c in self.bot.content.careers if c["id"] == self.sel.values[0])
        view = CareerView(self.bot, self.lang)
        first = cr["episodes"][0] if cr["episodes"] else None
        if first:
            view.add_item(OpenEpisodeButton(first, label=f"▶ {first}"))
        await interaction.response.edit_message(embed=career_embed(self.bot, cr, self.lang), view=view)


class Community(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="community", description="vLLM links, Taiwan community and events · 社群連結")
    async def community(self, interaction: discord.Interaction, private: bool = False) -> None:
        lang = await lang_of(interaction)
        await interaction.response.send_message(embed=community_embed(self.bot, lang), ephemeral=private)

    @app_commands.command(name="events", description="Meetups, talks and BoFs (Taiwan first) · 活動")
    async def events(self, interaction: discord.Interaction, private: bool = False) -> None:
        lang = await lang_of(interaction)
        await interaction.response.send_message(embed=events_embed(self.bot, lang), ephemeral=private)

    @app_commands.command(name="career", description="Career paths vLLM skills lead to, and proof projects · 職涯路線")
    async def career(self, interaction: discord.Interaction, private: bool = True) -> None:
        lang = await lang_of(interaction)
        e = discord.Embed(title=t("career_title", lang), color=0x22C55E, description="\n".join(
            f"{cr['emoji']} **{L(cr['title'], lang)}**: {L(cr['pitch'], lang)}" for cr in self.bot.content.careers))
        await interaction.response.send_message(embed=e, view=CareerView(self.bot, lang), ephemeral=private)

    @app_commands.command(name="gfi", description="Open 'good first issue's in vLLM, live from GitHub · 新手 issue")
    async def gfi(self, interaction: discord.Interaction, private: bool = True) -> None:
        lang = await lang_of(interaction)
        await interaction.response.defer(ephemeral=private, thinking=True)
        try:
            issues = await self.bot.github.good_first_issues()
        except (aiohttp.ClientError, TimeoutError) as exc:
            log.info("gfi failed: %s", exc)
            return await interaction.followup.send(t("github_down", lang), ephemeral=True)
        e = discord.Embed(title=t("gfi_title", lang), color=0x22C55E, url=(
            "https://github.com/vllm-project/vllm/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22"))
        if not issues:
            e.description = t("gfi_none", lang)
        else:
            e.description = "\n".join(f"[#{i['number']}]({i['url']}) {clip(i['title'], 90)} · 💬 {i['comments']}"
                                      for i in issues)
        e.add_field(name="⚠️", value=t("gfi_tip", lang), inline=False)
        view = discord.ui.View(timeout=None)
        view.add_item(OpenEpisodeButton("E23", label="E23"))
        await interaction.followup.send(embed=e, view=view, ephemeral=private)


async def setup(bot) -> None:
    await bot.add_cog(Community(bot))
