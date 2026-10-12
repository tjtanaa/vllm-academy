"""/code /trace /glossary /trends /hottake — explore the vLLM codebase and the ecosystem."""
from __future__ import annotations

import random

import discord
from discord import app_commands
from discord.ext import commands

from ..content import CodeEntry
from ..i18n import L, t
from ..ui import OpenEpisodeButton, clip, lang_of, send_hottake

CODE_COLOR = 0x10B981
TREND_COLOR = 0x3B82F6


# =========================================================================== code map
def code_embed(bot, entry: CodeEntry, lang: str) -> discord.Embed:
    c = bot.content
    area = next((a for a in c.code_areas if a["id"] == entry.area), {"emoji": "🧭", "title": {"en": entry.area}})
    pin = c.code_pin
    e = discord.Embed(title=clip(f"{area['emoji']} {L(entry.title, lang)}", 256), url=c.permalink(entry),
                      description=f"**{t('code_owns', lang)}**\n{L(entry.owns, lang)}", color=CODE_COLOR)
    e.add_field(name=t("code_where", lang),
                value=f"[`{entry.path}`#L{entry.line}]({c.permalink(entry)})\n`{entry.symbol}`", inline=False)
    e.add_field(name=t("code_try", lang), value=clip(L(entry.try_, lang), 1024), inline=False)
    e.set_footer(text=t("code_pin", lang, short=pin["commit"][:10], date=pin["date"]) + f" · {L(area['title'], lang)}")
    return e


class CodeMapView(discord.ui.View):
    def __init__(self, bot, lang: str):
        super().__init__(timeout=900)
        self.bot, self.lang = bot, lang
        c = bot.content
        self.area = discord.ui.Select(placeholder=t("code_pick_area", lang), options=[
            discord.SelectOption(label=clip(L(a["title"], lang), 100), value=a["id"], emoji=a["emoji"],
                                 description=f"{sum(1 for e in c.code if e.area == a['id'])} components")
            for a in c.code_areas])
        self.area.callback = self._area
        self.add_item(self.area)
        self.entry: discord.ui.Select | None = None

    async def _area(self, interaction: discord.Interaction) -> None:
        aid = self.area.values[0]
        if self.entry is not None:
            self.remove_item(self.entry)
        entries = [e for e in self.bot.content.code if e.area == aid][:25]
        self.entry = discord.ui.Select(placeholder=t("code_pick_entry", self.lang), options=[
            discord.SelectOption(label=clip(L(e.title, self.lang).replace("`", ""), 100), value=e.id,
                                 description=clip(e.path, 100)) for e in entries])
        self.entry.callback = self._entry
        self.add_item(self.entry)
        await interaction.response.edit_message(view=self)

    async def _entry(self, interaction: discord.Interaction) -> None:
        entry = self.bot.content.code_entry(self.entry.values[0])
        await interaction.response.edit_message(embed=code_embed(self.bot, entry, self.lang), view=self)


# =========================================================================== trace
def trace_embed(bot, lang: str, index: int) -> discord.Embed:
    tr = bot.content.trace
    stops = tr["stops"]
    stop = stops[index]
    entry = bot.content.code_entry(stop["code"])
    desc = ""
    if index == 0:
        desc += L(tr["intro"], lang) + "\n\n"
    desc += f"### {stop['n']}. {L(stop['title'], lang)}\n{L(stop['what'], lang)}"
    e = discord.Embed(title=t("trace_title", lang, title=L(tr["title"], lang)), description=clip(desc, 4000),
                      color=CODE_COLOR)
    e.add_field(name=t("trace_carries", lang), value=f"`{L(stop['carries'], lang)}`", inline=False)
    if entry:
        e.add_field(name=t("code_where", lang),
                    value=f"[`{entry.path}`#L{entry.line}]({bot.content.permalink(entry)}) · `{entry.symbol}`",
                    inline=False)
    rail = "".join("●" if i == index else ("━" if i < index else "─") for i in range(len(stops)))
    e.set_footer(text=f"{t('trace_footer', lang, n=index + 1, total=len(stops), process=L(stop['process'], lang))}  {rail}")
    return e


