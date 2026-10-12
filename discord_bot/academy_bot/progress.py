"""XP, levels, streaks and badge rules. Pure functions, unit-tested."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

XP = {
    "episode": 50,
    "quiz_first_try": 15,
    "quiz_correct": 10,
    "lab": 75,
    "mock_max": 100,
    "daily_bonus": 5,
    "kvcalc_first": 10,
    "award": 200,
    "hottake_vote": 5,
}


@dataclass
class LevelInfo:
    level: int
    rank: dict
    next_rank: dict | None
    xp: int

    @property
    def progress(self) -> float:
        """Fraction of the way from this rank to the next (1.0 at max)."""
        if self.next_rank is None:
            return 1.0
        lo, hi = self.rank["xp"], self.next_rank["xp"]
        return max(0.0, min(1.0, (self.xp - lo) / max(1, hi - lo)))

    @property
    def to_next(self) -> int:
        return 0 if self.next_rank is None else max(0, self.next_rank["xp"] - self.xp)


def level_for(xp: int, ranks: list[dict]) -> LevelInfo:
    ranks = sorted(ranks, key=lambda r: r["xp"])
    current = ranks[0]
    nxt = None
    for i, r in enumerate(ranks):
        if xp >= r["xp"]:
            current = r
            nxt = ranks[i + 1] if i + 1 < len(ranks) else None
    return LevelInfo(level=current["level"], rank=current, next_rank=nxt, xp=xp)


def next_streak(last_active: date | None, today: date, streak: int) -> int:
    if last_active is None:
        return 1
    if last_active == today:
        return max(1, streak)
    if last_active == today - timedelta(days=1):
        return streak + 1
    return 1


@dataclass
class LearnerState:
    completed_episodes: set[str] = field(default_factory=set)
    hunts_solved: int = 0
    quiz_correct: int = 0
    streak: int = 0
    best_mock: int = 0
    used_kvcalc: bool = False
    badges: set[str] = field(default_factory=set)
    hot_takes_voted: int = 0


def earned_badges(state: LearnerState, season_episodes: dict[str, list[str]]) -> set[str]:
    """All badges the learner qualifies for (moderator-only badges excluded)."""
    got: set[str] = set()
    done = state.completed_episodes
    if "E01" in done:
        got.add("first_token")
    if "E07" in done and state.used_kvcalc:
        got.add("kv_accountant")
    if season_episodes.get("S1") and set(season_episodes["S1"]) <= done:
        got.add("pager")
    if season_episodes.get("S2") and set(season_episodes["S2"]) <= done:
        got.add("engine_builder")
    if state.hunts_solved >= 5:
        got.add("navigator")
    if state.best_mock >= 80:
        got.add("interview_ready")
    if state.streak >= 7:
        got.add("streak7")
    if state.quiz_correct >= 50:
        got.add("quiz_whiz")
    if state.hot_takes_voted >= 5:
        got.add("oracle")
    if season_episodes.get("S6") and set(season_episodes["S6"]) <= done:
        got.add("frontier")
    return got


def new_badges(state: LearnerState, season_episodes: dict[str, list[str]]) -> list[str]:
    return sorted(earned_badges(state, season_episodes) - state.badges)


def progress_bar(fraction: float, width: int = 10, full: str = "▰", empty: str = "▱") -> str:
    fraction = max(0.0, min(1.0, fraction))
    filled = round(fraction * width)
    return full * filled + empty * (width - filled)


def normalize_answer(text: str) -> str:
    text = text.strip().strip("`'\"“”‘’").strip()
    while text.startswith("./"):
        text = text[2:]
    return "".join(text.split()).lower().rstrip("/")


def check_hunt(answer: str, accepted: list[str]) -> bool:
    got = normalize_answer(answer)
    return any(got == normalize_answer(a) for a in accepted)


def mock_xp(score_pct: int) -> int:
    return round(XP["mock_max"] * max(0, min(100, score_pct)) / 100)
