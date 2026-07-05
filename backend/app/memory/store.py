"""Run persistence — zero-infra SQLite (MASTER_PLAN §7). Fail-soft by design:
a storage error must never kill a live pipeline; history is a convenience,
the SSE stream is the product.
"""
from __future__ import annotations

import asyncio
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import orjson

from ..agents.base import RunState

# EIP_DB_PATH lets a deploy point the SQLite file at a MOUNTED PERSISTENT VOLUME
# (e.g. a HF Space persistent disk) so history survives restarts. DATABASE_URL
# (postgres://…) is the managed-Postgres upgrade path — see README Phase 10.
_DB = Path(os.environ.get("EIP_DB_PATH")
           or (Path(__file__).resolve().parents[2] / "data" / "eip.db"))

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

# Phase 9 — outcome tracking: what the user actually did and how it turned out,
# so the platform can show its own calibration (did GO verdicts age well?).
_SCHEMA_OUTCOMES = """
CREATE TABLE IF NOT EXISTS outcomes (
    run_id       TEXT PRIMARY KEY,
    recorded_at  TEXT NOT NULL,
    decision     TEXT,   -- proceeded | declined | modified | pending
    status       TEXT,   -- good | mixed | bad | too_early
    note         TEXT
)"""

# Phase 10 — lightweight accounts + tiers. Anonymous-first: a stable client id
# (no password) owns its runs; tier gates depth/quota. Managed auth + Postgres
# is the documented upgrade path (README Phase 10).
_SCHEMA_USERS = """
CREATE TABLE IF NOT EXISTS users (
    user_id     TEXT PRIMARY KEY,
    email       TEXT,
    tier        TEXT NOT NULL DEFAULT 'free',
    created_at  TEXT NOT NULL,
    runs        INTEGER NOT NULL DEFAULT 0
)"""
_SCHEMA_RUN_USERS = """
CREATE TABLE IF NOT EXISTS run_users (
    run_id   TEXT PRIMARY KEY,
    user_id  TEXT NOT NULL
)"""


def _connect() -> sqlite3.Connection:
    _DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB)
    conn.execute(_SCHEMA)
    conn.execute(_SCHEMA_OUTCOMES)
    conn.execute(_SCHEMA_USERS)
    conn.execute(_SCHEMA_RUN_USERS)
    return conn


def _save_sync(state: RunState) -> None:
    blob = orjson.dumps({
        "brief": state.brief, "profile": state.profile, "scope": state.scope,
        "evidence": state.evidence, "outputs": state.outputs,
        "conflicts": state.conflicts, "dimensions": state.dimensions,
        "verdict": state.verdict,
    }).decode()
    user_id = (state.raw.get("user_id") or "").strip()
    with _connect() as c:
        c.execute(
            "INSERT OR REPLACE INTO runs VALUES (?,?,?,?,?,?,?)",
            (state.run_id, datetime.now(timezone.utc).isoformat(timespec="seconds"),
             state.raw.get("mode", "founder"),
             (state.raw.get("situation") or "")[:300],
             float(state.verdict.get("score", 0.0) or 0.0),
             state.verdict.get("band", ""), blob),
        )
        if user_id:
            c.execute("INSERT OR REPLACE INTO run_users VALUES (?,?)", (state.run_id, user_id))
            c.execute("UPDATE users SET runs = runs + 1 WHERE user_id = ?", (user_id,))


async def save_run(state: RunState) -> None:
    try:
        await asyncio.to_thread(_save_sync, state)
    except Exception:
        pass  # history is best-effort


def _list_sync(limit: int, user_id: str | None) -> list[dict[str, Any]]:
    with _connect() as c:
        if user_id:
            rows = c.execute(
                "SELECT r.id, r.created_at, r.mode, r.situation, r.score, r.band, o.decision, o.status "
                "FROM runs r JOIN run_users ru ON ru.run_id = r.id "
                "LEFT JOIN outcomes o ON o.run_id = r.id "
                "WHERE ru.user_id = ? ORDER BY r.created_at DESC LIMIT ?", (user_id, limit)).fetchall()
        else:
            rows = c.execute(
                "SELECT r.id, r.created_at, r.mode, r.situation, r.score, r.band, o.decision, o.status "
                "FROM runs r LEFT JOIN outcomes o ON o.run_id = r.id "
                "ORDER BY r.created_at DESC LIMIT ?", (limit,)).fetchall()
    return [{"id": r[0], "created_at": r[1], "mode": r[2], "situation": r[3],
             "score": r[4], "band": r[5],
             "outcome": ({"decision": r[6], "status": r[7]} if r[6] or r[7] else None)}
            for r in rows]


async def list_runs(limit: int = 50, user_id: str | None = None) -> list[dict[str, Any]]:
    try:
        return await asyncio.to_thread(_list_sync, limit, user_id)
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


# ── Phase 9: outcome tracking + calibration ───────────────────────────────────

