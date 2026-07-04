"""The wealth pipeline (Wealth mode): cashflow → allocation → goals → debt →
property/location → crucible → money-health verdict. Education, not advice.
"""
from __future__ import annotations

import asyncio
import traceback

from ..agents import studio
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
                "weighing_engine", "verdict_composer", "visualizer", "reporter"]

WEALTH_MANDATORY = {"salary_budget", "weighing_engine", "verdict_composer", "visualizer", "reporter"}


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
        # honor the board picker (money math core + synthesis always run)
        enabled = set(payload.get("agents_enabled") or [])
        scope = ([a for a in WEALTH_SCOPE if a in enabled or a in WEALTH_MANDATORY]
                 if enabled else WEALTH_SCOPE)
        benched = [a for a in WEALTH_SCOPE if a not in scope]

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
        on = set(scope)

        def wave(pairs):
            return [f(ctx) for a, f in pairs if a in on]

        # L1 — grounding (macro matters for allocation; news for schemes/rates)
        await asyncio.gather(*wave((("news_intel", v.news_intel), ("macro_data", v.macro_data))))

        # L2 — money math in parallel, narrative agents too (shared blackboard)
        await asyncio.gather(*wave((("salary_budget", wl.salary_budget),
                                    ("portfolio_allocator", wl.portfolio_allocator),
                                    ("fire_planner", wl.fire_planner))))
        await asyncio.gather(*wave((("debt_banking", wl.debt_banking),
                                    ("real_estate", wl.real_estate),
                                    ("location_scout", wl.location_scout))))

        # L3 — crucible (red team attacks the plan; bias auditor reads the framing)
        await asyncio.gather(*wave((("red_team", v.red_team), ("bias_auditor", v.bias_auditor))))

        # L4 — synthesis
        await wl.weighing_wealth(ctx)
        await wl.verdict_wealth(ctx)
        await asyncio.gather(studio.visualizer(ctx), studio.reporter(ctx))

        await save_run(ctx.state)
        await emitter.done(run_id)
    except Exception:
        await emitter.log("verdict_composer", traceback.format_exc(limit=3), "err")
        await emitter.error("pipeline failed — see log")
