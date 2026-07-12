"""The venture pipeline: L0 sequential → L1 ∥ → L2 ∥ → L3 → L4.

Phase 1 runs this as a structured asyncio DAG with the LangGraph-compatible
state shape; LangGraph checkpointing lands in Phase 3 when the debate loops
and long War-Room runs need pause/resume.
"""
from __future__ import annotations

import asyncio
import traceback

from ..agents import board, catalog, meta, orchestra, scenario, studio, venture as v
from ..agents.deliberate import deliberation_round, emit_result_set, refine_gateway
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
        from datetime import datetime, timezone
        await emitter.log("scope_planner",
                          f"FRESH RUN {run_id} · all grounding fetched LIVE at "
                          f"{datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC — nothing reused "
                          "from history except claims explicitly labelled MEMORY", "info")

        # Intelligent Mode (Advisory Engine) wraps the same pipeline with the
        # Boss/Manager/QA/HITL layer, gated by `advisory`
        advisory = bool(payload.get("advisory"))
        if advisory:
            await emitter.partial("run_id", run_id)   # the review endpoint needs it mid-run
            await orchestra.boss_brief(ctx)           # 🎩 conversation → brief

        # L0 — sequential (each feeds the next)
        await v.intake_parser(ctx)
        await v.context_profiler(ctx)
        await v.scope_planner(ctx)
        if advisory:
            await orchestra.manager_plan(ctx)         # 🎼 mode-aware dynamic routing

        # every wave is scope-driven: depth + the user's agent toggles decide who runs
        scoped = set(ctx.state.scope)

        def wave(mapping: dict) -> list:
            return [fn(ctx) for aid, fn in mapping.items() if aid in scoped]

        # L1 — grounding in parallel (web, news, live market, official macro, uploads)
        await asyncio.gather(*wave({
            "web_researcher": v.web_researcher, "news_intel": v.news_intel,
            "market_data": v.market_data, "macro_data": v.macro_data,
        }), v.doc_analyst(ctx))
        # RAG memory: similar past decisions land on the board as evidence,
        # then the retrieval agent indexes everything for per-specialist reads
        await v.memory_recall(ctx)
        await meta.rag_memory(ctx)

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

        # ═══ ROUND 1 — the COMPLETE first pass, results and all (notebook: IJK) ═══
        async def synthesis(round_no: int = 1) -> None:
            await board.cross_pollinate(ctx)
            await board.compliance_scan(ctx)
            if "connecting_dots" in scoped:
                await board.connecting_dots(ctx)
            await v.weighing_engine(ctx)
            await v.verdict_composer(ctx)
            await scenario.scenario_planner(ctx)   # Monte-Carlo the verdict (t0)
            await asyncio.gather(board.negotiation_coach(ctx),
                                 board.storytelling(ctx), studio.visualizer(ctx))
            if advisory:
                await orchestra.qa_gate(ctx, round_no)   # ✅ blocking, before the report
            # reporter runs LAST and ALONE (whole key pool) with its own
            # input-shrinking ladder — no outer rescue needed
            await studio.reporter(ctx)

        await synthesis(1)
        depth_now = (payload.get("depth") or "pulse").lower()
        n_rounds = int(payload.get("rounds") or (1 if depth_now == "pulse" else 2))
        if advisory and n_rounds < 2:
            await orchestra.hitl_checkpoint(ctx)   # 🧑‍⚖️ guard the only deliverable
        await emit_result_set(ctx, 1)   # ← the ROUND-1 RESULTS, published in full

        # ═══ ROUND 2 — the whole pipeline re-runs, L0 → L1 → L2 → L3 → L4,
        # every agent reading the full round-1 board (notebook: β γ ᾱ) ═══
        if n_rounds >= 2:
            ctx.state.rounds["verdict1"] = {"score": ctx.state.verdict.get("score"),
                                            "recommendation": ctx.state.verdict.get("recommendation")}
            await refine_gateway(ctx)          # L0 ✓✓
            await deliberation_round(ctx)      # L1 → L2 → L3 ✓✓ (incl. grounding + crucible)
            await synthesis(2)                 # L4 re-runs in full — the second results
            for aid in ("cross_pollinate", "compliance_scan",
                        *(["connecting_dots"] if "connecting_dots" in scoped else []),
                        "weighing_engine", "verdict_composer", "scenario_planner",
                        "negotiation_coach", "storytelling", "visualizer", "reporter"):
                await emitter.round(aid, 2)    # L4 ✓✓
            ctx.state.rounds["verdict2"] = {"score": ctx.state.verdict.get("score"),
                                            "recommendation": ctx.state.verdict.get("recommendation")}
            await emitter.partial("rounds", dict(ctx.state.rounds))
            if advisory:
                await orchestra.hitl_checkpoint(ctx)   # 🧑‍⚖️ guard the final deliverable
            await emit_result_set(ctx, 2)      # ← the ROUND-2 RESULTS, under round 1

        await save_run(ctx.state)
        # L5 — the outcome tracker closes the loop: calibration, in the open
        await meta.outcome_tracker(ctx)
        await emitter.done(run_id)
    except Exception:
        await emitter.log("verdict_composer", traceback.format_exc(limit=3), "err")
        await emitter.error("pipeline failed — see log")
