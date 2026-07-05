"""Phase-3 board agents — the venture cluster wave + deeper crucible/synthesis.

Same contract as every EIP agent: deterministic core that always answers,
LLM narrative that upgrades it, all figures sourced or flagged ESTIMATE.
Domain decompositions are ported from the legacy 38-agent generation
(market/legal/tax/policy agents) — the prompts survived, the mock data didn't.
"""
from __future__ import annotations

import re
from typing import Any

from .base import Ctx
from .venture import _scored_analysis

# ── L2: competitor intelligence ───────────────────────────────────────────────

async def competitor_intel(ctx: Ctx) -> None:
    aid, layer = "competitor_intel", "L2"
    await ctx.start(aid, layer)
    ev = ctx.state.evidence
    rivals = [e for e in ev if re.search(r"competitor|rival|brand|player|startup|raises|funding", e["text"], re.I)]
    await ctx.emit.log(aid, f"{len(rivals)} competitor signals on the evidence board", "info")
    det = max(2.0, 7.5 - len(rivals) * 0.4)
    fallback = {
        "verdict_line": f"{len(rivals)} live competitor signals — density screen only",
        "score": round(det, 1), "confidence": 0.3,
        "analysis": "Deterministic screen: competitive density from live search/news hits. "
                    "Add a key/model for positioning-map analysis.",
        "assumptions": ["Signal density approximates crowding"], "numbers_used": [],
    }
    out = await _scored_analysis(
        ctx, aid,
        "You are a competitor-intelligence analyst. Map who competes, how they are positioned, "
        "where the moats are, and where the whitespace is.",
        "From the evidence, identify the strongest competitors and their positioning, entry barriers, "
        "and one exploitable whitespace. Score 0-10 how winnable this space is for THIS founder "
        "(higher = more winnable).", fallback)
    await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
    await ctx.finish(aid, layer, out)


# ── L2: GTM & distribution ────────────────────────────────────────────────────

async def gtm_distribution(ctx: Ctx) -> None:
    aid, layer = "gtm_distribution", "L2"
    await ctx.start(aid, layer)
    b = ctx.state.brief
    team = {"solo": 1, "2_5": 3, "5_20": 10, "20_plus": 25}.get(b.get("team_size", "solo"), 1)
    det = 4.0 + (1.0 if team >= 3 else 0.0) + (0.5 if b.get("stage") in ("mvp", "traction", "scaling") else 0.0)
    await ctx.emit.log(aid, f"execution base: team {team} · stage {b.get('stage')}", "code")
    fallback = {
        "verdict_line": f"Execution screen: team of {team} at {b.get('stage')} stage",
        "score": round(det, 1), "confidence": 0.3,
        "analysis": "Deterministic screen from team size and stage only. Add a key/model for a "
                    "channel-by-channel GTM plan.",
        "assumptions": ["Team size proxies execution capacity"], "numbers_used": [],
    }
    out = await _scored_analysis(
        ctx, aid,
        "You are a go-to-market strategist. Channels, launch sequencing, CAC reality-checks, "
        "distribution advantages. India-first when geography says so.",
        "Design the realistic first GTM motion: 2-3 channels in order, expected CAC pressure, one "
        "distribution edge to build. Score 0-10 for EXECUTION feasibility with this team and stage.",
        fallback)
    await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
    await ctx.finish(aid, layer, out)


# ── L2: legal ─────────────────────────────────────────────────────────────────

async def legal(ctx: Ctx) -> None:
    aid, layer = "legal", "L2"
    await ctx.start(aid, layer)
    fallback = {
        "verdict_line": "Standard early-stage legal hygiene applies — no red flags detectable without analysis",
        "score": 6.0, "confidence": 0.25,
        "analysis": "Deterministic checklist: entity formation (Pvt Ltd vs LLP), founder agreement, "
                    "IP assignment, basic contracts. Add a key/model for sector-specific exposure.",
        "assumptions": ["No unusual IP or liability profile"], "numbers_used": [],
    }
    out = await _scored_analysis(
        ctx, aid,
        "You are a startup counsel for Indian ventures. Entity structure, founder agreements, IP, "
        "liability, key contracts. Practical, not academic.",
        "Identify the 3 most material legal exposures for this venture and the structure you would "
        "choose. Score 0-10 for REGULATORY/legal cleanliness (higher = fewer landmines).", fallback)
    await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
    await ctx.finish(aid, layer, out)


