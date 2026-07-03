"""Phase-7 wealth cluster — the money-management board (Wealth mode).

Deterministic money math first (budgeting ratios, allocation glide paths,
FIRE arithmetic), LLM narrative on top. Same constitution: sourced or
ESTIMATE-flagged figures, education not advice, the human decides.
"""
from __future__ import annotations

from typing import Any

from .base import Ctx
from .venture import _num, _scored_analysis

# ── L2: salary & budget (t0 core) ────────────────────────────────────────────

async def salary_budget(ctx: Ctx) -> None:
    aid, layer = "salary_budget", "L2"
    await ctx.start(aid, layer)
    raw = ctx.state.raw
    income = _num(raw.get("monthly_income"), 80000.0)
    expenses = _num(raw.get("monthly_expenses"), 50000.0)
    savings_rate = max(0.0, (income - expenses) / income * 100) if income > 0 else 0.0
    # 50/30/20 benchmark
    needs_cap, wants_cap, save_floor = income * 0.5, income * 0.3, income * 0.2
    await ctx.emit.log(aid, "no LLM in this stage — budgeting math only", "muted")
    await ctx.emit.log(aid, f"income ₹{income:,.0f} · expenses ₹{expenses:,.0f} · savings rate {savings_rate:.0f}%", "code")
    await ctx.emit.log(aid, f"50/30/20 benchmark: needs ≤₹{needs_cap:,.0f} · wants ≤₹{wants_cap:,.0f} · save ≥₹{save_floor:,.0f}", "code")
    verdict = ("excellent" if savings_rate >= 30 else "healthy" if savings_rate >= 20
               else "thin" if savings_rate >= 10 else "critical")
    score = min(9.5, max(1.0, savings_rate / 4))
    await ctx.emit.claim(aid, f"Savings rate {savings_rate:.0f}% — {verdict} "
                              f"(benchmark: 20%+ sustainable, 30%+ wealth-building)", confidence=0.85)
    await ctx.finish(aid, layer, {
        "verdict_line": f"savings rate {savings_rate:.0f}% ({verdict})",
        "score": round(score, 1), "confidence": 0.85,
        "monthly_surplus": round(income - expenses, 0), "savings_rate": round(savings_rate, 1),
        "analysis": f"₹{income - expenses:,.0f}/month surplus. 50/30/20 rule: needs ₹{needs_cap:,.0f}, "
                    f"wants ₹{wants_cap:,.0f}, savings floor ₹{save_floor:,.0f}.",
    })


# ── L2: portfolio allocator (t0 core) ────────────────────────────────────────

async def portfolio_allocator(ctx: Ctx) -> None:
    aid, layer = "portfolio_allocator", "L2"
    await ctx.start(aid, layer)
    raw = ctx.state.raw
    age = int(_num(raw.get("age"), 30))
    risk = (raw.get("risk_appetite") or "moderate").lower()
    # age-based glide path with risk tilt
    equity = max(20, min(90, (110 - age) + (10 if risk == "aggressive" else -10 if risk == "conservative" else 0)))
    debt = max(5, 90 - equity)
    gold = 5
    emergency = _num(raw.get("monthly_expenses"), 50000.0) * 6
    await ctx.emit.log(aid, "no LLM in this stage — allocation glide-path math only", "muted")
    await ctx.emit.log(aid, f"age {age} · {risk} → equity {equity}% · debt {debt}% · gold {gold}%", "code")
    await ctx.emit.log(aid, f"emergency fund first: 6 months ≈ ₹{emergency:,.0f} in liquid funds [ESTIMATE]", "info")
    await ctx.emit.claim(aid, f"Benchmark allocation for a {age}-year-old {risk} investor: "
                              f"{equity}% equity / {debt}% debt / {gold}% gold — after a "
                              f"₹{emergency:,.0f} emergency fund", confidence=0.8)
    await ctx.finish(aid, layer, {
        "verdict_line": f"{equity}/{debt}/{gold} equity-debt-gold glide path",
        "score": 7.0, "confidence": 0.8,
        "allocation": {"equity_pct": equity, "debt_pct": debt, "gold_pct": gold},
        "emergency_fund": round(emergency, 0),
        "analysis": "Index-first equity (low-cost), duration-matched debt, gold as inflation hedge. "
                    "Rebalance yearly; allocation is a starting benchmark, not advice.",
    })


# ── L2: FIRE / goal planner (t0 core) ────────────────────────────────────────

