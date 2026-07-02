"""Phase-1 venture agents. Every agent follows the same contract:

    deterministic core  →  always produces a result (zero keys, zero network)
    + LLM narrative     →  upgrades depth when any route on the ladder works
    + events            →  stage / log / claim / usage over SSE

No agent may invent a number: figures either carry a source from the evidence
board or are labelled estimates (EIP Constitution #1).
"""
from __future__ import annotations

import re
from typing import Any

from ..grounding import web
from .base import Ctx

# ── L0: intake parser ─────────────────────────────────────────────────────────

_STAGES = ["ideation", "validation", "mvp", "traction", "scaling", "expansion"]

def _heuristic_brief(raw: dict[str, Any]) -> dict[str, Any]:
    text = (raw.get("situation") or "").strip()
    lower = text.lower()
    stage = next((s for s in _STAGES if s in lower), raw.get("stage") or "ideation")
    return {
        "summary": text[:400] or "Unspecified venture idea",
        "industry": raw.get("industry") or "",
        "geography": raw.get("geography") or "India",
        "stage": stage,
        "budget_band": raw.get("budget_band") or "under_10L",
        "team_size": raw.get("team_size") or "solo",
        "uncertainty": raw.get("uncertainty") or "",
        "keywords": re.findall(r"[a-zA-Z]{4,}", lower)[:8],
    }


async def intake_parser(ctx: Ctx) -> None:
    aid, layer = "intake_parser", "L0"
    await ctx.start(aid, layer)
    raw = ctx.state.raw
    await ctx.emit.log(aid, f"> situation: {(raw.get('situation') or '')[:120]}…", "muted")

    brief = _heuristic_brief(raw)
    schema = ('{"summary": str, "industry": str, "geography": str, "stage": str, '
              '"budget_band": str, "team_size": str, "uncertainty": str, "keywords": [str]}')
    data, res = await ctx.llm.structured(
        "t1",
        "You extract a structured business brief from an entrepreneur's raw description. "
        "Never invent facts not present; empty string when unknown.",
        f"Description: {raw.get('situation','')}\nUser-set fields: industry={raw.get('industry','')} "
        f"geography={raw.get('geography','India')} stage={raw.get('stage','')} "
        f"budget={raw.get('budget_band','')} team={raw.get('team_size','')} "
        f"biggest_uncertainty={raw.get('uncertainty','')}",
        schema,
    )
    if data:
        for k, v in data.items():
            if v and k in brief:
                brief[k] = v
        await ctx.emit.log(aid, f"parsed via {res.route}", "ok")
    else:
        await ctx.emit.log(aid, "LLM unavailable — heuristic parse (demo-grade)", "warn")

    ctx.state.brief = brief
    await ctx.emit.log(aid, f"industry: {brief['industry'] or '?'} · geo: {brief['geography']} · stage: {brief['stage']}", "info")
    await ctx.emit.partial("brief", brief)
    await ctx.finish(aid, layer, brief, res.route, res.tokens)


# ── L0: context profiler ──────────────────────────────────────────────────────

async def context_profiler(ctx: Ctx) -> None:
    aid, layer = "context_profiler", "L0"
    await ctx.start(aid, layer)
    b = ctx.state.brief
    budget = b.get("budget_band", "under_10L")
    profile = {
        "persona": "solo founder" if b.get("team_size") == "solo" else "founding team",
        "capital_band": budget,
        "risk_capacity": "low" if budget in ("under_10L", "10L_1Cr") and b.get("stage") in ("ideation", "validation") else "moderate",
        "experience_hint": b.get("stage"),
        "geography": b.get("geography", "India"),
    }
    ctx.state.profile = profile
    await ctx.emit.log(aid, f"talking to: {profile['persona']} · capital {profile['capital_band']} · risk capacity {profile['risk_capacity']}", "info")
    await ctx.emit.log(aid, "output will be calibrated to this profile (Constitution #4)", "muted")
    await ctx.finish(aid, layer, profile)


# ── L0: scope planner ─────────────────────────────────────────────────────────