# ── L2: tax (India-first) ─────────────────────────────────────────────────────

async def tax(ctx: Ctx) -> None:
    aid, layer = "tax", "L2"
    await ctx.start(aid, layer)
    geo = ctx.state.brief.get("geography", "India")
    det_notes = ("GST registration mandatory past ₹40L turnover (₹20L services); composition scheme "
                 "≤₹1.5Cr; Section 80-IAC startup exemption needs DPIIT recognition" if geo == "India"
                 else "jurisdiction-specific — add a key for detail")
    await ctx.emit.log(aid, f"baseline: {det_notes}", "code")
    fallback = {
        "verdict_line": "Standard tax posture for stage — thresholds noted, no optimization modelled",
        "score": 6.0, "confidence": 0.3,
        "analysis": f"Deterministic baseline ({geo}): {det_notes}.",
        "assumptions": ["Revenue below GST threshold at launch"], "numbers_used": [],
    }
    out = await _scored_analysis(
        ctx, aid,
        "You are a tax strategist (India-first: GST, income tax, startup exemptions). Legitimate "
        "optimization only; flag classification ambiguities.",
        "Lay out the tax posture: GST classification for this product/service, applicable exemptions, "
        "one legitimate optimization, one classification risk. Score 0-10 for tax simplicity/burden "
        "(higher = simpler).", fallback)
    await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
    await ctx.finish(aid, layer, out)


# ── L2: policy & compliance ───────────────────────────────────────────────────

async def policy_compliance(ctx: Ctx) -> None:
    aid, layer = "policy_compliance", "L2"
    await ctx.start(aid, layer)
    ev_reg = [e for e in ctx.state.evidence if re.search(r"regulat|complian|licen[cs]|FSSAI|SEBI|RBI|ban|policy|act\b", e["text"], re.I)]
    await ctx.emit.log(aid, f"{len(ev_reg)} regulatory signals in evidence", "info")
    fallback = {
        "verdict_line": f"{len(ev_reg)} regulatory signals found — compliance calendar needs a model",
        "score": max(3.0, 6.5 - len(ev_reg) * 0.5), "confidence": 0.3,
        "analysis": "Deterministic screen: regulatory signal density from live evidence. "
                    "Add a key/model for the acts/rules calendar.",
        "assumptions": ["No sector-specific licensing beyond signals found"], "numbers_used": [],
    }
    out = await _scored_analysis(
        ctx, aid,
        "You are a regulatory-compliance analyst (India-first: FSSAI, AYUSH, SEBI, RBI, CCI, state "
        "rules as relevant). Cite specific acts/rules when the evidence supports them.",
        "Build the compliance picture: which regulators/acts apply, licences needed before launch, "
        "any tightening trends in evidence. Score 0-10 for regulatory ease (higher = lighter burden).",
        fallback)
    await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
    await ctx.finish(aid, layer, out)


# ── L2: industry expert ───────────────────────────────────────────────────────

async def industry_expert(ctx: Ctx) -> None:
    aid, layer = "industry_expert", "L2"
    await ctx.start(aid, layer)
    fallback = {
        "verdict_line": "Sector dynamics require a model — no deterministic industry priors shipped",
        "score": 5.0, "confidence": 0.2,
        "analysis": "Add a key/model for sector benchmarks (margins, cycles, failure modes).",
        "assumptions": [], "numbers_used": [],
    }
    out = await _scored_analysis(
        ctx, aid,
        "You are a 20-year operator in this specific industry. Unit-economics benchmarks, typical "
        "failure modes, what insiders know that outsiders don't.",
        "Give the insider view: 2 sector benchmarks that matter (with ESTIMATE tags unless evidenced), "
        "the most common failure mode for new entrants, one non-obvious dynamic. Score 0-10 for how "
        "attractive this industry is to enter now.", fallback)
    await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
    await ctx.finish(aid, layer, out)


