"""Tiny terminal helpers shared by the zero-install labs. Standard library only."""
from __future__ import annotations

import os
import sys
import time

_ON = sys.stdout.isatty() and os.getenv("NO_COLOR") is None and os.getenv("TERM") != "dumb"

CODES = {
    "reset": "0", "bold": "1", "dim": "2", "under": "4",
    "red": "31", "green": "32", "yellow": "33", "blue": "34", "magenta": "35", "cyan": "36", "white": "37",
    "gray": "90", "bred": "91", "bgreen": "92", "byellow": "93", "bblue": "94", "bmagenta": "95", "bcyan": "96",
}
# Request colors, in order of appearance.
PALETTE = ["bcyan", "bmagenta", "byellow", "bgreen", "bblue", "bred", "cyan", "magenta"]


def set_color(enabled: bool) -> None:
    global _ON
    _ON = enabled


def c(text: str, *styles: str) -> str:
    if not _ON or not styles:
        return text
    return "".join(f"\033[{CODES[s]}m" for s in styles) + text + "\033[0m"


def bar(fraction: float, width: int = 30, fill: str = "█", empty: str = "·", style: str = "bcyan") -> str:
    fraction = max(0.0, min(1.0, fraction))
    n = round(fraction * width)
    return c(fill * n, style) + c(empty * (width - n), "gray")


def pause(seconds: float) -> None:
    if seconds > 0:
        sys.stdout.flush()
        time.sleep(seconds)


def rule(title: str = "", width: int = 72) -> str:
    if not title:
        return c("─" * width, "gray")
    side = max(2, (width - len(title) - 2) // 2)
    return c("─" * side, "gray") + " " + c(title, "bold") + " " + c("─" * side, "gray")


def default_delay() -> float:
    return 0.35 if sys.stdout.isatty() else 0.0
