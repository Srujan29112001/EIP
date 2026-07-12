"""The trading pipeline (Trader mode): history → technicals → backtests →
signal ensemble → risk plan → crucible → setup verdict.

Same blackboard, same SSE contract, same glass box as the venture pipeline —
different specialists, and a verdict that is explicitly setup-quality
education, never advice (MASTER_PLAN §5.4).
"""
from __future__ import annotations

import asyncio
import traceback

from ..agents import board
from ..agents import catalog
from ..agents import markets as m
from ..agents import meta
from ..agents import orchestra
from ..agents import scenario
from ..agents.deliberate import deliberation_round, emit_result_set, refine_gateway
from ..agents import studio
from ..agents import venture as v
from ..agents.replay import replay_degraded
from ..agents.base import Ctx, RunState
from ..core.events import Emitter
from ..core.llm_gateway import EngineConfig, Gateway
from ..memory.store import save_run

TRADER_SCOPE = ["news_intel", "market_data", "macro_data", "rag_memory",
                "technical_analyst", "stock_analyst", "backtest_engineer",
                "quant_signals", "risk_manager",
                "fund_analyst", "options_desk", "microstructure",
                "red_team", "fact_checker", "bias_auditor",
                "weighing_engine", "verdict_composer", "scenario_planner", "negotiation_coach",
                "storytelling", "visualizer", "reporter", "outcome_tracker"]

# the desk can be hand-picked, but the data spine + synthesis cannot be benched
TRADER_MANDATORY = {"market_data", "technical_analyst", "rag_memory", "weighing_engine",
                    "verdict_composer", "scenario_planner", "negotiation_coach",
                    "storytelling", "visualizer", "reporter", "outcome_tracker"}


async def run_trading(run_id: str, payload: dict, emitter: Emitter) -> None:
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
        # ticker/style) into the payload BEFORE the deterministic trader intake
        advisory = bool(payload.get("advisory"))
        if advisory:
            await emitter.partial("run_id", run_id)
            await orchestra.boss_brief(ctx)

        # L0 — trader intake (deterministic; the symbol IS the brief)
        symbol = (payload.get("symbol") or "").strip().upper()
        style = payload.get("trading_style") or "swing"
        ctx.state.brief = {
            "summary": f"Trading analysis: {symbol} ({style} style)",
            "industry": "", "geography": payload.get("geography", "India"),
            "stage": style, "keywords": [symbol.lower()],
            "uncertainty": payload.get("uncertainty", ""),
            **({"user_thesis": str(payload["thesis"])[:300]} if payload.get("thesis") else {}),
        }
        ctx.state.profile = {"persona": f"{style} trader", "capital_band": payload.get("capital", ""),
                             "risk_capacity": f"{payload.get('risk_pct', 1)}% per trade",
                             "existing_position": payload.get("existing_position", 0),
                             "geography": payload.get("geography", "India")}
        # depth unlocks the wider board for traders too (world + human lenses)
        depth = str(payload.get("depth") or "pulse").lower()
        full_scope = TRADER_SCOPE + [a for a in catalog.TRADER_EXTRA.get(depth, [])
                                     if a not in TRADER_SCOPE]

        # honor the board picker (mandatory data spine + synthesis always run)
        enabled = set(payload.get("agents_enabled") or [])
        scope = ([a for a in full_scope if a in enabled or a in TRADER_MANDATORY]
                 if enabled else full_scope)
        benched = [a for a in full_scope if a not in scope]

        await emitter.stage("intake_parser", "done", "L0")
        await emitter.stage("context_profiler", "done", "L0")
        await emitter.log("scope_planner", f"trader desk: {symbol} · {style} · "
                          f"{len(scope)} specialists", "info")
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

        # L1 — the trader's evidence base (history must land before L2)
        await m.market_history(ctx)
        if "market_data" not in ctx.state.outputs:
            await emitter.error("symbol unresolved — try RELIANCE.NS / AAPL / ^NSEI")
            return
        await asyncio.gather(*(f(ctx) for a, f in
                               (("news_intel", v.news_intel), ("macro_data", v.macro_data)) if a in on))
        # RAG memory: similar past decisions land on the board as evidence,
        # then the retrieval agent indexes everything for per-specialist reads
        await v.memory_recall(ctx)
        await meta.rag_memory(ctx)

        # L2 — deterministic chain first (each feeds the next), narrative in parallel
        await m.technical_analyst(ctx)
        await asyncio.gather(*(f(ctx) for a, f in
                               (("backtest_engineer", m.backtest_engineer),
                                ("stock_analyst", m.stock_analyst)) if a in on))
        if "quant_signals" in on:
            await m.quant_signals(ctx)
        if "risk_manager" in on:
            await m.risk_manager(ctx)
        # education + wider lenses ride the same blackboard (funds/options/plumbing
        # plus whatever world/human specialists this depth convened)
        await asyncio.gather(*(f(ctx) for a, f in
                               (("fund_analyst", m.fund_analyst), ("options_desk", m.options_desk),
                                ("microstructure", m.microstructure)) if a in on),
                             *(catalog.LENS_AGENTS[a](ctx) for a in on
                               if a in catalog.LENS_AGENTS
                               and a not in ("fund_analyst", "options_desk", "microstructure")))

        # L3 — crucible
        await asyncio.gather(*(f(ctx) for a, f in
                               (("red_team", v.red_team), ("fact_checker", v.fact_checker),
                                ("bias_auditor", v.bias_auditor)) if a in on))

        # gap-detector: retry reduced-depth agents after a cooldown
        await replay_degraded(ctx)

        # ═══ ROUND 1 — the complete first pass, results and all ═══
        async def synthesis(round_no: int = 1) -> None:
            await board.cross_pollinate(ctx)
            await board.compliance_scan(ctx)
            await m.weighing_trader(ctx)
            await m.verdict_trader(ctx)
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
