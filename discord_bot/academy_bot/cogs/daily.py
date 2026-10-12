"""Scheduled posts: the bilingual Daily Drop (20:00 Taipei by default) and the vLLM Release Radar."""
from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import aiohttp
import discord
from discord.ext import commands, tasks

from ..drops import daily_drop, release_highlights, study_links, take_verdict
from ..i18n import both, t
from ..ui import (OpenEpisodeButton, clip, episode_cover_file, episode_embed, episode_view, hottake_embed,
                  hottake_file, hottake_view, hunt_embed, hunt_view, interview_view, quiz_embed, quiz_view)

log = logging.getLogger("academy")
KIND_KEY = {"quiz": "daily_quiz", "interview": "daily_interview", "term": "daily_term", "hunt": "daily_hunt",
            "hottake": "daily_hottake", "trend": "daily_trend", "episode": "daily_episode"}


async def render_drop(bot, day, lang: str | None = None) -> dict:
    """Message kwargs for the given day's drop (shared by the scheduler and /academy daily-now)."""
    lang = lang or bot.settings.default_lang
    kind, item = daily_drop(bot.content, day)
    head = (f"## {t('daily_title', 'zh', date=day.isoformat())}\n"
            f"-# {t('daily_title', 'en', date=day.isoformat())} · {t(KIND_KEY[kind], 'zh')} / {t(KIND_KEY[kind], 'en')}")
    out: dict = {"content": head}
    if kind == "quiz":
        out.update(embed=quiz_embed(bot, item, lang, await bot.store.quiz_solvers(item.id), bilingual=True),
                   view=quiz_view(item))
    elif kind == "interview":
        e = discord.Embed(title=f"🎤 {t(KIND_KEY[kind], lang)}", color=0xFBBF24,
                          description=f"### {item.q['zh']}\n### {item.q['en']}\n\n{t('iv_prompt', 'zh')}\n{t('iv_prompt', 'en')}")
        out.update(embed=e, view=interview_view(item, lang))
    elif kind == "term":
        e = discord.Embed(title=f"📚 {item['term']} · {item['zh_term']}", color=0x8B5CF6,
                          description=f"{item['zh']}\n\n{item['en']}")
        v = discord.ui.View(timeout=None)
        if bot.content.episode(item.get("episode", "")):
            v.add_item(OpenEpisodeButton(item["episode"], label=item["episode"]))
        out.update(embed=e, view=v)
    elif kind == "hunt":
        out.update(embed=hunt_embed(bot, item, lang), view=hunt_view(item, lang))
    elif kind == "hottake":
        agree, disagree = await bot.store.tally(item["id"])
        verdict, note = take_verdict(item, await bot.store.setting(0, f"verdict:{item['id']}"))
        out.update(embed=hottake_embed(bot, item, lang, verdict=verdict, note=note), view=hottake_view(item, lang),
                   file=hottake_file(item, agree, disagree, verdict))
    elif kind == "trend":
        e = discord.Embed(title=f"{item['emoji']} {item['title']['zh']}\n{item['title']['en']}", url=item["source"],
                          color=0x3B82F6, description=f"{both(item['body'], chr(10) * 2)}\n\n💡 {both(item['why'], ' / ')}")
        v = discord.ui.View(timeout=None)
        v.add_item(discord.ui.Button(label=t("source", lang), emoji="📎", url=item["source"]))
        if bot.content.episode(item.get("episode", "")):
            v.add_item(OpenEpisodeButton(item["episode"], label=item["episode"]))
        out.update(embed=e, view=v)
    elif kind == "episode":
        out.update(embed=episode_embed(bot, item, lang), view=episode_view(bot, item, lang),
                   file=episode_cover_file(bot, item))
    return out


def release_embed(bot, rel: dict) -> discord.Embed:
    e = discord.Embed(title=f"{t('release_title', 'zh', tag=rel['tag'])} · {t('release_title', 'en', tag=rel['tag'])}",
                      url=rel["url"], color=0x30A2FF)
    hl = release_highlights(rel["body"])
    if hl:
        e.description = clip("\n".join(f"• {h}" for h in hl), 3500)
    eps = [bot.content.episode(x) for x in study_links(rel["body"])]
    if eps:
        e.add_field(name=f"{t('release_learn', 'zh')} · {t('release_learn', 'en')}",
                    value="\n".join(f"`{ep.id}` {ep.title['zh']} · {ep.title['en']}" for ep in eps if ep), inline=False)
    e.set_footer(text=rel.get("published", "")[:10])
    return e


class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        # start after login (on_ready can fire again on reconnect, so guard against double starts)
        if not self.daily_loop.is_running():
            self.daily_loop.start()
        if self.bot.settings.release_radar and not self.release_loop.is_running():
            self.release_loop.start()

    def cog_unload(self) -> None:
        self.daily_loop.cancel()
        self.release_loop.cancel()

    async def _channels(self, key: str, fallback: int | None) -> list[discord.abc.Messageable]:
        ids = {int(v) for _, v in await self.bot.store.guilds_with(key) if v and v.isdigit()}
        if fallback:
            ids.add(fallback)
        out = []
        for cid in ids:
            ch = self.bot.get_channel(cid)
            if ch is None:
                try:
                    ch = await self.bot.fetch_channel(cid)
                except discord.HTTPException:
                    continue
            out.append(ch)
        return out

    @tasks.loop(minutes=5)
    async def daily_loop(self) -> None:
        now = datetime.now(ZoneInfo(self.bot.settings.timezone))
        if now.hour < self.bot.settings.daily_hour:
            return
        day = now.date()
        for ch in await self._channels("daily_channel", self.bot.settings.daily_channel_id):
            if not await self.bot.store.mark_posted(f"daily:{ch.id}", day.isoformat()):
                continue
            try:
                await ch.send(**await render_drop(self.bot, day))
            except discord.HTTPException as exc:
                log.warning("daily drop to %s failed: %s", ch, exc)

    @tasks.loop(hours=3)
    async def release_loop(self) -> None:
        try:
            rel = await self.bot.github.latest_release()
        except (aiohttp.ClientError, TimeoutError) as exc:
            log.info("release radar: %s", exc)
            return
        if not rel:
            return
        seen = await self.bot.store.setting(0, "last_release")
        if seen is None:  # first run: remember the current release, don't announce old news
            await self.bot.store.set_setting(0, "last_release", rel["tag"])
            return
        if seen == rel["tag"]:
            return
        await self.bot.store.set_setting(0, "last_release", rel["tag"])
        for ch in await self._channels("announce_channel", self.bot.settings.announce_channel_id):
            try:
                await ch.send(embed=release_embed(self.bot, rel))
            except discord.HTTPException as exc:
                log.warning("release radar to %s failed: %s", ch, exc)


async def setup(bot) -> None:
    await bot.add_cog(Daily(bot))
