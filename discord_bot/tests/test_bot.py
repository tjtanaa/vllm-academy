"""Boot the bot offline (no token, no network) and check every embed against Discord's limits."""
import asyncio
from datetime import date, timedelta

import discord

from academy_bot import cards
from academy_bot.bot import AcademyBot
from academy_bot.config import Settings
from academy_bot.store import Store


def embed_ok(e: discord.Embed) -> None:
    assert len(e) <= 6000, e.title
    assert len(e.title or "") <= 256 and len(e.description or "") <= 4096
    assert len(e.fields) <= 25
    for f in e.fields:
        assert 0 < len(f.name) <= 256 and 0 < len(f.value) <= 1024, f.name


def view_ok(v: discord.ui.View) -> None:
    assert len(v.children) <= 25
    for item in v.children:
        if isinstance(item, discord.ui.Button):
            assert len(item.label or "") <= 80
            assert item.url or len(item.custom_id or "") <= 100
        if isinstance(item, discord.ui.Select):
            assert 1 <= len(item.options) <= 25
            for o in item.options:
                assert len(o.label) <= 100 and len(o.description or "") <= 100


def with_bot(test):
    """Run an async test body against a freshly booted offline bot (no plugin needed)."""
    def wrapper():
        async def main():
            s = Settings()
            s.token = ""
            s.release_radar = False
            b = AcademyBot(s, store=Store(":memory:"))
            await b.store.open()
            await b.setup_hook()
            try:
                await test(b)
            finally:
                for name in list(b.cogs):
                    await b.remove_cog(name)
                await b.github.close()
                await b.store.close()
        asyncio.run(main())
    wrapper.__name__ = test.__name__
    return wrapper


@with_bot
async def test_all_commands_register(bot):
    names = {c.name for c in bot.tree.get_commands()}
    expected = {"start", "lang", "path", "episode", "lab", "quiz", "interview", "mock", "hunt", "code", "trace",
                "glossary", "trends", "hottake", "community", "events", "career", "gfi", "profile", "leaderboard",
                "kvcalc", "academy"}
    assert expected <= names
    assert len(names) <= 100
    for cmd in bot.tree.walk_commands():
        assert len(cmd.description) <= 100, cmd.qualified_name


@with_bot
async def test_episode_and_lab_embeds_fit(bot):
    from academy_bot.ui import episode_embed, episode_view, lab_step_embed
    for lang in ("en", "zh"):
        for ep in bot.content.episodes:
            embed_ok(episode_embed(bot, ep, lang))
            view_ok(episode_view(bot, ep, lang))
        for lab in bot.content.labs:
            for i in range(len(lab.steps[lang])):
                embed_ok(lab_step_embed(bot, lab, lang, i))


@with_bot
async def test_explore_and_community_embeds_fit(bot):
    from academy_bot.cogs.community import career_embed, community_embed, events_embed
    from academy_bot.cogs.explore import CodeMapView, code_embed, term_embed, trace_embed, trend_embed, trends_overview
    from academy_bot.ui import hottake_embed, hottake_view
    for lang in ("en", "zh"):
        for e in bot.content.code:
            embed_ok(code_embed(bot, e, lang))
        for i in range(len(bot.content.trace["stops"])):
            embed_ok(trace_embed(bot, lang, i))
        for g in bot.content.glossary:
            embed_ok(term_embed(bot, g, lang))
        for tr in bot.content.trends["trends"]:
            embed_ok(trend_embed(bot, tr, lang))
        embed_ok(trends_overview(bot, lang))
        embed_ok(community_embed(bot, lang))
        embed_ok(events_embed(bot, lang))
        for cr in bot.content.careers:
            embed_ok(career_embed(bot, cr, lang))
        for h in bot.content.hottakes["takes"]:
            embed_ok(hottake_embed(bot, h, lang, verdict="partly", note="test"))
            view_ok(hottake_view(h, lang))
        view_ok(CodeMapView(bot, lang))


@with_bot
async def test_daily_drops_render_for_a_week(bot):
    from academy_bot.cogs.daily import render_drop
    for i in range(7):
        out = await render_drop(bot, date(2026, 10, 12) + timedelta(days=i))
        assert len(out["content"]) <= 2000
        embed_ok(out["embed"])
        view_ok(out["view"])


@with_bot
async def test_votes_and_badge_flow(bot):
    st = bot.store
    for i in range(1, 6):
        assert await st.vote(42, f"ht-{i:02d}", agree=i % 2 == 0)
    assert not await st.vote(42, "ht-01", agree=True)  # changing a vote isn't a new vote
    assert await st.tally("ht-01") == (1, 0)
    state = await st.learner_state(42)
    assert state.hot_takes_voted == 5


def test_cards_render():
    png = cards.hottake_card(take_id="ht-01", claim_en="The Rust frontend becomes the default",
                             claim_zh="Rust 前端會變成預設", confidence=35, judge_on="2026-12-31",
                             agree=7, disagree=3, verdict="partly")
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    seasons = [(f"S{i}", i, 4, 0xFDBA34) for i in range(7)]
    png = cards.profile_card(name="tester", avatar=None, level=2, rank_en="KV Cadet", rank_zh="KV 見習生", xp=420,
                             to_next=480, progress=0.2, streak=3, position=1, badges=["Oracle"], seasons=seasons)
    assert png[:4] == b"\x89PNG"
