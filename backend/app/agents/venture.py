"""Phase-1 venture agents. Every agent follows the same contract:

    deterministic core  →  always produces a result (zero keys, zero network)
    + LLM narrative     →  upgrades depth when any route on the ladder works
    + events            →  stage / log / claim / usage over SSE

No agent may invent a number: figures either carry a source from the evidence
board or are labelled estimates (EIP Constitution #1).
"""
from __future__ import annotations

import asyncio
import re
from typing import Any

from ..grounding import macro, market, web
from .base import Ctx

# ── L0: intake parser ─────────────────────────────────────────────────────────

_STAGES = ["ideation", "validation", "mvp", "traction", "scaling", "expansion"]

def _heuristic_brief(raw: dict[str, Any]) -> dict[str, Any]:
    text = (raw.get("situation") or "").strip()
    lower = text.lower()
    stage = next((s for s in _STAGES if s in lower), raw.get("stage") or "ideation")
    brief = {
        "summary": text[:400] or "Unspecified venture idea",
        "industry": raw.get("industry") or "",
        "geography": raw.get("geography") or "India",
        "stage": stage,
        "budget_band": raw.get("budget_band") or "under_10L",
        "team_size": raw.get("team_size") or "solo",
        "uncertainty": raw.get("uncertainty") or "",
        "keywords": re.findall(r"[a-zA-Z]{4,}", lower)[:8],
    }
    # founder extras flow straight to every specialist via the brief
    for k in ("target_customer", "competitors", "revenue_model"):
        if raw.get(k):
            brief[k] = str(raw[k])[:200]
    return brief


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
        schema, agent=aid,
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
    depth = (ctx.state.raw.get("depth") or "pulse").lower()
    spine = ["web_researcher", "news_intel", "market_data", "macro_data",
             "market_analyst", "finance_modeler",
             "red_team", "fact_checker", "bias_auditor",
             "weighing_engine", "verdict_composer", "storytelling", "visualizer", "reporter"]
    board_wave = ["competitor_intel", "market_research", "banking", "gtm_distribution", "legal", "tax",
                  "policy_compliance", "industry_expert", "devils_advocate", "connecting_dots"]
    human_wave = ["human_behaviour", "human_needs", "consumer_analysis", "production_ops",
                  "philosophy_ethics", "money_happiness", "philanthropy_impact"]
    world_wave = ["business_model", "marketing_strategy",
                  "subsidies_schemes", "hr_talent", "optimization_predictor", "regulator",
                  "macroeconomist", "geopolitics", "intl_markets", "trends", "esg_impact"]
    scope = (spine if depth == "pulse"
             else spine + board_wave + human_wave if depth == "board"
             else spine + board_wave + human_wave + world_wave)
    label = {"pulse": "Pulse", "board": "Board Meeting", "war_room": "War Room"}.get(depth, "Pulse")
    if depth == "war_room":
        await ctx.emit.log(aid, "war room: full board + world cluster + open debate rounds", "muted")

    # the user can hand-pick the board (agent toggles in the wizard); the
    # synthesis layer is never optional — someone has to sign the verdict
    enabled = set(ctx.state.raw.get("agents_enabled") or [])
    if enabled:
        mandatory = {"weighing_engine", "verdict_composer", "storytelling", "visualizer", "reporter"}
        dropped = [a for a in scope if a not in enabled and a not in mandatory]
        scope = [a for a in scope if a in enabled or a in mandatory]
        if dropped:
            await ctx.emit.log(aid, f"benched by you: {', '.join(dropped)}", "muted")
            for d in dropped:
                await ctx.emit.stage(d, "skipped", "")
    ctx.state.scope = scope
    await ctx.emit.log(aid, f"convening {len(scope)} specialists for a {label} run", "info")
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


# ── L1: market data (t0 — pure data, no LLM) ─────────────────────────────────

