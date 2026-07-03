"""The trading pipeline (Trader mode): history → technicals → backtests →
signal ensemble → risk plan → crucible → setup verdict.

Same blackboard, same SSE contract, same glass box as the venture pipeline —
different specialists, and a verdict that is explicitly setup-quality
education, never advice (MASTER_PLAN §5.4).
"""
from __future__ import annotations

import asyncio
import traceback

from ..agents import markets as m
from ..agents import venture as v
from ..agents.base import Ctx, RunState
from ..core.events import Emitter
from ..core.llm_gateway import EngineConfig, Gateway
from ..memory.store import save_run

TRADER_SCOPE = ["news_intel", "market_data", "macro_data",
                "technical_analyst", "stock_analyst", "backtest_engineer",
                "quant_signals", "risk_manager",
                "red_team", "fact_checker", "bias_auditor",
                "weighing_engine", "verdict_composer"]


async def run_trading(run_id: str, payload: dict, emitter: Emitter) -> None:
    try:
        eng = payload.get("engine") or {}
        cfg = EngineConfig(**{k: val for k, val in eng.items() if k in EngineConfig.__dataclass_fields__})
        ctx = Ctx(emit=emitter, llm=Gateway(cfg), state=RunState(run_id=run_id, raw=payload))

        # L0 — trader intake (deterministic; the symbol IS the brief)
        symbol = (payload.get("symbol") or "").strip().upper()
        style = payload.get("trading_style") or "swing"
        ctx.state.brief = {
            "summary": f"Trading analysis: {symbol} ({style} style)",
            "industry": "", "geography": payload.get("geography", "India"),
            "stage": style, "keywords": [symbol.lower()],
            "uncertainty": payload.get("uncertainty", ""),
        }
        ctx.state.profile = {"persona": f"{style} trader", "capital_band": payload.get("capital", ""),
                             "risk_capacity": f"{payload.get('risk_pct', 1)}% per trade",
                             "geography": payload.get("geography", "India")}
        await emitter.stage("intake_parser", "done", "L0")
        await emitter.stage("context_profiler", "done", "L0")
        await emitter.log("scope_planner", f"trader desk: {symbol} · {style} · "
                          f"{len(TRADER_SCOPE)} specialists", "info")
        ctx.state.scope = TRADER_SCOPE
        for s in TRADER_SCOPE:
            await emitter.stage(s, "queued", "")
        await emitter.partial("brief", ctx.state.brief)
        await emitter.partial("scope", TRADER_SCOPE)
        await emitter.stage("scope_planner", "done", "L0")

        # L1 — the trader's evidence base (history must land before L2)
        await m.market_history(ctx)
        if "market_data" not in ctx.state.outputs:
            await emitter.error("symbol unresolved — try RELIANCE.NS / AAPL / ^NSEI")
            return
        await asyncio.gather(v.news_intel(ctx), v.macro_data(ctx))

        # L2 — deterministic chain first (each feeds the next), narrative in parallel
        await m.technical_analyst(ctx)
        await asyncio.gather(m.backtest_engineer(ctx), m.stock_analyst(ctx))
        await m.quant_signals(ctx)
        await m.risk_manager(ctx)

        # L3 — crucible
        await asyncio.gather(v.red_team(ctx), v.fact_checker(ctx), v.bias_auditor(ctx))

        # L4 — synthesis
        await m.weighing_trader(ctx)
        await m.verdict_trader(ctx)

        await save_run(ctx.state)
        await emitter.done(run_id)
    except Exception:
        await emitter.log("verdict_composer", traceback.format_exc(limit=3), "err")
        await emitter.error("pipeline failed — see log")
