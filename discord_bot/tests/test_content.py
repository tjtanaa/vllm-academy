"""The content pack is the curriculum: every link, id and translation must hold together."""
import re

from academy_bot.config import REPO_ROOT
from academy_bot.content import parse_lab_markdown, validate


def test_content_validates(content):
    assert validate(content, REPO_ROOT) == []


def test_counts(content):
    assert len(content.episodes) == 28
    assert [e.id for e in content.episodes] == [f"E{i:02d}" for i in range(1, 29)]
    assert len(content.labs) == 9
    assert len(content.hottakes["takes"]) >= 10
    assert {s.id for s in content.seasons} == {f"S{i}" for i in range(7)}


def test_every_episode_has_three_quizzes(content):
    for e in content.episodes:
        assert len(content.quizzes_for(e.id)) >= 3, e.id


def test_labs_are_bilingual_with_checkpoints(content):
    for lab in content.labs:
        assert len(lab.steps["en"]) == len(lab.steps["zh"]) >= 5, lab.id
        assert lab.path["zh"].endswith(".zh-TW.md"), lab.id
        for lang in ("en", "zh"):
            for st in lab.steps[lang]:
                assert st.checkpoint and st.body and st.code, (lab.id, lang, st.title)


def test_lab_parser_format():
    md = "# T\n\n## 1. One\nDo it.\n\n```bash\necho hi\n```\n\n> ✅ **檢查點：** ok\n\n## Notes\nignored"
    title, steps = parse_lab_markdown(md)
    assert title == "T" and len(steps) == 1
    assert steps[0].code == "echo hi" and steps[0].checkpoint == "ok"


def test_routes_cover_new_season(content):
    route = content.route("speedrun")
    assert route and "E27" in route["path"] and len(route["path"]) == 10


def test_hottakes_are_labelled_speculation(content):
    for h in content.hottakes["takes"]:
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", str(h["judge_on"])), h["id"]
        assert 0 < h["confidence"] < 100


def test_relative_links_in_academy_markdown_exist():
    root = REPO_ROOT / "academy"
    bad = []
    for md in list(root.rglob("*.md")):
        for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", md.read_text(encoding="utf-8")):
            if target.startswith(("http", "mailto:")):
                continue
            if not (md.parent / target).resolve().exists():
                bad.append(f"{md.relative_to(REPO_ROOT)} → {target}")
    assert bad == []


def test_no_simplified_chinese_terms_in_zh_files():
    banned = ["内存", "代码", "服务器", "默认", "运行", "数据", "网络", "硬件", "软件", "视频", "简历"]
    hits = []
    for p in (REPO_ROOT / "academy").rglob("*.zh-TW.md"):
        text = p.read_text(encoding="utf-8")
        hits += [f"{p.name}: {w}" for w in banned if w in text]
    assert hits == []