async def scope_planner(ctx: Ctx) -> None:
    aid, layer = "scope_planner", "L0"
    await ctx.start(aid, layer)
    # Phase 1: fixed venture spine. Depth/mode-aware scoping arrives with the full roster.
    scope = ["web_researcher", "news_intel", "market_analyst", "finance_modeler",
             "red_team", "weighing_engine", "verdict_composer"]
    ctx.state.scope = scope
    await ctx.emit.log(aid, f"convening {len(scope)} specialists for a Pulse run", "info")
    for s in scope:
        await ctx.emit.stage(s, "queued", "")
    await ctx.emit.partial("scope", scope)
    await ctx.finish(aid, layer, {"scope": scope})


# ── L1: web researcher ────────────────────────────────────────────────────────

async def web_researcher(ctx: Ctx) -> None:
    aid, layer = "web_researcher", "L1"
    await ctx.start(aid, layer)
    b = ctx.state.brief
    topic = b.get("industry") or " ".join(b.get("keywords", [])[:3]) or b["summary"][:60]
    geo = b.get("geography", "India")
    queries = [
        f"{topic} market size {geo}",
        f"{topic} competitors startups {geo}",
        f"{topic} industry challenges regulation {geo}",
    ]
    total = 0
    for q in queries:
        await ctx.emit.log(aid, f"⌕ {q}", "code")
        results = await web.search(q, n=4)
        for r in results:
            if not r["url"]:
                continue
            total += 1
            await ctx.emit.claim(
                aid, f"{r['title']}: {r['snippet'][:160]}",
                source={"url": r["url"], "name": r["title"][:60]}, confidence=0.55,
            )
            ctx.state.evidence.append({"text": f"{r['title']} — {r['snippet']}",
                                       "source": {"url": r["url"]}, "agent": aid})
    kind = "ok" if total else "warn"
    await ctx.emit.log(aid, f"{total} sourced findings on the evidence board" if total
                       else "web unreachable — continuing without live web evidence", kind)
    await ctx.finish(aid, layer, {"findings": total})


# ── L1: news intelligence ─────────────────────────────────────────────────────

async def news_intel(ctx: Ctx) -> None:
    aid, layer = "news_intel", "L1"
    await ctx.start(aid, layer)
    b = ctx.state.brief
    topic = b.get("industry") or " ".join(b.get("keywords", [])[:3]) or "startups"
    await ctx.emit.log(aid, f"⌕ google-news: {topic} ({b.get('geography','India')})", "code")
    items = await web.news(topic, n=6, region=b.get("geography", "India"))
    for it in items:
        await ctx.emit.claim(aid, it["title"],
                             source={"url": it["url"], "name": it["source"], "date": it["published"][:16]},
                             confidence=0.6)
        ctx.state.evidence.append({"text": f"NEWS: {it['title']} ({it['published'][:16]})",
                                   "source": {"url": it["url"]}, "agent": aid})
    kind = "ok" if items else "warn"
    await ctx.emit.log(aid, f"{len(items)} current headlines captured" if items
                       else "news feed unreachable — continuing", kind)
    await ctx.finish(aid, layer, {"headlines": len(items)})


# ── L2 helper: scored analysis via LLM with deterministic fallback ────────────

_ANALYSIS_SCHEMA = ('{"verdict_line": str, "score": float (0-10), "confidence": float (0-1), '
                    '"analysis": str (<=180 words), "assumptions": [str], "numbers_used": '
                    '[{"figure": str, "source": "url or ESTIMATE"}]}')


async def _scored_analysis(ctx: Ctx, aid: str, system: str, ask: str,
                           fallback: dict[str, Any]) -> dict[str, Any]:
    data, res = await ctx.llm.structured(
        "t2", system + " Cite evidence-board items when possible; any uninvented figure "
        "must be tagged ESTIMATE. Be specific, never generic.",
        f"BRIEF: {ctx.state.brief}\nPROFILE: {ctx.state.profile}\n"
        f"EVIDENCE BOARD:\n{ctx.state.evidence_digest()}\n\nTASK: {ask}",
        _ANALYSIS_SCHEMA, max_tokens=900,
    )
    if data and isinstance(data.get("score"), (int, float)):
        data["score"] = max(0.0, min(10.0, float(data["score"])))
        data["confidence"] = max(0.05, min(0.95, float(data.get("confidence", 0.5))))
        data["route"] = res.route
        await ctx.emit.log(aid, f"analysis via {res.route}", "ok")
        await ctx.emit.usage(aid, res.tokens, res.route)
        return data
    await ctx.emit.log(aid, "LLM unavailable — deterministic core only (reduced depth)", "warn")
    return fallback


