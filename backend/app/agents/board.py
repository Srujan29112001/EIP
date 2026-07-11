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
from .registry import BY_ID
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


# ── L4: cross-pollination — every L2 specialist read against every other ──────

async def cross_pollinate(ctx: Ctx) -> None:
    """The second synthesis pass the A2A mesh promises: every domain specialist's
    headline is put in front of every other, so the board's findings reinforce
    or collide in the OPEN. Lights the whole intra-L2 mesh live (collab events)
    and surfaces the synergies/tensions/emergent insights no single agent saw."""
    aid, layer = "cross_pollinate", "L4"
    await ctx.start(aid, layer)
    o = ctx.state.outputs
    l2 = [k for k, v in o.items()
          if isinstance(v, dict) and v.get("verdict_line")
          and (BY_ID[k].layer if k in BY_ID else "") == "L2"]
    if len(l2) < 2:
        await ctx.emit.log(aid, "not enough specialists produced to cross-pollinate", "muted")
        await ctx.finish(aid, layer, {"verdict_line": "cross-pollination skipped — too few specialists",
                                      "connections": [], "emergent": [], "degraded": True})
        return

    # every specialist now formally reads every other → light the full mesh live
    for a in l2:
        await ctx.emit.collab(a, [p for p in l2 if p != a])
    await ctx.emit.log(aid, f"cross-reading {len(l2)} specialists — "
                            f"{len(l2) * (len(l2) - 1) // 2} pairs on the board", "muted")

    headlines = {k: str(o[k].get("verdict_line"))[:140] for k in l2}
    scores = {k: o[k].get("score") for k in l2 if isinstance(o[k].get("score"), (int, float))}
    schema = ('{"connections": [{"a": agent_id, "b": agent_id, "type": "synergy"|"tension", '
              '"insight": str (<=28 words — the combined so-what)}], '
              '"emergent": [str (<=24 words) — 2-3 board-level insights visible only across the whole board]}')
    data, res = await ctx.llm.structured(
        "t3",
        "You are the board's cross-pollinator. You are handed EVERY specialist's headline finding. "
        "Find the pairs where two specialists' findings REINFORCE each other (synergy) or COLLIDE "
        "(tension), and state the combined insight the decision-maker should act on. Use the EXACT "
        "agent ids given. Then name 2-3 emergent insights that appear only when the whole board is "
        "read together. Be specific; never just restate one agent.",
        f"BRIEF: {ctx.state.brief}\nSPECIALIST HEADLINES (id -> finding):\n"
        + "\n".join(f"- {k}: {v}" for k, v in headlines.items()),
        schema, max_tokens=850, agent=aid)

    ids = set(l2)
    conns: list[dict[str, Any]] = []
    seen_pairs: set[frozenset[str]] = set()
    for c in ((data or {}).get("connections") or []):
        if not isinstance(c, dict):
            continue
        a, b = c.get("a"), c.get("b")
        if a in ids and b in ids and a != b and frozenset((a, b)) not in seen_pairs:
            seen_pairs.add(frozenset((a, b)))
            typ = "tension" if str(c.get("type", "")).lower().startswith("t") else "synergy"
            conns.append({"a": a, "b": b, "type": typ, "insight": str(c.get("insight", ""))[:200]})
    conns = conns[:7]
    emergent = [str(e)[:200] for e in ((data or {}).get("emergent") or []) if e][:3]

    degraded = False
    if conns or emergent:
        await ctx.emit.usage(aid, res.tokens, res.route)
        for c in conns:
            if c["type"] == "tension":
                await ctx.emit.conflict(c["a"], c["b"], c["insight"])
            await ctx.emit.claim(aid, f"{c['a']} & {c['b']} — {c['insight']}", confidence=0.5)
        await ctx.emit.log(aid, f"{len(conns)} cross-links · {len(emergent)} emergent insights", "ok")
    else:
        # deterministic fallback: pair by score extremes so there is always a read
        degraded = True
        if len(scores) >= 2:
            ranked = sorted(scores, key=lambda k: scores[k], reverse=True)
            if ranked[0] != ranked[1]:
                conns.append({"a": ranked[0], "b": ranked[1], "type": "synergy",
                              "insight": "The two strongest reads on the board — the core of the case rests here."})
            if ranked[0] != ranked[-1]:
                conns.append({"a": ranked[0], "b": ranked[-1], "type": "tension",
                              "insight": "The widest disagreement on the board — resolve this before committing."})
        await ctx.emit.log(aid, "LLM unavailable — deterministic score-based cross-links only", "warn")

    result = {"verdict_line": f"{len(conns)} cross-links across {len(l2)} specialists",
              "connections": conns, "emergent": emergent, "degraded": degraded}
    await ctx.emit.partial("cross_insights", result)
    await ctx.finish(aid, layer, result)


