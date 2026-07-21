"""Shared run-state (the blackboard) and the agent execution context."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..core.events import Emitter
from ..core.llm_gateway import Gateway
from ..memory.rag import rank_evidence


@dataclass
class RunState:
    """The typed blackboard every agent reads and writes (MASTER_PLAN §3.3)."""
    run_id: str
    raw: dict[str, Any]                                  # intake payload from UI
    brief: dict[str, Any] = field(default_factory=dict)   # L0: structured situation
    profile: dict[str, Any] = field(default_factory=dict) # L0: who is asking
    scope: list[str] = field(default_factory=list)        # L0: agent ids to fire
    evidence: list[dict[str, Any]] = field(default_factory=list)   # L1 claims (cited)
    outputs: dict[str, dict[str, Any]] = field(default_factory=dict)  # agent_id → structured output
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    dimensions: dict[str, float] = field(default_factory=dict)     # L4 radar
    verdict: dict[str, Any] = field(default_factory=dict)
    # two-round deliberation: round-1 snapshot + per-agent score deltas, so the
    # verdict can show HOW the board changed its mind after the all-to-all read
    rounds: dict[str, Any] = field(default_factory=dict)

    def evidence_digest(self, limit: int = 24, query: str = "") -> str:
        """The evidence an agent reads. With a query, this is the RAG read:
        the `limit` items most RELEVANT to this agent's question (BM25),
        instead of the first `limit` by arrival order."""
        picked = rank_evidence(self.evidence, query, limit)
        lines = []
        for c in picked:
            src = c.get("source") or {}
            tag = src.get("url") or src.get("name") or "unsourced"
            lines.append(f"- {c['text']} [{tag}]")
        return "\n".join(lines) if lines else "(no external evidence gathered)"


@dataclass
class Ctx:
    emit: Emitter
    llm: Gateway
    state: RunState

    async def start(self, agent_id: str, layer: str) -> None:
        await self.emit.stage(agent_id, "active", layer)

    async def finish(self, agent_id: str, layer: str, result: dict[str, Any] | None = None,
                     route: str = "", tokens: int = 0) -> None:
        # honest status: a deterministic-only run is "degraded" (amber), not
        # "done" — and it must say WHY (strict engine: zero silent fallbacks).
        degraded = bool(isinstance(result, dict) and result.get("degraded"))
        if degraded and isinstance(result, dict):
            # the gateway's ACTUAL error wins over any generic string the agent
            # hardcoded — that is the real cause the user needs to see.
            reason = str(getattr(self.llm, "_errors", {}).get(agent_id, "")
                         or result.get("degraded_reason")
                         or getattr(self.llm, "last_error", "") or "").strip()
            if reason:
                result["degraded_reason"] = reason
                await self.emit.log(
                    agent_id, f"engine failed → deterministic core only: {reason}", "warn")
        if result is not None:
            self.state.outputs[agent_id] = result
            # stream the structured output → Decision Room agent accordion
            await self.emit.partial("agent_output", {"agent": agent_id, "output": result})
        if tokens:
            await self.emit.usage(agent_id, tokens, route)
        if degraded and self.state.raw.get("mode") == "intelligent":
            # Advisory-Engine contract (Intelligent Mode ONLY — other modes'
            # event streams stay exactly as they were): say EXPLICITLY that
            # no model was reached — the deterministic core answered alone.
            await self.emit.skipped_no_llm(agent_id)
        await self.emit.stage(agent_id, "degraded" if degraded else "done", layer)

    async def fail(self, agent_id: str, layer: str, msg: str) -> None:
        await self.emit.log(agent_id, msg, "err")
        await self.emit.stage(agent_id, "error", layer)
