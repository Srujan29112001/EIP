"""Scenario Planner (L4, t0) — Monte-Carlo the verdict.

Pure deterministic math, no LLM: the board's dimension scores are perturbed
1000 times under assumption noise (wider when the board's confidence is low),
giving a DISTRIBUTION over the verdict instead of a single number — P10/P50/
P90, the probability of GO vs NO-GO, and the dimension that most often breaks
the case. This is the first "future improvements" agent to graduate into the
roster: predictions with an explicit uncertainty band.
"""
from __future__ import annotations

import random
import statistics
from typing import Any

from .base import Ctx

_DRAWS = 1000


async def scenario_planner(ctx: Ctx) -> None:
    aid, layer = "scenario_planner", "L4"
    await ctx.start(aid, layer)
    dims = {k: float(v) for k, v in (ctx.state.dimensions or {}).items()
            if isinstance(v, (int, float))}
    if len(dims) < 2:
        await ctx.emit.log(aid, "not enough dimensions to simulate", "muted")
        await ctx.finish(aid, layer, {"verdict_line": "scenario simulation skipped — no dimensions",
                                      "degraded": False})
        return

    # noise per dimension: wider when the contributing agents were less confident
    confs = [float(o.get("confidence")) for o in ctx.state.outputs.values()
             if isinstance(o, dict) and isinstance(o.get("confidence"), (int, float))]
    avg_conf = statistics.fmean(confs) if confs else 0.5
    sigma = 0.6 + (1.0 - avg_conf) * 1.2   # 0.6 (confident board) … 1.8 (guessing board)

    rng = random.Random(ctx.state.run_id)   # seeded → reproducible per run
    keys = list(dims)
    overalls: list[float] = []
    fail_hits = {k: 0 for k in keys}
    for _ in range(_DRAWS):
        draw = {k: min(10.0, max(0.0, rng.gauss(dims[k], sigma))) for k in keys}
        overall = statistics.fmean(draw.values())
        overalls.append(overall)
        if overall < 4.5:   # a NO-GO draw — which dimension dragged it?
            worst = min(keys, key=lambda k: draw[k] - dims[k])
            fail_hits[worst] += 1

    overalls.sort()
    p10 = round(overalls[int(_DRAWS * 0.10)], 1)
    p50 = round(overalls[int(_DRAWS * 0.50)], 1)
    p90 = round(overalls[int(_DRAWS * 0.90)], 1)
    # 14-bin histogram over 0-10 → the "1000 simulated verdicts" distribution chart
    n_bins, step = 14, 10.0 / 14
    bins = [0] * n_bins
    for o in overalls:
        bins[min(n_bins - 1, int(o / step))] += 1
    prob_go = round(sum(1 for o in overalls if o >= 7.0) / _DRAWS, 2)
    prob_nogo = round(sum(1 for o in overalls if o < 4.5) / _DRAWS, 2)
    breaks_it = max(fail_hits, key=fail_hits.get) if any(fail_hits.values()) else ""

    line = (f"P50 {p50}/10 · band {p10}–{p90} · P(GO) {int(prob_go * 100)}% · "
            f"P(NO-GO) {int(prob_nogo * 100)}%")
    await ctx.emit.log(aid, f"{_DRAWS} scenario draws (σ={sigma:.2f} from board confidence) — {line}", "code")
    if breaks_it:
        await ctx.emit.log(aid, f"what breaks the case most often: {breaks_it}", "info")
        await ctx.emit.claim(aid, f"Under uncertainty the case most often breaks on {breaks_it} "
                                  f"(P(NO-GO) {int(prob_nogo * 100)}%)", confidence=0.7)
    out: dict[str, Any] = {
        "verdict_line": line, "degraded": False,
        "p10": p10, "p50": p50, "p90": p90,
        "prob_go": prob_go, "prob_nogo": prob_nogo,
        "sigma": round(sigma, 2), "breaks_it": breaks_it, "draws": _DRAWS,
        "bins": bins, "bin_start": 0.0, "bin_step": round(step, 3),
    }
    await ctx.finish(aid, layer, out)
