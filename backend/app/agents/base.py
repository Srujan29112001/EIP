"""Shared run-state (the blackboard) and the agent execution context."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..core.events import Emitter
from ..core.llm_gateway import Gateway


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

    def evidence_digest(self, limit: int = 24) -> str:
        lines = []
        for c in self.evidence[:limit]:
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
        if result is not None:
            self.state.outputs[agent_id] = result
            # stream the structured output → Decision Room agent accordion
            await self.emit.partial("agent_output", {"agent": agent_id, "output": result})
        if tokens:
            await self.emit.usage(agent_id, tokens, route)
        await self.emit.stage(agent_id, "done", layer)

    async def fail(self, agent_id: str, layer: str, msg: str) -> None:
        await self.emit.log(agent_id, msg, "err")
        await self.emit.stage(agent_id, "error", layer)
