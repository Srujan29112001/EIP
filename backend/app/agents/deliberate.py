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


def _line_of(out: dict[str, Any]) -> str:
    """A one-line summary of ANY agent's output — verdict_line when present,
    else the first informative field (so grounding/crucible agents that never
    produce a scored verdict still deliberate in round 2)."""
    for key in ("verdict_line", "no_case", "summary", "note"):
        if out.get(key):
            return str(out[key])
    for key in ("attacks", "checks", "biases", "key_facts", "insights"):
        v = out.get(key)
        if isinstance(v, list) and v:
            return str(v[0])[:120]
    return "completed round 1"


def _refinables(ctx: Ctx) -> dict[str, list[str]]:
    """layer → agent ids eligible for round 2: any LLM-tier agent (not t0
    math) with an output, in L1/L2/L3 — grounding and crucible included."""
    by_layer: dict[str, list[str]] = {l: [] for l in _ROUND2_LAYERS}
    for k, v in ctx.state.outputs.items():
        meta = BY_ID.get(k)
        if (meta and meta.layer in _ROUND2_LAYERS and meta.tier != "t0"
                and isinstance(v, dict)):
            by_layer[meta.layer].append(k)
    return by_layer


def _headlines(ctx: Ctx, ids: list[str]) -> str:
    o = ctx.state.outputs
    lines = []
    for k in ids:
        s = o[k].get("score")
        tag = f" (score {s}/10)" if isinstance(s, (int, float)) else ""
        lines.append(f"- {k}: {_line_of(o[k])[:110]}{tag}")
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
        own = (f"YOUR ROUND-1 FINDING: {_line_of(prev)}"
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


async def refine_gateway(ctx: Ctx) -> None:
    """L0's round 2 — the gateway re-reads its own framing in the light of the
    round-1 results. The intake brief and profile are REFINED (not re-parsed —
    the user's input is fixed, like the notebook's 'User Input = A'), and the
    scope planner re-audits board coverage. Each earns its second ✓."""
    v1 = ctx.state.rounds.get("verdict1") or {}
    top = _headlines(ctx, [a for ids in _refinables(ctx).values() for a in ids][:14])

    # intake_parser: sharpen the brief with what the board actually found
    await ctx.emit.stage("intake_parser", "active", "L0")
    schema = ('{"keywords": [str x4-8 (refined, incl. themes the board surfaced)], '
              '"uncertainty": str (<=15 words - the REAL open question after round 1)}')
    data, res = await ctx.llm.structured(
        "t1",
        "You are the intake parser in deliberation round 2. The user's input is fixed; "
        "refine the BRIEF's keywords and core uncertainty using what the board found in round 1.",
        f"BRIEF: {str(ctx.state.brief)[:400]}\nROUND-1 VERDICT: {v1}\nBOARD FINDINGS:\n{top[:1200]}",
        schema, max_tokens=250, agent="intake_parser")
    if data and isinstance(data.get("keywords"), list) and data["keywords"]:
        ctx.state.brief["keywords"] = [str(k)[:40] for k in data["keywords"]][:8]
        if data.get("uncertainty"):
            ctx.state.brief["uncertainty"] = str(data["uncertainty"])[:120]
        await ctx.emit.usage("intake_parser", res.tokens, res.route)
        await ctx.emit.partial("brief", ctx.state.brief)
        await ctx.emit.log("intake_parser", "round 2: brief sharpened with the board's findings", "info")
        await ctx.emit.stage("intake_parser", "done", "L0")
        await ctx.emit.round("intake_parser", 2)
    else:
        await ctx.emit.stage("intake_parser", "done", "L0")

    # context_profiler: deterministic re-read (risk posture vs the round-1 verdict)
    await ctx.emit.stage("context_profiler", "active", "L0")
    score = v1.get("score")
    if isinstance(score, (int, float)):
        posture = ("verdict supports the profile's risk capacity" if score >= 6
                   else "verdict is below the comfort line — profile flags caution")
        ctx.state.profile["round2_posture"] = posture
        await ctx.emit.log("context_profiler", f"round 2: {posture}", "info")
    await ctx.emit.stage("context_profiler", "done", "L0")
    await ctx.emit.round("context_profiler", 2)

    # scope_planner: deterministic coverage audit of the convened board
    await ctx.emit.stage("scope_planner", "active", "L0")
    degraded = [k for k, v in ctx.state.outputs.items()
                if isinstance(v, dict) and v.get("degraded")]
    await ctx.emit.log("scope_planner",
                       f"round 2 coverage audit: {len(ctx.state.outputs)} agents reported, "
                       f"{len(degraded)} still deterministic-only", "info" if not degraded else "warn")
    await ctx.emit.stage("scope_planner", "done", "L0")
    await ctx.emit.round("scope_planner", 2)


def result_snapshot(ctx: Ctx, round_no: int) -> dict[str, Any]:
    """A COMPLETE result set for one round — verdict, dimensions, pitch,
    cross-links, compliance, charts, report — so the Results view can show
    round 1 and round 2 side by side, in full."""
    o = ctx.state.outputs
    story = o.get("storytelling") or {}
    cross = o.get("cross_pollinate") or {}
    comp = o.get("compliance_scan") or {}
    return {
        "round": round_no,
        "verdict": dict(ctx.state.verdict),
        "dimensions": dict(ctx.state.dimensions),
        "story": {k: story.get(k) for k in ("hook", "narrative", "one_liner", "three_beats")
                  if story.get(k)},
        "cross": {"connections": (cross.get("connections") or [])[:7],
                  "emergent": (cross.get("emergent") or [])[:3]},
        "compliance": (comp.get("alerts") or [])[:8],
        "charts": (o.get("visualizer", {}) or {}).get("charts") or [],
        "report": str((o.get("reporter", {}) or {}).get("report_md") or "")[:24000],
    }


async def emit_result_set(ctx: Ctx, round_no: int) -> None:
    snap = result_snapshot(ctx, round_no)
    ctx.state.rounds.setdefault("results", {})[str(round_no)] = {
        k: snap[k] for k in ("verdict", "dimensions", "story")}   # persist the light core
    await ctx.emit.partial("result_set", snap)


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