class TraceView(discord.ui.View):
    def __init__(self, bot, lang: str, index: int = 0):
        super().__init__(timeout=1800)
        self.bot, self.lang, self.index = bot, lang, index
        self.total = len(bot.content.trace["stops"])
        self.prev = discord.ui.Button(label=t("btn_prev", lang), emoji="◀️", style=discord.ButtonStyle.secondary)
        self.next = discord.ui.Button(label=t("btn_fwd", lang), emoji="▶️", style=discord.ButtonStyle.primary)
        self.prev.callback, self.next.callback = self._prev, self._next
        self.add_item(self.prev)
        self.add_item(self.next)
        self.code_btn: discord.ui.Button | None = None
        self._sync()

    def _sync(self) -> None:
        self.prev.disabled = self.index == 0
        self.next.disabled = self.index >= self.total - 1
        if self.code_btn is not None:
            self.remove_item(self.code_btn)
        entry = self.bot.content.code_entry(self.bot.content.trace["stops"][self.index]["code"])
        if entry:
            self.code_btn = discord.ui.Button(label=t("btn_code", self.lang), emoji="🔗",
                                              url=self.bot.content.permalink(entry))
            self.add_item(self.code_btn)

    async def _go(self, interaction: discord.Interaction, delta: int) -> None:
        self.index = max(0, min(self.total - 1, self.index + delta))
        self._sync()
        await interaction.response.edit_message(embed=trace_embed(self.bot, self.lang, self.index), view=self)

    async def _prev(self, interaction):
        await self._go(interaction, -1)

    async def _next(self, interaction):
        await self._go(interaction, +1)


# =========================================================================== glossary / trends
def term_embed(bot, g: dict, lang: str) -> discord.Embed:
    primary, other = (g["zh"], g["en"]) if lang == "zh" else (g["en"], g["zh"])
    e = discord.Embed(title=t("glossary_title", lang, term=f"{g['term']} · {g['zh_term']}"),
                      description=f"{primary}\n\n-# {other}", color=0x8B5CF6)
    ep = bot.content.episode(g.get("episode", ""))
    if ep:
        e.set_footer(text=f"{ep.id} · {L(ep.title, lang)}")
    return e


def trend_embed(bot, tr: dict, lang: str) -> discord.Embed:
    e = discord.Embed(title=clip(f"{tr['emoji']} {L(tr['title'], lang)}", 256), url=tr["source"],
                      description=f"{L(tr['body'], lang)}\n\n**{t('trend_why', lang)}:** {L(tr['why'], lang)}",
                      color=TREND_COLOR)
    ep = bot.content.episode(tr.get("episode", ""))
    e.set_footer(text=t("trend_more", lang, ep=f"{ep.id} · {L(ep.title, lang)}" if ep else "-"))
    return e


def trends_overview(bot, lang: str) -> discord.Embed:
    trends = bot.content.trends
    e = discord.Embed(title=t("trend_title", lang, date=trends.get("as_of", "?")), color=TREND_COLOR)
    for tr in trends["trends"][:12]:
        e.add_field(name=clip(f"{tr['emoji']} {L(tr['title'], lang)}", 256),
                    value=clip(f"{L(tr['why'], lang)} · [{t('source', lang)}]({tr['source']}) · {tr['episode']}", 1024),
                    inline=False)
    return e