# ── L2: market analyst ────────────────────────────────────────────────────────

async def market_analyst(ctx: Ctx) -> None:
    aid, layer = "market_analyst", "L2"
    await ctx.start(aid, layer)
    ev = [e for e in ctx.state.evidence]
    competitor_hits = sum(1 for e in ev if re.search(r"competitor|rival|startup|player", e["text"], re.I))
    await ctx.emit.log(aid, f"evidence board: {len(ev)} items · {competitor_hits} competition signals", "info")

    det_score = 6.0 - min(2.0, competitor_hits * 0.3) + (0.5 if len(ev) > 6 else 0.0)
    fallback = {
        "verdict_line": f"Signal-count heuristic: {competitor_hits} competition mentions in {len(ev)} findings",
        "score": round(det_score, 1), "confidence": 0.3,
        "analysis": "Deterministic screen only — competition density inferred from live search hits. "
                    "Add an API key or local model for full market analysis.",
        "assumptions": ["Search-hit density approximates competitive intensity"],
        "numbers_used": [],
    }
    out = await _scored_analysis(
        ctx, aid,
        "You are a rigorous market analyst for early-stage ventures.",
        "Assess market attractiveness: demand signals, growth, competitive intensity, timing. "
        "Score 0-10 for MARKET dimension.", fallback)
    await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
    for n in out.get("numbers_used", [])[:5]:
        flag = "sourced" if str(n.get("source", "")).startswith("http") else "ESTIMATE"
        await ctx.emit.log(aid, f"№ {n.get('figure','')} [{flag}]", "code")
    await ctx.finish(aid, layer, out)


# ── L2: finance modeler (deterministic math core) ────────────────────────────

_BUDGET_LAKHS = {"under_10L": 7.0, "10L_1Cr": 50.0, "1Cr_10Cr": 500.0, "above_10Cr": 2000.0}

async def finance_modeler(ctx: Ctx) -> None:
    aid, layer = "finance_modeler", "L2"
    await ctx.start(aid, layer)
    b, p = ctx.state.brief, ctx.state.profile
    capital_l = _BUDGET_LAKHS.get(b.get("budget_band", "under_10L"), 7.0)
    team = {"solo": 1, "2_5": 3, "5_20": 10, "20_plus": 25}.get(b.get("team_size", "solo"), 1)
    burn_l = round(team * 0.9 + 0.8, 1)                # ₹L/month: salaries+overhead heuristic
    runway = round(capital_l / burn_l, 1)
    await ctx.emit.log(aid, f"capital ≈ ₹{capital_l}L · est. burn ₹{burn_l}L/mo (team of {team}) [ESTIMATE]", "code")
    await ctx.emit.log(aid, f"runway ≈ {runway} months before revenue", "info")
    det_score = max(1.0, min(9.0, runway / 3.0))
    fallback = {
        "verdict_line": f"≈{runway} months runway at heuristic burn — {'thin' if runway < 9 else 'workable'}",
        "score": round(det_score, 1), "confidence": 0.45,
        "analysis": f"Deterministic model: ₹{capital_l}L capital / ₹{burn_l}L monthly burn (team {team}) "
                    f"= {runway} months runway. Benchmarks: <9mo thin, 12-18mo standard seed runway.",
        "assumptions": [f"Burn heuristic ₹{burn_l}L/mo", "No revenue before month 6"],
        "numbers_used": [{"figure": f"runway {runway} months", "source": "ESTIMATE"}],
    }
    out = await _scored_analysis(
        ctx, aid,
        "You are a startup finance modeler focused on unit economics and survival math.",
        f"Deterministic core computed: capital ₹{capital_l}L, burn ₹{burn_l}L/mo, runway {runway} months. "
        "Assess financial viability (score 0-10 for ECONOMICS): runway adequacy, capital-intensity of this "
        "industry, path to first revenue, unit-economics risks.", fallback)
    out.setdefault("deterministic", {})["runway_months"] = runway
    out["deterministic"].update({"capital_lakhs": capital_l, "burn_lakhs_pm": burn_l})
    await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
    await ctx.finish(aid, layer, out)


