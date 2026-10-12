"""Load and validate the bilingual Academy content (academy/content/*.yaml, academy/labs/*.md).

Pure Python: no Discord imports, so it can be tested and reused by tools.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .i18n import LANGS

Bi = dict  # {"en": ..., "zh": ...}


@dataclass
class Season:
    id: str
    emoji: str
    color: int
    title: Bi
    tagline: Bi


@dataclass
class Episode:
    id: str
    season: str
    minutes: int
    title: Bi
    hook: Bi
    aha: Bi
    tldr: Bi
    pro: Bi
    followup: Bi
    lab: str | None
    lab_hint: Bi
    deep_dive: str
    code: list[str]
    xp: int = 50

    @property
    def number(self) -> int:
        return int(self.id[1:])


@dataclass
class Quiz:
    id: str
    episode: str
    q: Bi
    options: Bi
    answer: int
    explain: Bi


@dataclass
class InterviewQ:
    id: str
    level: str
    kind: str
    episode: str
    q: Bi
    points: Bi
    followups: Bi
    red_flags: Bi


@dataclass
class Hunt:
    id: str
    xp: int
    difficulty: int
    q: Bi
    hint: Bi
    answers: list[str]
    explain: Bi
    code: str


@dataclass
class CodeEntry:
    id: str
    area: str
    title: Bi
    path: str
    line: int
    symbol: str
    owns: Bi
    try_: Bi


@dataclass
class LabStep:
    title: str
    body: str
    code: str | None
    checkpoint: str | None


@dataclass
class Lab:
    id: str
    title: Bi
    path: Bi  # repo-relative markdown paths per language
    steps: dict[str, list[LabStep]]
    xp: int = 75


@dataclass
class Content:
    seasons: list[Season]
    routes: list[dict]
    ranks: list[dict]
    badges: list[dict]
    episodes: list[Episode]
    quizzes: list[Quiz]
    interview: list[InterviewQ]
    hunts: list[Hunt]
    code_pin: dict
    code_areas: list[dict]
    code: list[CodeEntry]
    trace: dict
    glossary: list[dict]
    trends: dict
    careers: list[dict]
    community: dict
    labs: list[Lab] = field(default_factory=list)
    hottakes: dict = field(default_factory=lambda: {"takes": []})

    # ---- lookups ----
    def episode(self, ep_id: str) -> Episode | None:
        ep_id = normalize_episode_id(ep_id)
        return next((e for e in self.episodes if e.id == ep_id), None)

    def season(self, season_id: str) -> Season | None:
        return next((s for s in self.seasons if s.id == season_id), None)

    def season_episodes(self, season_id: str) -> list[Episode]:
        return [e for e in self.episodes if e.season == season_id]

    def next_episode(self, ep_id: str) -> Episode | None:
        ids = [e.id for e in self.episodes]
        if ep_id not in ids:
            return None
        i = ids.index(ep_id)
        return self.episodes[i + 1] if i + 1 < len(ids) else None

    def quizzes_for(self, ep_id: str) -> list[Quiz]:
        return [q for q in self.quizzes if q.episode == ep_id]

    def quiz(self, quiz_id: str) -> Quiz | None:
        return next((q for q in self.quizzes if q.id == quiz_id), None)

    def interview_q(self, iv_id: str) -> InterviewQ | None:
        return next((q for q in self.interview if q.id == iv_id), None)

    def hunt(self, hunt_id: str) -> Hunt | None:
        hunt_id = hunt_id.upper()
        return next((h for h in self.hunts if h.id == hunt_id), None)

    def code_entry(self, code_id: str) -> CodeEntry | None:
        return next((c for c in self.code if c.id == code_id), None)

    def lab(self, lab_id: str) -> Lab | None:
        lab_id = lab_id.upper()
        return next((lab for lab in self.labs if lab.id == lab_id), None)

    def hottake(self, take_id: str) -> dict | None:
        take_id = take_id.strip().lower()
        return next((h for h in self.hottakes.get("takes", []) if h["id"] == take_id), None)

    def route(self, route_id: str) -> dict | None:
        return next((r for r in self.routes if r["id"] == route_id), None)

    def badge(self, badge_id: str) -> dict | None:
        return next((b for b in self.badges if b["id"] == badge_id), None)

    def term(self, query: str) -> dict | None:
        q = query.strip().lower()
        for g in self.glossary:
            names = [g["term"].lower(), g["zh_term"].lower()] + [a.lower() for a in g.get("aliases", [])]
            if q in names:
                return g
        for g in self.glossary:
            if q and (q in g["term"].lower() or q in g["zh_term"].lower()):
                return g
        return None

    def permalink(self, entry: CodeEntry) -> str:
        repo, commit = self.code_pin["repo"], self.code_pin["commit"]
        anchor = f"#L{entry.line}" if entry.line and entry.line > 1 else ""
        return f"https://github.com/{repo}/blob/{commit}/{entry.path}{anchor}"

    def summary(self) -> str:
        return (f"{len(self.episodes)} episodes, {len(self.quizzes)} quizzes, {len(self.interview)} interview Qs, "
                f"{len(self.hunts)} hunts, {len(self.code)} code entries, {len(self.glossary)} terms, "
                f"{len(self.labs)} labs, {len(self.hottakes.get('takes', []))} hot takes")


def normalize_episode_id(value: str) -> str:
    value = value.strip().upper()
    m = re.match(r"^E?(\d{1,2})", value)
    return f"E{int(m.group(1)):02d}" if m else value


def _color(hex_color: str) -> int:
    return int(hex_color.lstrip("#"), 16)


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# ---------------- lab markdown parsing ----------------
_STEP_RE = re.compile(r"^##\s+(\d+)[.)、]\s*(.+?)\s*$", re.M)
_CODE_RE = re.compile(r"```[a-zA-Z0-9_-]*\n(.*?)```", re.S)
_CHECK_RE = re.compile(r"^>\s*(?:✅\s*)?\*\*(?:Checkpoint|檢查點)[:：]?\*\*[:：]?\s*(.+?)$", re.M)
_TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.M)


def parse_lab_markdown(text: str) -> tuple[str, list[LabStep]]:
    """Split a lab file into numbered steps (`## 1. Title`).

    Each step keeps its first paragraph, its first code block and its
    `> ✅ **Checkpoint:** ...` line. The format is enforced by tests.
    """
    title_m = _TITLE_RE.search(text)
    title = title_m.group(1).strip() if title_m else ""
    matches = list(_STEP_RE.finditer(text))
    steps: list[LabStep] = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        # stop the last step at the next level-2 heading that is not numbered
        chunk = text[m.end():end]
        nxt = re.search(r"^##\s+(?!\d)", chunk, re.M)
        if nxt:
            chunk = chunk[:nxt.start()]
        code_m = _CODE_RE.search(chunk)
        check_m = _CHECK_RE.search(chunk)
        prose = _CODE_RE.sub("", chunk)
        prose = _CHECK_RE.sub("", prose)
        paragraphs = [p.strip() for p in prose.strip().split("\n\n") if p.strip() and not p.strip().startswith(">")]
        body = paragraphs[0] if paragraphs else ""
        steps.append(LabStep(title=m.group(2).strip(), body=body,
                             code=code_m.group(1).rstrip() if code_m else None,
                             checkpoint=check_m.group(1).strip() if check_m else None))
    return title, steps


def load_labs(labs_dir: Path, repo_root: Path) -> list[Lab]:
    labs: list[Lab] = []
    if not labs_dir.is_dir():
        return labs
    for en_path in sorted(labs_dir.glob("Q*-*.md")):
        if en_path.name.endswith(".zh-TW.md"):
            continue
        lab_id = en_path.name.split("-", 1)[0].upper()
        zh_path = en_path.with_name(en_path.name[:-3] + ".zh-TW.md")
        en_title, en_steps = parse_lab_markdown(en_path.read_text(encoding="utf-8"))
        if zh_path.exists():
            zh_title, zh_steps = parse_lab_markdown(zh_path.read_text(encoding="utf-8"))
        else:
            zh_title, zh_steps = en_title, en_steps
        rel = lambda p: p.resolve().relative_to(repo_root.resolve()).as_posix()  # noqa: E731
        labs.append(Lab(id=lab_id, title={"en": en_title, "zh": zh_title},
                        path={"en": rel(en_path), "zh": rel(zh_path) if zh_path.exists() else rel(en_path)},
                        steps={"en": en_steps, "zh": zh_steps}))
    return labs


# ---------------- loader ----------------
def load_content(content_dir: Path, labs_dir: Path | None = None, repo_root: Path | None = None) -> Content:
    content_dir = Path(content_dir)
    seasons_doc = _load(content_dir / "seasons.yaml")
    episodes: list[Episode] = []
    for f in sorted((content_dir / "episodes").glob("*.yaml")):
        for e in _load(f)["episodes"]:
            episodes.append(Episode(**e))
    episodes.sort(key=lambda e: e.number)
    quizzes = [Quiz(**q) for q in _load(content_dir / "quizzes.yaml")["quizzes"]]
    interview = [InterviewQ(**q) for q in _load(content_dir / "interview.yaml")["interview"]]
    hunts = [Hunt(**h) for h in _load(content_dir / "hunts.yaml")["hunts"]]
    code_doc = _load(content_dir / "codemap.yaml")
    code = []
    for c in code_doc["entries"]:
        c = dict(c)
        c["try_"] = c.pop("try")
        code.append(CodeEntry(**c))
    content = Content(
        seasons=[Season(id=s["id"], emoji=s["emoji"], color=_color(s["color"]), title=s["title"], tagline=s["tagline"])
                 for s in seasons_doc["seasons"]],
        routes=seasons_doc["routes"],
        ranks=sorted(seasons_doc["ranks"], key=lambda r: r["xp"]),
        badges=seasons_doc["badges"],
        episodes=episodes,
        quizzes=quizzes,
        interview=interview,
        hunts=hunts,
        code_pin=code_doc["pin"],
        code_areas=code_doc["areas"],
        code=code,
        trace=_load(content_dir / "trace.yaml"),
        glossary=_load(content_dir / "glossary.yaml")["glossary"],
        trends=_load(content_dir / "trends.yaml"),
        careers=_load(content_dir / "careers.yaml")["careers"],
        community=_load(content_dir / "community.yaml"),
    )
    if (content_dir / "hottakes.yaml").exists():
        content.hottakes = _load(content_dir / "hottakes.yaml")
    if labs_dir is not None:
        content.labs = load_labs(Path(labs_dir), Path(repo_root or content_dir.parents[1]))
    return content


# ---------------- validation ----------------
def _bi_ok(value: Any, where: str, errors: list[str], *, list_len_match: bool = True) -> None:
    if not isinstance(value, dict):
        errors.append(f"{where}: expected {{en, zh}} mapping")
        return
    for lang in LANGS:
        v = value.get(lang)
        if v in (None, "", []):
            errors.append(f"{where}: missing '{lang}'")
    if list_len_match and isinstance(value.get("en"), list) and isinstance(value.get("zh"), list):
        if len(value["en"]) != len(value["zh"]):
            errors.append(f"{where}: en/zh list lengths differ ({len(value['en'])} vs {len(value['zh'])})")


def validate(content: Content, repo_root: Path | None = None) -> list[str]:
    """Return a list of problems; empty means the content pack is consistent."""
    errors: list[str] = []
    season_ids = {s.id for s in content.seasons}
    ep_ids = [e.id for e in content.episodes]
    code_ids = {c.id for c in content.code}
    lab_ids = {lab.id for lab in content.labs}
    if len(set(ep_ids)) != len(ep_ids):
        errors.append("duplicate episode ids")
    for s in content.seasons:
        _bi_ok(s.title, f"season {s.id}.title", errors)
        _bi_ok(s.tagline, f"season {s.id}.tagline", errors)
    for e in content.episodes:
        w = f"episode {e.id}"
        if e.season not in season_ids:
            errors.append(f"{w}: unknown season {e.season}")
        for name in ("title", "hook", "aha", "tldr", "pro", "followup", "lab_hint"):
            _bi_ok(getattr(e, name), f"{w}.{name}", errors)
        for c in e.code:
            if c not in code_ids:
                errors.append(f"{w}: unknown code entry '{c}'")
        if e.lab and content.labs and e.lab not in lab_ids:
            errors.append(f"{w}: unknown lab '{e.lab}'")
        if repo_root and not (Path(repo_root) / e.deep_dive).exists():
            errors.append(f"{w}: deep_dive path missing: {e.deep_dive}")
        if not content.quizzes_for(e.id):
            errors.append(f"{w}: has no quiz questions")
        if len(L_safe(e.aha, "en")) > 1900 or len(L_safe(e.aha, "zh")) > 1900:
            errors.append(f"{w}: aha too long for an embed")
    seen = set()
    for q in content.quizzes:
        w = f"quiz {q.id}"
        if q.id in seen:
            errors.append(f"{w}: duplicate id")
        seen.add(q.id)
        if q.episode not in ep_ids:
            errors.append(f"{w}: unknown episode {q.episode}")
        _bi_ok(q.q, f"{w}.q", errors)
        _bi_ok(q.options, f"{w}.options", errors)
        _bi_ok(q.explain, f"{w}.explain", errors)
        n = len(q.options.get("en", []))
        if not 2 <= n <= 5:
            errors.append(f"{w}: needs 2-5 options")
        if not 0 <= q.answer < n:
            errors.append(f"{w}: answer index out of range")
        for lang in LANGS:
            if any(len(o) > 200 for o in q.options.get(lang, [])):
                errors.append(f"{w}: option longer than 200 chars ({lang})")
    for iv in content.interview:
        w = f"interview {iv.id}"
        if iv.level not in {"junior", "mid", "senior"}:
            errors.append(f"{w}: bad level {iv.level}")
        if iv.episode not in ep_ids:
            errors.append(f"{w}: unknown episode {iv.episode}")
        for name in ("q", "points", "followups", "red_flags"):
            _bi_ok(getattr(iv, name), f"{w}.{name}", errors)
    for h in content.hunts:
        w = f"hunt {h.id}"
        for name in ("q", "hint", "explain"):
            _bi_ok(getattr(h, name), f"{w}.{name}", errors)
        if not h.answers:
            errors.append(f"{w}: no answers")
        if h.code not in code_ids:
            errors.append(f"{w}: unknown code entry {h.code}")
    for c in content.code:
        w = f"code {c.id}"
        for name in ("title", "owns", "try_"):
            _bi_ok(getattr(c, name), f"{w}.{name}", errors)
        if c.area not in {a["id"] for a in content.code_areas}:
            errors.append(f"{w}: unknown area {c.area}")
    for stop in content.trace["stops"]:
        if stop["code"] not in code_ids:
            errors.append(f"trace stop {stop['n']}: unknown code entry {stop['code']}")
        for name in ("process", "title", "what", "carries"):
            _bi_ok(stop[name], f"trace stop {stop['n']}.{name}", errors)
    for g in content.glossary:
        if not g.get("en") or not g.get("zh"):
            errors.append(f"glossary {g.get('term')}: missing language")
        if g.get("episode") not in ep_ids:
            errors.append(f"glossary {g.get('term')}: unknown episode")
    for tr in content.trends["trends"]:
        for name in ("title", "body", "why"):
            _bi_ok(tr[name], f"trend {tr['id']}.{name}", errors)
        if not str(tr.get("source", "")).startswith("https://"):
            errors.append(f"trend {tr['id']}: needs an https source")
    for h in content.hottakes.get("takes", []):
        w = f"hottake {h.get('id')}"
        for name in ("claim", "evidence", "wrong_if"):
            _bi_ok(h.get(name), f"{w}.{name}", errors)
        if not 0 < int(h.get("confidence", 0)) < 100:
            errors.append(f"{w}: confidence must be 1-99")
        if not str(h.get("source", "")).startswith("https://"):
            errors.append(f"{w}: needs an https source")
        if h.get("episode") not in ep_ids:
            errors.append(f"{w}: unknown episode {h.get('episode')}")
        if h.get("verdict") not in (None, "right", "wrong", "partly"):
            errors.append(f"{w}: verdict must be right, wrong or partly")
    for r in content.routes:
        for ep in r["path"]:
            if ep not in ep_ids:
                errors.append(f"route {r['id']}: unknown episode {ep}")
    for cr in content.careers:
        for name in ("title", "pitch", "skills", "proof"):
            _bi_ok(cr[name], f"career {cr['id']}.{name}", errors)
        for ep in cr["episodes"]:
            if ep not in ep_ids:
                errors.append(f"career {cr['id']}: unknown episode {ep}")
    for lab in content.labs:
        en, zh = lab.steps["en"], lab.steps["zh"]
        if len(en) < 3:
            errors.append(f"lab {lab.id}: fewer than 3 numbered steps")
        if len(en) != len(zh):
            errors.append(f"lab {lab.id}: en has {len(en)} steps, zh has {len(zh)}")
        for i, step in enumerate(en, 1):
            if not step.checkpoint:
                errors.append(f"lab {lab.id} step {i}: missing checkpoint")
    return errors


def L_safe(value: Any, lang: str) -> str:
    if isinstance(value, dict):
        v = value.get(lang) or ""
        return "\n".join(v) if isinstance(v, list) else str(v)
    return str(value or "")