class Explore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---- autocomplete
    async def code_ac(self, interaction: discord.Interaction, current: str):
        lang = await lang_of(interaction)
        cur = current.lower()
        out = []
        for e in self.bot.content.code:
            label = f"{L(e.title, lang)} · {e.path}".replace("`", "")
            if not cur or cur in label.lower() or cur in e.id:
                out.append(app_commands.Choice(name=clip(label, 100), value=e.id))
        return out[:25]

    async def term_ac(self, interaction: discord.Interaction, current: str):
        cur = current.lower()
        out = []
        for g in self.bot.content.glossary:
            label = f"{g['term']} · {g['zh_term']}"
            if not cur or cur in label.lower() or any(cur in a.lower() for a in g.get("aliases", [])):
                out.append(app_commands.Choice(name=clip(label, 100), value=g["term"]))
        return out[:25]

    async def trend_ac(self, interaction: discord.Interaction, current: str):
        lang = await lang_of(interaction)
        cur = current.lower()
        return [app_commands.Choice(name=clip(f"{tr['emoji']} {L(tr['title'], lang)}", 100), value=tr["id"])
                for tr in self.bot.content.trends["trends"]
                if not cur or cur in L(tr["title"], lang).lower() or cur in tr["id"]][:25]

    async def take_ac(self, interaction: discord.Interaction, current: str):
        lang = await lang_of(interaction)
        cur = current.lower()
        return [app_commands.Choice(name=clip(f"{h['id']} · {h['emoji']} {L(h['claim'], lang)}", 100), value=h["id"])
                for h in self.bot.content.hottakes.get("takes", [])
                if not cur or cur in L(h["claim"], lang).lower() or cur in h["id"]][:25]

    # ---- commands
    @app_commands.command(name="code", description="vLLM code map: where things live, with permalinks · 程式碼地圖")
    @app_commands.describe(entry="Component (search by name or path)", private="Only you can see it · 只有你看得到")
    @app_commands.autocomplete(entry=code_ac)
    async def code(self, interaction: discord.Interaction, entry: str | None = None, private: bool = True) -> None:
        lang = await lang_of(interaction)
        view = CodeMapView(self.bot, lang)
        if entry:
            e = self.bot.content.code_entry(entry)
            if e is None:
                return await interaction.response.send_message(t("not_found", lang, what=entry), ephemeral=True)
            embed = code_embed(self.bot, e, lang)
        else:
            pin = self.bot.content.code_pin
            embed = discord.Embed(title=t("code_title", lang), color=CODE_COLOR,
                                  description=f"{t('code_pick_hint', lang)}\n\n{L(pin['note'], lang)}")
            for a in self.bot.content.code_areas:
                names = [L(e.title, lang) for e in self.bot.content.code if e.area == a["id"]]
                embed.add_field(name=f"{a['emoji']} {L(a['title'], lang)}", value=clip(" · ".join(names), 1024),
                                inline=False)
        await self.bot.reward(interaction, 0, "tool:code")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=private)

    @app_commands.command(name="trace", description="Follow one request through vLLM in 12 stops · 一個請求，十二站")
    @app_commands.describe(stop="Jump to a stop (1–12)", private="Only you can see it · 只有你看得到")
    async def trace(self, interaction: discord.Interaction, stop: app_commands.Range[int, 1, 12] = 1,
                    private: bool = True) -> None:
        lang = await lang_of(interaction)
        idx = min(stop, len(self.bot.content.trace["stops"])) - 1
        await self.bot.reward(interaction, 0, "tool:trace")
        await interaction.response.send_message(embed=trace_embed(self.bot, lang, idx),
                                                view=TraceView(self.bot, lang, idx), ephemeral=private)

    @app_commands.command(name="glossary", description="Look up an inference term (EN + 中文) · 名詞解釋")
    @app_commands.describe(term="e.g. KV cache, prefill, goodput, 推測解碼")
    @app_commands.autocomplete(term=term_ac)
    async def glossary(self, interaction: discord.Interaction, term: str, private: bool = False) -> None:
        lang = await lang_of(interaction)
        g = self.bot.content.term(term)
        if g is None:
            return await interaction.response.send_message(t("not_found", lang, what=term), ephemeral=True)
        view = discord.ui.View(timeout=None)
        if self.bot.content.episode(g.get("episode", "")):
            view.add_item(OpenEpisodeButton(g["episode"], label=g["episode"]))
        await interaction.response.send_message(embed=term_embed(self.bot, g, lang), view=view, ephemeral=private)

    @app_commands.command(name="trends", description="What's happening in vLLM right now, with sources · vLLM 最新趨勢")
    @app_commands.describe(trend="Open one trend card (leave empty for the overview)")
    @app_commands.autocomplete(trend=trend_ac)
    async def trends(self, interaction: discord.Interaction, trend: str | None = None, private: bool = False) -> None:
        lang = await lang_of(interaction)
        if trend:
            tr = next((x for x in self.bot.content.trends["trends"] if x["id"] == trend), None)
            if tr is None:
                return await interaction.response.send_message(t("not_found", lang, what=trend), ephemeral=True)
            view = discord.ui.View(timeout=None)
            view.add_item(discord.ui.Button(label=t("source", lang), emoji="📎", url=tr["source"]))
            if self.bot.content.episode(tr.get("episode", "")):
                view.add_item(OpenEpisodeButton(tr["episode"], label=tr["episode"]))
            return await interaction.response.send_message(embed=trend_embed(self.bot, tr, lang), view=view,
                                                           ephemeral=private)
        await interaction.response.send_message(embed=trends_overview(self.bot, lang), ephemeral=private)

    @app_commands.command(name="hottake", description="🔮 Hot Take Court: vote on a dated vLLM prediction · 大膽預測")
    @app_commands.describe(take="Pick one (empty = one you haven't voted on)", private="Only you can see it")
    @app_commands.autocomplete(take=take_ac)
    async def hottake(self, interaction: discord.Interaction, take: str | None = None, private: bool = False) -> None:
        lang = await lang_of(interaction)
        takes = self.bot.content.hottakes.get("takes", [])
        if not takes:
            return await interaction.response.send_message(t("not_found", lang, what="hot takes"), ephemeral=True)
        if take:
            chosen = self.bot.content.hottake(take)
            if chosen is None:
                return await interaction.response.send_message(t("not_found", lang, what=take), ephemeral=True)
        else:
            voted = await self.bot.store.voted_takes(interaction.user.id)
            fresh = [h for h in takes if h["id"] not in voted and not h.get("verdict")]
            chosen = random.choice(fresh or takes)
        await interaction.response.defer(ephemeral=private, thinking=True)
        await send_hottake(interaction, chosen, ephemeral=private)


async def setup(bot) -> None:
    await bot.add_cog(Explore(bot))