async def market_data(ctx: Ctx) -> None:
    aid, layer = "market_data", "L1"
    await ctx.start(aid, layer)
    b = ctx.state.brief
    geo = b.get("geography", "India")
    idx_sym, idx_label = market.INDEX.get(geo, market.INDEX["India"])
    sector = market.sector_for(f"{b.get('industry','')} {b.get('summary','')}")

    targets = [(idx_sym, idx_label)] + ([sector] if sector else [])
    for sym, label in targets:
        await ctx.emit.log(aid, f"⌕ yfinance: {sym} ({label})", "code")
    pulses = [p for p in await asyncio.gather(*(market.pulse(s, l) for s, l in targets)) if p]

    for p in pulses:
        text = (f"{p['label']}: 1y {p['ret_1y_pct']:+.1f}% · 3m {p['ret_3m_pct']:+.1f}% "
                f"· volatility {p['volatility_pct']:.0f}%")
        await ctx.emit.claim(aid, text, source={"url": p["source_url"], "name": "Yahoo Finance"},
                             confidence=0.85)
        ctx.state.evidence.append({"text": f"MARKET: {text}", "source": {"url": p["source_url"]},
                                   "agent": aid})
    kind = "ok" if pulses else "warn"
    await ctx.emit.log(aid, f"{len(pulses)} live market series on the board" if pulses
                       else "market data unreachable — continuing", kind)
    await ctx.finish(aid, layer, {"pulses": pulses})


# ── L1: macro data (t0 — official series, no LLM) ────────────────────────────

async def macro_data(ctx: Ctx) -> None:
    aid, layer = "macro_data", "L1"
    await ctx.start(aid, layer)
    geo = ctx.state.brief.get("geography", "India")
    await ctx.emit.log(aid, f"⌕ world bank: {geo} macro series", "code")
    rows = await macro.series(geo)
    for r in rows:
        text = f"{r['name']}: {r['value']} ({r['year']}, {r['country']})"
        await ctx.emit.claim(aid, text, source={"url": r["source_url"], "name": "World Bank"},
                             confidence=0.9)
        ctx.state.evidence.append({"text": f"MACRO: {text}", "source": {"url": r["source_url"]},
                                   "agent": aid})
    kind = "ok" if rows else "warn"
    await ctx.emit.log(aid, f"{len(rows)} official macro indicators captured" if rows
                       else "world bank unreachable — continuing", kind)
    await ctx.finish(aid, layer, {"series": rows})


# ── L1: document analyst (uploads → the evidence board) ──────────────────────

async def doc_analyst(ctx: Ctx) -> None:
    aid, layer = "doc_analyst", "L1"
    docs = [d for d in (ctx.state.raw.get("documents") or [])
            if isinstance(d, dict) and (d.get("text") or "").strip()]
    if not docs:
        return  # nothing uploaded — agent silently stands down
    await ctx.start(aid, layer)
    total_chunks = 0
    for d in docs[:3]:
        name = str(d.get("name") or "document")[:60]
        text = str(d["text"])[:20000]
        await ctx.emit.log(aid, f"reading {name} · {len(text):,} chars", "code")
        # coarse chunks straight onto the shared board — every agent sees them
        chunks = [text[i:i + 700] for i in range(0, min(len(text), 5600), 700)]
        for ch in chunks:
            ctx.state.evidence.append({"text": f"DOC[{name}]: {ch[:300]}",
                                       "source": {"name": name}, "agent": aid})
        total_chunks += len(chunks)
        schema = '{"key_facts": [str x3 (figures/clauses/claims worth flagging)], "doc_type": str}'
        data, res = await ctx.llm.structured(
            "t2",
            "You extract the decision-relevant facts from a business document. Only facts present "
            "in the text; include figures verbatim.",
            f"DOCUMENT ({name}), first pages:\n{text[:6000]}", schema, max_tokens=500, agent=aid)
        if data and isinstance(data.get("key_facts"), list):
            await ctx.emit.usage(aid, res.tokens, res.route)
            for fact in data["key_facts"][:3]:
                await ctx.emit.claim(aid, f"{name}: {fact}", source={"name": name}, confidence=0.75)
                ctx.state.evidence.append({"text": f"DOC-FACT[{name}]: {fact}",
                                           "source": {"name": name}, "agent": aid})
        else:
            await ctx.emit.log(aid, "LLM unavailable — raw chunks on the board without extraction", "warn")
    await ctx.emit.log(aid, f"{total_chunks} chunks from {len(docs)} document(s) now ground every agent", "ok")
    await ctx.finish(aid, layer, {"documents": [d.get("name") for d in docs], "chunks": total_chunks})


