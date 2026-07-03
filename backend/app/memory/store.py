"""Run persistence — zero-infra SQLite (MASTER_PLAN §7). Fail-soft by design:
a storage error must never kill a live pipeline; history is a convenience,
the SSE stream is the product.
"""
from __future__ import annotations

import asyncio
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import orjson

from ..agents.base import RunState

_DB = Path(__file__).resolve().parents[2] / "data" / "eip.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id          TEXT PRIMARY KEY,
    created_at  TEXT NOT NULL,
    mode        TEXT,
    situation   TEXT,
    score       REAL,
    band        TEXT,
    state_json  TEXT NOT NULL
)"""


def _connect() -> sqlite3.Connection:
    _DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB)
    conn.execute(_SCHEMA)
    return conn


def _save_sync(state: RunState) -> None:
    blob = orjson.dumps({
        "brief": state.brief, "profile": state.profile, "scope": state.scope,
        "evidence": state.evidence, "outputs": state.outputs,
        "conflicts": state.conflicts, "dimensions": state.dimensions,
        "verdict": state.verdict,
    }).decode()
    with _connect() as c:
        c.execute(
            "INSERT OR REPLACE INTO runs VALUES (?,?,?,?,?,?,?)",
            (state.run_id, datetime.now(timezone.utc).isoformat(timespec="seconds"),
             state.raw.get("mode", "founder"),
             (state.raw.get("situation") or "")[:300],
             float(state.verdict.get("score", 0.0) or 0.0),
             state.verdict.get("band", ""), blob),
        )


async def save_run(state: RunState) -> None:
    try:
        await asyncio.to_thread(_save_sync, state)
    except Exception:
        pass  # history is best-effort


def _list_sync(limit: int) -> list[dict[str, Any]]:
    with _connect() as c:
        rows = c.execute(
            "SELECT id, created_at, mode, situation, score, band FROM runs "
            "ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    return [{"id": r[0], "created_at": r[1], "mode": r[2], "situation": r[3],
             "score": r[4], "band": r[5]} for r in rows]


async def list_runs(limit: int = 50) -> list[dict[str, Any]]:
    try:
        return await asyncio.to_thread(_list_sync, limit)
    except Exception:
        return []


def _get_sync(run_id: str) -> dict[str, Any] | None:
    with _connect() as c:
        row = c.execute(
            "SELECT id, created_at, mode, situation, score, band, state_json "
            "FROM runs WHERE id = ?", (run_id,)).fetchone()
    if not row:
        return None
    return {"id": row[0], "created_at": row[1], "mode": row[2], "situation": row[3],
            "score": row[4], "band": row[5], "state": orjson.loads(row[6])}


async def get_run(run_id: str) -> dict[str, Any] | None:
    try:
        return await asyncio.to_thread(_get_sync, run_id)
    except Exception:
        return None