# ── L3: devil's advocate ──────────────────────────────────────────────────────

async def devils_advocate(ctx: Ctx) -> None:
    aid, layer = "devils_advocate", "L3"
    await ctx.start(aid, layer)
    await ctx.emit.log(aid, "mandate: steel-man the NO — the strongest honest case against", "muted")
    schema = ('{"no_case": str (<=120 words, the strongest coherent argument for NOT doing this), '
              '"strongest_point": str, "what_would_flip_me": str}')
    data, res = await ctx.llm.structured(
        "t3",
        "You are the devil's advocate. Argue the NO case as a smart, honest skeptic would — not "
        "strawman pessimism. You want the founder to succeed by making them face the best counter-case.",
        f"BRIEF: {ctx.state.brief}\nANALYST VERDICT LINES: "
        f"{ {k: v.get('verdict_line') for k, v in ctx.state.outputs.items() if isinstance(v, dict) and v.get('verdict_line')} }\n"
        f"EVIDENCE:\n{ctx.state.evidence_digest(12)}",
        schema, max_tokens=600, agent=aid,
    )
    if not data:
        data = {"no_case": "At this stage the honest NO case is generic but real: most ventures die of "
                           "no-demand discovered too late. Without validated willingness-to-pay, capital "
                           "converts to inventory and ads, not learning.",
                "strongest_point": "No demand validation yet",
                "what_would_flip_me": "20 strangers pre-ordering at full price"}
        await ctx.emit.log(aid, "LLM unavailable — canonical NO case applied", "warn")
    else:
        await ctx.emit.usage(aid, res.tokens, res.route)
    await ctx.emit.log(aid, data.get("no_case", ""), "warn")
    await ctx.emit.claim(aid, f"Steel-manned NO: {data.get('strongest_point','')}", confidence=0.6)
    await ctx.emit.log(aid, f"what would flip me: {data.get('what_would_flip_me','')}", "info")
    await ctx.finish(aid, layer, data)


# ── L4: connecting dots ───────────────────────────────────────────────────────

async def connecting_dots(ctx: Ctx) -> None:
    aid, layer = "connecting_dots", "L4"
    await ctx.start(aid, layer)
    await ctx.emit.log(aid, "looking across domains for patterns no single agent can see", "muted")
    schema = ('{"insights": [{"pattern": str (<=35 words, must connect >=2 domains), '
              '"domains": [str], "implication": str (<=25 words)}], "weak_signal": str}')
    lines = {k: v.get("verdict_line") for k, v in ctx.state.outputs.items()
             if isinstance(v, dict) and v.get("verdict_line")}
    data, res = await ctx.llm.structured(
        "t3",
        "You are the cross-domain synthesizer. Find second-order patterns that emerge only when "
        "domains are combined (e.g. macro trend × regulatory shift × competitor move). Never repeat "
        "what a single agent already said.",
        f"BRIEF: {ctx.state.brief}\nDOMAIN VERDICTS: {lines}\nEVIDENCE:\n{ctx.state.evidence_digest(14)}",
        schema, max_tokens=700, agent=aid,
    )
    insights = (data or {}).get("insights") or []
    insights = [i for i in insights if isinstance(i, dict)][:3]
    if insights:
        await ctx.emit.usage(aid, res.tokens, res.route)
        for ins in insights:
            await ctx.emit.claim(aid, f"{ins.get('pattern','')} → {ins.get('implication','')}",
                                 confidence=0.55)
        if (data or {}).get("weak_signal"):
            await ctx.emit.log(aid, f"weak signal: {data['weak_signal']}", "info")
    else:
        await ctx.emit.log(aid, "LLM unavailable — cross-domain synthesis needs a model (skipped honestly)", "warn")
    await ctx.finish(aid, layer, {"insights": insights, "weak_signal": (data or {}).get("weak_signal", "")})


# ── Phase-7 venture extras + world cluster ────────────────────────────────────
# Same contract, same blackboard; each is a domain lens over the shared evidence.

