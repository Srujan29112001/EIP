"""The venture pipeline: L0 sequential → L1 ∥ → L2 ∥ → L3 → L4.

Phase 1 runs this as a structured asyncio DAG with the LangGraph-compatible
state shape; LangGraph checkpointing lands in Phase 3 when the debate loops
and long War-Room runs need pause/resume.
"""
from __future__ import annotations

import asyncio
import traceback

from ..agents import board, catalog, studio, venture as v
from ..agents.base import Ctx, RunState
from ..core.events import Emitter
from ..core.llm_gateway import EngineConfig, Gateway
from ..memory.store import save_run


async def run_venture(run_id: str, payload: dict, emitter: Emitter) -> None:
    try:
        # Tolerate unknown engine keys from older/newer clients — a version skew
        # must never brick the run before the try block can report it.
        eng = payload.get("engine") or {}
        cfg = EngineConfig(**{k: v for k, v in eng.items() if k in EngineConfig.__dataclass_fields__})
        ctx = Ctx(emit=emitter, llm=Gateway(cfg), state=RunState(run_id=run_id, raw=payload))
        status = await ctx.llm.status()
        route_note = ("demo (deterministic cores only)" if cfg.compute == "demo"
                      else f"local={'✓' if status['local'] else '✗'} · cloud={status['cloud'] or '—'}")
        await emitter.log("scope_planner", f"engine: {route_note}", "muted")

        # L0 — sequential (each feeds the next)
        await v.intake_parser(ctx)
        await v.context_profiler(ctx)
        await v.scope_planner(ctx)

        # every wave is scope-driven: depth + the user's agent toggles decide who runs
        scoped = set(ctx.state.scope)

        def wave(mapping: dict) -> list:
            return [fn(ctx) for aid, fn in mapping.items() if aid in scoped]

        # L1 — grounding in parallel (web, news, live market, official macro, uploads)
        await asyncio.gather(*wave({
            "web_researcher": v.web_researcher, "news_intel": v.news_intel,
            "market_data": v.market_data, "macro_data": v.macro_data,
        }), v.doc_analyst(ctx))

        # L2 — domain analysis in parallel (spine + every convened lens agent)
        await asyncio.gather(*wave({
            "market_analyst": v.market_analyst, "finance_modeler": v.finance_modeler,
            **catalog.LENS_AGENTS,
        }))

        # L3 — crucible in parallel (attack the thesis, check the facts, audit the framing)
        await asyncio.gather(*wave({
            "red_team": v.red_team, "fact_checker": v.fact_checker,
            "bias_auditor": v.bias_auditor, "devils_advocate": board.devils_advocate,
        }))

        # L3.5 — War Room only: attacked analysts defend themselves in the open
        if (payload.get("depth") or "").lower() == "war_room":
            await board.debate_rounds(ctx)

        # L4 — synthesis
        if "connecting_dots" in scoped:
            await board.connecting_dots(ctx)
        await v.weighing_engine(ctx)
        await v.verdict_composer(ctx)
        await asyncio.gather(studio.visualizer(ctx), studio.reporter(ctx))

        await save_run(ctx.state)
        await emitter.done(run_id)
    except Exception:
        await emitter.log("verdict_composer", traceback.format_exc(limit=3), "err")
        await emitter.error("pipeline failed — see log")
