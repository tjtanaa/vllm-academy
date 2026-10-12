"""Runtime settings, read from environment variables (see .env.example)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int | None = None) -> int | None:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return int(value)


@dataclass
class Settings:
    token: str = ""
    guild_ids: list[int] = field(default_factory=list)
    content_dir: Path = REPO_ROOT / "academy" / "content"
    labs_dir: Path = REPO_ROOT / "academy" / "labs"
    assets_dir: Path = REPO_ROOT / "academy" / "assets"
    db_path: Path = REPO_ROOT / "discord_bot" / "data" / "academy.sqlite3"
    default_lang: str = "zh"
    timezone: str = "Asia/Taipei"
    daily_hour: int = 20
    daily_channel_id: int | None = None
    announce_channel_id: int | None = None
    github_token: str | None = None
    repo_url: str = "https://github.com/tjtanaa/vllm-academy"
    repo_branch: str = "main"
    level_roles: bool = True
    public_level_up: bool = True
    release_radar: bool = True

    @classmethod
    def from_env(cls) -> "Settings":
        s = cls()
        s.token = os.getenv("DISCORD_TOKEN", "")
        guilds = os.getenv("DISCORD_GUILD_IDS", "") or os.getenv("DISCORD_GUILD_ID", "")
        s.guild_ids = [int(g) for g in guilds.replace(" ", "").split(",") if g]
        if os.getenv("ACADEMY_CONTENT_DIR"):
            s.content_dir = Path(os.environ["ACADEMY_CONTENT_DIR"])
        if os.getenv("ACADEMY_LABS_DIR"):
            s.labs_dir = Path(os.environ["ACADEMY_LABS_DIR"])
        if os.getenv("ACADEMY_ASSETS_DIR"):
            s.assets_dir = Path(os.environ["ACADEMY_ASSETS_DIR"])
        if os.getenv("ACADEMY_DB_PATH"):
            s.db_path = Path(os.environ["ACADEMY_DB_PATH"])
        lang = os.getenv("ACADEMY_DEFAULT_LANG", s.default_lang).lower()
        s.default_lang = "zh" if lang.startswith("zh") else "en"
        s.timezone = os.getenv("ACADEMY_TIMEZONE", s.timezone)
        s.daily_hour = _env_int("ACADEMY_DAILY_HOUR", s.daily_hour) or 0
        s.daily_channel_id = _env_int("ACADEMY_DAILY_CHANNEL_ID")
        s.announce_channel_id = _env_int("ACADEMY_ANNOUNCE_CHANNEL_ID")
        s.github_token = os.getenv("GITHUB_TOKEN") or None
        s.repo_url = os.getenv("ACADEMY_REPO_URL", s.repo_url).rstrip("/")
        s.repo_branch = os.getenv("ACADEMY_REPO_BRANCH", s.repo_branch)
        s.level_roles = _env_bool("ACADEMY_LEVEL_ROLES", s.level_roles)
        s.public_level_up = _env_bool("ACADEMY_PUBLIC_LEVEL_UP", s.public_level_up)
        s.release_radar = _env_bool("ACADEMY_RELEASE_RADAR", s.release_radar)
        return s

    def repo_link(self, relative_path: str) -> str:
        """GitHub URL for a file in this repository."""
        while relative_path.startswith("./"):
            relative_path = relative_path[2:]
        relative_path = relative_path.lstrip("/")
        return f"{self.repo_url}/blob/{self.repo_branch}/{relative_path}"
