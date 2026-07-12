"""Intelligent Mode = THE ORCHESTRA (the composition engine).

One general advisory ensemble (any business/life brief — not the founder/
trader/wealth boards). Every PLAYER runs its 4–5 junior INSTRUMENTS as real
sub-tasks (conductor.play), the 🎼 Manager decomposes the brief into a task
graph across them, a blocking QA gate + human review guard regulated content,
and a general MCDA weighing turns the scores into the verdict. Grounding,
crucible and delivery reuse EIP's proven agents, with their instruments shown
as an overlay so the two-tier glass box lights up for every player.
"""
from __future__ import annotations

import asyncio
import traceback

from ..agents import board, conductor, meta, orchestra as orch, scenario, studio, venture as v
from ..agents.deliberate import emit_result_set
from ..agents.replay import replay_degraded
from ..agents.base import Ctx, RunState
from ..agents.score import DEPTH_FAMILIES
from ..core.events import Emitter
from ..core.llm_gateway import EngineConfig, Gateway
from ..memory.store import save_run


async def _boss_intro(ctx: Ctx) -> None:
    """🎩 Boss — general intake: distil the conversation into the brief text so
    the whole orchestra builds on the real problem (no mode routing here)."""
    aid = "boss"
    await ctx.emit.stage(aid, "active", "L0")
    convo = ctx.state.raw.get("conversation") or []
    if convo:
        from ..agents.orchestra import _transcript
        transcript = _transcript(convo)
        system = ("You are the Boss 🎩 — you ran the intake conversation. Write the handoff brief "
                  "for the orchestra: the REAL problem behind the ask, constraints, success "
                  "criteria and sensitivity. Never invent facts.")
        user = f"CONVERSATION:\n{transcript}\n\nWritten situation: {str(ctx.state.raw.get('situation') or '')[:400]}"
        schema = ('{"situation": str (<=90 words), "industry": str, "geography": str, '
                  '"success_criteria": str, "sensitivity": "public"|"confidential"}')
        data, res = await ctx.llm.structured("t3", system, user, schema, max_tokens=500, agent=aid)
        if data and str(data.get("situation") or "").strip():
            ctx.state.raw["situation"] = str(data["situation"])[:900]
            for k in ("industry", "geography", "success_criteria", "sensitivity"):
                if str(data.get(k) or "").strip() and not str(ctx.state.raw.get(k) or "").strip():
                    ctx.state.raw[k] = str(data[k])[:300]
            await ctx.emit.claim(aid, f"The real ask: {str(data['situation'])[:140]}", confidence=0.7)
        else:
            ctx.state.raw["situation"] = (str(ctx.state.raw.get("situation") or "")
                                          + "\n\nINTAKE:\n" + transcript)[:2400]
        await conductor.overlay_instruments(ctx, "intake_parser", [])  # noop-safe
    await ctx.emit.log(aid, "intake captured — handing the score to the Manager", "ok")
    await ctx.emit.stage(aid, "done", "L0")


