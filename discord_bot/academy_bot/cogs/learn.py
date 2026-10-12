"""/start /lang /path /episode /lab — the learning flow."""
from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from ..content import normalize_episode_id
from ..i18n import L, t
from ..progress import progress_bar
from ..ui import (LabView, banner_file, clip, lab_step_embed, lang_of, send_episode, start_embed, start_view)


class PathView(discord.ui.View):
    def __init__(self, bot, lang: str, done: set[str]):
        super().__init__(timeout=900)
        self.bot, self.lang, self.done = bot, lang, done
        c = bot.content
        self.season_select = discord.ui.Select(
            placeholder=t("path_select_season", lang),
            options=[discord.SelectOption(label=clip(f"{s.id} · {L(s.title, lang)}", 100), value=s.id, emoji=s.emoji,
                                          description=clip(L(s.tagline, lang), 100)) for s in c.seasons])
        self.season_select.callback = self._season
        self.add_item(self.season_select)

    async def _season(self, interaction: discord.Interaction) -> None:
        sid = self.season_select.values[0]
        c = self.bot.content
        s = c.season(sid)
        eps = c.season_episodes(sid)
        lines = [f"{'✅' if e.id in self.done else '⬜'} **{e.id}** · {L(e.title, self.lang)} · "
                 f"{t('minutes', self.lang, n=e.minutes)}" for e in eps]
        emb = discord.Embed(title=f"{s.emoji} {s.id} · {L(s.title, self.lang)}",
                            description=f"*{L(s.tagline, self.lang)}*\n\n" + "\n".join(lines), color=s.color)
        view = discord.ui.View(timeout=900)
        sel = discord.ui.Select(placeholder=t("path_select_episode", self.lang),
                                options=[discord.SelectOption(label=clip(f"{e.id} · {L(e.title, self.lang)}", 100),
                                                              value=e.id, emoji="✅" if e.id in self.done else "▶️")
                                         for e in eps])

        async def open_ep(inter: discord.Interaction) -> None:
            ep = c.episode(sel.values[0])
            await send_episode(inter, ep, ephemeral=True)

        sel.callback = open_ep
        view.add_item(sel)
        await interaction.response.send_message(embed=emb, view=view, ephemeral=True)


class Learn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------------------------------------------------ autocomplete
    async def episode_ac(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        lang = await lang_of(interaction)
        cur = current.lower().strip()
        out = []
        for e in self.bot.content.episodes:
            label = f"{e.id} · {L(e.title, lang)}"
            if not cur or cur in label.lower() or cur in e.title["en"].lower() or cur in e.title["zh"]:
                out.append(app_commands.Choice(name=clip(label, 100), value=e.id))
        return out[:25]

    async def lab_ac(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        lang = await lang_of(interaction)
        cur = current.lower()
        return [app_commands.Choice(name=clip(f"{lab.id} · {L(lab.title, lang)}", 100), value=lab.id)
                for lab in self.bot.content.labs if cur in f"{lab.id} {L(lab.title, lang)}".lower()][:25]

    # ------------------------------------------------------------------ commands
    @app_commands.command(name="start", description="Start vLLM Academy: pick a route and language · 開始學習")
    async def start(self, interaction: discord.Interaction) -> None:
        await self.bot.store.user(interaction.user.id)
        await interaction.response.send_message(embed=start_embed(self.bot), view=start_view(self.bot),
                                                file=banner_file(self.bot))

    @app_commands.command(name="lang", description="Set your language · 設定語言")
    @app_commands.describe(language="English or 繁體中文")
    @app_commands.choices(language=[app_commands.Choice(name="English", value="en"),
                                    app_commands.Choice(name="繁體中文", value="zh")])
    async def lang(self, interaction: discord.Interaction, language: app_commands.Choice[str]) -> None:
        await self.bot.set_lang(interaction.user.id, language.value)
        await interaction.response.send_message(t("lang_set", language.value), ephemeral=True)

    @app_commands.command(name="path", description="Your learning map and progress · 學習地圖與進度")
    async def path(self, interaction: discord.Interaction) -> None:
        lang = await lang_of(interaction)
        c = self.bot.content
        user = await self.bot.store.user(interaction.user.id)
        done = await self.bot.store.items(interaction.user.id, "episode")
        lines = []
        for s in c.seasons:
            eps = [e.id for e in c.season_episodes(s.id)]
            n = len([e for e in eps if e in done])
            lines.append(f"{s.emoji} **{s.id} · {L(s.title, lang)}**\n`{progress_bar(n / len(eps), 12)}` {n}/{len(eps)}")
        route = c.route(user.route) if user.route else None
        order = route["path"] if route else [e.id for e in c.episodes]
        nxt = next((e for e in order if e not in done), None)
        head = (t("path_route", lang, route=f"{route['emoji']} {L(route['title'], lang)}",
                  ep=f"{nxt} · {L(c.episode(nxt).title, lang)}" if nxt else "🏁")
                if route else t("no_route", lang))
        total = len(c.episodes)
        emb = discord.Embed(title=t("path_title", lang),
                            description=f"{head}\n\n`{progress_bar(len(done) / total, 20)}` **{len(done)}/{total}**\n\n"
                                        + "\n".join(lines), color=0xFDBA34)
        emb.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=emb, view=PathView(self.bot, lang, done), ephemeral=True)

    @app_commands.command(name="episode", description="Open an episode (E01–E28) · 打開一集")
    @app_commands.describe(episode="e.g. E08 or 'paged'", private="Only you can see it · 只有你看得到")
    @app_commands.autocomplete(episode=episode_ac)
    async def episode(self, interaction: discord.Interaction, episode: str | None = None,
                      private: bool = False) -> None:
        c = self.bot.content
        if episode:
            ep = c.episode(normalize_episode_id(episode))
        else:
            done = await self.bot.store.items(interaction.user.id, "episode")
            user = await self.bot.store.user(interaction.user.id)
            route = c.route(user.route) if user.route else None
            order = route["path"] if route else [e.id for e in c.episodes]
            ep = c.episode(next((e for e in order if e not in done), order[0]))
        if ep is None:
            lang = await lang_of(interaction)
            return await interaction.response.send_message(t("not_found", lang, what=episode), ephemeral=True)
        await send_episode(interaction, ep, ephemeral=private)

    @app_commands.command(name="lab", description="Step-by-step hands-on labs · 一步一步的實作關卡")
    @app_commands.describe(lab="Q1–Q9", private="Only you can see it · 只有你看得到")
    @app_commands.autocomplete(lab=lab_ac)
    async def lab(self, interaction: discord.Interaction, lab: str | None = None, private: bool = True) -> None:
        lang = await lang_of(interaction)
        c = self.bot.content
        if not lab:
            done = await self.bot.store.items(interaction.user.id, "lab")
            lines = []
            for item in c.labs:
                steps = len(item.steps[lang] or item.steps["en"])
                lines.append(f"{'✅' if item.id in done else '🧪'} **{item.id}** · {L(item.title, lang)} · {steps} steps")
            emb = discord.Embed(title=t("lab_list", lang), description="\n".join(lines) + "\n\n`/lab Q2`",
                                color=0x8B5CF6)
            return await interaction.response.send_message(embed=emb, ephemeral=private)
        item = c.lab(lab)
        if item is None:
            return await interaction.response.send_message(t("not_found", lang, what=lab), ephemeral=True)
        await interaction.response.send_message(embed=lab_step_embed(self.bot, item, lang, 0),
                                                view=LabView(self.bot, item, lang, interaction.user.id),
                                                ephemeral=private)


async def setup(bot) -> None:
    await bot.add_cog(Learn(bot))
