"""Run the bot:  python -m academy_bot  (from the discord_bot/ directory).

Extra commands:
    python -m academy_bot --check          validate the content pack and exit (no token needed)
    python -m academy_bot --render-cards   pre-render episode covers and the banner into academy/assets/cards
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    """Tiny .env reader so a pip install of python-dotenv isn't required."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="academy_bot", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--check", action="store_true", help="validate content and exit")
    p.add_argument("--render-cards", action="store_true", help="render episode covers + banner PNGs and exit")
    a = p.parse_args(argv)
    _load_dotenv(Path.cwd() / ".env")
    _load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    from .config import REPO_ROOT, Settings
    from .content import load_content, validate

    settings = Settings.from_env()
    content = load_content(settings.content_dir, settings.labs_dir, REPO_ROOT)
    problems = validate(content, REPO_ROOT)
    if a.check:
        print(content.summary())
        for prob in problems:
            print(" -", prob)
        print("OK" if not problems else f"{len(problems)} problem(s)")
        return 1 if problems else 0
    if a.render_cards:
        from . import cards
        out = settings.assets_dir / "cards"
        out.mkdir(parents=True, exist_ok=True)
        (out / "banner.png").write_bytes(cards.banner())
        for ep in content.episodes:
            s = content.season(ep.season)
            (out / f"{ep.id}.png").write_bytes(cards.episode_cover(
                ep_id=ep.id, title_en=ep.title["en"], title_zh=ep.title["zh"], season_label_en=f"{s.id} {s.title['en']}",
                season_label_zh=s.title["zh"], color=s.color, minutes=ep.minutes, xp=ep.xp))
        print(f"Rendered banner + {len(content.episodes)} covers into {out}"
              + ("" if cards.has_cjk_font() else " (WARNING: no CJK font found; Chinese will not render)"))
        return 0
    if not settings.token:
        print("DISCORD_TOKEN is not set. Copy discord_bot/.env.example to discord_bot/.env and fill it in.",
              file=sys.stderr)
        return 2
    if problems:
        logging.getLogger("academy").warning("%d content problem(s); run with --check for details", len(problems))

    from .bot import AcademyBot
    AcademyBot(settings).run(settings.token, log_handler=None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