# ── Phase-15 expansion — the full catalog build-out (13 new lenses) ───────────

async def ai_ml_strategist(ctx: Ctx) -> None:
    await _lens(ctx, "ai_ml_strategist",
        "You are an AI & ML strategist: AI feasibility for THIS business, model build-vs-buy, "
        "data moats, AI governance and the EU-AI-Act/DPDP-style obligations that may apply.",
        "Give the AI read: where AI genuinely helps this venture (or doesn't), build-vs-buy for the "
        "first use case, the data moat potential, one governance obligation to respect. "
        "Score 0-10 for AI leverage.",
        "AI-leverage read needs a model", 5.0)


async def data_analytics(ctx: Ctx) -> None:
    await _lens(ctx, "data_analytics",
        "You are a data science & analytics lead: data strategy, instrumentation, the metrics tree, "
        "and what can honestly be predicted at this stage.",
        "Design the data spine: the 4-5 metrics that matter first (the metric tree), what to "
        "instrument from day one, one prediction that becomes possible after 90 days of data. "
        "Score 0-10 for data-advantage potential.",
        "Data-strategy read needs a model", 5.0)


async def software_architecture(ctx: Ctx) -> None:
    await _lens(ctx, "software_architecture",
        "You are a software architect: technical feasibility, architecture shape, build-cost/time "
        "ESTIMATES, scalability and the buy-vs-build stack choices.",
        "Give the build read: the simplest architecture that works, rough build cost + time to MVP "
        "(ESTIMATE, show the math), the scaling wall, one thing NOT to build. "
        "Score 0-10 for technical feasibility.",
        "Build estimate needs a model", 5.5)


async def product_ux(ctx: Ctx) -> None:
    await _lens(ctx, "product_ux",
        "You are a product & UX strategist: user research, product-market-fit signals, the core "
        "loop, onboarding friction.",
        "Give the product read: the ONE core user loop, the riskiest UX assumption, the PMF signal "
        "to watch weekly, one onboarding fix. Score 0-10 for product-market-fit potential.",
        "Product read needs a model", 5.0)


async def cybersecurity_privacy(ctx: Ctx) -> None:
    await _lens(ctx, "cybersecurity_privacy",
        "You are a cybersecurity & privacy lead: threat model, privacy-by-design (DPDP/GDPR), "
        "certification readiness (SOC2/ISO), and what a breach would cost this venture.",
        "Give the security read: the 2 most likely threats, the privacy obligation that applies "
        "from day one, the certification that unlocks enterprise sales, one cheap hardening move. "
        "Score 0-10 for security/privacy readiness.",
        "Security posture needs a model", 5.5)


async def deep_tech(ctx: Ctx) -> None:
    await _lens(ctx, "deep_tech",
        "You are an emerging/deep-tech analyst: technology readiness levels (TRL), hype-vs-real "
        "maturity, and what frontier tech could disrupt or enable this venture.",
        "Give the frontier read: the emerging technology most relevant here with its honest TRL, "
        "whether it enables or threatens this venture, and the realistic adoption window. "
        "Score 0-10 for deep-tech tailwind.",
        "Frontier read needs a model", 5.0)


async def fundraising_capital(ctx: Ctx) -> None:
    await _lens(ctx, "fundraising_capital",
        "You are a fundraising strategist: round strategy, investor-type match, the deck's spine, "
        "terms to accept vs refuse. Distinct from bank credit (the Banker covers that).",
        "Design the raise: should they raise at all vs bootstrap, the right round size + investor "
        "type for this stage, the 3 deck slides that must land, one term to never sign. "
        "Score 0-10 for fundability.",
        "Raise strategy needs a model", 5.0)


async def sales_revops(ctx: Ctx) -> None:
    await _lens(ctx, "sales_revops",
        "You are a sales & revenue-ops lead: sales motion design, playbooks, pipeline math, "
        "compensation that doesn't backfire.",
        "Design the sales motion: founder-led vs inside vs field for this ticket size, the pipeline "
        "math (leads→close ESTIMATE), the first sales hire trigger, one comp-plan trap. "
        "Score 0-10 for sales-motion clarity.",
        "Sales-motion read needs a model", 5.0)


