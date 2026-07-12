"""The conductor — Intelligent Mode's two-tier orchestra engine.

Every PLAYER (main expert) here runs its 4–5 junior INSTRUMENTS as real
sub-tasks: one structured call produces a distinct finding for each instrument,
which the player then synthesizes into an integrated take + a 0–10 score. Each
instrument is streamed as an `instrument` event so the glass box lights up both
tiers. The Manager decomposes the brief into a task graph across the players,
and a general (mode-agnostic) MCDA weighing turns the scores into the verdict.
"""
from __future__ import annotations

import asyncio
from typing import Any

from ..core.events import Emitter
from .base import Ctx
from .score import (ORCHESTRA_DIMENSIONS, DEPTH_FAMILIES, FAMILY_BY_ID, PLAYER_BY_ID,
                    Player, players_in)
from .venture import _num

# family → pipeline layer (drives the rail/flow-map grouping)
_LAYER_OF = {"02": "L0", "03": "L1", "04": "L2", "05": "L2", "06": "L2",
             "07": "L2", "08": "L2", "09": "L2", "10": "L3", "11": "L4"}

_SEM = asyncio.Semaphore(6)

_PLAY_SCHEMA = ('{"instruments": [{"name": str (the exact instrument name given), '
                '"finding": str (<=26 words — this junior\'s specific result for THIS brief, '
                'concrete not generic)}], '
                '"synthesis": str (<=90 words — your integrated take once every instrument reports), '
                '"verdict_line": str (<=110 chars), "score": float (0-10), "confidence": float (0-1), '
                '"key_insights": [str x2 (non-obvious, cross-instrument)], '
                '"what_would_change": str (<=20 words)}')


def layer_of(player: Player) -> str:
    return _LAYER_OF.get(player.family, "L2")


def _peer_headlines(ctx: Ctx, exclude: str, limit: int = 12) -> str:
    lines = []
    for pid, out in ctx.state.outputs.items():
        if pid == exclude or not isinstance(out, dict):
            continue
        vl = out.get("verdict_line")
        if vl:
            s = out.get("score")
            tag = f" ({s}/10)" if isinstance(s, (int, float)) else ""
            lines.append(f"- {pid}: {str(vl)[:100]}{tag}")
        if len(lines) >= limit:
            break
    return "\n".join(lines) if lines else "(you are among the first to report)"


async def play(ctx: Ctx, player: Player, brief_note: str = "") -> dict[str, Any]:
    """Run one player as a LEAD conducting its instruments (the two-tier unit)."""
    aid, layer = player.id, layer_of(player)
    fam = FAMILY_BY_ID.get(player.family)
    async with _SEM:
        await ctx.start(aid, layer)
        insts = player.instruments
        inst_list = "\n".join(f"  · {i.name} — {i.skill}" for i in insts)
        user_brief = str(ctx.state.raw.get("agent_context", {}).get(aid) or "").strip()
        system = (f"You are {player.name} {player.emoji}, a LEAD expert in an advisory orchestra "
                  f"({fam.name if fam else ''}). Your role: {player.role} You conduct "
                  f"{len(insts)} junior specialists (your instruments). For EACH instrument, produce "
                  "its specific finding for THIS brief — concrete, grounded in the evidence, never "
                  "generic. Then synthesize all of them into your integrated take and a defensible "
                  "0–10 score. Never invent numbers; cite the evidence or tag ESTIMATE.")
        user = (f"BRIEF: {str(ctx.state.brief)[:600]}\nPROFILE: {str(ctx.state.profile)[:240]}\n"
                + (f"USER'S DIRECT BRIEF TO YOU: {user_brief}\n" if user_brief else "")
                + (f"MANAGER'S NOTE: {brief_note}\n" if brief_note else "")
                + f"\nYOUR INSTRUMENTS (produce a finding for each, by exact name):\n{inst_list}\n\n"
                + f"WHAT COLLEAGUES HAVE FOUND SO FAR:\n{_peer_headlines(ctx, aid)}\n\n"
                + f"EVIDENCE BOARD:\n{ctx.state.evidence_digest(12, player.name)}\n\n"
                + "TASK: conduct your instruments, then give your integrated take + score.")
        await ctx.emit.prompt(aid, system, user)
        data, res = await ctx.llm.structured("t2", system, user, _PLAY_SCHEMA,
                                             max_tokens=760, agent=aid)

    findings = {}
    if data and isinstance(data.get("instruments"), list):
        for item in data["instruments"]:
            if isinstance(item, dict) and item.get("name"):
                findings[str(item["name"]).strip().lower()] = str(item.get("finding") or "")[:240]

    out: dict[str, Any] = {"player": True, "family": player.family}
    inst_out = []
    for i in insts:
        finding = findings.get(i.name.lower(), "")
        degraded_inst = not finding
        if degraded_inst:
            finding = f"(no model reached — {i.skill})"
        inst_out.append({"name": i.name, "skill": i.skill, "finding": finding})
        await ctx.emit.instrument(aid, i.name, i.skill, finding,
                                  "degraded" if degraded_inst else "done")

    if data and data.get("verdict_line"):
        out.update({
            "verdict_line": str(data.get("verdict_line"))[:200],
            "score": max(0.0, min(10.0, _num(data.get("score"), 5.0))),
            "confidence": max(0.05, min(0.95, _num(data.get("confidence"), 0.5))),
            "analysis": str(data.get("synthesis") or "")[:1200],
            "key_insights": [str(x)[:140] for x in (data.get("key_insights") or [])][:2],
            "what_would_change": str(data.get("what_would_change") or "")[:160],
            "instruments": inst_out, "route": res.route,
        })
        await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
        await ctx.emit.usage(aid, res.tokens, res.route)
    else:
        # honest degradation — the instruments still show, deterministically
        out.update({
            "verdict_line": f"{player.name}: no model reached — {len(insts)} instruments "
                            "carry deterministic placeholders",
            "analysis": player.role, "instruments": inst_out, "degraded": True,
            "key_insights": [], "what_would_change": "",
        })
        await ctx.emit.log(aid, "no model reached — instruments ran deterministic only", "warn")
    ctx.state.outputs[aid] = out
    await ctx.finish(aid, layer, out, res.route, res.tokens)
    return out


