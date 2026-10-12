"""/academy … — moderator tools: one-command server setup, panels, awards, verdicts, reload."""
from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from ..i18n import L, t
from ..progress import XP
from ..ui import banner_file, lang_of, start_embed, start_view
from .daily import render_drop

CATEGORY = "🎓 vLLM Academy"
# (name, topic, settings key)
CHANNELS = [
    ("start-here", "Start here: /start · 從這裡開始", "start_channel"),
    ("daily-drop", "Daily vLLM Drop at 20:00 Taipei · 每日一練", "daily_channel"),
    ("hot-takes", "🔮 Hot Take Court: vote, argue, get graded · 大膽預測法庭", None),
    ("release-radar", "New vLLM releases + what to study · 版本雷達", "announce_channel"),
    ("show-your-work", "Lab outputs, benchmarks, PRs · 成果分享", None),
    ("labs-help", "Stuck on a lab? Ask here · 實作求救", None),
    ("mock-interviews", "Find a mock-interview partner · 模擬面試揪團", None),
]
RANK_COLORS = [0x94A3B8, 0x60A5FA, 0x34D399, 0xA78BFA, 0xF472B6, 0xFDBA34]


class Admin(commands.GroupCog, group_name="academy", group_description="Moderator tools · 管理員工具"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        perms = getattr(interaction.user, "guild_permissions", None)
        if interaction.guild is None or not perms or not perms.manage_guild:
            await interaction.response.send_message(t("admin_only", await lang_of(interaction)), ephemeral=True)
            return False
        return True

    async def take_ac(self, interaction: discord.Interaction, current: str):
        return [app_commands.Choice(name=f"{h['id']} · {h['claim']['en']}"[:100], value=h["id"])
                for h in self.bot.content.hottakes.get("takes", []) if current.lower() in h["id"] + h["claim"]["en"].lower()][:25]

    async def badge_ac(self, interaction: discord.Interaction, current: str):
        return [app_commands.Choice(name=f"{b['emoji']} {b['name']['en']} · {b['name']['zh']}", value=b["id"])
                for b in self.bot.content.badges if current.lower() in b["id"]][:25]

    @app_commands.command(name="setup", description="Create the Academy channels and rank roles · 一鍵建立頻道與身分組")
    @app_commands.describe(confirm="False = show the plan only; True = apply it")
    @app_commands.default_permissions(manage_guild=True)
    async def setup_cmd(self, interaction: discord.Interaction, confirm: bool = False) -> None:
        lang = await lang_of(interaction)
        guild = interaction.guild
        cat = discord.utils.get(guild.categories, name=CATEGORY)
        plan = [f"{'✓' if cat else '+'} category **{CATEGORY}**"]
        for name, _, _ in CHANNELS:
            exists = cat and discord.utils.get(cat.text_channels, name=name)
            plan.append(f"{'✓' if exists else '+'} #{name}")
        for r in self.bot.content.ranks:
            rname = f"{r['emoji']} {r['name']['en']}"
            plan.append(f"{'✓' if discord.utils.get(guild.roles, name=rname) else '+'} role {rname}")
        if not confirm:
            return await interaction.response.send_message(t("setup_plan", lang, plan="\n".join(plan)), ephemeral=True)
        await interaction.response.defer(ephemeral=True, thinking=True)
        if cat is None:
            cat = await guild.create_category(CATEGORY, reason="vLLM Academy setup")
        for name, topic, key in CHANNELS:
            ch = discord.utils.get(cat.text_channels, name=name)
            if ch is None:
                ch = await guild.create_text_channel(name, category=cat, topic=topic, reason="vLLM Academy setup")
            if key:
                await self.bot.store.set_setting(guild.id, key, str(ch.id))
        for r, color in zip(self.bot.content.ranks, RANK_COLORS):
            rname = f"{r['emoji']} {r['name']['en']}"
            if discord.utils.get(guild.roles, name=rname) is None:
                await guild.create_role(name=rname, colour=discord.Colour(color), hoist=r["level"] >= 4,
                                        reason="vLLM Academy rank")
        start = discord.utils.get(cat.text_channels, name="start-here")
        if start:
            await start.send(embed=start_embed(self.bot), view=start_view(self.bot), file=banner_file(self.bot))
        await interaction.followup.send(t("setup_done", lang, plan="\n".join(p.replace("+", "✓", 1) for p in plan)),
                                        ephemeral=True)

    @app_commands.command(name="post-start", description="Post the welcome panel here · 在這裡發布歡迎面板")
    @app_commands.default_permissions(manage_guild=True)
    async def post_start(self, interaction: discord.Interaction) -> None:
        await interaction.channel.send(embed=start_embed(self.bot), view=start_view(self.bot), file=banner_file(self.bot))
        await interaction.response.send_message(t("start_posted", await lang_of(interaction)), ephemeral=True)

    @app_commands.command(name="daily-now", description="Post today's Daily Drop in this channel · 立即發布每日一練")
    @app_commands.default_permissions(manage_guild=True)
    async def daily_now(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        await interaction.channel.send(**await render_drop(self.bot, self.bot.today()))
        await interaction.followup.send(t("daily_posted", await lang_of(interaction)), ephemeral=True)

    @app_commands.command(name="award", description="Grant a badge (e.g. Merged) with bonus XP · 頒發徽章")
    @app_commands.autocomplete(badge=badge_ac)
    @app_commands.default_permissions(manage_guild=True)
    async def award(self, interaction: discord.Interaction, member: discord.Member, badge: str) -> None:
        lang = await lang_of(interaction)
        b = self.bot.content.badge(badge)
        if b is None:
            return await interaction.response.send_message(t("award_badge_unknown", lang, b=badge), ephemeral=True)
        await self.bot.store.grant_badge(member.id, b["id"])
        res = await self.bot.store.add_xp(member.id, XP["award"], f"award:{b['id']}", self.bot.today())
        from ..progress import level_for
        await self.bot.sync_rank_role(member, level_for(res.new_xp, self.bot.content.ranks).level)
        await interaction.response.send_message(
            t("award_done", lang, badge=f"{b['emoji']} {L(b['name'], lang)}", user=member.mention, xp=XP["award"]))

    @app_commands.command(name="verdict", description="Judge a hot take when its date arrives · 判決大膽預測")
    @app_commands.autocomplete(take=take_ac)
    @app_commands.choices(verdict=[app_commands.Choice(name="Right · 猜中", value="right"),
                                   app_commands.Choice(name="Wrong · 猜錯", value="wrong"),
                                   app_commands.Choice(name="Partly · 對一半", value="partly")])
    @app_commands.default_permissions(manage_guild=True)
    async def verdict(self, interaction: discord.Interaction, take: str, verdict: app_commands.Choice[str],
                      note: str = "") -> None:
        lang = await lang_of(interaction)
        if self.bot.content.hottake(take) is None:
            return await interaction.response.send_message(t("not_found", lang, what=take), ephemeral=True)
        await self.bot.store.set_setting(0, f"verdict:{take}", f"{verdict.value}|{note}")
        await interaction.response.send_message(t("verdict_set", lang, id=take, verdict=verdict.name), ephemeral=True)

    @app_commands.command(name="reload", description="Reload YAML content and labs without restarting · 重新載入內容")
    @app_commands.default_permissions(manage_guild=True)
    async def reload(self, interaction: discord.Interaction) -> None:
        summary = self.bot.reload_content()
        await interaction.response.send_message(t("reloaded", await lang_of(interaction), summary=summary), ephemeral=True)


async def setup(bot) -> None:
    await bot.add_cog(Admin(bot))
