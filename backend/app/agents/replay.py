"""Gap-detector replay (Phase 9) — and the pragmatic fix for free-tier rate
limits. After the board runs, any agent that only reached its deterministic
core (degraded) is retried once, AFTER a cooldown long enough for a
per-minute token/request quota to refresh. On one free key this typically
rescues most of the reduced-depth agents so the final board is fully narrated.
"""
from __future__ import annotations

import asyncio

from . import board, human, markets, venture as v, wealth
from .base import Ctx

# every agent whose depth an LLM can restore (t0 deterministic agents are
# never "degraded", so they are intentionally absent here)
RERUNNABLE = {
    "market_analyst": v.market_analyst,
    "finance_modeler": v.finance_modeler,
    "red_team": v.red_team,
    "fact_checker": v.fact_checker,
    **board.BOARD_AGENTS,      # competitor_intel … devils_advocate, connecting_dots
    **board.WORLD_WAVE,        # macroeconomist … esg_impact
    **human.HUMAN_AGENTS,      # human_behaviour … philanthropy_impact
    "stock_analyst": markets.stock_analyst,
    "fund_analyst": markets.fund_analyst,
    "options_desk": markets.options_desk,
    "microstructure": markets.microstructure,
    "debt_banking": wealth.debt_banking,
    "real_estate": wealth.real_estate,
    "location_scout": wealth.location_scout,
}


async def replay_degraded(ctx: Ctx, passes: int = 2, cooldown: float = 22.0) -> bool:
    """Retry reduced-depth agents after a cooldown. Returns True if any were
    rescued (so the caller can refresh the synthesis layer)."""
    rescued_any = False
    for p in range(passes):
        degraded = [aid for aid, out in ctx.state.outputs.items()
                    if isinstance(out, dict) and out.get("degraded") and aid in RERUNNABLE]
        if not degraded:
            break
        # only worth retrying if a live route exists at all
        status = await ctx.llm.status()
        if not status.get("cloud") and not status.get("local"):
            await ctx.emit.log("scope_planner",
                               f"gap-detector: {len(degraded)} agents reduced-depth, but no LLM configured — "
                               "add API keys to narrate them", "warn")
            break
        await ctx.emit.log("scope_planner",
                           f"gap-detector pass {p + 1}: retrying {len(degraded)} reduced-depth agents "
                           f"after a {int(cooldown)}s cooldown (quota refresh)", "warn")
        await asyncio.sleep(cooldown)
        # sequential + gentle: one key's per-minute budget is the constraint
        for aid in degraded:
            try:
                await RERUNNABLE[aid](ctx)
            except Exception:
                pass
        now_degraded = sum(1 for aid in degraded
                           if ctx.state.outputs.get(aid, {}).get("degraded"))
        rescued = len(degraded) - now_degraded
        rescued_any = rescued_any or rescued > 0
        await ctx.emit.log("scope_planner",
                           f"gap-detector: rescued {rescued}/{len(degraded)} agents",
                           "ok" if rescued else "muted")
        # stop if everyone is rescued, or if a pass rescued nobody (keys are
        # dead, not merely rate-limited — a second cooldown won't help)
        if now_degraded == 0 or rescued == 0:
            break
    return rescued_any
