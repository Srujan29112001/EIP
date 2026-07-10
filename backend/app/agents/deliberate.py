"""Round-2 deliberation — the all-to-all golden-arc pass.

Round 1 runs the domain layer in two waves, so early agents never see their
peers and late agents see only wave 1 (the ordering unfairness). Round 2 fixes
that: EVERY domain specialist re-runs with the FULL board's round-1 findings in
its prompt — the first agent now reads everyone, exactly like the last one.

The round-1 snapshot is kept (RunState.rounds) so the results can show both
rounds side by side: who revised their score after reading the whole board,
who converged, who dug in. Weighing/verdict/reporter then run on the REFINED
outputs — the verdict reflects a board that has actually deliberated.
"""
from __future__ import annotations

import asyncio
from typing import Any

from .base import Ctx
from .registry import BY_ID
from .venture import _ANALYSIS_SCHEMA, _num

# refine calls are smaller than round-1 analysis (no research block, tighter
# ask) but there are many at once — same semaphore discipline as the gateway
_SEM = asyncio.Semaphore(6)


def _l2_scored(ctx: Ctx) -> list[str]:
    """Domain specialists that produced a scored round-1 finding."""
    out = []
    for k, v in ctx.state.outputs.items():
        if (isinstance(v, dict) and v.get("verdict_line")
                and isinstance(v.get("score"), (int, float))
                and k in BY_ID and BY_ID[k].layer == "L2"):
            out.append(k)
    return out


async def _refine_one(ctx: Ctx, aid: str, headlines: str, peers_all: list[str]) -> bool:
    """One specialist re-reads the FULL board and refines its round-1 finding.
    Returns True if the refinement upgraded the output (LLM answered)."""
    prev = ctx.state.outputs[aid]
    meta = BY_ID[aid]
    async with _SEM:
        await ctx.emit.stage(aid, "active", "L2")
        # the full mesh goes live: this agent is now reading EVERY colleague
        await ctx.emit.collab(aid, peers_all)
        system = (f"You are {meta.name}, the '{aid}' specialist on a decision board, in "
                  "DELIBERATION ROUND 2. In round 1 every specialist analyzed independently; "
                  "now the full board's findings are in front of you. Refine YOUR analysis in "
                  "the light of ALL of them: revise your score if a colleague's evidence "
                  "genuinely moves you, defend it if it doesn't, and surface the NEW insight "
                  "you could only see with the whole board visible. Never just restate round 1.")
        user = (f"BRIEF: {ctx.state.brief}\n"
                f"YOUR ROUND-1 FINDING: {prev.get('verdict_line')} "
                f"(score {prev.get('score')}/10, confidence {prev.get('confidence')})\n"
                f"THE FULL BOARD'S ROUND-1 FINDINGS (every specialist):\n{headlines}\n\n"
                f"TASK: Your refined take as {meta.name}. Keep your domain lens — do not drift "
                "into colleagues' specialties; INTEGRATE them. If you change your score, say "
                "why in the analysis. key_insights must be round-2 insights (cross-agent), "
                "not repeats.")
        await ctx.emit.prompt(aid, system, user)   # glass box: round-2 prompt visible too
        data, res = await ctx.llm.structured("t2", system, user, _ANALYSIS_SCHEMA,
                                             max_tokens=700, agent=aid)
    if data and isinstance(data.get("score"), (int, float)):
        refined: dict[str, Any] = dict(prev)   # keep numbers_used, research, etc.
        for k in ("verdict_line", "score", "confidence", "analysis",
                  "key_insights", "what_would_change", "assumptions"):
            if data.get(k) is not None:
                refined[k] = data[k]
        refined["score"] = max(0.0, min(10.0, _num(refined.get("score"), 5.0)))
        refined["confidence"] = max(0.05, min(0.95, _num(refined.get("confidence"), 0.5)))
        refined["degraded"] = False
        refined["route"] = res.route
        refined["round"] = 2
        delta = round(refined["score"] - _num(prev.get("score"), refined["score"]), 2)
        if abs(delta) >= 0.1:
            await ctx.emit.log(aid, f"round 2: revised {prev.get('score')} → "
                                    f"{refined['score']} after reading the full board", "info")
        await ctx.emit.usage(aid, res.tokens, res.route)
        await ctx.finish(aid, "L2", refined)
        return True
    # LLM starved on the refine → keep the round-1 finding, restore its status
    await ctx.emit.log(aid, "round 2 skipped for this agent (no LLM) — round-1 finding stands", "muted")
    await ctx.emit.stage(aid, "degraded" if prev.get("degraded") else "done", "L2")
    return False


async def deliberation_round(ctx: Ctx) -> None:
    """The second pass over the whole domain layer (notebook flow, pages 1-2)."""
    l2 = _l2_scored(ctx)
    if len(l2) < 3:
        return   # nothing meaningful to deliberate
    o = ctx.state.outputs
    round1 = {k: {"score": o[k].get("score"), "verdict_line": o[k].get("verdict_line"),
                  "confidence": o[k].get("confidence")} for k in l2}
    ctx.state.rounds = {"round1": round1}
    headlines = "\n".join(
        f"- {k}: {str(o[k].get('verdict_line'))[:120]} (score {o[k].get('score')}/10)"
        for k in l2)
    await ctx.emit.log("scope_planner",
                       f"⟳ deliberation round 2 — all {len(l2)} specialists re-read the FULL board "
                       f"({len(l2) * (len(l2) - 1)} directed hand-offs)", "info")

    results = await asyncio.gather(
        *(_refine_one(ctx, aid, headlines, [p for p in l2 if p != aid]) for aid in l2),
        return_exceptions=True)
    refined_n = sum(1 for r in results if r is True)

    deltas = []
    for k in l2:
        before = _num(round1[k].get("score"), 0.0)
        after = _num(o[k].get("score"), before)
        deltas.append({"agent": k, "before": round(before, 1), "after": round(after, 1),
                       "delta": round(after - before, 2)})
    revised = sum(1 for d in deltas if abs(d["delta"]) >= 0.3)
    ctx.state.rounds["round2"] = {k: {"score": o[k].get("score"),
                                      "verdict_line": o[k].get("verdict_line")} for k in l2}
    ctx.state.rounds["deltas"] = deltas
    ctx.state.rounds["refined"] = refined_n
    ctx.state.rounds["revised"] = revised
    await ctx.emit.partial("rounds", {"round1": round1, "round2": ctx.state.rounds["round2"],
                                      "deltas": deltas, "refined": refined_n, "revised": revised})
    await ctx.emit.log("scope_planner",
                       f"deliberation done — {refined_n}/{len(l2)} refined, {revised} revised "
                       f"their score after seeing everyone", "ok" if refined_n else "warn")
