"""The wealth pipeline (Wealth mode): cashflow → allocation → goals → debt →
property/location → crucible → money-health verdict. Education, not advice.
"""
from __future__ import annotations

import asyncio
import traceback

from ..agents import board
from ..agents import catalog
from ..agents import meta
from ..agents import orchestra
from ..agents import scenario
from ..agents import studio
from ..agents.deliberate import deliberation_round, emit_result_set, refine_gateway
from ..agents import wealth as wl
from ..agents import venture as v
from ..agents.replay import replay_degraded
from ..agents.base import Ctx, RunState
from ..core.events import Emitter
from ..core.llm_gateway import EngineConfig, Gateway
from ..memory.store import save_run

WEALTH_SCOPE = ["news_intel", "macro_data", "rag_memory",
                "salary_budget", "portfolio_allocator", "fire_planner",
                "debt_banking", "real_estate", "location_scout",
                "red_team", "bias_auditor",
                "weighing_engine", "verdict_composer", "scenario_planner", "negotiation_coach",
                "storytelling", "visualizer", "reporter", "outcome_tracker"]

WEALTH_MANDATORY = {"salary_budget", "rag_memory", "weighing_engine", "verdict_composer",
                    "scenario_planner", "negotiation_coach", "storytelling", "visualizer",
                    "reporter", "outcome_tracker"}


