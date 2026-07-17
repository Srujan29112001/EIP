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


def _peer_headlines(ctx: Ctx, exclude: str, limit: int = 12) -> tuple[str, list[str]]:
    """(headline block, the peer ids injected) — the ids drive the gold collab arcs."""
    lines: list[str] = []
    ids: list[str] = []
    for pid, out in ctx.state.outputs.items():
        if pid == exclude or not isinstance(out, dict):
            continue
        vl = out.get("verdict_line")
        if vl:
            s = out.get("score")
            tag = f" ({s}/10)" if isinstance(s, (int, float)) else ""
            lines.append(f"- {pid}: {str(vl)[:100]}{tag}")
            ids.append(pid)
        if len(lines) >= limit:
            break
    return ("\n".join(lines) if lines else "(you are among the first to report)"), ids


# per-player depth (the Manager's "cast, then set depth" — everyone contributes,
# the Scope Planner decides who writes a novel and who writes a memo)
_DEPTH_TOKENS = {"deep": 1000, "standard": 760, "light": 520}
_DEPTH_NOTE = {
    "deep": "The Manager cast you DEEP on this engagement — this dimension is load-bearing. "
            "Each instrument finding must be specific and evidenced; go past the obvious.",
    "light": "The Manager cast you LIGHT — cover your dimension crisply, one sharp finding "
             "per instrument, no padding.",
}


async def play(ctx: Ctx, player: Player, brief_note: str = "") -> dict[str, Any]:
    """Run one player as a LEAD conducting its instruments (the two-tier unit).
    Honours the Manager's score: team-lead casting, per-player depth, and the
    hand-off question assigned to this player."""
    aid, layer = player.id, layer_of(player)
    fam = FAMILY_BY_ID.get(player.family)
    plan = ctx.state.rounds.get("task_graph") or {}
    is_lead = plan.get("team_lead") == aid
    depth = str((plan.get("depths") or {}).get(aid) or "standard")
    handoff = next((str(k.get("q") or "") for k in (plan.get("key_questions") or [])
                    if isinstance(k, dict) and k.get("assign") == aid), "")
    async with _SEM:
        await ctx.start(aid, layer)
        insts = player.instruments
        inst_list = "\n".join(f"  · {i.name} — {i.skill}" for i in insts)
        user_brief = str(ctx.state.raw.get("agent_context", {}).get(aid) or "").strip()
        peers_block, peer_ids = _peer_headlines(ctx, aid)
        system = (f"You are {player.name} {player.emoji}, a LEAD expert in an advisory orchestra "
                  f"({fam.name if fam else ''}). Your role: {player.role} "
                  + ("You are also THE ENGAGEMENT LEAD the Manager cast for this brief — your "
                     "section carries the thesis; colleagues will calibrate against you. " if is_lead else "")
                  + f"You conduct {len(insts)} junior specialists (your instruments). For EACH "
                  "instrument, produce its specific finding for THIS brief — concrete, grounded in "
                  "the evidence, never generic. Then synthesize all of them into your integrated "
                  "take and a defensible 0–10 score. Never invent numbers; cite the evidence or "
                  "tag ESTIMATE." + (" " + _DEPTH_NOTE[depth] if depth in _DEPTH_NOTE else ""))
        user = (f"BRIEF: {str(ctx.state.brief)[:600]}\nPROFILE: {str(ctx.state.profile)[:240]}\n"
                + (f"USER'S DIRECT BRIEF TO YOU: {user_brief}\n" if user_brief else "")
                + (f"MANAGER'S HAND-OFF QUESTION TO YOU (answer it explicitly): {handoff}\n" if handoff else "")
                + (f"MANAGER'S NOTE: {brief_note}\n" if brief_note else "")
                + f"\nYOUR INSTRUMENTS (produce a finding for each, by exact name):\n{inst_list}\n\n"
                + f"WHAT COLLEAGUES HAVE FOUND SO FAR:\n{peers_block}\n\n"
                + f"EVIDENCE BOARD:\n{ctx.state.evidence_digest(14 if depth == 'deep' else 10, player.name)}\n\n"
                + "TASK: conduct your instruments, then give your integrated take + score.")
        await ctx.emit.prompt(aid, system, user)
        data, res = await ctx.llm.structured(
            "t3" if is_lead else "t2", system, user, _PLAY_SCHEMA,
            max_tokens=_DEPTH_TOKENS.get(depth, 760) + (240 if is_lead else 0), agent=aid)
        if peer_ids:
            # A2A: this player audibly built on these colleagues — light the gold arcs
            await ctx.emit.collab(aid, peer_ids[:10])

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
        # honest degradation — but the deterministic core still ANSWERS
        # (Constitution rule 11: a score exists at every node, even zero-key);
        # neutral 5.0 nudged by how much evidence this player's dimension has
        ev_hits = len([e for e in ctx.state.evidence
                       if player.name.split(" ")[0].lower() in str(e.get("text", "")).lower()])
        det_score = round(min(6.5, 5.0 + 0.25 * min(ev_hits, 6)), 2)
        out.update({
            "verdict_line": f"{player.name}: no model reached — deterministic baseline "
                            f"{det_score}/10, {len(insts)} instruments carry placeholders",
            "analysis": player.role, "instruments": inst_out, "degraded": True,
            "score": det_score, "confidence": 0.3,
            "key_insights": [], "what_would_change": "a reachable model would narrate this section",
        })
        await ctx.emit.log(aid, "no model reached — deterministic baseline shipped (amber)", "warn")
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
    # intake_parser/context_profiler store the brief/profile dict ITSELF as
    # their output — overlaying onto the shared object would pollute every
    # downstream prompt with instruments; detach onto a copy first
    if out is ctx.state.brief or out is ctx.state.profile:
        out = dict(out)
        ctx.state.outputs[player_id] = out
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