async def fire_planner(ctx: Ctx) -> None:
    aid, layer = "fire_planner", "L2"
    await ctx.start(aid, layer)
    raw = ctx.state.raw
    expenses_m = _num(raw.get("monthly_expenses"), 50000.0)
    income_m = _num(raw.get("monthly_income"), 80000.0)
    savings = _num(raw.get("current_savings"), 500000.0)
    fire_number = expenses_m * 12 * 25          # 4% rule
    surplus = max(0.0, income_m - expenses_m)
    # years to FIRE at 11% nominal (Indian equity long-run ESTIMATE), 6% inflation → ~5% real
    r = 0.05 / 12
    months = 0
    corpus = savings
    while corpus < fire_number and months < 720:
        corpus = corpus * (1 + r) + surplus
        months += 1
    years = months / 12
    await ctx.emit.log(aid, "no LLM in this stage — 4%-rule arithmetic only", "muted")
    await ctx.emit.log(aid, f"FIRE number = 25 × annual expenses ≈ ₹{fire_number:,.0f} [ESTIMATE: 4% rule]", "code")
    await ctx.emit.log(aid, f"at ₹{surplus:,.0f}/mo invested (5% real): ~{years:.1f} years to FIRE", "code")
    score = max(1.0, min(9.5, 10 - years / 4))
    await ctx.emit.claim(aid, f"Financial independence ≈ ₹{fire_number:,.0f}; on the current surplus "
                              f"that is ~{years:.0f} years away (real-return estimate)", confidence=0.7)
    await ctx.finish(aid, layer, {
        "verdict_line": f"FIRE ≈ ₹{fire_number / 1e7:.2f}Cr · ~{years:.0f} years at current surplus",
        "score": round(score, 1), "confidence": 0.7,
        "fire_number": round(fire_number, 0), "years_to_fire": round(years, 1),
        "analysis": "4% withdrawal rule with 5% real return assumption. Every ₹10k/month more surplus "
                    "pulls the date years closer — the savings rate is the lever, not returns.",
    })


# ── L2: debt & banking (t2) ───────────────────────────────────────────────────

async def debt_banking(ctx: Ctx) -> None:
    aid, layer = "debt_banking", "L2"
    await ctx.start(aid, layer)
    fallback = {
        "verdict_line": "Debt hygiene checklist applied — details need a model",
        "score": 6.0, "confidence": 0.3,
        "analysis": "Order of operations: kill >12% debt first (credit cards, personal loans), "
                    "keep one rewards card fully paid, ladder FDs for near-term goals.",
        "assumptions": ["No high-interest debt unless stated"], "numbers_used": [],
    }
    out = await _scored_analysis(
        ctx, aid,
        "You are a personal-banking and debt strategist (India-first: home/auto/personal loans, "
        "credit cards, FDs, PPF/EPF).",
        "From the profile, lay out the debt-and-banking posture: what to pay off first and why, what "
        "credit is healthy, one banking optimization. Score 0-10 for debt health (10 = clean).", fallback)
    await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
    await ctx.finish(aid, layer, out)


# ── L2: real estate (t2) ──────────────────────────────────────────────────────

async def real_estate(ctx: Ctx) -> None:
    aid, layer = "real_estate", "L2"
    await ctx.start(aid, layer)
    fallback = {
        "verdict_line": "Rent-vs-buy needs city data — price-to-rent heuristic applied",
        "score": 5.0, "confidence": 0.3,
        "analysis": "Rule of thumb: price-to-annual-rent >25 favours renting + investing the difference; "
                    "REITs give property exposure without concentration risk.",
        "assumptions": ["Metro-India price-to-rent ratios 30-45 [ESTIMATE]"], "numbers_used": [],
    }
    out = await _scored_analysis(
        ctx, aid,
        "You are a real-estate analyst (India-first): rent-vs-buy math, REITs, city micro-markets.",
        "Given the profile and city, assess: rent vs buy for them now, REIT alternative, one timing "
        "consideration from the evidence. Score 0-10 for how favourable property is for THIS person now.",
        fallback)
    await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
    await ctx.finish(aid, layer, out)


# ── L2: location opportunity scout (t2) ──────────────────────────────────────

async def location_scout(ctx: Ctx) -> None:
    aid, layer = "location_scout", "L2"
    await ctx.start(aid, layer)
    city = ctx.state.raw.get("city") or ctx.state.brief.get("geography", "India")
    fallback = {
        "verdict_line": f"Location scan for {city} needs a model — evidence-board signals only",
        "score": 5.0, "confidence": 0.25,
        "analysis": "Add a key/model for city-specific schemes, costs and opportunities.",
        "assumptions": [], "numbers_used": [],
    }
    out = await _scored_analysis(
        ctx, aid,
        f"You are a local-opportunity scout for {city}. Government schemes, cost of living arbitrage, "
        "local market gaps, side-income opportunities appropriate to the person's profile.",
        f"For someone in {city} with this profile, surface: one scheme/subsidy they likely qualify for, "
        "one local money opportunity, one cost arbitrage. Score 0-10 for location advantage.", fallback)
    await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
    await ctx.finish(aid, layer, out)