async def customer_success(ctx: Ctx) -> None:
    await _lens(ctx, "customer_success",
        "You are a customer-success & retention lead: onboarding, activation, expansion revenue, "
        "churn saves. (The Cohort Analyst does the curves; you do the OPERATING plan.)",
        "Design retention operations: the activation moment to engineer, the onboarding step that "
        "kills churn, the expansion-revenue lever, one save-play for at-risk customers. "
        "Score 0-10 for retention-ops readiness.",
        "Retention-ops read needs a model", 5.0)


async def partnerships_bd(ctx: Ctx) -> None:
    await _lens(ctx, "partnerships_bd",
        "You are a partnerships & BD strategist: alliances, channel partners, deal structures "
        "that don't give the company away.",
        "Design the partnership play: the ONE partner type that changes the trajectory, the deal "
        "structure to offer, what to never exclusivity away, and the first outreach. "
        "Score 0-10 for partnership leverage.",
        "Partnership read needs a model", 5.0)


async def brand_creative(ctx: Ctx) -> None:
    await _lens(ctx, "brand_creative",
        "You are a brand & creative director: identity, naming, positioning territory, the "
        "creative direction that fits the audience and budget.",
        "Give the brand read: the positioning territory to own (vs competitors on the board), a "
        "naming direction, the ONE brand asset to invest in first. Score 0-10 for brand-edge potential.",
        "Brand read needs a model", 5.0)


async def pr_communications(ctx: Ctx) -> None:
    await _lens(ctx, "pr_communications",
        "You are a PR & communications strategist: media relations, the story angles journalists "
        "actually take, crisis comms preparedness.",
        "Design the comms plan: the press-worthy angle in this venture, the 2 outlets/beats that "
        "matter, the crisis scenario to pre-draft for. Score 0-10 for earned-media potential.",
        "Comms read needs a model", 5.0)


async def founder_coaching(ctx: Ctx) -> None:
    await _lens(ctx, "founder_coaching",
        "You are a founder coach & org designer: the founder's leverage, decision hygiene, the org "
        "and culture that scaling will demand.",
        "Coach the founder: the biggest founder-side risk in this plan, the weekly decision ritual "
        "to adopt, the first culture norm to write down, when to hire a complement. "
        "Score 0-10 for founder-org readiness.",
        "Founder-coaching read needs a model", 5.5)


# ── L4: compliance alerts — deterministic regulatory red-flag scan ────────────

_COMPLIANCE_AGENTS = ("policy_compliance", "regulator", "legal", "tax", "subsidies_schemes",
                      "debt_banking", "banking", "options_desk")
_RED_FLAG = re.compile(
    r"licen[cs]|permit|prohibit|\bban\b|mandatory|penal|non[- ]?complian|breach|SEBI|RBI|"
    r"FSSAI|AYUSH|CCI|GST|DPIIT|KYC|AML|FEMA|infring|liabilit|lawsuit|tighten|crackdown",
    re.I)