_DECISIONS = {"proceeded", "declined", "modified", "pending"}
_STATUSES = {"good", "mixed", "bad", "too_early"}


def _save_outcome_sync(run_id: str, decision: str, status: str, note: str) -> None:
    with _connect() as c:
        c.execute("INSERT OR REPLACE INTO outcomes VALUES (?,?,?,?,?)",
                  (run_id, datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   decision if decision in _DECISIONS else "pending",
                   status if status in _STATUSES else "too_early", (note or "")[:600]))


async def save_outcome(run_id: str, decision: str, status: str, note: str = "") -> bool:
    try:
        await asyncio.to_thread(_save_outcome_sync, run_id, decision, status, note)
        return True
    except Exception:
        return False


def _get_outcome_sync(run_id: str) -> dict[str, Any] | None:
    with _connect() as c:
        row = c.execute("SELECT run_id, recorded_at, decision, status, note FROM outcomes "
                        "WHERE run_id = ?", (run_id,)).fetchone()
    if not row:
        return None
    return {"run_id": row[0], "recorded_at": row[1], "decision": row[2],
            "status": row[3], "note": row[4]}


async def get_outcome(run_id: str) -> dict[str, Any] | None:
    try:
        return await asyncio.to_thread(_get_outcome_sync, run_id)
    except Exception:
        return None


def _track_record_sync() -> dict[str, Any]:
    """Did the board's verdicts age well? Cross-tabs the recommendation band
    against the recorded outcome — the platform's own calibration scorecard."""
    with _connect() as c:
        rows = c.execute(
            "SELECT r.band, r.score, o.decision, o.status FROM runs r "
            "JOIN outcomes o ON o.run_id = r.id "
            "WHERE o.status IS NOT NULL AND o.status != 'too_early'").fetchall()
    total = len(rows)
    by_status: dict[str, int] = {}
    good_go = go = 0
    for band, _score, _dec, status in rows:
        by_status[status] = by_status.get(status, 0) + 1
        is_go = str(band or "").upper() in ("GO", "CONDITIONAL_GO")
        if is_go:
            go += 1
            if status == "good":
                good_go += 1
    tracked_total = 0
    with _connect() as c:
        tracked_total = c.execute("SELECT COUNT(*) FROM outcomes").fetchone()[0]
    return {
        "graded": total, "tracked": tracked_total,
        "by_status": by_status,
        "go_hit_rate": round(good_go / go, 2) if go else None,
        "go_count": go,
    }


async def track_record() -> dict[str, Any]:
    try:
        return await asyncio.to_thread(_track_record_sync)
    except Exception:
        return {"graded": 0, "tracked": 0, "by_status": {}, "go_hit_rate": None, "go_count": 0}


# ── Phase 10: lightweight accounts + tiers ────────────────────────────────────

# what each tier unlocks (informational + soft-gating; no payment wall yet)
TIERS = {
    "free": {"label": "Free", "max_depth": "war_room", "daily_runs": 25,
             "note": "Full board, all three modes, bring-your-own-keys."},
    "pro": {"label": "Pro", "max_depth": "war_room", "daily_runs": 500,
            "note": "Higher quota, priority server keys, saved boards."},
}


def _get_or_create_user_sync(user_id: str, email: str | None) -> dict[str, Any]:
    with _connect() as c:
        row = c.execute("SELECT user_id, email, tier, created_at, runs FROM users WHERE user_id = ?",
                        (user_id,)).fetchone()
        if row is None:
            c.execute("INSERT INTO users (user_id, email, tier, created_at, runs) VALUES (?,?,?,?,0)",
                      (user_id, email or "", "free",
                       datetime.now(timezone.utc).isoformat(timespec="seconds")))
            row = (user_id, email or "", "free",
                   datetime.now(timezone.utc).isoformat(timespec="seconds"), 0)
        elif email and email != row[1]:
            c.execute("UPDATE users SET email = ? WHERE user_id = ?", (email, user_id))
            row = (row[0], email, row[2], row[3], row[4])
    tier = row[2] if row[2] in TIERS else "free"
    return {"user_id": row[0], "email": row[1], "tier": tier, "created_at": row[3],
            "runs": row[4], "tier_info": TIERS[tier]}


async def get_or_create_user(user_id: str, email: str | None = None) -> dict[str, Any]:
    try:
        return await asyncio.to_thread(_get_or_create_user_sync, user_id, email)
    except Exception:
        return {"user_id": user_id, "email": email or "", "tier": "free",
                "created_at": "", "runs": 0, "tier_info": TIERS["free"]}


def _set_tier_sync(user_id: str, tier: str) -> bool:
    if tier not in TIERS:
        return False
    with _connect() as c:
        c.execute("UPDATE users SET tier = ? WHERE user_id = ?", (tier, user_id))
    return True


async def set_tier(user_id: str, tier: str) -> bool:
    try:
        return await asyncio.to_thread(_set_tier_sync, user_id, tier)
    except Exception:
        return False
