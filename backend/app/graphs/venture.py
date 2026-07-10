"""The venture pipeline: L0 sequential → L1 ∥ → L2 ∥ → L3 → L4.

Phase 1 runs this as a structured asyncio DAG with the LangGraph-compatible
state shape; LangGraph checkpointing lands in Phase 3 when the debate loops
and long War-Room runs need pause/resume.
"""
from __future__ import annotations

import asyncio
import traceback

from ..agents import board, catalog, studio, venture as v
from ..agents.deliberate import deliberation_round
from ..agents.replay import replay_degraded
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
        # RAG memory: similar past decisions land on the board as evidence
        await v.memory_recall(ctx)

        # L2 — two waves so experts talk to EACH OTHER (A2A): foundational
        # analysts first, then integrative agents that read their findings
        l2_all = {"market_analyst": v.market_analyst, "finance_modeler": v.finance_modeler,
                  **catalog.LENS_AGENTS}
        wave1 = {a: f for a, f in l2_all.items() if a in catalog.L2_FOUNDATIONAL}
        wave2 = {a: f for a, f in l2_all.items() if a not in catalog.L2_FOUNDATIONAL}
        await asyncio.gather(*wave(wave1))
        await asyncio.gather(*wave(wave2))

        # L3 — crucible in parallel (attack the thesis, check the facts, audit the framing)
        await asyncio.gather(*wave({
            "red_team": v.red_team, "fact_checker": v.fact_checker,
            "bias_auditor": v.bias_auditor, "devils_advocate": board.devils_advocate,
        }))

        # L3.5 — War Room only: attacked analysts defend themselves in the open
        if (payload.get("depth") or "").lower() == "war_room":
            await board.debate_rounds(ctx)

        # gap-detector: rescue any agent that only reached its deterministic
        # core, by retrying after the rate-limit window refreshes
        await replay_degraded(ctx)

        # ROUND 2 — the notebook's full second pass. First take the ROUND-1
        # VERDICT (the first result set), then every layer re-runs L1→L2→L3
        # with the whole board visible, then the verdict is taken AGAIN on the
        # deliberated board. Both verdicts ship. Pulse stays single-round.
        depth_now = (payload.get("depth") or "pulse").lower()
        n_rounds = int(payload.get("rounds") or (1 if depth_now == "pulse" else 2))
        if n_rounds >= 2:
            await v.weighing_engine(ctx)
            await v.verdict_composer(ctx)
            ctx.state.rounds["verdict1"] = {"score": ctx.state.verdict.get("score"),
                                            "recommendation": ctx.state.verdict.get("recommendation")}
            await deliberation_round(ctx)

        # L4 — synthesis (on the deliberated board)
        await board.cross_pollinate(ctx)
        await board.compliance_scan(ctx)
        if "connecting_dots" in scoped:
            await board.connecting_dots(ctx)
        await v.weighing_engine(ctx)
        await v.verdict_composer(ctx)
        if n_rounds >= 2:
            ctx.state.rounds["verdict2"] = {"score": ctx.state.verdict.get("score"),
                                            "recommendation": ctx.state.verdict.get("recommendation")}
            await emitter.partial("rounds", dict(ctx.state.rounds))
        # storytelling frames the pitch from the verdict; visualizer builds charts.
        # reporter runs LAST and ALONE so the biggest single call gets the whole
        # key pool to itself, then self-heals via its own retry ladder — no outer
        # rescue needed (the ladder spans a full minute of quota refreshes).
        await asyncio.gather(board.storytelling(ctx), studio.visualizer(ctx))
        await studio.reporter(ctx)

        await save_run(ctx.state)
        await emitter.done(run_id)
    except Exception:
        await emitter.log("verdict_composer", traceback.format_exc(limit=3), "err")
        await emitter.error("pipeline failed — see log")