async def run_orchestra(run_id: str, payload: dict, emitter: Emitter) -> None:
    try:
        eng = payload.get("engine") or {}
        cfg = EngineConfig(**{k: val for k, val in eng.items() if k in EngineConfig.__dataclass_fields__})
        payload = {**payload, "orchestra": True, "advisory": True}
        ctx = Ctx(emit=emitter, llm=Gateway(cfg), state=RunState(run_id=run_id, raw=payload))
        status = await ctx.llm.status()
        route_note = ("demo (deterministic cores only)" if cfg.compute == "demo"
                      else f"local={'✓' if status['local'] else '✗'} · cloud={status['cloud'] or '—'}")
        await emitter.partial("run_id", run_id)
        await emitter.log("manager", f"engine: {route_note}", "muted")
        from datetime import datetime, timezone
        await emitter.log("manager",
                          f"🎼 THE ORCHESTRA · FRESH RUN {run_id} · grounding fetched LIVE at "
                          f"{datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC — every player runs "
                          "its junior instruments; nothing reused except claims labelled MEMORY", "info")
        depth = str(payload.get("depth") or "board").lower()

        # ── 🎩 Boss + L0 framing (real parser/profiler set brief & profile) ──
        await _boss_intro(ctx)
        await v.intake_parser(ctx)
        await conductor.overlay_instruments(ctx, "intake_parser", [
            f"stage: {ctx.state.brief.get('stage')}", f"industry: {ctx.state.brief.get('industry') or '—'}",
            f"geography: {ctx.state.brief.get('geography')}",
            f"uncertainty: {ctx.state.brief.get('uncertainty') or '—'}",
            "brief normalised onto the schema"])
        await v.context_profiler(ctx)
        await conductor.overlay_instruments(ctx, "context_profiler", [
            f"persona: {ctx.state.profile.get('persona')}",
            f"capital band: {ctx.state.profile.get('capital_band')}",
            f"risk capacity: {ctx.state.profile.get('risk_capacity')}",
            f"geography: {ctx.state.profile.get('geography')}", "precedent recalled from memory"])

        # ── 🎼 Manager — score the brief into the task graph (the DAG) ──
        cast = await conductor.manager_score(ctx, depth)
        note = str((ctx.state.rounds.get("task_graph") or {}).get("focus") or "")
        ctx.state.scope = [p for ps in cast.values() for p in ps]
        for p in ctx.state.scope:
            await emitter.stage(p, "queued", "")

        # ── L1 grounding (real evidence) + instrument overlays ──
        await asyncio.gather(v.web_researcher(ctx), v.news_intel(ctx),
                             v.market_data(ctx), v.macro_data(ctx))
        await v.doc_analyst(ctx)
        await v.memory_recall(ctx)
        await meta.rag_memory(ctx)
        ev = ctx.state.evidence
        for pid in ("web_researcher", "news_intel", "market_data", "macro_data"):
            if pid in ctx.state.outputs:
                hits = [e["text"] for e in ev if e.get("agent") == pid][:5]
                await conductor.overlay_instruments(ctx, pid, hits or ["live source queried"])

        # ── L2 movements — the two-tier stars: play every convened player ──
        # family 03's grounding four already ran; play the rest of research + all
        # of analysis/strategy/legal/tech/commercial/human, movement by movement
        GROUNDED = {"web_researcher", "news_intel", "market_data", "macro_data"}
        for fam in DEPTH_FAMILIES.get(depth, DEPTH_FAMILIES["board"]):
            fam_cast = [p for p in cast.get(fam, []) if p not in GROUNDED]
            await conductor.play_family(ctx, fam, fam_cast, note)

        # ── L3 crucible (real EIP agents) + instrument overlays ──
        await asyncio.gather(v.red_team(ctx), v.fact_checker(ctx),
                             v.bias_auditor(ctx), board.devils_advocate(ctx))
        rt = ctx.state.outputs.get("red_team") or {}
        await conductor.overlay_instruments(ctx, "red_team",
            [a.get("attack", "") for a in (rt.get("attacks") or [])] + [f"kill risk: {rt.get('kill_risk', '')}"])
        fc = ctx.state.outputs.get("fact_checker") or {}
        await conductor.overlay_instruments(ctx, "fact_checker",
            [f"{c.get('verdict')}: {c.get('claim', '')[:60]}" for c in (fc.get("checks") or [])])
        ba = ctx.state.outputs.get("bias_auditor") or {}
        await conductor.overlay_instruments(ctx, "bias_auditor",
            [f"{b.get('bias')}: {b.get('note', '')}" for b in (ba.get("findings") or [])])
        da = ctx.state.outputs.get("devils_advocate") or {}
        await conductor.overlay_instruments(ctx, "devils_advocate", [str(da.get("no_case") or "")])
        await replay_degraded(ctx)

        # ── L4 synthesis + delivery (reuse EIP's rich synthesis) ──
        await board.cross_pollinate(ctx)
        await board.compliance_scan(ctx)
        if "connecting_dots" in ctx.state.scope:
            await board.connecting_dots(ctx)
        await conductor.weighing_orchestra(ctx)          # ⚖️ general MCDA verdict
        await scenario.scenario_planner(ctx)
        await asyncio.gather(board.negotiation_coach(ctx),
                             board.storytelling(ctx), studio.visualizer(ctx))
        await orch.qa_gate(ctx, 1)                       # ✅ blocking, before the report
        await studio.reporter(ctx)

        # delivery instrument overlays
        cp = ctx.state.outputs.get("connecting_dots") or {}
        await conductor.overlay_instruments(ctx, "connecting_dots",
            [str(x) for x in (cp.get("patterns") or cp.get("insights") or [])])
        st = ctx.state.outputs.get("storytelling") or {}
        await conductor.overlay_instruments(ctx, "storytelling",
            [st.get("hook", ""), st.get("narrative", ""), st.get("one_liner", "")]
            + [str(b) for b in (st.get("three_beats") or [])])
        vz = ctx.state.outputs.get("visualizer") or {}
        await conductor.overlay_instruments(ctx, "visualizer",
            [f"chart: {c.get('title', c.get('kind', ''))}" for c in (vz.get("charts") or [])])
        vd = ctx.state.verdict
        await conductor.overlay_instruments(ctx, "verdict_composer", [
            f"recommendation: {vd.get('recommendation')}", f"score: {vd.get('score')}/10",
            vd.get("reasoning", ""), *(vd.get("next_steps") or [])])
        rp = ctx.state.outputs.get("reporter") or {}
        await conductor.overlay_instruments(ctx, "reporter",
            [f"report assembled ({len(str(rp.get('report_md') or ''))} chars)"])

        # ── 🧑‍⚖️ human review of regulated content, then publish ──
        await orch.hitl_checkpoint(ctx)
        await emit_result_set(ctx, 1)

        await save_run(ctx.state)
        await meta.outcome_tracker(ctx)
        await emitter.done(run_id)
    except Exception:
        await emitter.log("verdict_composer", traceback.format_exc(limit=3), "err")
        await emitter.error("orchestra failed — see log")