WEALTH_AGENTS = {
    "salary_budget": salary_budget,
    "portfolio_allocator": portfolio_allocator,
    "fire_planner": fire_planner,
    "debt_banking": debt_banking,
    "real_estate": real_estate,
    "location_scout": location_scout,
}


# ── L4: wealth weighing (t0) ──────────────────────────────────────────────────

async def weighing_wealth(ctx: Ctx) -> None:
    aid, layer = "weighing_engine", "L4"
    await ctx.start(aid, layer)
    await ctx.emit.log(aid, "no LLM in this stage — weighted money math only", "muted")
    o = ctx.state.outputs

    def sc(k: str, d: float = 5.0) -> float:
        out = o.get(k, {})
        return max(0.5, _num(out.get("score"), d))

    dims = {
        "Cashflow": sc("salary_budget"),
        "Allocation": sc("portfolio_allocator"),
        "GoalFit": sc("fire_planner"),
        "DebtHealth": sc("debt_banking"),
        "Opportunity": (sc("real_estate") + sc("location_scout")) / 2,
    }
    dims = {k: round(min(10.0, v), 1) for k, v in dims.items()}
    ctx.state.dimensions = dims
    weights = {"Cashflow": 0.3, "Allocation": 0.2, "GoalFit": 0.25, "DebtHealth": 0.15, "Opportunity": 0.1}
    overall = round(sum(dims[k] * w for k, w in weights.items()), 1)
    for k, v in dims.items():
        await ctx.emit.log(aid, f"{k:<11} {v}/10", "code")
    await ctx.emit.partial("radar", {"dimensions": dims, "overall": overall})
    await ctx.finish(aid, layer, {"dimensions": dims, "overall": overall, "dissent": ctx.state.conflicts})


_WEALTH_VERDICT_SCHEMA = (
    '{"recommendation": "ON_TRACK"|"NEEDS_REBALANCING"|"AT_RISK", '
    '"reasoning": str (3 sentences, cite the numbers), "sensitivities": [str x3], '
    '"risks": [{"text": str, "source_agent": str, "severity": float}], '
    '"opportunities": [{"text": str, "source_agent": str}], '
    '"next_steps": [str x5 — concrete money actions this month], '
    '"teach": str (2 sentences: the principle behind the plan)}')


async def verdict_wealth(ctx: Ctx) -> None:
    aid, layer = "verdict_composer", "L4"
    await ctx.start(aid, layer)
    w = ctx.state.outputs.get("weighing_engine", {})
    overall = _num(w.get("overall"), 5.0)
    band = "ON_TRACK" if overall >= 7 else "NEEDS_REBALANCING" if overall >= 4.5 else "AT_RISK"
    compact = {k: v.get("verdict_line") for k, v in ctx.state.outputs.items()
               if isinstance(v, dict) and v.get("verdict_line")}
    fallback = {
        "recommendation": band,
        "reasoning": f"Money health {overall}/10 from deterministic cores. Add a model/key for the full plan.",
        "sensitivities": ["Savings rate", "Return assumptions", "Emergency-fund coverage"],
        "risks": [{"text": a.get("attack", ""), "source_agent": "red_team",
                   "severity": _num(a.get("severity"), 0.5)} for a in ctx.state.conflicts[:4]],
        "opportunities": [],
        "next_steps": ["Automate the savings transfer on salary day", "Build the 6-month emergency fund first",
                       "Move surplus to index SIPs per the allocation", "Kill any >12% interest debt now",
                       "Re-run EIP after any income change"],
        "teach": "Wealth is a savings-rate game compounded by time. The plan matters less than the automation.",
    }
    data, res = await ctx.llm.structured(
        "t3",
        "You compose a personal money-health decision document. Calibrated to the person, concrete, "
        "never guaranteed-return language, never specific security recommendations. You may NOT change "
        "the numeric score.",
        f"PROFILE: {ctx.state.profile}\nDIMENSIONS: {ctx.state.dimensions} → {overall}/10 ({band})\n"
        f"AGENT LINES: {compact}\nEVIDENCE:\n{ctx.state.evidence_digest(10)}",
        _WEALTH_VERDICT_SCHEMA, max_tokens=1000, agent=aid,
    )
    if data:
        data["recommendation"] = data.get("recommendation") or band
        for k, v in fallback.items():
            data.setdefault(k, v)
        await ctx.emit.usage(aid, res.tokens, res.route)
    else:
        data = fallback
        await ctx.emit.log(aid, "LLM unavailable — deterministic verdict document", "warn")
    verdict = {"score": overall, "band": band, "dimensions": ctx.state.dimensions, **data}
    ctx.state.verdict = verdict
    await ctx.emit.log(aid, f"MONEY HEALTH: {verdict['recommendation']} · {overall}/10", "ok")
    await ctx.emit.partial("verdict", verdict)
    await ctx.finish(aid, layer, verdict)