async def overlay_instruments(ctx: Ctx, player_id: str, findings: list[str]) -> None:
    """Show the instruments of a player that ran as a real EIP agent (grounding,
    crucible, delivery) — map its output items onto its named instruments so the
    two-tier glass box lights up for every player, not just the play()'d ones."""
    p = PLAYER_BY_ID.get(player_id)
    if p is None:
        return
    out = ctx.state.outputs.get(player_id)
    findings = [str(f)[:240] for f in findings if str(f).strip()]
    inst_out = []
    for idx, i in enumerate(p.instruments):
        finding = findings[idx] if idx < len(findings) else i.skill
        inst_out.append({"name": i.name, "skill": i.skill, "finding": finding})
        await ctx.emit.instrument(player_id, i.name, i.skill, finding, "done")
    if isinstance(out, dict):
        out["instruments"] = inst_out
        out.setdefault("player", True)
        out.setdefault("family", p.family)


async def play_family(ctx: Ctx, family_id: str, cast: list[str], brief_note: str = "") -> None:
    """Run every convened player in a family concurrently (a movement)."""
    players = [PLAYER_BY_ID[p] for p in cast if p in PLAYER_BY_ID
               and PLAYER_BY_ID[p].family == family_id]
    if players:
        await asyncio.gather(*(play(ctx, p, brief_note) for p in players),
                             return_exceptions=True)


# ── 🎼 Manager — decompose the brief into a task graph over the players ───────