async def _lens(ctx: Ctx, aid: str, system: str, ask: str, det_line: str, det_score: float = 5.0) -> None:
    """Compact _scored_analysis wrapper for narrative-first agents."""
    await ctx.start(aid, "L2")
    fallback = {"verdict_line": det_line, "score": det_score, "confidence": 0.25,
                "analysis": "Add a key/model for the full read.", "assumptions": [], "numbers_used": []}
    out = await _scored_analysis(ctx, aid, system, ask, fallback)
    await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
    await ctx.finish(aid, "L2", out)


async def business_model(ctx: Ctx) -> None:
    await _lens(ctx, "business_model",
        "You are a business-model analyst (canvas thinking: value prop, channels, revenue streams, "
        "cost structure) and recommender.",
        "Map the implied business model, name its weakest block, and recommend the best-fit model "
        "variant (e.g. subscription vs D2C one-off vs B2B2C) with one revenue experiment. "
        "Score 0-10 for model soundness.",
        "Business-model canvas needs a model — no deterministic prior")


async def marketing_strategy(ctx: Ctx) -> None:
    await _lens(ctx, "marketing_strategy",
        "You are a growth marketer: positioning, CAC/LTV realism, brand wedge, growth loops.",
        "Design the marketing wedge: positioning line, first growth loop, CAC pressure-test against "
        "the evidence. Score 0-10 for marketing leverage.",
        "Marketing plan needs a model — evidence-density screen only")


async def subsidies_schemes(ctx: Ctx) -> None:
    await _lens(ctx, "subsidies_schemes",
        "You are a government-schemes analyst (India-first: Startup India, MSME, PLI, state schemes, "
        "DPIIT, Mudra). You surface money founders leave on the table.",
        "List the 2-3 schemes/subsidies this venture most plausibly qualifies for, what each is worth, "
        "and the catch. Score 0-10 for scheme leverage available.",
        "Scheme scan needs a model — none detectable deterministically", 4.0)


async def hr_talent(ctx: Ctx) -> None:
    await _lens(ctx, "hr_talent",
        "You are a startup talent strategist: team gaps, hiring order, salary benchmarks, ESOP hygiene.",
        "Given team size and stage: the first 2 hires (in order), realistic salary bands [ESTIMATE], "
        "and the biggest team risk. Score 0-10 for team readiness.",
        "Team screen: size/stage heuristic only")


async def optimization_predictor(ctx: Ctx) -> None:
    await _lens(ctx, "optimization_predictor",
        "You are the loophole/optimization predictor: legitimate structural optimizations (tax, "
        "regulatory, incentive stacking) AND the risk each carries. Never advise anything illegal; "
        "flag grey zones explicitly.",
        "Identify 2 legitimate optimizations others in this sector use (structure, timing, incentive "
        "stacking), each with its risk/grey-zone rating. Score 0-10 for optimization headroom.",
        "Optimization scan needs a model", 4.5)


async def regulator(ctx: Ctx) -> None:
    await _lens(ctx, "regulator",
        "You are a regulator-watch analyst (SEBI, RBI, CCI, FSSAI, TRAI, state bodies): who regulates "
        "this, their current enforcement mood, what draws scrutiny.",
        "Name the regulators that matter here, their current posture from the evidence, and the one "
        "action most likely to draw scrutiny. Score 0-10 for regulatory calm (10 = friendly).",
        "Regulator map needs a model — evidence signals only")


async def macroeconomist(ctx: Ctx) -> None:
    await _lens(ctx, "macroeconomist",
        "You are a macroeconomist. Use the macro series on the evidence board (GDP, inflation, rates) — "
        "never invent figures.",
        "Read the cycle from the board's macro data: where are we, what does it mean for THIS decision "
        "(funding climate, demand, input costs)? Score 0-10 for macro tailwind.",
        "Macro read uses board data only — needs a model for narrative")


async def geopolitics(ctx: Ctx) -> None:
    await _lens(ctx, "geopolitics",
        "You are a geopolitics analyst: trade routes, sanctions, supply chains, bilateral tensions.",
        "From the evidence, the 1-2 geopolitical exposures this decision has (supply chain, export "
        "market, input dependency) and one hedge. Score 0-10 for geopolitical insulation.",
        "Geopolitical scan needs a model", 6.0)


