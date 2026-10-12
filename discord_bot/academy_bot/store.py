"""SQLite persistence (aiosqlite). One file, no server to run."""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import aiosqlite

from .progress import LearnerState, next_streak

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY,
    lang        TEXT,
    route       TEXT,
    xp          INTEGER NOT NULL DEFAULT 0,
    streak      INTEGER NOT NULL DEFAULT 0,
    last_active TEXT,
    best_mock   INTEGER NOT NULL DEFAULT 0,
    created     REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS progress (
    user_id INTEGER NOT NULL,
    kind    TEXT NOT NULL,      -- episode | lab | hunt | tool
    item_id TEXT NOT NULL,
    ts      REAL NOT NULL,
    PRIMARY KEY (user_id, kind, item_id)
);
CREATE TABLE IF NOT EXISTS quiz_attempts (
    user_id INTEGER NOT NULL,
    quiz_id TEXT NOT NULL,
    correct INTEGER NOT NULL,
    ts      REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS quiz_attempts_user ON quiz_attempts(user_id, quiz_id);
CREATE TABLE IF NOT EXISTS badges (
    user_id  INTEGER NOT NULL,
    badge_id TEXT NOT NULL,
    ts       REAL NOT NULL,
    PRIMARY KEY (user_id, badge_id)
);
CREATE TABLE IF NOT EXISTS xp_log (
    user_id INTEGER NOT NULL,
    amount  INTEGER NOT NULL,
    reason  TEXT NOT NULL,
    ts      REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id INTEGER NOT NULL,
    key      TEXT NOT NULL,
    value    TEXT,
    PRIMARY KEY (guild_id, key)
);
CREATE TABLE IF NOT EXISTS hottake_votes (
    user_id INTEGER NOT NULL,
    take_id TEXT NOT NULL,
    agree   INTEGER NOT NULL,   -- 1 agree, 0 disagree
    ts      REAL NOT NULL,
    PRIMARY KEY (user_id, take_id)
);
CREATE TABLE IF NOT EXISTS posted (
    scope TEXT NOT NULL,        -- e.g. daily:<guild_id> or release
    key   TEXT NOT NULL,        -- e.g. 2026-10-12 or v0.31.0
    ts    REAL NOT NULL,
    PRIMARY KEY (scope, key)
);
"""


@dataclass
class User:
    user_id: int
    lang: str | None
    route: str | None
    xp: int
    streak: int
    last_active: str | None
    best_mock: int


@dataclass
class XPResult:
    old_xp: int
    new_xp: int
    streak: int


class Store:
    def __init__(self, path: Path | str):
        self.path = str(path)
        self.db: aiosqlite.Connection | None = None

    async def open(self) -> "Store":
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.db = await aiosqlite.connect(self.path)
        self.db.row_factory = aiosqlite.Row
        await self.db.executescript(SCHEMA)
        await self.db.commit()
        return self

    async def close(self) -> None:
        if self.db is not None:
            await self.db.close()
            self.db = None

    # ---------- users ----------
    async def user(self, user_id: int) -> User:
        assert self.db is not None
        async with self.db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
        if row is None:
            await self.db.execute("INSERT OR IGNORE INTO users (user_id, created) VALUES (?, ?)", (user_id, time.time()))
            await self.db.commit()
            return User(user_id, None, None, 0, 0, None, 0)
        return User(row["user_id"], row["lang"], row["route"], row["xp"], row["streak"], row["last_active"], row["best_mock"])

    async def set_lang(self, user_id: int, lang: str) -> None:
        await self.user(user_id)
        await self.db.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))
        await self.db.commit()

    async def set_route(self, user_id: int, route: str) -> None:
        await self.user(user_id)
        await self.db.execute("UPDATE users SET route = ? WHERE user_id = ?", (route, user_id))
        await self.db.commit()

    async def add_xp(self, user_id: int, amount: int, reason: str, today: date) -> XPResult:
        """Add XP and update the streak. Amount may be 0 (still counts as activity)."""
        u = await self.user(user_id)
        last = date.fromisoformat(u.last_active) if u.last_active else None
        streak = next_streak(last, today, u.streak)
        new_xp = u.xp + max(0, amount)
        await self.db.execute("UPDATE users SET xp = ?, streak = ?, last_active = ? WHERE user_id = ?",
                              (new_xp, streak, today.isoformat(), user_id))
        if amount:
            await self.db.execute("INSERT INTO xp_log VALUES (?, ?, ?, ?)", (user_id, amount, reason, time.time()))
        await self.db.commit()
        return XPResult(u.xp, new_xp, streak)

    async def set_best_mock(self, user_id: int, score: int) -> None:
        await self.user(user_id)
        await self.db.execute("UPDATE users SET best_mock = MAX(best_mock, ?) WHERE user_id = ?", (score, user_id))
        await self.db.commit()

    # ---------- progress ----------
    async def mark(self, user_id: int, kind: str, item_id: str) -> bool:
        """Record completion. Returns True if this is the first time."""
        cur = await self.db.execute("INSERT OR IGNORE INTO progress VALUES (?, ?, ?, ?)",
                                    (user_id, kind, item_id, time.time()))
        await self.db.commit()
        return cur.rowcount == 1

    async def has(self, user_id: int, kind: str, item_id: str) -> bool:
        async with self.db.execute("SELECT 1 FROM progress WHERE user_id=? AND kind=? AND item_id=?",
                                   (user_id, kind, item_id)) as cur:
            return await cur.fetchone() is not None

    async def items(self, user_id: int, kind: str) -> set[str]:
        async with self.db.execute("SELECT item_id FROM progress WHERE user_id=? AND kind=?", (user_id, kind)) as cur:
            return {r[0] async for r in cur}

    # ---------- quizzes ----------
    async def record_quiz(self, user_id: int, quiz_id: str, correct: bool) -> bool:
        """Store an attempt. Returns True if it was the user's first attempt at this quiz."""
        async with self.db.execute("SELECT COUNT(*) FROM quiz_attempts WHERE user_id=? AND quiz_id=?",
                                   (user_id, quiz_id)) as cur:
            (n,) = await cur.fetchone()
        await self.db.execute("INSERT INTO quiz_attempts VALUES (?, ?, ?, ?)", (user_id, quiz_id, int(correct), time.time()))
        await self.db.commit()
        return n == 0

    async def quiz_solvers(self, quiz_id: str) -> int:
        async with self.db.execute("SELECT COUNT(DISTINCT user_id) FROM quiz_attempts WHERE quiz_id=? AND correct=1",
                                   (quiz_id,)) as cur:
            (n,) = await cur.fetchone()
        return n

    async def quiz_correct_count(self, user_id: int) -> int:
        async with self.db.execute("SELECT COUNT(DISTINCT quiz_id) FROM quiz_attempts WHERE user_id=? AND correct=1",
                                   (user_id,)) as cur:
            (n,) = await cur.fetchone()
        return n

    async def unanswered_quizzes(self, user_id: int, quiz_ids: list[str]) -> list[str]:
        async with self.db.execute("SELECT DISTINCT quiz_id FROM quiz_attempts WHERE user_id=? AND correct=1",
                                   (user_id,)) as cur:
            done = {r[0] async for r in cur}
        return [q for q in quiz_ids if q not in done]

    # ---------- badges ----------
    async def badges(self, user_id: int) -> set[str]:
        async with self.db.execute("SELECT badge_id FROM badges WHERE user_id=?", (user_id,)) as cur:
            return {r[0] async for r in cur}

    async def grant_badge(self, user_id: int, badge_id: str) -> bool:
        cur = await self.db.execute("INSERT OR IGNORE INTO badges VALUES (?, ?, ?)", (user_id, badge_id, time.time()))
        await self.db.commit()
        return cur.rowcount == 1

    async def learner_state(self, user_id: int) -> LearnerState:
        u = await self.user(user_id)
        return LearnerState(
            completed_episodes=await self.items(user_id, "episode"),
            hunts_solved=len(await self.items(user_id, "hunt")),
            quiz_correct=await self.quiz_correct_count(user_id),
            streak=u.streak,
            best_mock=u.best_mock,
            used_kvcalc=await self.has(user_id, "tool", "kvcalc"),
            badges=await self.badges(user_id),
            hot_takes_voted=await self.votes_cast(user_id),
        )

    # ---------- hot takes ----------
    async def vote(self, user_id: int, take_id: str, agree: bool) -> bool:
        """Record or change a vote. Returns True if this is the user's first vote on this take."""
        async with self.db.execute("SELECT 1 FROM hottake_votes WHERE user_id=? AND take_id=?",
                                   (user_id, take_id)) as cur:
            existed = await cur.fetchone() is not None
        await self.db.execute("INSERT OR REPLACE INTO hottake_votes VALUES (?, ?, ?, ?)",
                              (user_id, take_id, int(agree), time.time()))
        await self.db.commit()
        return not existed

    async def tally(self, take_id: str) -> tuple[int, int]:
        async with self.db.execute("SELECT SUM(agree), COUNT(*) FROM hottake_votes WHERE take_id=?", (take_id,)) as cur:
            row = await cur.fetchone()
        agree = int(row[0] or 0)
        return agree, int(row[1] or 0) - agree

    async def voted_takes(self, user_id: int) -> set[str]:
        async with self.db.execute("SELECT take_id FROM hottake_votes WHERE user_id=?", (user_id,)) as cur:
            return {r[0] async for r in cur}

    async def votes_cast(self, user_id: int) -> int:
        async with self.db.execute("SELECT COUNT(*) FROM hottake_votes WHERE user_id=?", (user_id,)) as cur:
            (n,) = await cur.fetchone()
        return int(n)

    # ---------- leaderboard ----------
    async def leaderboard(self, limit: int = 10, since: float | None = None) -> list[tuple[int, int]]:
        if since is None:
            sql, args = "SELECT user_id, xp FROM users WHERE xp > 0 ORDER BY xp DESC, user_id LIMIT ?", (limit,)
        else:
            sql = ("SELECT user_id, SUM(amount) AS s FROM xp_log WHERE ts >= ? GROUP BY user_id "
                   "HAVING s > 0 ORDER BY s DESC, user_id LIMIT ?")
            args = (since, limit)
        async with self.db.execute(sql, args) as cur:
            return [(r[0], r[1]) async for r in cur]

    async def rank_of(self, user_id: int) -> int:
        u = await self.user(user_id)
        async with self.db.execute("SELECT COUNT(*) FROM users WHERE xp > ?", (u.xp,)) as cur:
            (n,) = await cur.fetchone()
        return n + 1

    # ---------- guild settings / posted markers ----------
    async def set_setting(self, guild_id: int, key: str, value: str | None) -> None:
        await self.db.execute("INSERT OR REPLACE INTO guild_settings VALUES (?, ?, ?)", (guild_id, key, value))
        await self.db.commit()

    async def setting(self, guild_id: int, key: str) -> str | None:
        async with self.db.execute("SELECT value FROM guild_settings WHERE guild_id=? AND key=?", (guild_id, key)) as cur:
            row = await cur.fetchone()
        return row[0] if row else None

    async def guilds_with(self, key: str) -> list[tuple[int, str]]:
        async with self.db.execute("SELECT guild_id, value FROM guild_settings WHERE key=? AND value IS NOT NULL",
                                   (key,)) as cur:
            return [(r[0], r[1]) async for r in cur]

    async def mark_posted(self, scope: str, key: str) -> bool:
        cur = await self.db.execute("INSERT OR IGNORE INTO posted VALUES (?, ?, ?)", (scope, key, time.time()))
        await self.db.commit()
        return cur.rowcount == 1

    async def was_posted(self, scope: str, key: str) -> bool:
        async with self.db.execute("SELECT 1 FROM posted WHERE scope=? AND key=?", (scope, key)) as cur:
            return await cur.fetchone() is not None
