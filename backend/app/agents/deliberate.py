"""Round-2 deliberation — the all-to-all golden-arc pass, for EVERY layer.

The notebook flow (design pages 1-2): the user's input is fixed, then every
processing layer runs TWICE. Round 1 is the normal pipeline (each layer sees
only what came before it). Round 2 re-runs the layers LEFT TO RIGHT — L1, then
L2, then L3 — and every agent's round-2 prompt contains the FULL board's
round-1 findings plus the refreshed output of every layer already re-run. So
the first agent reads everyone, exactly like the last; grounding re-reads the
world knowing what the board found; the crucible re-attacks the refined board.

The round-1 snapshot (and the round-1 verdict, taken by the graphs before this
pass) is preserved so results show BOTH rounds: who revised, who converged,
and how the verdict itself moved. Weighing/verdict/synthesis then run again on
the deliberated board. Every successful refine emits a `round` event → the
second ✓ badge in the UI.

t0 agents (pure math: prices, indicators, backtests, sizing, budget math) are
excluded — re-running arithmetic with "context" would be theatre, not honesty.
"""
from __future__ import annotations

import asyncio
from typing import Any

from .base import Ctx
from .registry import BY_ID
from .venture import _ANALYSIS_SCHEMA, _num

_SEM = asyncio.Semaphore(6)

# layers re-run in round 2, in the notebook's left-to-right order
_ROUND2_LAYERS = ("L1", "L2", "L3")

# narrative agents (no numeric score) refine with a lighter schema
_NARRATIVE_SCHEMA = ('{"verdict_line": str (<=120 chars, refined), '
                     '"analysis": str (<=120 words — what changes now that you have read the full board), '
                     '"key_insights": [str x2 (cross-agent, round-2 insights)]}')


def _refinables(ctx: Ctx) -> dict[str, list[str]]:
    """layer → agent ids eligible for round 2: produced a verdict_line, is an
    LLM-tier agent (not t0 math), and lives in a round-2 layer."""
    by_layer: dict[str, list[str]] = {l: [] for l in _ROUND2_LAYERS}
    for k, v in ctx.state.outputs.items():
        meta = BY_ID.get(k)
        if (meta and meta.layer in _ROUND2_LAYERS and meta.tier != "t0"
                and isinstance(v, dict) and v.get("verdict_line")):
            by_layer[meta.layer].append(k)
    return by_layer


def _headlines(ctx: Ctx, ids: list[str]) -> str:
    o = ctx.state.outputs
    lines = []
    for k in ids:
        s = o[k].get("score")
        tag = f" (score {s}/10)" if isinstance(s, (int, float)) else ""
        lines.append(f"- {k}: {str(o[k].get('verdict_line'))[:110]}{tag}")
    return "\n".join(lines)