async def intl_markets(ctx: Ctx) -> None:
    await _lens(ctx, "intl_markets",
        "You are an international-expansion analyst: which foreign market fits first, entry mode, "
        "cross-border friction.",
        "If this ever goes beyond its home market: the most natural first foreign market, entry mode, "
        "and the friction to expect. Score 0-10 for international optionality.",
        "International read needs a model", 5.0)


async def trends(ctx: Ctx) -> None:
    await _lens(ctx, "trends",
        "You are a trends and weak-signals analyst. You look for what is emerging in the evidence "
        "before it is obvious — never repeat what other agents already said.",
        "From the news/evidence: one emerging trend that helps this decision, one that threatens it, "
        "one weak signal nobody prices in yet. Score 0-10 for trend alignment.",
        "Trend scan needs a model — headline density only")


async def esg_impact(ctx: Ctx) -> None:
    await _lens(ctx, "esg_impact",
        "You are an ESG and impact analyst: environmental footprint, social impact, governance "
        "hygiene — and where impact is a commercial edge, not a cost.",
        "Assess the ESG posture: the material environmental/social factor here, one way impact "
        "becomes a moat (procurement, brand, capital access). Score 0-10 for ESG position.",
        "ESG read needs a model", 5.5)


async def market_research(ctx: Ctx) -> None:
    await _lens(ctx, "market_research",
        "You are a market-research lead: TAM/SAM/SOM sizing, customer segmentation, primary + "
        "secondary research synthesis, demand signals. Use figures from the evidence board; tag "
        "anything not sourced as ESTIMATE.",
        "Size the opportunity: TAM / SAM / SOM (sourced or ESTIMATE), the 2-3 real customer segments "
        "with rough size, and the single strongest demand signal. Score 0-10 for opportunity size.",
        "Market sizing needs a model — evidence-board figures only", 5.5)


async def banking(ctx: Ctx) -> None:
    await _lens(ctx, "banking",
        "You are a business-banking and investment-banking advisor (India-first): working-capital "
        "and term loans, credit lines, banking schemes (Mudra, CGTMSE, Stand-Up India, PMEGP), "
        "capital structure, and how a banker / investment banker would fund or structure this. "
        "Legitimate structures only; flag what a lender will scrutinise.",
        "Lay out the banking & capital plan: the most fitting credit facility or banking scheme, one "
        "capital-structure move (debt vs equity mix), and the one thing a banker will demand before "
        "lending. Score 0-10 for financeability.",
        "Banking read needs a model", 5.5)


async def storytelling(ctx: Ctx) -> None:
    """L4 communication agent — turns the board's analysis into a pitch story.
    Runs after the verdict so it can frame the honest narrative."""
    aid, layer = "storytelling", "L4"
    await ctx.start(aid, layer)
    lines = {k: v.get("verdict_line") for k, v in ctx.state.outputs.items()
             if isinstance(v, dict) and v.get("verdict_line")}
    schema = ('{"hook": str (one-sentence pitch hook), "narrative": str (a ~120-word founder/pitch '
              'story grounded in the findings, no hype), "one_liner": str (the elevator line), '
              '"three_beats": [str x3 — problem, insight, why-now]}')
    data, res = await ctx.llm.structured(
        "t3",
        "You are a master business storyteller. Turn the board's analysis into a compelling but "
        "HONEST pitch narrative — the story a founder tells an investor. Grounded in the findings, "
        "no exaggeration; if the verdict is weak, tell the turnaround story instead.",
        f"BRIEF: {ctx.state.brief}\nVERDICT: {ctx.state.verdict.get('score')}/10 "
        f"{ctx.state.verdict.get('recommendation')}\nBOARD FINDINGS: {lines}",
        schema, max_tokens=800, agent=aid)
    if data and data.get("narrative"):
        await ctx.emit.usage(aid, res.tokens, res.route)
        await ctx.emit.partial("story", data)
        await ctx.emit.log(aid, f"hook: {str(data.get('hook',''))[:90]}", "ok")
        out = {"verdict_line": data.get("one_liner") or str(data.get("hook", ""))[:90],
               "degraded": False, **data}
    else:
        out = {"verdict_line": "Pitch narrative needs a model",
               "hook": str(ctx.state.brief.get("summary", ""))[:90], "narrative": "",
               "three_beats": [], "degraded": True}
        await ctx.emit.log(aid, "LLM unavailable — no narrative", "warn")
    await ctx.finish(aid, layer, out)


