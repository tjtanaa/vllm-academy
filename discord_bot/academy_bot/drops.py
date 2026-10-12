"""Pure logic for scheduled posts: the Daily Drop rotation and Release Radar study links.

No Discord imports, so it is unit-tested directly.
"""
from __future__ import annotations

import re
from datetime import date

from .content import Content

# Monday=0 … Sunday=6. Friday is hot-take day, the same day the vLLM Weekly newsletter goes out.
WEEKLY_ROTATION = {0: "quiz", 1: "interview", 2: "term", 3: "hunt", 4: "hottake", 5: "trend", 6: "episode"}


def _pick(items: list, day: date, salt: int = 0):
    if not items:
        return None
    return items[(day.toordinal() * 7 + salt) % len(items)]


def daily_drop(content: Content, day: date) -> tuple[str, object]:
    """Return (kind, item) for the given day. Deterministic, so a restart never posts a different drop."""
    kind = WEEKLY_ROTATION[day.weekday()]
    pools = {
        "quiz": content.quizzes,
        "interview": content.interview,
        "term": content.glossary,
        "hunt": content.hunts,
        "hottake": [h for h in content.hottakes.get("takes", []) if not h.get("verdict")],
        "trend": content.trends.get("trends", []),
        "episode": content.episodes,
    }
    item = _pick(pools[kind], day)
    if item is None:  # empty pool: fall back to a quiz
        return "quiz", _pick(content.quizzes, day)
    return kind, item


# Release-note keywords → episodes worth (re)watching. Order matters: first matches are listed first.
STUDY_MAP: list[tuple[str, str]] = [
    (r"specul|eagle|mtp|dflash|draft", "E17"),
    (r"quant|fp8|fp4|nvfp4|int4|awq|gptq|w4a16", "E18"),
    (r"tensor.?parallel|pipeline.?parallel|expert.?parallel|\bep\b|all2all|all-to-all|moe", "E19"),
    (r"disagg|p/d|kv.?transfer|connector|nixl|mooncake|lmcache", "E20"),
    (r"offload|hisparse|tier", "E21"),
    (r"\brl\b|weight.?transfer|rollout|sleep", "E22"),
    (r"prefix|cache hit", "E10"),
    (r"chunked|max.?num.?batched|max.?num.?(active.?)?seqs|schedul|preempt", "E11"),
    (r"cuda.?graph|torch\.compile|compile|attention backend|flashinfer|flashmla|triton|rocm|kernel", "E15"),
    (r"model runner|mrv2|runner v2", "E15"),
    (r"preload|snapshot|criu|fast start|ipc_cache|startup|cold", "E28"),
    (r"agent|agentx|tool.?call", "E27"),
    (r"new model|support for|day.?0|architecture", "E16"),
    (r"frontend|openai|api server|rust|grpc|render", "E13"),
]


def study_links(release_body: str, limit: int = 4) -> list[str]:
    """Episodes that help a learner understand a release, ranked by first mention."""
    text = (release_body or "").lower()
    hits: list[tuple[int, str]] = []
    for pattern, ep in STUDY_MAP:
        m = re.search(pattern, text)
        if m and ep not in [e for _, e in hits]:
            hits.append((m.start(), ep))
    hits.sort()
    return [ep for _, ep in hits[:limit]]


def release_highlights(body: str, limit: int = 8) -> list[str]:
    """First bullet lines of a GitHub release body, cleaned for an embed."""
    out = []
    for line in (body or "").splitlines():
        s = line.strip()
        if not re.match(r"^[-*•]\s+", s):
            continue
        s = re.sub(r"^[-*•]\s+", "", s)
        s = re.sub(r"\(\[?#\d+\]?(\([^)]*\))?\)", "", s)  # drop "(#12345)" PR refs
        s = re.sub(r"https?://\S+", "", s).strip(" ,;")
        if len(s) > 4:
            out.append(s[:180])
        if len(out) >= limit:
            break
    return out


def take_verdict(take: dict, override: str | None = None) -> tuple[str | None, str]:
    """A moderator override (stored in the DB as 'verdict|note') wins over the YAML verdict."""
    if override:
        verdict, _, note = override.partition("|")
        return verdict or None, note
    return take.get("verdict"), take.get("verdict_note", "")