# ── L2 helper: scored analysis via LLM with deterministic fallback ────────────

_ANALYSIS_SCHEMA = ('{"verdict_line": str, "score": float (0-10), "confidence": float (0-1), '
                    '"analysis": str (<=200 words, specific), '
                    '"key_insights": [str x2 (non-obvious, each <=25 words — the things a paying '
                    'client underlines)], '
                    '"what_would_change": str (<=20 words: what evidence would flip your score), '
                    '"assumptions": [str], "numbers_used": '
                    '[{"figure": str, "source": "url or ESTIMATE"}]}')

# each domain agent's research sub-agent: a targeted live query template.
# {industry}/{geo}/{city}/{summary} are filled from the brief at run time.
_RESEARCH_Q: dict[str, str] = {
    "market_analyst": "{industry} market size growth {geo}",
    "competitor_intel": "{industry} top competitors funding {geo}",
    "gtm_distribution": "{industry} customer acquisition channels {geo}",
    "legal": "{industry} legal requirements business {geo}",
    "tax": "{industry} GST tax treatment {geo}",
    "policy_compliance": "{industry} regulations licence requirements {geo}",
    "industry_expert": "{industry} industry benchmarks margins {geo}",
    "business_model": "{industry} business model unit economics",
    "marketing_strategy": "{industry} marketing CAC benchmarks {geo}",
    "subsidies_schemes": "{industry} government scheme subsidy startup {geo}",
    "hr_talent": "{industry} startup salary benchmarks {geo}",
    "optimization_predictor": "{industry} tax structure optimization {geo}",
    "regulator": "{industry} regulator enforcement news {geo}",
    "macroeconomist": "{geo} economic outlook interest rates 2026",
    "geopolitics": "{industry} supply chain geopolitics risk",
    "intl_markets": "{industry} international expansion exports {geo}",
    "trends": "{industry} emerging trends 2026",
    "esg_impact": "{industry} sustainability ESG {geo}",
    "stock_analyst": "{summary} outlook analysis",
    "fund_analyst": "{industry} sector mutual funds performance",
    "debt_banking": "loan interest rates {geo} 2026",
    "real_estate": "{city} property prices rent trends 2026",
    "location_scout": "{city} government schemes business opportunities",
    "consumer_analysis": "{industry} consumer behaviour survey {geo}",
    "human_behaviour": "{industry} customer psychology buying triggers",
    "human_needs": "{industry} customer pain points unmet needs",
    "production_ops": "{industry} manufacturing supply chain costs {geo}",
    "philanthropy_impact": "{industry} social impact CSR {geo}",
}


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return ""