async def manager_score(ctx: Ctx, depth: str) -> dict[str, list[str]]:
    """Cast the orchestra for this brief and emit the task graph (the DAG the
    glass box draws). Returns {family_id: [player_ids]} — the movements."""
    aid, layer = "manager", "L0"
    await ctx.emit.stage(aid, "queued", layer)
    await ctx.start(aid, layer)
    fams = list(DEPTH_FAMILIES.get(depth, DEPTH_FAMILIES["board"]))
    active = ["02"] + fams + ["10", "11"]
    cast: dict[str, list[str]] = {f: [p.id for p in players_in(f)] for f in active}

    # honour the board picker: benched players drop out (mandatory spine stays)
    enabled = set(ctx.state.raw.get("agents_enabled") or [])
    mandatory = {"intake_parser", "context_profiler", "scope_planner", "weighing_engine",
                 "red_team", "fact_checker", "bias_auditor", "connecting_dots",
                 "verdict_composer", "storytelling", "visualizer", "reporter"}
    if enabled:
        for f in cast:
            cast[f] = [p for p in cast[f] if p in enabled or p in mandatory]

    # a light LLM pass names the plan's focus + flags regulated content
    focus, regulated = "", False
    schema = ('{"focus": str (<=30 words — the plan\'s centre of gravity for this brief), '
              '"regulated": bool (legal/tax/financial/investment advice present)}')
    data, res = await ctx.llm.structured(
        "t3",
        "You are the Manager 🎼 conducting an advisory orchestra. You do not analyse; you PLAN. "
        "Given the brief and the cast, state the plan's focus and whether it touches regulated "
        "legal/tax/financial content.",
        f"BRIEF: {str(ctx.state.brief)[:600]}\nCAST: "
        + ", ".join(p for ps in cast.values() for p in ps),
        schema, max_tokens=200, agent=aid)
    if data:
        focus = str(data.get("focus") or "")[:200]
        regulated = bool(data.get("regulated"))
        await ctx.emit.usage(aid, res.tokens, res.route)

    n_players = sum(len(v) for v in cast.values())
    n_inst = sum(len(PLAYER_BY_ID[p].instruments) for ps in cast.values() for p in ps if p in PLAYER_BY_ID)
    movements = [{
        "id": f, "name": FAMILY_BY_ID[f].name, "color": FAMILY_BY_ID[f].color,
        "layer": _LAYER_OF.get(f, "L2"),
        "players": [{"id": p, "name": PLAYER_BY_ID[p].name, "emoji": PLAYER_BY_ID[p].emoji,
                     "instruments": [i.name for i in PLAYER_BY_ID[p].instruments]}
                    for p in cast[f] if p in PLAYER_BY_ID],
    } for f in active if cast.get(f)]
    graph = {"focus": focus, "regulated": regulated, "depth": depth,
             "n_players": n_players, "n_instruments": n_inst, "movements": movements,
             "edges": [[active[i], active[i + 1]] for i in range(len(active) - 1)],
             "route": res.route if data else "deterministic"}
    ctx.state.rounds["task_graph"] = graph
    await ctx.emit.partial("task_graph", graph)
    await ctx.emit.log(aid, f"scored the brief: {n_players} players · {n_inst} instruments across "
                            f"{len(movements)} movements" + (f" · {focus}" if focus else ""), "info")
    await ctx.finish(aid, layer, {
        "verdict_line": f"Orchestra scored — {n_players} players, {n_inst} instruments, "
                        f"{len(movements)} movements", "focus": focus, "regulated": regulated,
        "degraded": not bool(data)}, res.route if data else "", res.tokens if data else 0)
    return cast


# ── ⚖️ Weighing Engine — general MCDA verdict (deterministic t0) ──────────────

_BANDS = [(7.0, "GO", "PROCEED"), (4.5, "CONDITIONAL_GO", "PROCEED WITH CONDITIONS"),
          (0.0, "NO_GO", "RECONSIDER")]


async def weighing_orchestra(ctx: Ctx) -> None:
    """The Weighing Engine player scores the whole orchestra deterministically:
    each dimension = mean of its producing players' scores; missing dimensions
    renormalize; crucible penalties subtract; weighted sum → verdict band."""
    aid, layer = "weighing_engine", "L4"
    await ctx.start(aid, layer)
    o = ctx.state.outputs
    dims: dict[str, float] = {}
    for dim, producers in ORCHESTRA_DIMENSIONS.items():
        scores = [_num(o[p].get("score"), None) for p in producers
                  if p in o and isinstance(o[p].get("score"), (int, float))]
        scores = [s for s in scores if s is not None]
        if scores:
            dims[dim] = round(sum(scores) / len(scores), 2)
    if not dims:
        dims = {"Opportunity": 5.0}

    # crucible penalty: unsupported fact-checks + high-severity red-team attacks
    penalty = 0.0
    fc = o.get("fact_checker") or {}
    bad = sum(1 for c in (fc.get("checks") or []) if isinstance(c, dict)
              and str(c.get("verdict")) in ("unsupported", "contradicted"))
    rt = o.get("red_team") or {}
    attacks = sum(1 for a in (rt.get("attacks") or []) if isinstance(a, dict)
                  and _num(a.get("severity"), 0) >= 0.7)
    penalty = min(1.5, 0.2 * bad + 0.25 * attacks)

    base = sum(dims.values()) / len(dims)
    score = max(0.0, min(10.0, round(base - penalty, 2)))
    band = next((b for thr, b, _ in _BANDS if score >= thr), "NO_GO")
    label = next((lbl for thr, b, lbl in _BANDS if b == band), "RECONSIDER")

    ctx.state.dimensions = dims
    ctx.state.verdict = {
        "score": score, "band": label, "recommendation": band,
        "dimensions": dims,
        "reasoning": (f"Weighted MCDA across {len(dims)} dimensions "
                      f"({', '.join(dims)}) minus {penalty:.2f} crucible penalty "
                      f"({bad} unsupported claims, {attacks} severe attacks)."),
    }
    await ctx.emit.partial("radar", {"dimensions": dims, "overall": score})
    await ctx.emit.partial("verdict", ctx.state.verdict)
    await ctx.emit.log(aid, f"orchestra verdict: {score}/10 → {label} "
                            f"(penalty −{penalty:.2f})", "ok")
    await ctx.finish(aid, layer, {"verdict_line": f"{label} · {score}/10", **ctx.state.verdict})