async def run_wealth(run_id: str, payload: dict, emitter: Emitter) -> None:
    try:
        eng = payload.get("engine") or {}
        cfg = EngineConfig(**{k: val for k, val in eng.items() if k in EngineConfig.__dataclass_fields__})
        ctx = Ctx(emit=emitter, llm=Gateway(cfg), state=RunState(run_id=run_id, raw=payload))
        from datetime import datetime, timezone
        await emitter.log("scope_planner",
                          f"FRESH RUN {run_id} · all grounding fetched LIVE at "
                          f"{datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC — nothing reused "
                          "from history except claims explicitly labelled MEMORY", "info")

        # Intelligent Mode: the 🎩 Boss distils the conversation (and lifts the
        # income/expense figures) into the payload BEFORE the wealth intake
        advisory = bool(payload.get("advisory"))
        if advisory:
            await emitter.partial("run_id", run_id)
            await orchestra.boss_brief(ctx)

        # L0 — deterministic wealth intake
        city = payload.get("city") or "India"
        ctx.state.brief = {
            "summary": f"Money-health check: ₹{payload.get('monthly_income', 0):,.0f}/mo income, "
                       f"goals: {payload.get('goals', 'financial independence')}",
            "industry": "personal finance", "geography": payload.get("geography", "India"),
            "stage": "wealth", "keywords": ["salary", "savings", "investing", city.lower()],
            "uncertainty": payload.get("uncertainty", ""),
        }
        ctx.state.profile = {
            "persona": "earner/saver", "age": payload.get("age"),
            "income_band": payload.get("monthly_income"), "city": city,
            "risk_capacity": payload.get("risk_appetite", "moderate"),
            "dependents": payload.get("dependents", 0),
            "current_debt": payload.get("current_debt", 0),
            "monthly_sip": payload.get("monthly_sip", 0),
            "geography": payload.get("geography", "India"),
        }
        # depth unlocks the wider board for savers too (world + human lenses)
        depth = str(payload.get("depth") or "pulse").lower()
        full_scope = WEALTH_SCOPE + [a for a in catalog.WEALTH_EXTRA.get(depth, [])
                                     if a not in WEALTH_SCOPE]

        # honor the board picker (money math core + synthesis always run)
        enabled = set(payload.get("agents_enabled") or [])
        scope = ([a for a in full_scope if a in enabled or a in WEALTH_MANDATORY]
                 if enabled else full_scope)
        benched = [a for a in full_scope if a not in scope]

        await emitter.stage("intake_parser", "done", "L0")
        await emitter.stage("context_profiler", "done", "L0")
        await emitter.log("scope_planner", f"wealth desk: {len(scope)} specialists · {city}", "info")
        if benched:
            await emitter.log("scope_planner", f"benched by you: {', '.join(benched)}", "muted")
            for b in benched:
                await emitter.stage(b, "skipped", "")
        ctx.state.scope = scope
        for s in scope:
            await emitter.stage(s, "queued", "")
        await emitter.partial("brief", ctx.state.brief)
        await emitter.partial("scope", scope)
        await emitter.stage("scope_planner", "done", "L0")
        if advisory:
            await orchestra.manager_plan(ctx)   # 🎼 mode-aware dynamic routing
        on = set(ctx.state.scope)

        def wave(pairs):
            return [f(ctx) for a, f in pairs if a in on]

        # L1 — grounding (macro matters for allocation; news for schemes/rates)
        await asyncio.gather(*wave((("news_intel", v.news_intel), ("macro_data", v.macro_data))))
        # RAG memory: similar past decisions land on the board as evidence,
        # then the retrieval agent indexes everything for per-specialist reads
        await v.memory_recall(ctx)
        await meta.rag_memory(ctx)

        # L2 — money math in parallel, narrative agents too (shared blackboard)
        await asyncio.gather(*wave((("salary_budget", wl.salary_budget),
                                    ("portfolio_allocator", wl.portfolio_allocator),
                                    ("fire_planner", wl.fire_planner))))
        await asyncio.gather(*wave((("debt_banking", wl.debt_banking),
                                    ("real_estate", wl.real_estate),
                                    ("location_scout", wl.location_scout))),
                             *(catalog.LENS_AGENTS[a](ctx) for a in on
                               if a in catalog.LENS_AGENTS
                               and a not in ("debt_banking", "real_estate", "location_scout")))

        # L3 — crucible (red team attacks the plan; bias auditor reads the framing)
        await asyncio.gather(*wave((("red_team", v.red_team), ("bias_auditor", v.bias_auditor))))

        # gap-detector: retry reduced-depth agents after a cooldown
        await replay_degraded(ctx)

        # ═══ ROUND 1 — the complete first pass, results and all ═══
        async def synthesis(round_no: int = 1) -> None:
            await board.cross_pollinate(ctx)
            await board.compliance_scan(ctx)
            await wl.weighing_wealth(ctx)
            await wl.verdict_wealth(ctx)
            await scenario.scenario_planner(ctx)
            await asyncio.gather(board.negotiation_coach(ctx),
                                 board.storytelling(ctx), studio.visualizer(ctx))
            if advisory:
                await orchestra.qa_gate(ctx, round_no)   # ✅ blocking, before the report
            await studio.reporter(ctx)   # last & alone, input-shrinking ladder

        await synthesis(1)
        n_rounds = int(payload.get("rounds") or (1 if depth == "pulse" else 2))
        if advisory and n_rounds < 2:
            await orchestra.hitl_checkpoint(ctx)   # 🧑‍⚖️ guard the only deliverable
        await emit_result_set(ctx, 1)

        # ═══ ROUND 2 — the whole pipeline re-runs, L0 → L4 ═══
        if n_rounds >= 2:
            ctx.state.rounds["verdict1"] = {"score": ctx.state.verdict.get("score"),
                                            "recommendation": ctx.state.verdict.get("recommendation")}
            await refine_gateway(ctx)
            await deliberation_round(ctx)
            await synthesis(2)
            for aid in ("cross_pollinate", "compliance_scan", "weighing_engine",
                        "verdict_composer", "scenario_planner", "negotiation_coach",
                        "storytelling", "visualizer", "reporter"):
                await emitter.round(aid, 2)
            ctx.state.rounds["verdict2"] = {"score": ctx.state.verdict.get("score"),
                                            "recommendation": ctx.state.verdict.get("recommendation")}
            await emitter.partial("rounds", dict(ctx.state.rounds))
            if advisory:
                await orchestra.hitl_checkpoint(ctx)   # 🧑‍⚖️ guard the final deliverable
            await emit_result_set(ctx, 2)

        await save_run(ctx.state)
        await meta.outcome_tracker(ctx)
        await emitter.done(run_id)
    except Exception:
        await emitter.log("verdict_composer", traceback.format_exc(limit=3), "err")
        await emitter.error("pipeline failed — see log")