async def compliance_scan(ctx: Ctx) -> None:
    """Deterministic scan of the regulatory/legal/tax specialists + evidence for
    red flags a founder must not miss. No LLM — it reads what the board already
    produced and elevates the compliance-critical items into their own channel."""
    aid, layer = "compliance_scan", "L4"
    await ctx.start(aid, layer)
    o = ctx.state.outputs
    alerts: list[dict[str, Any]] = []
    for agent_id in _COMPLIANCE_AGENTS:
        out = o.get(agent_id)
        if not isinstance(out, dict):
            continue
        line = str(out.get("verdict_line") or "")
        score = out.get("score")
        hit = bool(_RED_FLAG.search(line)) or bool(_RED_FLAG.search(str(out.get("analysis") or "")))
        low = isinstance(score, (int, float)) and score < 5.5
        if hit or low:
            sev = ("high" if (isinstance(score, (int, float)) and score < 4.0)
                   else "medium" if (low or hit) else "low")
            alerts.append({
                "agent": agent_id, "severity": sev,
                "text": line or f"{agent_id} flagged a compliance concern",
                "action": (out.get("assumptions") or [""])[0] if isinstance(out.get("assumptions"), list) else "",
                "score": score if isinstance(score, (int, float)) else None,
            })
    # regulatory tightening signals straight off the evidence board
    for e in ctx.state.evidence:
        txt = str(e.get("text") or "")
        if re.search(r"tighten|crackdown|new rule|amendment|ban\b|prohibit|penalt", txt, re.I):
            alerts.append({"agent": str(e.get("agent") or "news_intel"), "severity": "medium",
                           "text": txt[:200], "action": "verify against the latest official circular",
                           "score": None})
    # de-dup + rank (high → medium), cap
    order = {"high": 0, "medium": 1, "low": 2}
    seen: set[str] = set()
    ranked = []
    for a in sorted(alerts, key=lambda x: order.get(x["severity"], 3)):
        key = a["text"][:60].lower()
        if key in seen:
            continue
        seen.add(key)
        ranked.append(a)
    ranked = ranked[:8]

    highs = sum(1 for a in ranked if a["severity"] == "high")
    await ctx.emit.partial("compliance_alerts", {"alerts": ranked, "high": highs})
    if ranked:
        await ctx.emit.log(aid, f"{len(ranked)} compliance alert(s) · {highs} high-severity", "warn" if highs else "info")
    else:
        await ctx.emit.log(aid, "no regulatory red flags detected in the board's output", "ok")
    await ctx.finish(aid, layer, {"verdict_line": f"{len(ranked)} compliance alert(s), {highs} high",
                                  "alerts": ranked})


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


# ── Phase-13 expansion — the "future improvements" agents, implemented ────────

async def pricing_strategist(ctx: Ctx) -> None:
    await _lens(ctx, "pricing_strategist",
        "You are a pricing strategist: Van-Westendorp thinking, value-based pricing, "
        "willingness-to-pay bands, price architecture (anchor/decoy/tiers). Ground in the "
        "evidence; tag unsourced numbers ESTIMATE.",
        "Design the price architecture: the WTP band for the target segment (ESTIMATE ok), the "
        "recommended price + tier structure, and ONE pricing experiment to run first. "
        "Score 0-10 for pricing power.",
        "Pricing read needs a model — WTP band unestimated", 5.0)


async def supply_chain(ctx: Ctx) -> None:
    await _lens(ctx, "supply_chain",
        "You are a supply-chain analyst: input dependencies, single-source fragility, logistics "
        "cost share, buffer strategy. India-first when the geography says so.",
        "Map the supply chain: the 2-3 critical inputs and their sourcing risk, the single point "
        "of failure, logistics cost as % of COGS (ESTIMATE ok), one resilience move. "
        "Score 0-10 for supply resilience.",
        "Supply-chain map needs a model", 5.0)


async def cohort_retention(ctx: Ctx) -> None:
    await _lens(ctx, "cohort_retention",
        "You are a cohort & retention analyst: retention curves, LTV by cohort, churn drivers, "
        "repeat-purchase economics.",
        "Project the retention reality: expected M1/M3/M6 retention for this category (ESTIMATE), "
        "the dominant churn driver, LTV:CAC implication, one retention lever. "
        "Score 0-10 for retention durability.",
        "Retention curve needs a model", 5.0)


async def cap_table(ctx: Ctx) -> None:
    await _lens(ctx, "cap_table",
        "You are a cap-table and dilution modeler: round math, ESOP pools, founder dilution "
        "across scenarios, clean vs messy structures.",
        "Model the equity path: a sensible first-round structure for this stage, founder % after "
        "two rounds (ESTIMATE math shown), the ESOP reserve, one cap-table mistake to avoid. "
        "Score 0-10 for founder-equity health on the current plan.",
        "Dilution math needs a model", 5.5)


async def patent_ip(ctx: Ctx) -> None:
    await _lens(ctx, "patent_ip",
        "You are a patent / IP scout: prior-art signals, freedom-to-operate, what is protectable "
        "(marks, designs, process), India + global filings awareness.",
        "Give the IP read: what here is protectable and how, the freedom-to-operate risk level, "
        "one filing worth its fee, one infringement trap. Score 0-10 for IP defensibility.",
        "IP scan needs a model", 5.0)


async def insurance_risk(ctx: Ctx) -> None:
    await _lens(ctx, "insurance_risk",
        "You are an insurance & risk-transfer advisor: what is insurable, what liability to "
        "transfer vs retain, the covers a lender or landlord will demand.",
        "Lay out risk transfer: the 2-3 covers this venture actually needs (with rough premium "
        "band, ESTIMATE), the liability best transferred by contract, the uninsurable risk to "
        "engineer around. Score 0-10 for risk transferability.",
        "Insurance read needs a model", 5.5)


