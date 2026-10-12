import sys
from pathlib import Path

import pytest

BOT_DIR = Path(__file__).resolve().parents[1]
REPO = BOT_DIR.parent
sys.path.insert(0, str(BOT_DIR))
sys.path.insert(0, str(REPO / "academy" / "labs"))

from academy_bot.config import REPO_ROOT, Settings  # noqa: E402
from academy_bot.content import load_content  # noqa: E402


@pytest.fixture(scope="session")
def content():
    s = Settings()
    return load_content(s.content_dir, s.labs_dir, REPO_ROOT)