# ── 🎼 Manager — SCORE the brief into a task graph over the players ───────────
# The conversation's contract: cast every player (coverage), then SET DEPTH per
# player; select the engagement lead; write the hand-off questions (the DAG's
# contracts); the Whiplash standard — every player and every instrument works.

_SCORE_SCHEMA = ('{"team_lead": str (ONE player id — the expert whose dimension carries this '
                 'specific brief), '
                 '"focus": str (<=30 words — the plan\'s centre of gravity), '
                 '"regulated": bool (legal/tax/financial/investment advice present), '
                 '"convene": [str (ONLY the analytical player ids THIS brief actually needs — '
                 'typically 12-35; leave out everything peripheral)], '
                 '"bench": [{"id": str (a player you deliberately did NOT convene), '
                 '"reason": str (<=14 words — why this brief does not need them)} x3-10], '
                 '"deep": [str x3-6 (convened ids whose dimension is LOAD-BEARING — they go deep)], '
                 '"light": [str x0-8 (convened ids kept crisp)], '
                 '"key_questions": [{"assign": str (convened id), "q": str (<=20 words — the '
                 'hand-off question that player MUST answer for the thesis)} x4-7], '
                 '"rounds": int (1 = simple brief, one pass · 2 = full two-round deliberation), '
                 '"debate": bool (open live debate rounds — only for high-stakes/contested briefs), '
                 '"beyond_hint": str (<=20 words — the direction the client did NOT ask about '
                 'but should hear)}')

# the unbenchable spine: framing (02), adversarial QA (10), delivery (11) —
# someone always parses, someone always attacks, someone always signs
_SPINE_FAMILIES = ("02", "10", "11")
_ANALYTICAL_FAMILIES = ("03", "04", "05", "06", "07", "08", "09")
# zero-key fallback cast: the proven general board (tech joins only when the
# Manager can actually reason about whether the brief needs it)
_FALLBACK_FAMILIES = ("03", "04", "05", "06", "08", "09")


