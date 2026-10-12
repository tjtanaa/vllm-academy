"""/profile /leaderboard /kvcalc — your progress card, the ranking and the memory calculator."""
from __future__ import annotations

import io
import time

import discord
from discord import app_commands
from discord.ext import commands

from .. import cards, kvcalc
from ..i18n import L, t
from ..progress import XP, level_for
from ..ui import OpenEpisodeButton, lang_of

DTYPE_CHOICES = [app_commands.Choice(name=d, value=d) for d in kvcalc.DTYPES]
MEDALS = ["🥇", "🥈", "🥉"]


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def profile_png(self, member: discord.abc.User) -> bytes:
        bot = self.bot
        u = await bot.store.user(member.id)
        info = level_for(u.xp, bot.content.ranks)
        done = await bot.store.items(member.id, "episode")
        seasons = [(s.id, len(set(eps) & done), len(eps), s.color)
                   for s in bot.content.seasons for eps in [[e.id for e in bot.content.season_episodes(s.id)]]]
        owned = await bot.store.badges(member.id)
        badge_names = [b["name"]["en"] for b in bot.content.badges if b["id"] in owned]
        try:
            avatar = await member.display_avatar.replace(size=256, format="png").read()
        except (discord.HTTPException, AttributeError):
            avatar = None
        return cards.profile_card(name=member.display_name, avatar=avatar, level=info.level,
                                  rank_en=info.rank["name"]["en"], rank_zh=info.rank["name"]["zh"], xp=u.xp,
                                  to_next=info.to_next, progress=info.progress, streak=u.streak,
                                  position=await bot.store.rank_of(member.id), badges=badge_names, seasons=seasons)

    @app_commands.command(name="profile", description="Your Academy card: level, streak, seasons, badges · 個人卡片")
    @app_commands.describe(member="Someone else's card (optional)")
    async def profile(self, interaction: discord.Interaction, member: discord.Member | None = None,
                      private: bool = False) -> None:
        lang = await lang_of(interaction)
        target = member or interaction.user
        await interaction.response.defer(ephemeral=private, thinking=True)
        png = await self.profile_png(target)
        u = await self.bot.store.user(target.id)
        owned = await self.bot.store.badges(target.id)
        e = discord.Embed(title=t("profile_title", lang, user=target.display_name), color=0xFDBA34)
        if owned:
            e.description = " ".join(f"{b['emoji']} {L(b['name'], lang)}" for b in self.bot.content.badges
                                     if b["id"] in owned)
        if u.route and (route := self.bot.content.route(u.route)):
            e.add_field(name="🗺️", value=f"{route['emoji']} {L(route['title'], lang)}", inline=True)
        if u.best_mock:
            e.add_field(name="🎯 /mock", value=f"{u.best_mock}%", inline=True)
        e.set_image(url="attachment://profile.png")
        await interaction.followup.send(embed=e, file=discord.File(io.BytesIO(png), filename="profile.png"),
                                        ephemeral=private)

    @app_commands.command(name="leaderboard", description="Top learners this week or all time · 排行榜")
    @app_commands.choices(period=[app_commands.Choice(name="This week · 本週", value="week"),
                                  app_commands.Choice(name="All time · 總榜", value="all")])
    async def leaderboard(self, interaction: discord.Interaction,
                          period: app_commands.Choice[str] | None = None) -> None:
        lang = await lang_of(interaction)
        week = period is None or period.value == "week"
        rows = await self.bot.store.leaderboard(10, since=time.time() - 7 * 86400 if week else None)
        e = discord.Embed(title=f"{t('lb_title', lang)} · {t('lb_week' if week else 'lb_all', lang)}", color=0xFDBA34)
        if not rows:
            e.description = t("lb_empty", lang)
        else:
            lines = []
            for i, (uid, xp) in enumerate(rows):
                total = (await self.bot.store.user(uid)).xp
                info = level_for(total, self.bot.content.ranks)
                medal = MEDALS[i] if i < 3 else f"`#{i + 1}`"
                lines.append(f"{medal} <@{uid}> · **{xp:,} XP** · {info.rank['emoji']} Lv.{info.level}")
            e.description = "\n".join(lines)
        me = await self.bot.store.user(interaction.user.id)
        e.set_footer(text=t("lb_you", lang, rank=await self.bot.store.rank_of(interaction.user.id), xp=me.xp))
        await interaction.response.send_message(embed=e, allowed_mentions=discord.AllowedMentions.none())

    # ------------------------------------------------------------------ kvcalc
    async def model_ac(self, interaction: discord.Interaction, current: str):
        cur = current.lower()
        return [app_commands.Choice(name=f"{m.name} ({m.attention.upper()}, {m.params_b:g}B)", value=m.name)
                for m in kvcalc.MODELS.values() if cur in m.name][:25]

    async def gpu_ac(self, interaction: discord.Interaction, current: str):
        cur = current.lower()
        return [app_commands.Choice(name=f"{n} · {g:g} GiB", value=n) for n, g in kvcalc.GPUS.items()
                if cur in n.lower()][:25]

    @app_commands.command(name="kvcalc", description="KV-cache memory calculator: will it fit? (E07) · KV 記憶體計算機")
    @app_commands.describe(model="Model preset", context="Context length in tokens", users="Concurrent sequences",
                           gpu="GPU type", gpus="Number of GPUs (tensor parallel)", kv_dtype="KV cache dtype",
                           weight_dtype="Weight dtype")
    @app_commands.autocomplete(model=model_ac, gpu=gpu_ac)
    @app_commands.choices(kv_dtype=DTYPE_CHOICES, weight_dtype=DTYPE_CHOICES)
    async def kvcalc_cmd(self, interaction: discord.Interaction, model: str = "llama-3.1-8b",
                         context: app_commands.Range[int, 1, 10_000_000] = 8192,
                         users: app_commands.Range[int, 1, 100_000] = 1, gpu: str = "H100-80G",
                         gpus: app_commands.Range[int, 1, 1024] = 1,
                         kv_dtype: app_commands.Choice[str] | None = None,
                         weight_dtype: app_commands.Choice[str] | None = None, private: bool = False) -> None:
        lang = await lang_of(interaction)
        spec = kvcalc.find_model(model)
        if spec is None:
            return await interaction.response.send_message(
                t("kv_unknown_model", lang, m=model, list=", ".join(kvcalc.MODELS)), ephemeral=True)
        found = kvcalc.find_gpu(gpu)
        if found is None:
            return await interaction.response.send_message(
                t("kv_unknown_gpu", lang, g=gpu, list=", ".join(kvcalc.GPUS)), ephemeral=True)
        gpu_name, gpu_mem = found
        kvd = kv_dtype.value if kv_dtype else "bf16"
        wd = weight_dtype.value if weight_dtype else "bf16"
        r = kvcalc.compute(spec, context=context, users=users, kv_dtype=kvd, weight_dtype=wd, gpus=gpus,
                           gpu_mem_gib=gpu_mem)
        hb = kvcalc.human_bytes
        if not r.weights_fit:
            verdict = t("kv_noweights", lang)
        elif r.fits:
            verdict = t("kv_fits", lang, maxseq=r.max_seqs)
        else:
            verdict = t("kv_nofit", lang, maxseq=r.max_seqs)
        e = discord.Embed(title=t("kv_title", lang, model=spec.name), description=verdict,
                          color=0x34D399 if r.fits else 0xEF4444)
        e.add_field(name=t("kv_per_token", lang), value=hb(r.kv_per_token), inline=True)
        e.add_field(name=t("kv_per_seq", lang, ctx=f"{context:,}"), value=hb(r.kv_per_seq), inline=True)
        e.add_field(name=t("kv_total", lang, users=users), value=hb(r.kv_total), inline=True)
        e.add_field(name=t("kv_weights", lang), value=hb(r.weights), inline=True)
        e.add_field(name=t("kv_capacity", lang, gpus=gpus, gpu=gpu_name), value=hb(r.budget), inline=True)
        e.add_field(name=t("kv_formula", lang), value=f"`{r.formula}`", inline=False)
        e.set_footer(text=t("kv_assumptions", lang, util=r.util))
        png = cards.kv_card(model=spec.name, subtitle=t("kv_card_sub", "en", ctx=f"{context:,}", users=users, gpus=gpus,
                                                          gpu=gpu_name, kvd=kvd.upper(), wd=wd.upper()),
                            per_token=hb(r.kv_per_token), per_seq=hb(r.kv_per_seq), max_seqs=r.max_seqs,
                            weights_gib=r.weights / kvcalc.GIB, kv_gib=r.kv_total / kvcalc.GIB,
                            budget_gib=r.budget / kvcalc.GIB, fits=r.fits)
        e.set_image(url="attachment://kv.png")
        first = await self.bot.store.mark(interaction.user.id, "tool", "kvcalc")
        lines = await self.bot.reward(interaction, XP["kvcalc_first"] if first else 0, "tool:kvcalc")
        view = discord.ui.View(timeout=None)
        view.add_item(OpenEpisodeButton("E07", label="E07"))
        await interaction.response.send_message(content="\n".join(lines) or None, embed=e, view=view,
                                                file=discord.File(io.BytesIO(png), filename="kv.png"),
                                                ephemeral=private)


async def setup(bot) -> None:
    await bot.add_cog(Profile(bot))