# ── the agent-to-agent affinity map (A2A) ──────────────────────────────────────
# Which colleagues' findings each agent should read and build on. The graph runs
# "foundational" analysts first, then "integrative" ones, so these peers already
# have outputs on the board when an integrative agent reads them. This is what
# makes experts talk to EACH OTHER, not just to the common crucible/synthesis.
PEERS: dict[str, list[str]] = {
    # foundational cross-talk (light)
    "competitor_intel": ["market_analyst", "market_research"],
    "industry_expert": ["market_analyst", "macroeconomist"],
    "consumer_analysis": ["human_behaviour", "market_research"],
    "market_research": ["market_analyst", "competitor_intel"],
    # integrative agents synthesize the foundational ones
    "business_model": ["market_analyst", "market_research", "finance_modeler", "competitor_intel", "consumer_analysis"],
    "marketing_strategy": ["consumer_analysis", "competitor_intel", "market_research", "human_behaviour"],
    "gtm_distribution": ["market_analyst", "consumer_analysis", "competitor_intel", "marketing_strategy"],
    "hr_talent": ["finance_modeler", "industry_expert", "business_model"],
    "production_ops": ["industry_expert", "finance_modeler", "business_model"],
    "subsidies_schemes": ["finance_modeler", "policy_compliance", "banking"],
    "banking": ["finance_modeler", "subsidies_schemes", "tax", "business_model"],
    "optimization_predictor": ["tax", "legal", "policy_compliance", "banking"],
    "regulator": ["policy_compliance", "legal"],
    "trends": ["market_research", "macroeconomist", "consumer_analysis"],
    "geopolitics": ["macroeconomist", "intl_markets", "production_ops"],
    "intl_markets": ["market_analyst", "competitor_intel", "industry_expert"],
    "esg_impact": ["production_ops", "philosophy_ethics", "consumer_analysis"],
    "human_needs": ["consumer_analysis", "human_behaviour"],
    "money_happiness": ["finance_modeler", "human_needs"],
    "philosophy_ethics": ["human_behaviour", "consumer_analysis", "esg_impact"],
    "philanthropy_impact": ["esg_impact", "philosophy_ethics"],
    # markets cluster
    "stock_analyst": ["technical_analyst", "macroeconomist"],
    "fund_analyst": ["stock_analyst", "risk_manager"],
    "options_desk": ["technical_analyst", "risk_manager"],
    # wealth cluster
    "fire_planner": ["salary_budget", "portfolio_allocator"],
    "real_estate": ["salary_budget", "debt_banking", "banking"],
    "debt_banking": ["salary_budget", "banking"],
    "location_scout": ["subsidies_schemes"],
}


