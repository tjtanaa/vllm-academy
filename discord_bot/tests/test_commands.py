"""Call the real slash-command handlers with a fake interaction (no network) to catch runtime errors."""
import asyncio
from types import SimpleNamespace

import discord
from discord import app_commands

from academy_bot.bot import AcademyBot
from academy_bot.config import Settings
from academy_bot.store import Store
from academy_bot.ui import HotTakeVoteButton


class FakeResponse:
    def __init__(self, sink):
        self.sink, self._done = sink, False

    def is_done(self):
        return self._done

    async def send_message(self, content=None, **kw):
        self._done = True
        self.sink.append(("send", content, kw))

    async def defer(self, **kw):
        self._done = True

    async def edit_message(self, **kw):
        self.sink.append(("edit", None, kw))


class FakeFollowup:
    def __init__(self, sink):
        self.sink = sink

    async def send(self, content=None, **kw):
        self.sink.append(("followup", content, kw))


class FakeAvatar:
    url = "https://cdn.discordapp.com/embed/avatars/0.png"

    def replace(self, **kw):
        return self

    async def read(self):
        raise discord.HTTPException(SimpleNamespace(status=404, reason="offline"), "offline")


def fake_interaction(bot, sink, uid=1001):
    user = SimpleNamespace(id=uid, display_name="Tester", mention=f"<@{uid}>", display_avatar=FakeAvatar(),
                           guild_permissions=SimpleNamespace(manage_guild=False))
    return SimpleNamespace(client=bot, user=user, guild=None, channel=None, message=None,
                           response=FakeResponse(sink), followup=FakeFollowup(sink))


def cmd(bot, name) -> app_commands.Command:
    return next(c for c in bot.tree.walk_commands() if c.qualified_name == name)


async def call(bot, name, sink, **kwargs):
    c = cmd(bot, name)
    await c.callback(c.binding, fake_interaction(bot, sink), **kwargs)


def test_commands_run_offline():
    async def main():
        s = Settings()
        s.token = ""
        bot = AcademyBot(s, store=Store(":memory:"))
        await bot.store.open()
        await bot.setup_hook()
        sink: list = []
        try:
            await call(bot, "kvcalc", sink, model="llama-3.1-70b", context=131072, users=2, gpu="H100", gpus=4,
                       kv_dtype=None, weight_dtype=None, private=True)
            assert sink[-1][2]["embed"].title.startswith(("🧮", "KV")) or "KV" in sink[-1][2]["embed"].title
            await call(bot, "hottake", sink, take="ht-03", private=True)
            assert sink[-1][0] == "followup" and sink[-1][2]["file"].filename == "ht-03.png"
            await call(bot, "hottake", sink, take=None, private=True)
            await call(bot, "trends", sink, trend=None, private=True)
            await call(bot, "trends", sink, trend="t-systemone", private=True)
            await call(bot, "code", sink, entry="scheduler", private=True)
            await call(bot, "code", sink, entry=None, private=True)
            await call(bot, "trace", sink, stop=5, private=True)
            await call(bot, "glossary", sink, term="cold start", private=True)
            await call(bot, "community", sink, private=True)
            await call(bot, "events", sink, private=True)
            await call(bot, "career", sink, private=True)
            await call(bot, "profile", sink, member=None, private=True)
            assert sink[-1][2]["file"].filename == "profile.png"
            await call(bot, "leaderboard", sink, period=None)
            # the learning + practice flow from the first draft
            await call(bot, "start", sink)
            await call(bot, "path", sink)
            await call(bot, "episode", sink, episode="E27", private=True)
            assert sink[-1][2]["file"].filename == "E27.png"
            await call(bot, "lab", sink, lab="Q2", private=True)
            await call(bot, "lab", sink, lab=None, private=True)
            await call(bot, "quiz", sink, episode="E28", private=True)
            await call(bot, "interview", sink, level=None, kind=None, private=True)
            await call(bot, "mock", sink, level=None)
            await call(bot, "hunt", sink, hunt="H5", private=True)
            # vote through the persistent button
            btn = HotTakeVoteButton("ht-06", "y")
            await btn.callback(fake_interaction(bot, sink))
            assert "🔥 1" in sink[-1][1]
            # non-moderators are stopped by the /academy group check
            admin = bot.get_cog("Admin")
            assert await admin.interaction_check(fake_interaction(bot, sink)) is False
            for kind, content, kw in sink:
                for e in [kw.get("embed")] if kw.get("embed") else []:
                    assert len(e) <= 6000
        finally:
            for name in list(bot.cogs):
                await bot.remove_cog(name)
            await bot.github.close()
            await bot.store.close()
    asyncio.run(main())