async def sustainability_acct(ctx: Ctx) -> None:
    await _lens(ctx, "sustainability_accountant",
        "You are a sustainability accountant: carbon/impact quantified into cost and moat — "
        "compliance today, pricing power and procurement preference tomorrow.",
        "Quantify sustainability: the main footprint driver (ESTIMATE), the cost of cleaning it "
        "vs the moat it buys (green procurement, premium positioning), one credible claim that "
        "won't be greenwashing. Score 0-10 for sustainability advantage.",
        "Impact accounting needs a model", 5.0)


async def sentiment_analyst(ctx: Ctx) -> None:
    await _lens(ctx, "sentiment_analyst",
        "You are a sentiment analyst: read the live news/web evidence as a DEMAND SIGNAL — "
        "consumer mood, category buzz, backlash risk. Never invent items not on the board.",
        "Read the sentiment: the net mood in the live evidence toward this category (bullish/"
        "neutral/bearish and why), the strongest positive and negative signal, what would flip "
        "it. Score 0-10 for demand-signal strength.",
        "Sentiment read needs a model — evidence counted only", 5.0)


async def negotiation_coach(ctx: Ctx) -> None:
    """L4 — turns the verdict into the next conversation: BATNA, anchors, concessions."""
    aid, layer = "negotiation_coach", "L4"
    await ctx.start(aid, layer)
    lines = {k: v.get("verdict_line") for k, v in list(ctx.state.outputs.items())[:24]
             if isinstance(v, dict) and v.get("verdict_line")}
    schema = ('{"counterparty": str (who the next negotiation is with), '
              '"batna": str (<=25 words — the walk-away alternative), '
              '"anchor": str (<=20 words — the opening position, with a number if evidenced), '
              '"concessions": [str x2 (<=15 words each — what to give, in order)], '
              '"walk_away": str (<=15 words — the red line), '
              '"verdict_line": str (<=90 chars)}')
    data, res = await ctx.llm.structured(
        "t3",
        "You are a negotiation coach. Turn the board's verdict into the user's NEXT conversation "
        "(investor, bank, landlord, supplier, or broker — pick the most imminent). Give BATNA, "
        "anchor, ordered concessions, and the walk-away line. Grounded in the findings only.",
        f"BRIEF: {str(ctx.state.brief)[:400]}\nVERDICT: {ctx.state.verdict.get('score')}/10 "
        f"{ctx.state.verdict.get('recommendation')}\nFINDINGS: {lines}",
        schema, max_tokens=500, agent=aid)
    if data and data.get("batna"):
        await ctx.emit.usage(aid, res.tokens, res.route)
        await ctx.emit.log(aid, f"next table: {str(data.get('counterparty',''))[:60]} · "
                                f"anchor: {str(data.get('anchor',''))[:60]}", "ok")
        out = {"verdict_line": data.get("verdict_line") or f"negotiation plan vs {data.get('counterparty')}",
               "degraded": False, **data}
    else:
        out = {"verdict_line": "Negotiation plan needs a model", "batna": "", "anchor": "",
               "concessions": [], "degraded": True}
        await ctx.emit.log(aid, "LLM unavailable — no negotiation plan", "warn")
    await ctx.finish(aid, layer, out)


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
    # Phase-13 expansion lenses
    "pricing_strategist": pricing_strategist,
    "supply_chain": supply_chain,
    "cohort_retention": cohort_retention,
    "cap_table": cap_table,
    "patent_ip": patent_ip,
    "insurance_risk": insurance_risk,
    "sustainability_accountant": sustainability_acct,
    "sentiment_analyst": sentiment_analyst,
    # Phase-15 catalog build-out
    "ai_ml_strategist": ai_ml_strategist,
    "data_analytics": data_analytics,
    "software_architecture": software_architecture,
    "product_ux": product_ux,
    "cybersecurity_privacy": cybersecurity_privacy,
    "deep_tech": deep_tech,
    "fundraising_capital": fundraising_capital,
    "sales_revops": sales_revops,
    "customer_success": customer_success,
    "partnerships_bd": partnerships_bd,
    "brand_creative": brand_creative,
    "pr_communications": pr_communications,
    "founder_coaching": founder_coaching,
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
