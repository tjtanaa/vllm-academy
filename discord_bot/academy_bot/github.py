"""Minimal GitHub REST client for good-first-issues and the release radar, with a small TTL cache."""
from __future__ import annotations

import logging
import time
from urllib.parse import quote

import aiohttp

log = logging.getLogger("academy.github")
API = "https://api.github.com"
VLLM = "vllm-project/vllm"


class GitHub:
    def __init__(self, token: str | None = None, ttl: float = 600.0):
        self.token = token
        self.ttl = ttl
        self._session: aiohttp.ClientSession | None = None
        self._cache: dict[str, tuple[float, object]] = {}

    async def _get(self, path: str) -> object:
        hit = self._cache.get(path)
        if hit and time.monotonic() - hit[0] < self.ttl:
            return hit[1]
        if self._session is None or self._session.closed:
            headers = {"Accept": "application/vnd.github+json", "User-Agent": "vllm-academy-bot"}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            self._session = aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=15))
        async with self._session.get(API + path) as resp:
            resp.raise_for_status()
            data = await resp.json()
        self._cache[path] = (time.monotonic(), data)
        return data

    async def good_first_issues(self, limit: int = 8) -> list[dict]:
        q = f'repo:{VLLM} is:issue is:open label:"good first issue" no:assignee'
        data = await self._get(f"/search/issues?q={quote(q)}&sort=created&order=desc&per_page={limit}")
        return [{"number": i["number"], "title": i["title"], "url": i["html_url"],
                 "comments": i.get("comments", 0), "labels": [lb["name"] for lb in i.get("labels", [])]}
                for i in data.get("items", [])]  # type: ignore[union-attr]

    async def latest_release(self) -> dict | None:
        self._cache.pop(f"/repos/{VLLM}/releases/latest", None)  # always fresh for the radar
        data = await self._get(f"/repos/{VLLM}/releases/latest")
        if not isinstance(data, dict) or "tag_name" not in data:
            return None
        return {"tag": data["tag_name"], "name": data.get("name") or data["tag_name"], "url": data["html_url"],
                "body": data.get("body") or "", "published": data.get("published_at", "")}

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