async def manager_score(ctx: Ctx) -> dict[str, list[str]]:
    """The Manager owns the ENTIRE dynamic pipeline: from the whole ensemble it
    chooses which players to put to work and which to bench (with reasons),
    picks the engagement lead, sets each player's depth, writes the hand-off
    questions (the communication lines), and decides how many deliberation
    rounds the brief warrants. The client never picks a board or a depth —
    that is the Manager's job. Returns {family_id: [player_ids]}."""
    aid, layer = "manager", "L0"
    await ctx.emit.stage(aid, "queued", layer)
    await ctx.start(aid, layer)
    analytical_all = [p.id for f in _ANALYTICAL_FAMILIES for p in players_in(f)]

    focus, regulated, lead, beyond_hint = "", False, "", ""
    convened: list[str] = []
    bench_reasons: dict[str, str] = {}
    depths: dict[str, str] = {}
    key_questions: list[dict[str, str]] = []
    n_rounds, debate = 2, False
    candidates = "\n".join(f"- {p}: {PLAYER_BY_ID[p].role}" for p in analytical_all)
    system = ("You are the Manager 🎼 conducting an advisory orchestra — the Whiplash standard: "
              "you do not analyse, you PLAN, and you demand excellence. The Boss handed you the "
              "client's brief; now compose the engagement like a new piece of music: CHOOSE from "
              "the full ensemble exactly which players this brief needs (convene) and which it "
              "does not (bench, with the reason), pick the ONE engagement lead, set each convened "
              "player's depth, write the hand-off questions that wire the players together, and "
              "decide whether this brief needs one pass or the full two-round deliberation. "
              "Framing, adversarial QA and delivery always run — everything else is your call.")
    user = (f"BRIEF: {str(ctx.state.brief)[:600]}\nPROFILE: {str(ctx.state.profile)[:240]}\n\n"
            f"THE FULL ENSEMBLE (choose from these):\n{candidates}\n\n"
            "TASK: compose the engagement.")
    await ctx.emit.prompt(aid, system, user)
    data, res = await ctx.llm.structured("t3", system, user, _SCORE_SCHEMA,
                                         max_tokens=900, agent=aid)
    if data:
        focus = str(data.get("focus") or "")[:200]
        regulated = bool(data.get("regulated"))
        beyond_hint = str(data.get("beyond_hint") or "")[:160]
        convened = [str(p) for p in (data.get("convene") or []) if str(p) in analytical_all]
        for b in (data.get("bench") or [])[:12]:
            if isinstance(b, dict) and str(b.get("id") or "") in analytical_all:
                bench_reasons[str(b["id"])] = str(b.get("reason") or "")[:120]
        if str(data.get("team_lead") or "") in analytical_all:
            lead = str(data["team_lead"])
        for p in (data.get("deep") or [])[:6]:
            if str(p) in analytical_all:
                depths[str(p)] = "deep"
        for p in (data.get("light") or [])[:8]:
            if str(p) in analytical_all and str(p) not in depths:
                depths[str(p)] = "light"
        for k in (data.get("key_questions") or [])[:7]:
            if isinstance(k, dict) and k.get("q") and str(k.get("assign") or "") in analytical_all:
                key_questions.append({"assign": str(k["assign"]), "q": str(k["q"])[:160]})
        try:
            n_rounds = 2 if int(data.get("rounds") or 2) >= 2 else 1
        except Exception:
            n_rounds = 2
        debate = bool(data.get("debate"))
        await ctx.emit.usage(aid, res.tokens, res.route)

    # a cast too thin to cover the thesis falls back to the proven general board
    if len(convened) < 8:
        convened = [p.id for f in _FALLBACK_FAMILIES for p in players_in(f)]
        if not data:
            focus = "No model reachable — the general board convenes (deterministic cast)."
    if lead and lead not in convened:
        convened.append(lead)
    if not lead:
        lead = "market_analyst" if "market_analyst" in convened else convened[0]
    depths[lead] = "deep"
    # API callers may still pass agents_enabled — intersect, lead protected
    enabled = set(ctx.state.raw.get("agents_enabled") or [])
    if enabled:
        convened = [p for p in convened if p in enabled or p == lead]

    benched = [p for p in analytical_all if p not in convened]
    cast: dict[str, list[str]] = {}
    for f in ("02", *_ANALYTICAL_FAMILIES, "10", "11"):
        ids = ([p.id for p in players_in(f)] if f in _SPINE_FAMILIES
               else [p.id for p in players_in(f) if p.id in convened])
        if ids:
            cast[f] = ids
    active = list(cast.keys())

    n_players = sum(len(v) for v in cast.values())
    n_inst = sum(len(PLAYER_BY_ID[p].instruments) for ps in cast.values() for p in ps if p in PLAYER_BY_ID)
    movements = [{
        "id": f, "name": FAMILY_BY_ID[f].name, "color": FAMILY_BY_ID[f].color,
        "layer": _LAYER_OF.get(f, "L2"),
        "players": [{"id": p, "name": PLAYER_BY_ID[p].name, "emoji": PLAYER_BY_ID[p].emoji,
                     "instruments": [i.name for i in PLAYER_BY_ID[p].instruments]}
                    for p in cast[f] if p in PLAYER_BY_ID],
    } for f in active]
    graph = {"focus": focus, "regulated": regulated,
             "team_lead": lead, "depths": depths, "key_questions": key_questions,
             "rounds": n_rounds, "debate": debate, "beyond_hint": beyond_hint,
             "benched": [{"id": p, "reason": bench_reasons.get(p, "not needed for this brief")}
                         for p in benched],
             "n_players": n_players, "n_instruments": n_inst, "movements": movements,
             "edges": [[active[i], active[i + 1]] for i in range(len(active) - 1)],
             "route": res.route if data else "deterministic"}
    ctx.state.rounds["task_graph"] = graph
    await ctx.emit.partial("task_graph", graph)
    n_deep = sum(1 for d in depths.values() if d == "deep")
    n_light = sum(1 for d in depths.values() if d == "light")
    await ctx.emit.log(aid, f"composed the engagement: {n_players} players convened · "
                            f"{len(benched)} benched · lead: {lead} · {n_deep} deep / {n_light} "
                            f"light · {len(key_questions)} hand-off line(s) · "
                            f"{n_rounds} round(s){' · open debates' if debate else ''}"
                            + (f" · {focus}" if focus else ""), "info")
    for p in benched:
        await ctx.emit.stage(p, "skipped", "")
        if p in bench_reasons:
            await ctx.emit.log(aid, f"benched {p} — {bench_reasons[p]}", "muted")
    for k in key_questions:
        await ctx.emit.log(aid, f"hand-off → {k['assign']}: {k['q']}", "muted")
    await ctx.emit.collab(aid, [lead])
    await ctx.finish(aid, layer, {
        "verdict_line": f"Engagement composed — lead {lead} · {n_players} convened · "
                        f"{len(benched)} benched · {len(key_questions)} hand-offs · "
                        f"{n_rounds} round(s)",
        "focus": focus, "regulated": regulated, "team_lead": lead,
        "degraded": not bool(data)}, res.route if data else "", res.tokens if data else 0)
    return cast


