"""The wealth pipeline (Wealth mode): cashflow → allocation → goals → debt →
property/location → crucible → money-health verdict. Education, not advice.
"""
from __future__ import annotations

import asyncio
import traceback

from ..agents import wealth as wl
from ..agents import venture as v
from ..agents.base import Ctx, RunState
from ..core.events import Emitter
from ..core.llm_gateway import EngineConfig, Gateway
from ..memory.store import save_run

WEALTH_SCOPE = ["news_intel", "macro_data",
                "salary_budget", "portfolio_allocator", "fire_planner",
                "debt_banking", "real_estate", "location_scout",
                "red_team", "bias_auditor",
                "weighing_engine", "verdict_composer"]


async def run_wealth(run_id: str, payload: dict, emitter: Emitter) -> None:
    try:
        eng = payload.get("engine") or {}
        cfg = EngineConfig(**{k: val for k, val in eng.items() if k in EngineConfig.__dataclass_fields__})
        ctx = Ctx(emit=emitter, llm=Gateway(cfg), state=RunState(run_id=run_id, raw=payload))

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
            "geography": payload.get("geography", "India"),
        }
        await emitter.stage("intake_parser", "done", "L0")
        await emitter.stage("context_profiler", "done", "L0")
        await emitter.log("scope_planner", f"wealth desk: {len(WEALTH_SCOPE)} specialists · {city}", "info")
        ctx.state.scope = WEALTH_SCOPE
        for s in WEALTH_SCOPE:
            await emitter.stage(s, "queued", "")
        await emitter.partial("brief", ctx.state.brief)
        await emitter.partial("scope", WEALTH_SCOPE)
        await emitter.stage("scope_planner", "done", "L0")

        # L1 — grounding (macro matters for allocation; news for schemes/rates)
        await asyncio.gather(v.news_intel(ctx), v.macro_data(ctx))

        # L2 — money math in parallel, narrative agents too (shared blackboard)
        await asyncio.gather(wl.salary_budget(ctx), wl.portfolio_allocator(ctx), wl.fire_planner(ctx))
        await asyncio.gather(wl.debt_banking(ctx), wl.real_estate(ctx), wl.location_scout(ctx))

        # L3 — crucible (red team attacks the plan; bias auditor reads the framing)
        await asyncio.gather(v.red_team(ctx), v.bias_auditor(ctx))

        # L4 — synthesis
        await wl.weighing_wealth(ctx)
        await wl.verdict_wealth(ctx)

        await save_run(ctx.state)
        await emitter.done(run_id)
    except Exception:
        await emitter.log("verdict_composer", traceback.format_exc(limit=3), "err")
        await emitter.error("pipeline failed — see log")
