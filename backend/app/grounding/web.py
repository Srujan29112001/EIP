"""Key-free live grounding: DuckDuckGo search + Google News RSS.

Both fail soft (return []) — the pipeline continues with whatever evidence exists.
"""
from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import quote_plus

import feedparser


def _search_sync(query: str, n: int) -> list[dict[str, Any]]:
    from ddgs import DDGS
    out: list[dict[str, Any]] = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=n):
            out.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": (r.get("body", "") or "")[:280],
            })
    return out


async def search(query: str, n: int = 5) -> list[dict[str, Any]]:
    """EVERY call is a live fetch — nothing is cached between runs. Repeated
    identical queries can get throttled by the source (empty result), which
    used to read as 'stale'; one spaced retry recovers it."""
    for attempt in (1, 2):
        try:
            out = await asyncio.wait_for(asyncio.to_thread(_search_sync, query, n), timeout=20)
            if out:
                return out
        except Exception:
            pass
        if attempt == 1:
            await asyncio.sleep(2.5)   # throttle recovery before the retry
    return []


def _news_sync(query: str, n: int, region: str) -> list[dict[str, Any]]:
    gl, ceid = ("IN", "IN:en") if region.lower().startswith("ind") else ("US", "US:en")
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-{gl}&gl={gl}&ceid={ceid}"
    feed = feedparser.parse(url)
    out = []
    for e in feed.entries[:n]:
        out.append({
            "title": e.get("title", ""),
            "url": e.get("link", ""),
            "published": e.get("published", ""),
            "source": (e.get("source") or {}).get("title", "Google News"),
        })
    return out


async def news(query: str, n: int = 6, region: str = "India") -> list[dict[str, Any]]:
    """Live RSS fetch on every call — retried once if the feed comes back empty."""
    for attempt in (1, 2):
        try:
            out = await asyncio.wait_for(asyncio.to_thread(_news_sync, query, n, region), timeout=20)
            if out:
                return out
        except Exception:
            pass
        if attempt == 1:
            await asyncio.sleep(2.0)
    return []
