"""The venture pipeline: L0 sequential → L1 ∥ → L2 ∥ → L3 → L4.

Phase 1 runs this as a structured asyncio DAG with the LangGraph-compatible
state shape; LangGraph checkpointing lands in Phase 3 when the debate loops
and long War-Room runs need pause/resume.
"""
from __future__ import annotations

import asyncio
import traceback

from ..agents import venture as v
from ..agents.base import Ctx, RunState
from ..core.events import Emitter
from ..core.llm_gateway import EngineConfig, Gateway


async def run_venture(run_id: str, payload: dict, emitter: Emitter) -> None:
    cfg = EngineConfig(**(payload.get("engine") or {}))
    ctx = Ctx(emit=emitter, llm=Gateway(cfg), state=RunState(run_id=run_id, raw=payload))
    try:
        status = await ctx.llm.status()
        route_note = ("demo (deterministic cores only)" if cfg.compute == "demo"
                      else f"local={'✓' if status['local'] else '✗'} · cloud={status['cloud'] or '—'}")
        await emitter.log("scope_planner", f"engine: {route_note}", "muted")

        # L0 — sequential (each feeds the next)
        await v.intake_parser(ctx)
        await v.context_profiler(ctx)
        await v.scope_planner(ctx)

        # L1 — grounding in parallel
        await asyncio.gather(v.web_researcher(ctx), v.news_intel(ctx))

        # L2 — domain analysis in parallel
        await asyncio.gather(v.market_analyst(ctx), v.finance_modeler(ctx))

        # L3 — crucible
        await v.red_team(ctx)

        # L4 — synthesis
        await v.weighing_engine(ctx)
        await v.verdict_composer(ctx)

        await emitter.done(run_id)
    except Exception:
        await emitter.log("verdict_composer", traceback.format_exc(limit=3), "err")
        await emitter.error("pipeline failed — see log")