# ── ♻️ Orchestra replay — rescue degraded players WITHOUT losing their tiers ──

async def replay_players(ctx: Ctx, cooldown: float = 22.0) -> int:
    """The gap-detector for the two-tier orchestra: degraded players are
    re-PLAYED (through the same instruments executor) after a quota-refresh
    cooldown — never through the flat agents, which would stomp their
    instruments. Returns how many were rescued."""
    degraded = [pid for pid, out in ctx.state.outputs.items()
                if isinstance(out, dict) and out.get("degraded")
                and out.get("player") and out.get("instruments") and pid in PLAYER_BY_ID]
    if not degraded:
        return 0
    status = await ctx.llm.status()
    if not status.get("cloud") and not status.get("local"):
        await ctx.emit.log("manager",
                           f"gap-detector: {len(degraded)} player(s) reduced-depth, but no LLM "
                           "configured — add API keys to narrate their instruments", "warn")
        return 0
    await ctx.emit.log("manager",
                       f"gap-detector: re-playing {len(degraded)} reduced-depth player(s) after a "
                       f"{int(cooldown)}s cooldown (quota refresh) — instruments preserved", "warn")
    await asyncio.sleep(cooldown)
    rescued = 0
    for pid in degraded:
        try:
            out = await play(ctx, PLAYER_BY_ID[pid])
            if not out.get("degraded"):
                rescued += 1
        except Exception:
            pass
    await ctx.emit.log("manager", f"gap-detector: rescued {rescued}/{len(degraded)} player(s)",
                       "ok" if rescued else "muted")
    return rescued


# ── 🧾 Coverage & Completeness Auditor (a Manager junior · t0) ────────────────