def _num(value: Any, default: float) -> float:
    """LLM output is untrusted — coerce to float or fall back, never raise."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


async def _scored_analysis(ctx: Ctx, aid: str, system: str, ask: str,
                           fallback: dict[str, Any]) -> dict[str, Any]:
    system_full = (system + " Cite evidence-board items when possible; any uninvented figure "
                   "must be tagged ESTIMATE. Be specific, never generic — think like the one "
                   "specialist in the room who has actually done this before.")
    user_ctx = (ctx.state.raw.get("agent_context") or {}).get(aid, "")

    # ── research sub-agent: a targeted live query just for THIS specialist ──
    research_block = ""
    q_tpl = _RESEARCH_Q.get(aid)
    depth = str(ctx.state.raw.get("depth") or "pulse").lower()
    if q_tpl and (depth != "pulse" or aid in ("market_analyst", "stock_analyst")):
        b = ctx.state.brief
        q = " ".join(q_tpl.format_map(_SafeDict(
            industry=b.get("industry", ""), geo=b.get("geography", ""),
            city=str(ctx.state.raw.get("city") or b.get("geography", "")),
            summary=str(b.get("summary", ""))[:60])).split())
        await ctx.emit.log(aid, f"└ research sub-agent ⌕ {q}", "muted")
        hits = await web.search(q, 3)
        if hits:
            for h in hits:
                if h.get("url"):
                    ctx.state.evidence.append({"text": f"[{aid}] {h['title']} — {h['snippet'][:160]}",
                                               "source": {"url": h["url"]}, "agent": aid})
            research_block = ("MY SUB-AGENT'S FRESH RESEARCH (cite these):\n"
                              + "\n".join(f"- {h['title']}: {h['snippet'][:140]}" for h in hits) + "\n")
            await ctx.emit.log(aid, f"└ sub-agent returned {len(hits)} sources", "muted")

    # ── A2A: pull in colleagues' findings this agent should build on ──────
    peer_block = ""
    peer_ids = PEERS.get(aid, [])
    if peer_ids:
        got = []
        peer_lines = []
        for pid in peer_ids:
            po = ctx.state.outputs.get(pid)
            if isinstance(po, dict) and po.get("verdict_line"):
                got.append(pid)
                extra = ""
                ki = po.get("key_insights")
                if isinstance(ki, list) and ki:
                    extra = f" · {ki[0]}"
                peer_lines.append(f"- {pid} found: {po['verdict_line']}{extra}")
        if peer_lines:
            peer_block = ("YOUR COLLEAGUES ON THE BOARD ALREADY REPORTED (build on, reconcile or "
                          "push back on these — do not just repeat them):\n" + "\n".join(peer_lines) + "\n")
            await ctx.emit.log(aid, f"└ building on colleagues: {', '.join(got)}", "muted")
            await ctx.emit.collab(aid, got)

    user_full = (f"BRIEF: {ctx.state.brief}\nPROFILE: {ctx.state.profile}\n"
                 + (f"USER'S DIRECT BRIEF TO YOU: {str(user_ctx)[:500]}\n" if user_ctx else "")
                 + peer_block + research_block
                 + f"EVIDENCE BOARD:\n{ctx.state.evidence_digest(14)}\n\nTASK: {ask}")
    if user_ctx:
        await ctx.emit.log(aid, f"user brief → me: {str(user_ctx)[:90]}", "muted")
    await ctx.emit.prompt(aid, system_full, user_full)   # glass box: show the exact prompt
    data, res = await ctx.llm.structured(
        "t2", system_full, user_full, _ANALYSIS_SCHEMA, max_tokens=900, agent=aid,
    )
    if data and isinstance(data.get("score"), (int, float)):
        for k, v in fallback.items():          # partial LLM output inherits fallback keys
            data.setdefault(k, v)
        data["score"] = max(0.0, min(10.0, _num(data["score"], 5.0)))
        data["confidence"] = max(0.05, min(0.95, _num(data.get("confidence"), 0.5)))
        data["route"] = res.route
        data["degraded"] = False
        await ctx.emit.log(aid, f"analysis via {res.route}", "ok")
        await ctx.emit.usage(aid, res.tokens, res.route)
        return data
    await ctx.emit.log(aid, "LLM unavailable — deterministic core only (reduced depth)", "warn")
    fallback["degraded"] = True
    fallback["degraded_reason"] = ("No LLM answered this agent — every configured key was rate-limited "
                                   "or missing. Add more API keys (the studio takes up to 16 per provider) "
                                   "so the whole board gets narrated.")
    fallback.setdefault("route", "deterministic")
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
    # deterministic core → What-If simulator (client re-runs this math live)
    await ctx.emit.partial("finance_core", {"capital_lakhs": capital_l, "burn_lakhs_pm": burn_l,
                                            "runway_months": runway, "team": team})
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
        schema, max_tokens=800, agent=aid,
    )
    if data:
        # untrusted LLM shape: attacks must be dicts, severity numeric
        data["attacks"] = [a for a in data.get("attacks") or [] if isinstance(a, dict)]
    if not data or not data["attacks"]:
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
        sev = _num(atk.get("severity"), 0.5)
        await ctx.emit.log(aid, f"⚔ [{atk.get('target_agent','?')}] {atk.get('attack','')}", "err" if sev > 0.6 else "warn")
        await ctx.emit.conflict(aid, atk.get("target_agent", "?"), atk.get("attack", "")[:80])
        ctx.state.conflicts.append(atk)
    await ctx.emit.claim(aid, f"Kill risk: {data.get('kill_risk','')}", confidence=0.6)
    await ctx.finish(aid, layer, data)


# ── L3: fact checker ──────────────────────────────────────────────────────────

def _overlap(claim: str, evidence_texts: list[str]) -> float:
    """Cheap lexical support score: shared significant words / claim words."""
    words = {w for w in re.findall(r"[a-z]{5,}", claim.lower())}
    if not words:
        return 0.0
    best = 0.0
    for ev in evidence_texts:
        ev_words = set(re.findall(r"[a-z]{5,}", ev.lower()))
        best = max(best, len(words & ev_words) / len(words))
    return best


async def fact_checker(ctx: Ctx) -> None:
    aid, layer = "fact_checker", "L3"
    await ctx.start(aid, layer)
    await ctx.emit.log(aid, "mandate: every analyst claim must trace to the evidence board", "muted")

    # deterministic core: numbers audit + lexical support screen
    claims: list[str] = []
    estimates = sourced = 0
    for agent_id in ("market_analyst", "finance_modeler"):
        out = ctx.state.outputs.get(agent_id, {})
        if out.get("verdict_line"):
            claims.append(f"[{agent_id}] {out['verdict_line']}")
        for n in out.get("numbers_used", []) or []:
            if isinstance(n, dict) and str(n.get("source", "")).startswith("http"):
                sourced += 1
            else:
                estimates += 1
    ev_texts = [e["text"] for e in ctx.state.evidence]
    det_checks = [{"claim": c, "verdict": "supported" if _overlap(c, ev_texts) >= 0.25 else "unverified",
                   "note": "lexical screen vs evidence board"} for c in claims]

    schema = ('{"checks": [{"claim": str, "verdict": "supported"|"partly"|"unsupported"|"contradicted", '
              '"note": str (<=25 words)}]}')
    data, res = await ctx.llm.structured(
        "t2",
        "You are a fact checker. For each analyst claim, judge ONLY from the evidence provided — "
        "supported / partly / unsupported / contradicted. Never assume outside knowledge.",
        f"EVIDENCE BOARD:\n{ctx.state.evidence_digest(20)}\n\nCLAIMS:\n" + "\n".join(claims),
        schema, max_tokens=700, agent=aid,
    )
    checks = data.get("checks") if data else None
    if checks and isinstance(checks, list):
        checks = [c for c in checks if isinstance(c, dict)][:8]
        await ctx.emit.usage(aid, res.tokens, res.route)
    else:
        checks = det_checks
        await ctx.emit.log(aid, "LLM unavailable — lexical support screen only", "warn")

    bad = 0
    for c in checks:
        v = str(c.get("verdict", "unverified"))
        kind = "ok" if v == "supported" else "warn" if v in ("partly", "unverified") else "err"
        if v in ("unsupported", "contradicted"):
            bad += 1
        await ctx.emit.log(aid, f"[{v.upper()}] {str(c.get('claim',''))[:110]}", kind)
    await ctx.emit.log(aid, f"numbers audit: {sourced} sourced · {estimates} estimates", "code")
    await ctx.emit.claim(aid, f"Fact check: {len(checks)} claims reviewed, {bad} unsupported/contradicted, "
                              f"{estimates} unsourced figures flagged", confidence=0.7)
    await ctx.finish(aid, layer, {"checks": checks, "unsupported": bad,
                                  "numbers": {"sourced": sourced, "estimates": estimates}})


# ── L3: bias auditor ──────────────────────────────────────────────────────────
# Detection table ported (inverted: exploit → detect) from the legacy
# human_behaviour_agent bias database, extended with founder-specific biases.

_BIAS_SCREENS: list[tuple[str, str, str]] = [
    ("optimism bias", r"\b(definitely|surely|can'?t fail|guaranteed|everyone (will|wants)|huge market|no competition)\b",
     "Absolute language about uncertain outcomes — the base rate for new ventures disagrees."),
    ("confirmation bias", r"\b(i know|i'?m (sure|certain)|clearly|obviously|proves?)\b",
     "Certainty phrasing suggests seeking confirmation, not tests that could falsify the idea."),
    ("social proof", r"\b(everyone is doing|trending|hot right now|all my friends|viral)\b",
     "Popularity of a category is weak evidence of *your* unit economics."),
    ("sunk cost", r"\b(already (spent|built|invested|quit)|too far in|can'?t stop now)\b",
     "Past investment is not a reason to continue — only forward returns are."),
    ("scarcity/FOMO", r"\b(before it'?s too late|now or never|window is closing|last chance|miss out)\b",
     "Urgency framing short-circuits diligence; real windows rarely close in one quarter."),
    ("overconfidence", r"\b(easily|just need to|simple to|piece of cake|quickly capture|only \d+%)\b",
     "'Only 1% of the market' math and 'just' plans underestimate execution cost."),
    ("planning fallacy", r"\b(in (a|one|two|2|3|three) (week|month)s?\b|within \d+ (day|week)s)\b",
     "Timelines this tight are usually best-case; median outcomes run 2-3× longer."),
    ("authority bias", r"\b(guru|influencer said|billionaire|famous investor|podcast said)\b",
     "Advice from status, not from evidence about this specific market."),
]


async def bias_auditor(ctx: Ctx) -> None:
    aid, layer = "bias_auditor", "L3"
    await ctx.start(aid, layer)
    await ctx.emit.log(aid, "auditing the FRAMING, not the idea (Constitution: disagreement is data)", "muted")
    raw = ctx.state.raw
    framing = f"{raw.get('situation','')} {raw.get('uncertainty','')}"

    findings: list[dict[str, Any]] = []
    for bias, pattern, note in _BIAS_SCREENS:
        m = re.search(pattern, framing, re.I)
        if m:
            findings.append({"bias": bias, "quote": m.group(0), "note": note, "severity": 0.5})

    schema = ('{"biases": [{"bias": str, "quote": str (verbatim from the text), '
              '"note": str (<=25 words, specific), "severity": float (0-1)}]}')
    data, res = await ctx.llm.structured(
        "t3",
        "You are a cognitive-bias auditor for decision-making. Identify biases IN THE FOUNDER'S OWN "
        "FRAMING of their situation (not in the idea itself). Only report biases with a verbatim quote "
        "as evidence. Empty list if the framing is clean.",
        f"FOUNDER'S FRAMING:\n{framing[:1200]}\n\nPROFILE: {ctx.state.profile}",
        schema, max_tokens=600, agent=aid,
    )
    if data and isinstance(data.get("biases"), list):
        llm_findings = [b for b in data["biases"] if isinstance(b, dict) and b.get("bias")][:5]
        seen = {f["bias"] for f in findings}
        findings += [b for b in llm_findings if b.get("bias") not in seen]
        await ctx.emit.usage(aid, res.tokens, res.route)
    elif not findings:
        await ctx.emit.log(aid, "LLM unavailable — pattern screen found no flagrant bias markers", "info")

    for f in findings[:6]:
        await ctx.emit.bias("user_framing", f["bias"], f'"{str(f.get("quote",""))[:60]}" — {f.get("note","")}')
        await ctx.emit.log(aid, f"⚑ {f['bias']}: {str(f.get('quote',''))[:60]}", "warn")
    if not findings:
        await ctx.emit.log(aid, "no significant bias markers in your framing — rare, well done", "ok")
    await ctx.finish(aid, layer, {"findings": findings[:6]})


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
        return sum(_num(a.get("severity"), 0.5) for a in attacks if a.get("target_agent") == target) * 0.8

    evidence_quality = min(1.0, len(ctx.state.evidence) / 12.0)

    # Evidence dimension: coverage minus fact-check failures (Phase 2)
    fc = o.get("fact_checker", {})
    unsupported = int(_num(fc.get("unsupported"), 0))
    evidence_dim = max(0.5, evidence_quality * 10 - unsupported * 1.2)

    # Timing dimension: real macro + market pulse instead of the old 5.0 placeholder
    timing = 5.0
    for row in (o.get("macro_data", {}).get("series") or []):
        v = _num(row.get("value"), 0.0)
        if row.get("indicator") == "NY.GDP.MKTP.KD.ZG":
            timing += 1.0 if v >= 6.5 else 0.5 if v >= 4.0 else -1.0 if v < 2.5 else 0.0
        elif row.get("indicator") == "FP.CPI.TOTL.ZG":
            timing += 0.5 if v <= 4.0 else -1.0 if v >= 7.0 else 0.0
    pulses = o.get("market_data", {}).get("pulses") or []
    if pulses:
        idx = _num(pulses[0].get("ret_1y_pct"), 0.0)
        timing += 1.0 if idx >= 12 else 0.5 if idx >= 5 else -1.0 if idx < 0 else 0.0
        if len(pulses) > 1:
            sec = _num(pulses[1].get("ret_1y_pct"), 0.0)
            timing += 0.5 if sec >= 15 else -0.5 if sec <= -10 else 0.0
        await ctx.emit.log(aid, f"timing inputs: index 1y {idx:+.1f}% · macro series {len(o.get('macro_data', {}).get('series') or [])}", "code")

    def avg(agent_ids: list[str]) -> float | None:
        """Mean of available agent scores, each less its red-team penalty."""
        vals = [max(0.5, float(o[i]["score"]) - penalty(i)) for i in agent_ids
                if isinstance(o.get(i), dict) and isinstance(o[i].get("score"), (int, float))]
        return sum(vals) / len(vals) if vals else None

    dims = {
        "Market": avg(["market_analyst", "market_research", "competitor_intel", "industry_expert",
                       "trends", "consumer_analysis"]) or 5.0,
        "Economics": avg(["finance_modeler", "tax", "subsidies_schemes", "banking"]) or 5.0,
        "Evidence": evidence_dim,
        "Execution": avg(["gtm_distribution", "business_model", "marketing_strategy",
                          "hr_talent", "production_ops"]) or 5.0,
        "Timing": max(1.0, min(9.5, timing)),
    }
    regulatory = avg(["policy_compliance", "legal", "regulator"])
    if regulatory is not None:
        dims["Regulatory"] = regulatory
    # the human layer gets its own axis — does this fit the human, not just the market
    human_fit = avg(["human_behaviour", "human_needs", "money_happiness",
                     "philosophy_ethics", "philanthropy_impact"])
    if human_fit is not None:
        dims["HumanFit"] = human_fit
    dims = {k: round(min(10.0, v), 1) for k, v in dims.items()}
    ctx.state.dimensions = dims

    # base weights, renormalized over whichever dimensions this depth produced
    # (client What-If mirrors this — keep sim-charts.tsx weightsFor() in sync)
    base_w = {"Market": 0.25, "Economics": 0.25, "Evidence": 0.10, "Execution": 0.125,
              "Timing": 0.15, "Regulatory": 0.125, "HumanFit": 0.12}
    weights = {k: base_w[k] for k in dims if k in base_w}
    total_w = sum(weights.values()) or 1.0
    weights = {k: v / total_w for k, v in weights.items()}
    overall = round(sum(dims[k] * w for k, w in weights.items()), 1)

    conf_spread = abs(_num(market.get("confidence"), 0.5) - _num(fin.get("confidence"), 0.5))
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
    # compact context — full outputs blow past cheap-tier TPM limits (observed on Groq free tier)
    compact: dict[str, Any] = {}
    for k, out in ctx.state.outputs.items():
        if k in ("weighing_engine", "verdict_composer") or not isinstance(out, dict):
            continue
        c = {kk: out[kk] for kk in ("verdict_line", "score", "confidence", "kill_risk", "unsupported") if kk in out}
        if out.get("assumptions"):
            c["assumptions"] = out["assumptions"][:2]
        if isinstance(out.get("findings"), list):  # bias auditor (web_researcher's is an int)
            c["biases"] = [f.get("bias") for f in out["findings"] if isinstance(f, dict)][:5]
        if c:
            compact[k] = c
    data, res = await ctx.llm.structured(
        "t3",
        "You compose the final decision document for an entrepreneur. Honest, specific, calibrated to their "
        "profile. You may NOT change the numeric verdict — it is computed deterministically.",
        f"BRIEF: {ctx.state.brief}\nPROFILE: {ctx.state.profile}\n"
        f"DIMENSIONS: {ctx.state.dimensions} → overall {overall}/10 (band {band})\n"
        f"ANALYST SUMMARIES: {compact}\n"
        f"RED TEAM ATTACKS: {[{'target': a.get('target_agent'), 'attack': str(a.get('attack',''))[:140], 'severity': a.get('severity')} for a in ctx.state.conflicts[:4]]}\n"
        f"EVIDENCE:\n{ctx.state.evidence_digest(10)}",
        _VERDICT_SCHEMA, max_tokens=1100, agent=aid,
    )
    if data:
        data["recommendation"] = data.get("recommendation") or band
        await ctx.emit.usage(aid, res.tokens, res.route)
    else:
        data = fallback
        data["degraded"] = True
        await ctx.emit.log(aid, "LLM unavailable — deterministic verdict document", "warn")

    verdict = {"score": overall, "band": band, "dimensions": ctx.state.dimensions, **data}
    ctx.state.verdict = verdict
    await ctx.emit.log(aid, f"VERDICT: {verdict['recommendation']} · {overall}/10", "ok")
    await ctx.emit.partial("verdict", verdict)
    await ctx.finish(aid, layer, verdict)
