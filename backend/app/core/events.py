"""The SSE event contract — the single source of truth shared with the frontend.

Locked in Phase 0 (Helix method): the scripted demo producer and the real
pipeline emit *exactly* the same shapes, so the client never knows the difference.
"""
from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, Literal

import orjson

# "degraded" = the agent ran but only on its deterministic core (no LLM
# reachable — rate-limited or no key), so its depth is reduced. It is NOT the
# same as a clean "done"; the UI shows it amber and explains why.
StageStatus = Literal["queued", "active", "done", "degraded", "error", "skipped"]
LogKind = Literal["info", "code", "ok", "err", "warn", "muted"]


def _ser(payload: dict[str, Any]) -> str:
    return f"data: {orjson.dumps(payload).decode()}\n\n"


class Emitter:
    """Async fan-in queue every agent writes to; the SSE endpoint drains it."""

    def __init__(self) -> None:
        self.queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()

    # ── event constructors (the contract) ────────────────────────────────
    async def stage(self, agent: str, status: StageStatus, layer: str = "") -> None:
        await self.queue.put({"type": "stage", "agent": agent, "status": status, "layer": layer})

    async def log(self, agent: str, text: str, kind: LogKind = "info") -> None:
        await self.queue.put({"type": "log", "agent": agent, "kind": kind, "text": text})

    async def claim(self, agent: str, text: str, source: dict | None = None, confidence: float = 0.5) -> None:
        await self.queue.put({
            "type": "claim", "agent": agent,
            "claim": {"text": text, "source": source, "confidence": round(confidence, 2)},
        })

    async def conflict(self, a: str, b: str, topic: str) -> None:
        await self.queue.put({"type": "conflict", "a": a, "b": b, "topic": topic})

    async def collab(self, agent: str, peers: list[str]) -> None:
        """Agent-to-agent: `agent` built its analysis on these peers' findings.
        Drives the A2A edges in the flow map + decision graph."""
        await self.queue.put({"type": "collab", "agent": agent, "peers": peers})

    async def round(self, agent: str, round_: int) -> None:
        """An agent completed deliberation round N — drives the ✓✓ badges."""
        await self.queue.put({"type": "round", "agent": agent, "round": round_})

    async def prompt(self, agent: str, system: str, user: str) -> None:
        """Radical transparency: the exact prompt an agent sends to its model."""
        await self.queue.put({"type": "prompt", "agent": agent,
                              "system": system[:1600], "user": user[:2800]})

    async def debate(self, agent: str, round_: int, text: str, stance: str = "rebuttal") -> None:
        """A live agent-to-agent debate turn (War Room)."""
        await self.queue.put({"type": "debate", "agent": agent, "round": round_,
                              "stance": stance, "text": text})

    async def bias(self, target: str, bias: str, note: str) -> None:
        await self.queue.put({"type": "bias", "target": target, "bias": bias, "note": note})

    async def partial(self, section: str, data: Any) -> None:
        await self.queue.put({"type": "partial", "section": section, "data": data})

    async def usage(self, agent: str, tokens: int, route: str) -> None:
        await self.queue.put({"type": "usage", "agent": agent, "tokens": tokens, "route": route})

    async def done(self, run_id: str) -> None:
        await self.queue.put({"type": "done", "run_id": run_id})
        await self.queue.put(None)  # sentinel → close stream

    async def error(self, message: str) -> None:
        await self.queue.put({"type": "fatal", "message": message})
        await self.queue.put(None)

    # ── drain as SSE lines ────────────────────────────────────────────────
    async def sse(self) -> AsyncIterator[str]:
        while True:
            item = await self.queue.get()
            if item is None:
                break
            yield _ser(item)