# ── L3: red team ──────────────────────────────────────────────────────────────

async def red_team(ctx: Ctx) -> None:
    aid, layer = "red_team", "L3"
    await ctx.start(aid, layer)
    await ctx.emit.log(aid, "mandate: attack the thesis; assume the founder is wrong", "muted")
    outputs = {k: v for k, v in ctx.state.outputs.items() if k in ("market_analyst", "finance_modeler")}
    schema = ('{"attacks": [{"target_agent": str, "attack": str, "severity": float (0-1), '
              '"evidence": str}], "kill_risk": str}')
    data, res = await ctx.llm.structured(
        "t3",
        "You are the red team. Find the strongest evidence-backed reasons this venture fails. "
        "Attack specific claims made by other analysts, not generalities.",
        f"BRIEF: {ctx.state.brief}\nANALYST OUTPUTS: {outputs}\n"
        f"EVIDENCE:\n{ctx.state.evidence_digest()}\n"
        "Produce the 3 strongest attacks and the single most likely kill risk.",
        schema, max_tokens=800,
    )
    if not data:
        data = {"attacks": [
            {"target_agent": "market_analyst", "severity": 0.5,
             "attack": "Competitive intensity is inferred from search density, not validated demand — "
                       "the market signal could be noise.", "evidence": "evidence board coverage is thin"},
            {"target_agent": "finance_modeler", "severity": 0.6,
             "attack": "Runway model assumes revenue by month 6; most ventures at this stage take 12+ months "
                       "to first meaningful revenue.", "evidence": "heuristic burn model"},
        ], "kill_risk": "Running out of cash before demand is proven."}
        await ctx.emit.log(aid, "LLM unavailable — standard failure-mode audit applied", "warn")
    else:
        await ctx.emit.usage(aid, res.tokens, res.route)

    for atk in data.get("attacks", [])[:4]:
        sev = float(atk.get("severity", 0.5))
        await ctx.emit.log(aid, f"⚔ [{atk.get('target_agent','?')}] {atk.get('attack','')}", "err" if sev > 0.6 else "warn")
        await ctx.emit.conflict(aid, atk.get("target_agent", "?"), atk.get("attack", "")[:80])
        ctx.state.conflicts.append(atk)
    await ctx.emit.claim(aid, f"Kill risk: {data.get('kill_risk','')}", confidence=0.6)
    await ctx.finish(aid, layer, data)


# ── L4: weighing engine — PURE deterministic (Constitution #3) ───────────────

async def weighing_engine(ctx: Ctx) -> None:
    aid, layer = "weighing_engine", "L4"
    await ctx.start(aid, layer)
    await ctx.emit.log(aid, "no LLM in this stage — weighted evidence math only", "muted")
    o = ctx.state.outputs
    market = o.get("market_analyst", {})
    fin = o.get("finance_modeler", {})
    attacks = ctx.state.conflicts

    def penalty(target: str) -> float:
        return sum(float(a.get("severity", 0.5)) for a in attacks if a.get("target_agent") == target) * 0.8

    evidence_quality = min(1.0, len(ctx.state.evidence) / 12.0)
    dims = {
        "Market": max(0.5, float(market.get("score", 5.0)) - penalty("market_analyst")),
        "Economics": max(0.5, float(fin.get("score", 5.0)) - penalty("finance_modeler")),
        "Evidence": round(evidence_quality * 10, 1),
        "Execution": 5.0,   # placeholder until GTM/HR agents land (Phase 3)
        "Timing": 5.0,      # placeholder until trends/macro agents land (Phase 3)
    }
    dims = {k: round(min(10.0, v), 1) for k, v in dims.items()}
    ctx.state.dimensions = dims
    overall = round(
        (dims["Market"] * 0.3 + dims["Economics"] * 0.3 + dims["Evidence"] * 0.15
         + dims["Execution"] * 0.125 + dims["Timing"] * 0.125), 1)

    conf_spread = abs(float(market.get("confidence", 0.5)) - float(fin.get("confidence", 0.5)))
    for k, v in dims.items():
        await ctx.emit.log(aid, f"{k:<10} {v}/10", "code")
    await ctx.emit.log(aid, f"weighted score {overall}/10 · dissent recorded: {len(attacks)} attacks", "info")
    await ctx.emit.partial("radar", {"dimensions": dims, "overall": overall})
    await ctx.finish(aid, layer, {"dimensions": dims, "overall": overall,
                                  "dissent": attacks, "confidence_spread": round(conf_spread, 2)})


