"""Human-in-the-loop review registry (Intelligent Mode).

Regulated legal/tax/financial content pauses the pipeline until a reviewer
decides via POST /api/review/{run_id} — or the wait times out and the run
proceeds carrying an explicit UNREVIEWED watermark. The SSE stream is the
product (Constitution #14): a human gate may pause a run, never kill it.

The registry is in-memory and per-process — reviews are same-session by
design (the reviewer is the person watching the stream); the decision is
persisted afterwards inside the run state's `rounds.hitl` audit record.
"""
from __future__ import annotations

import asyncio
import time
from typing import Any

_GATES: dict[str, dict[str, Any]] = {}

DECISIONS = ("approve", "reject")


def open_gate(run_id: str, draft: dict[str, Any]) -> None:
    _GATES[run_id] = {
        "event": asyncio.Event(),
        "draft": draft,
        "decision": None,
        "note": "",
        "opened_at": time.time(),
    }


def peek(run_id: str) -> dict[str, Any] | None:
    """The review payload for GET /api/review/{run_id} — no internals leaked."""
    g = _GATES.get(run_id)
    if g is None:
        return None
    return {
        "run_id": run_id,
        "pending": g["decision"] is None,
        "decision": g["decision"],
        "opened_at": g["opened_at"],
        "draft": g["draft"],
    }


def resolve(run_id: str, decision: str, note: str = "") -> bool:
    """Record the human decision and wake the paused pipeline. One shot."""
    g = _GATES.get(run_id)
    if g is None or g["decision"] is not None:
        return False
    g["decision"] = decision if decision in DECISIONS else "approve"
    g["note"] = (note or "")[:500]
    g["event"].set()
    return True


async def wait(run_id: str, timeout: float = 300.0) -> dict[str, Any]:
    """Block the pipeline until the reviewer decides or the window lapses."""
    g = _GATES.get(run_id)
    if g is None:
        return {"decision": "timeout", "note": ""}
    try:
        await asyncio.wait_for(g["event"].wait(), timeout=max(10.0, timeout))
        return {"decision": g["decision"] or "approve", "note": g["note"]}
    except asyncio.TimeoutError:
        g["decision"] = "timeout"
        return {"decision": "timeout", "note": ""}
    finally:
        _GATES.pop(run_id, None)