async def coverage_audit(ctx: Ctx) -> dict[str, Any]:
    """The Manager junior that 'guarantees no relevant dimension was skipped':
    a deterministic sweep — dimensions produced, players degraded, instruments
    actually played — surfaced honestly, never hidden."""
    o = ctx.state.outputs
    scope = set(ctx.state.scope)
    produced, missing, out_of_scope = [], [], []
    for dim, producers in ORCHESTRA_DIMENSIONS.items():
        convened = [p for p in producers if p in scope]
        if not convened:
            out_of_scope.append(dim)     # the Manager's cast — a choice, not a gap
        elif any(p in o and isinstance(o[p].get("score"), (int, float)) for p in convened):
            produced.append(dim)
        else:
            missing.append(dim)
    players = [pid for pid, out in o.items()
               if isinstance(out, dict) and pid in PLAYER_BY_ID
               and (out.get("player") or out.get("instruments"))]
    degraded = [pid for pid in players if o[pid].get("degraded")]
    inst_total = inst_played = 0
    for pid in players:
        for i in (o[pid].get("instruments") or []):
            inst_total += 1
            if i.get("finding") and not str(i["finding"]).startswith("(no model"):
                inst_played += 1
    report = {"dims_produced": produced, "dims_missing": missing,
              "dims_out_of_scope": out_of_scope,
              "players": len(players), "degraded": len(degraded),
              "instruments_played": inst_played, "instruments_total": inst_total}
    ctx.state.rounds["coverage"] = report
    await ctx.emit.partial("coverage", report)
    kind = "ok" if not missing and not degraded else "warn"
    await ctx.emit.log("manager",
                       f"coverage audit: {len(produced)}/{len(produced) + len(missing)} in-scope "
                       f"dimensions produced · {inst_played}/{inst_total} instruments played · "
                       f"{len(degraded)} player(s) degraded"
                       + (f" · MISSING: {', '.join(missing)}" if missing else " — no in-scope dimension skipped")
                       + (f" · out of scope by the Manager's cast: {', '.join(out_of_scope)}"
                          if out_of_scope else ""), kind)
    return report


# ── ⚡ Conflict rulings — Weighing + Devil's stress it, the Manager decides ────

async def manager_rulings(ctx: Ctx) -> None:
    """The conversation's conflict protocol: when experts disagree, score it
    (Weighing) and stress it (Red Team / Devil's Advocate), then the MANAGER
    rules and records the rationale in the ledger."""
    conflicts: list[str] = []
    for atk in (ctx.state.outputs.get("red_team") or {}).get("attacks") or []:
        if isinstance(atk, dict) and atk.get("attack"):
            conflicts.append(f"[red_team vs {atk.get('target_agent', '?')}] {str(atk['attack'])[:140]}")
    for c in (ctx.state.outputs.get("cross_pollinate") or {}).get("connections") or []:
        if isinstance(c, dict) and str(c.get("type")) == "tension":
            conflicts.append(f"[{c.get('a', '?')} × {c.get('b', '?')}] {str(c.get('insight') or '')[:140]}")
    if not conflicts:
        ctx.state.rounds["rulings"] = []
        return
    aid = "manager"
    await ctx.emit.log(aid, f"resolving {min(len(conflicts), 3)} open conflict(s) — weighed, "
                            "stressed by the crucible, now the Manager rules", "info")
    schema = ('{"rulings": [{"topic": str (<=12 words), "ruling": str (<=25 words — the decision), '
              '"rationale": str (<=25 words — why, citing the evidence side that won)} x1-3]}')
    data, res = await ctx.llm.structured(
        "t3",
        "You are the Manager 🎼. Experts on your board disagree. The Weighing Engine has scored "
        "the board and the crucible has stressed both sides — now YOU rule on each conflict and "
        "record the rationale. Decisive, evidence-first, no fence-sitting.",
        f"BOARD VERDICT: {str(ctx.state.verdict.get('score'))}/10 "
        f"({ctx.state.verdict.get('recommendation')})\nDIMENSIONS: {ctx.state.dimensions}\n"
        "OPEN CONFLICTS:\n" + "\n".join(f"- {c}" for c in conflicts[:3]),
        schema, max_tokens=450, agent=aid)
    rulings = []
    if data and isinstance(data.get("rulings"), list):
        rulings = [{k: str(r.get(k) or "")[:200] for k in ("topic", "ruling", "rationale")}
                   for r in data["rulings"] if isinstance(r, dict) and r.get("ruling")][:3]
        await ctx.emit.usage(aid, res.tokens, res.route)
    if not rulings:
        # deterministic ruling: the weighed number IS the decision record
        rulings = [{"topic": c.split("]")[0].strip("["),
                    "ruling": f"Stands as weighed — board score {ctx.state.verdict.get('score')}/10 "
                              f"({ctx.state.verdict.get('recommendation')}).",
                    "rationale": "No model reachable — the deterministic weighing is the tie-breaker."}
                   for c in conflicts[:2]]
    ctx.state.rounds["rulings"] = rulings
    await ctx.emit.partial("rulings", rulings)
    for r in rulings:
        await ctx.emit.log(aid, f"⚖ RULING · {r['topic']}: {r['ruling']}", "info")