# ── L4: verdict composer ──────────────────────────────────────────────────────

_VERDICT_SCHEMA = ('{"recommendation": "GO"|"CONDITIONAL_GO"|"NO_GO", "reasoning": str (3 sentences), '
                   '"sensitivities": [str x3], "risks": [{"text": str, "source_agent": str, "severity": float}], '
                   '"opportunities": [{"text": str, "source_agent": str}], "next_steps": [str x5], '
                   '"teach": str (2 sentences: how to think about this class of decision)}')

async def verdict_composer(ctx: Ctx) -> None:
    aid, layer = "verdict_composer", "L4"
    await ctx.start(aid, layer)
    w = ctx.state.outputs.get("weighing_engine", {})
    overall = float(w.get("overall", 5.0))
    band = "GO" if overall >= 7 else "CONDITIONAL_GO" if overall >= 4.5 else "NO_GO"
    await ctx.emit.log(aid, f"score {overall}/10 comes from the weighing engine — the LLM writes words, not the number", "muted")

    fallback = {
        "recommendation": band,
        "reasoning": f"Weighted score {overall}/10 across {len(ctx.state.dimensions)} dimensions. "
                     f"Red team logged {len(ctx.state.conflicts)} attacks. "
                     "Deterministic verdict — add a model/key for full reasoning.",
        "sensitivities": ["Evidence coverage", "Burn-rate assumption", "Competitive density signal"],
        "risks": [{"text": a.get("attack", ""), "source_agent": "red_team",
                   "severity": a.get("severity", 0.5)} for a in ctx.state.conflicts[:5]],
        "opportunities": [], "next_steps": [
            "Validate demand with 20 target-customer interviews",
            "Rebuild the burn model with real quotes",
            "Map the top 5 competitors' pricing and positioning",
            "List applicable regulations for the sector",
            "Re-run EIP in Board-Meeting depth once data improves"],
        "teach": "A verdict is only as good as its weakest sourced input. Improve the evidence, not the score.",
    }
    data, res = await ctx.llm.structured(
        "t3",
        "You compose the final decision document for an entrepreneur. Honest, specific, calibrated to their "
        "profile. You may NOT change the numeric verdict — it is computed deterministically.",
        f"BRIEF: {ctx.state.brief}\nPROFILE: {ctx.state.profile}\n"
        f"DIMENSIONS: {ctx.state.dimensions} → overall {overall}/10 (band {band})\n"
        f"ANALYST OUTPUTS: { {k: v for k, v in ctx.state.outputs.items() if k not in ('weighing_engine',)} }\n"
        f"RED TEAM: {ctx.state.conflicts}\nEVIDENCE:\n{ctx.state.evidence_digest()}",
        _VERDICT_SCHEMA, max_tokens=1400,
    )
    if data:
        data["recommendation"] = data.get("recommendation") or band
        await ctx.emit.usage(aid, res.tokens, res.route)
    else:
        data = fallback
        await ctx.emit.log(aid, "LLM unavailable — deterministic verdict document", "warn")

    verdict = {"score": overall, "band": band, "dimensions": ctx.state.dimensions, **data}
    ctx.state.verdict = verdict
    await ctx.emit.log(aid, f"VERDICT: {verdict['recommendation']} · {overall}/10", "ok")
    await ctx.emit.partial("verdict", verdict)
    await ctx.finish(aid, layer, verdict)