WORLD_WAVE = {
    "business_model": business_model,
    "marketing_strategy": marketing_strategy,
    "market_research": market_research,
    "subsidies_schemes": subsidies_schemes,
    "banking": banking,
    "hr_talent": hr_talent,
    "optimization_predictor": optimization_predictor,
    "regulator": regulator,
    "macroeconomist": macroeconomist,
    "geopolitics": geopolitics,
    "intl_markets": intl_markets,
    "trends": trends,
    "esg_impact": esg_impact,
}


# ── L3.5: debate rounds (War Room) ───────────────────────────────────────────
# When the Crucible lands an attack, the attacked analyst gets one rebuttal.
# Concessions lower that analyst's confidence; standing firm is preserved as
# open dissent. Either way the argument itself streams to the Boardroom.

async def debate_rounds(ctx: Ctx) -> None:
    attacks = sorted(
        (a for a in ctx.state.conflicts if isinstance(a, dict) and a.get("target_agent") in ctx.state.outputs),
        key=lambda a: -float(a.get("severity", 0.5) or 0.5),
    )[:3]
    if not attacks:
        return
    await ctx.emit.log("red_team", f"war room: {len(attacks)} attacks go to open debate", "muted")

    for rnd, atk in enumerate(attacks, start=1):
        target = str(atk.get("target_agent"))
        out = ctx.state.outputs.get(target, {})
        await ctx.emit.debate("red_team", rnd, str(atk.get("attack", ""))[:400], stance="attack")

        schema = ('{"rebuttal": str (<=60 words, specific), "concede": bool, '
                  '"revised_confidence": float (0-1)}')
        data, res = await ctx.llm.structured(
            "t3",
            f"You are the {target} agent defending your analysis in front of the board. "
            "If the attack is right, concede honestly and revise your confidence down. "
            "If it is wrong, rebut with specifics from your analysis or the evidence.",
            f"YOUR ANALYSIS: {out.get('verdict_line','')} — {str(out.get('analysis',''))[:500]}\n"
            f"YOUR CONFIDENCE: {out.get('confidence', 0.5)}\n"
            f"THE ATTACK: {atk.get('attack','')}\nATTACK EVIDENCE: {atk.get('evidence','')}",
            schema, max_tokens=400, agent=target,
        )
        if data and data.get("rebuttal"):
            await ctx.emit.usage(target, res.tokens, res.route)
            conceded = bool(data.get("concede"))
            await ctx.emit.debate(target, rnd, str(data["rebuttal"])[:400],
                                  stance="concession" if conceded else "rebuttal")
            if conceded:
                try:
                    revised = max(0.05, min(float(data.get("revised_confidence", 0.3)),
                                            float(out.get("confidence", 0.5))))
                except (TypeError, ValueError):
                    revised = 0.3
                out["confidence"] = revised
                await ctx.emit.log(target, f"conceded — confidence revised to {revised:.2f}", "warn")
            else:
                await ctx.emit.log(target, "stands by the analysis — dissent preserved", "info")
        else:
            await ctx.emit.debate(target, rnd,
                                  "Stands by the deterministic core; the attack is noted and preserved as dissent.",
                                  stance="rebuttal")


# id → coroutine map for the depth-aware graph
BOARD_AGENTS = {
    "competitor_intel": competitor_intel,
    "gtm_distribution": gtm_distribution,
    "legal": legal,
    "tax": tax,
    "policy_compliance": policy_compliance,
    "industry_expert": industry_expert,
    "devils_advocate": devils_advocate,
    "connecting_dots": connecting_dots,
}