# ── 🌟 Above & Beyond — "you didn't ask, but you should know" ─────────────────

async def above_and_beyond(ctx: Ctx) -> None:
    """The conversation's mechanism, verbatim: Trends & Weak Signals +
    Connecting Dots + the Coverage Auditor produce the 'you didn't ask, but
    you should know' section of EVERY deliverable. Fail-soft: assembles
    deterministically when no model is reachable."""
    aid = "manager"
    o = ctx.state.outputs
    trends = o.get("trends") or {}
    dots = o.get("connecting_dots") or {}
    cross = o.get("cross_pollinate") or {}
    coverage = ctx.state.rounds.get("coverage") or {}
    hint = str((ctx.state.rounds.get("task_graph") or {}).get("beyond_hint") or "")
    raw_signals = ([str(x) for x in (trends.get("key_insights") or [])]
                   + [str(x) for x in (dots.get("key_insights") or dots.get("insights") or [])]
                   + [str(x) for x in (cross.get("emergent") or [])])[:8]

    schema = ('{"items": [{"insight": str (<=28 words — something the client did NOT ask about '
              'but materially needs to know), "why": str (<=18 words — why it matters to THIS '
              'decision), "source": str (the player id it came from)} x3-5]}')
    data, res = await ctx.llm.structured(
        "t3",
        "You are the Manager 🎼 assembling the ABOVE-AND-BEYOND section — the things the client "
        "did not ask about but must hear (the whole point of a great advisory board). Draw from "
        "the weak signals, cross-domain patterns and emergent insights. Never restate what the "
        "client already asked; each item must be genuinely additive.",
        f"BRIEF: {str(ctx.state.brief)[:400]}\n"
        + (f"MANAGER'S HINT: {hint}\n" if hint else "")
        + "SIGNALS FROM THE BOARD:\n" + "\n".join(f"- {s[:140]}" for s in raw_signals)
        + f"\nUNCOVERED DIMENSIONS: {', '.join(coverage.get('dims_missing') or []) or 'none'}",
        schema, max_tokens=500, agent=aid)
    items = []
    if data and isinstance(data.get("items"), list):
        items = [{"insight": str(i.get("insight") or "")[:220],
                  "why": str(i.get("why") or "")[:160],
                  "source": str(i.get("source") or "")[:40]}
                 for i in data["items"] if isinstance(i, dict) and i.get("insight")][:5]
        await ctx.emit.usage(aid, res.tokens, res.route)
    if not items:
        # deterministic assembly — the section ALWAYS ships (fail-soft), drawing
        # from every honest signal the board produced without a model
        srcs = ["trends", "connecting_dots", "cross_pollinate"]
        items = [{"insight": s[:220], "why": "surfaced by the board beyond the brief's framing",
                  "source": srcs[min(idx, 2)]}
                 for idx, s in enumerate(raw_signals[:3])]
        kill = str((o.get("red_team") or {}).get("kill_risk") or "")
        if kill:
            items.append({"insight": f"The single most likely kill risk: {kill[:170]}",
                          "why": "you asked about the upside; this is the downside that decides it",
                          "source": "red_team"})
        breaks = str((o.get("scenario_planner") or {}).get("breaks_it") or "")
        if breaks:
            items.append({"insight": f"What breaks the plan under uncertainty: {breaks[:170]}",
                          "why": "the Monte-Carlo tail matters more than the median",
                          "source": "scenario_planner"})
        no_case = str((o.get("devils_advocate") or {}).get("no_case") or "")
        if no_case and len(items) < 4:
            items.append({"insight": f"The steel-manned case against: {no_case[:170]}",
                          "why": "the strongest opposing view, argued on purpose",
                          "source": "devils_advocate"})
        for dim in (coverage.get("dims_missing") or [])[:1]:
            items.append({"insight": f"The {dim} dimension was not covered at this depth — "
                                     "a deeper run would convene those specialists.",
                          "why": "an unexamined dimension is an unpriced risk", "source": "manager"})
        items = items[:5]
    ctx.state.rounds["beyond"] = items
    await ctx.emit.partial("beyond", items)
    await ctx.emit.log(aid, f"🌟 above & beyond — {len(items)} thing(s) you didn't ask about "
                            "but should know", "ok")


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
