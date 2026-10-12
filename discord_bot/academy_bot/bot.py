"""The bot: wiring, XP rewards, level roles and command sync."""
from __future__ import annotations

import logging
from datetime import date, datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands

from .config import REPO_ROOT, Settings
from .content import Content, load_content, validate
from .github import GitHub
from .i18n import L, t
from .progress import level_for, new_badges
from .store import Store
from .ui import DYNAMIC_ITEMS

log = logging.getLogger("academy")

COGS = (
    "academy_bot.cogs.learn",
    "academy_bot.cogs.practice",
    "academy_bot.cogs.explore",
    "academy_bot.cogs.community",
    "academy_bot.cogs.profile",
    "academy_bot.cogs.admin",
    "academy_bot.cogs.daily",
)


class AcademyBot(commands.Bot):
    def __init__(self, settings: Settings, *, store: Store | None = None):
        intents = discord.Intents.default()  # no privileged intents needed: slash commands only
        super().__init__(command_prefix=commands.when_mentioned, intents=intents, help_command=None)
        self.settings = settings
        self.content: Content = self.load_content()
        self.store = store or Store(settings.db_path)
        self.github = GitHub(settings.github_token)
        self.cover_cache: dict[str, bytes] = {}
        self._lang_cache: dict[int, str] = {}

    # ------------------------------------------------------------------ setup
    def load_content(self) -> Content:
        content = load_content(self.settings.content_dir, self.settings.labs_dir, REPO_ROOT)
        problems = validate(content, REPO_ROOT)
        for p in problems:
            log.warning("content: %s", p)
        log.info("Loaded %s", content.summary())
        return content

    def reload_content(self) -> str:
        self.content = self.load_content()
        self.cover_cache.clear()
        return self.content.summary()

    async def setup_hook(self) -> None:
        if self.store.db is None:
            await self.store.open()
        self.add_dynamic_items(*DYNAMIC_ITEMS)
        for ext in COGS:
            await self.load_extension(ext)
        await self.sync_commands()

    async def sync_commands(self) -> None:
        if not self.settings.token:  # offline/test construction
            return
        if self.settings.guild_ids:
            for gid in self.settings.guild_ids:
                guild = discord.Object(id=gid)
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                log.info("Synced %d commands to guild %s", len(synced), gid)
        else:
            synced = await self.tree.sync()
            log.info("Synced %d global commands (may take up to an hour to appear)", len(synced))

    async def on_ready(self) -> None:
        log.info("Logged in as %s (%s) in %d guild(s)", self.user, getattr(self.user, "id", "?"), len(self.guilds))
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                             name="/start · vLLM Academy"))

    async def close(self) -> None:
        await self.github.close()
        await self.store.close()
        await super().close()

    # ------------------------------------------------------------------ helpers
    def today(self) -> date:
        return datetime.now(ZoneInfo(self.settings.timezone)).date()

    async def lang_for(self, user_id: int) -> str:
        if user_id in self._lang_cache:
            return self._lang_cache[user_id]
        u = await self.store.user(user_id)
        lang = u.lang or self.settings.default_lang
        return lang

    async def set_lang(self, user_id: int, lang: str) -> None:
        await self.store.set_lang(user_id, lang)
        self._lang_cache[user_id] = lang

    def season_episode_map(self) -> dict[str, list[str]]:
        return {s.id: [e.id for e in self.content.season_episodes(s.id)] for s in self.content.seasons}

    async def reward(self, interaction: discord.Interaction, amount: int, reason: str) -> list[str]:
        """Give XP (may be 0 to just count activity), handle streak, badges, level-up. Returns lines to show."""
        user = interaction.user
        lang = await self.lang_for(user.id)
        res = await self.store.add_xp(user.id, amount, reason, self.today())
        lines: list[str] = []
        state = await self.store.learner_state(user.id)
        for badge_id in new_badges(state, self.season_episode_map()):
            if await self.store.grant_badge(user.id, badge_id):
                b = self.content.badge(badge_id)
                if b:
                    lines.append(t("badge_earned", lang, badge=f"{b['emoji']} {L(b['name'], lang)}"))
        before = level_for(res.old_xp, self.content.ranks)
        after = level_for(res.new_xp, self.content.ranks)
        if after.level > before.level:
            rank = after.rank
            lines.append(t("level_up", lang, user=user.mention, level=after.level,
                           rank=f"{rank['emoji']} {L(rank['name'], lang)}", xp=res.new_xp))
            await self._on_level_up(interaction, after.level)
        if amount and res.streak > 1:
            lines.append(t("streak", lang, n=res.streak))
        return lines

    async def _on_level_up(self, interaction: discord.Interaction, level: int) -> None:
        guild, member = interaction.guild, interaction.user
        rank = next((r for r in self.content.ranks if r["level"] == level), None)
        if rank is None:
            return
        if self.settings.public_level_up and isinstance(interaction.channel, discord.abc.Messageable):
            try:
                text = (f"🎉 {member.mention} → **Lv.{level} {rank['emoji']} {rank['name']['zh']} · {rank['name']['en']}**")
                await interaction.channel.send(text, allowed_mentions=discord.AllowedMentions(users=False))
            except discord.HTTPException:
                pass
        if self.settings.level_roles and guild and isinstance(member, discord.Member):
            await self.sync_rank_role(member, level)

    async def sync_rank_role(self, member: discord.Member, level: int) -> None:
        names = {r["level"]: f"{r['emoji']} {r['name']['en']}" for r in self.content.ranks}
        target = discord.utils.get(member.guild.roles, name=names.get(level, ""))
        if target is None:
            return
        stale = [r for r in member.roles if r.name in names.values() and r != target]
        try:
            if stale:
                await member.remove_roles(*stale, reason="vLLM Academy rank change")
            if target not in member.roles:
                await member.add_roles(target, reason="vLLM Academy level up")
        except discord.HTTPException as exc:
            log.info("Could not update rank role for %s: %s", member, exc)