async def _refine_one(ctx: Ctx, aid: str, board_block: str, peers_all: list[str],
                      verdict_note: str) -> bool:
    """One agent's round 2: re-read the FULL board, refine, second ✓ on success."""
    prev = ctx.state.outputs[aid]
    meta = BY_ID[aid]
    scored = isinstance(prev.get("score"), (int, float))
    schema = _ANALYSIS_SCHEMA if scored else _NARRATIVE_SCHEMA
    async with _SEM:
        await ctx.emit.stage(aid, "active", meta.layer)
        await ctx.emit.collab(aid, peers_all)
        role_hint = {"L1": "You gathered the ground truth; now re-read your evidence knowing "
                           "what the whole board concluded — what did everyone miss or over-read?",
                     "L2": "Keep your domain lens — INTEGRATE colleagues, do not drift into "
                           "their specialties. If you change your score, say why.",
                     "L3": "Re-attack: the board has refined itself since your first pass — "
                           "find what NOW deserves the strongest challenge."}[meta.layer]
        system = (f"You are {meta.name}, the '{aid}' specialist, in DELIBERATION ROUND 2. "
                  "Round 1 was independent analysis; now the FULL board's findings are in front "
                  "of you. Refine YOUR output in the light of ALL of them. Never just restate "
                  f"round 1. {role_hint}")
        own = (f"YOUR ROUND-1 FINDING: {prev.get('verdict_line')}"
               + (f" (score {prev.get('score')}/10)" if scored else ""))
        user = (f"BRIEF: {str(ctx.state.brief)[:500]}\n{own}\n{verdict_note}"
                f"THE FULL BOARD, ROUND 1 (every specialist):\n{board_block}\n\n"
                f"TASK: your refined round-2 take as {meta.name}. key_insights must be "
                "cross-agent insights you could only see with the whole board visible.")
        await ctx.emit.prompt(aid, system, user)
        data, res = await ctx.llm.structured("t2", system, user, schema, max_tokens=650, agent=aid)
    if data and data.get("verdict_line") and (not scored or isinstance(data.get("score"), (int, float))):
        refined: dict[str, Any] = dict(prev)
        for k in ("verdict_line", "score", "confidence", "analysis",
                  "key_insights", "what_would_change", "assumptions"):
            if data.get(k) is not None:
                refined[k] = data[k]
        if scored:
            refined["score"] = max(0.0, min(10.0, _num(refined.get("score"), 5.0)))
            refined["confidence"] = max(0.05, min(0.95, _num(refined.get("confidence"), 0.5)))
            delta = round(refined["score"] - _num(prev.get("score"), refined["score"]), 2)
            if abs(delta) >= 0.1:
                await ctx.emit.log(aid, f"round 2: revised {prev.get('score')} → {refined['score']} "
                                        "after reading the full board", "info")
        refined["degraded"] = False
        refined["route"] = res.route
        refined["round"] = 2
        await ctx.emit.usage(aid, res.tokens, res.route)
        await ctx.finish(aid, meta.layer, refined)
        await ctx.emit.round(aid, 2)   # the second ✓
        return True
    await ctx.emit.log(aid, "round 2 skipped for this agent (no LLM) — round-1 finding stands", "muted")
    await ctx.emit.stage(aid, "degraded" if prev.get("degraded") else "done", meta.layer)
    return False


async def deliberation_round(ctx: Ctx) -> None:
    """The full second pass: L1 → L2 → L3, each layer reading the refreshed
    board left behind by the layers already re-run (notebook pages 1-2)."""
    by_layer = _refinables(ctx)
    all_ids = [a for ids in by_layer.values() for a in ids]
    if len(all_ids) < 3:
        return
    o = ctx.state.outputs
    round1 = {k: {"score": o[k].get("score"), "verdict_line": o[k].get("verdict_line"),
                  "confidence": o[k].get("confidence")} for k in all_ids}
    ctx.state.rounds.update({"round1": round1})
    v1 = ctx.state.rounds.get("verdict1")
    verdict_note = (f"ROUND-1 BOARD VERDICT: {v1}\n" if v1 else "")
    await ctx.emit.log("scope_planner",
                       f"⟳ deliberation round 2 — {len(all_ids)} agents across "
                       f"L1/L2/L3 re-read the FULL board, layer by layer", "info")

    refined_n = 0
    for layer in _ROUND2_LAYERS:
        ids = by_layer[layer]
        if not ids:
            continue
        # headlines are REBUILT before each layer, so L2's round 2 reads the
        # refreshed L1, and L3's round 2 reads the refreshed L1+L2
        board_block = _headlines(ctx, all_ids)
        results = await asyncio.gather(
            *(_refine_one(ctx, aid, board_block, [p for p in all_ids if p != aid], verdict_note)
              for aid in ids),
            return_exceptions=True)
        refined_n += sum(1 for r in results if r is True)

    deltas = []
    for k in all_ids:
        b, a = round1[k].get("score"), o[k].get("score")
        if isinstance(b, (int, float)) and isinstance(a, (int, float)):
            deltas.append({"agent": k, "before": round(float(b), 1), "after": round(float(a), 1),
                           "delta": round(float(a) - float(b), 2)})
    revised = sum(1 for d in deltas if abs(d["delta"]) >= 0.3)
    ctx.state.rounds.update({
        "round2": {k: {"score": o[k].get("score"), "verdict_line": o[k].get("verdict_line")}
                   for k in all_ids},
        "deltas": deltas, "refined": refined_n, "revised": revised,
    })
    await ctx.emit.partial("rounds", dict(ctx.state.rounds))
    await ctx.emit.log("scope_planner",
                       f"deliberation done — {refined_n}/{len(all_ids)} refined across all layers, "
                       f"{revised} revised their score", "ok" if refined_n else "warn")
