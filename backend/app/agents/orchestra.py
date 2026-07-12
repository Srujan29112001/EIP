"""The Advisory Engine orchestration layer — Intelligent Mode's four brains.

🎩 Boss    — conversational intake: a multi-turn dialogue (not a form) distilled
             into the structured Brief. It never advises; it listens and captures.
🎼 Manager — dynamic orchestrator: plans the board for THIS specific brief from
             the whole convocable pool, but always WITHIN the guaranteed spine,
             so coverage is never lost (blueprint: "plan dynamically, spine locked").
✅ QA gate — blocking: fact-check failures, high-severity red-team attacks and
             framing biases become a pass/fail verdict BEFORE the report is
             written; failing agents are re-dispatched once, then weighing and
             verdict re-run. Nothing bad flows downstream silently.
🧑‍⚖️ HITL   — regulated legal/tax/financial content pauses for human review
             before the final deliverable publishes (timeout → explicit
             UNREVIEWED watermark; the stream never dies waiting on a human).
"""
from __future__ import annotations

import asyncio
import re
from typing import Any

from ..core import hitl
from ..core.llm_gateway import Gateway
from .base import Ctx
from .registry import BY_ID, ROSTER

# ═══════════════════════════════════════════════════════════════════════════
# ENGAGEMENT-MODE CLASSIFICATION (Advisory Engine · Diagram 4)
# The Boss classifies every intake into an engagement type; the Manager then
# routes to THAT type's roster + deterministic cores. This is the whole point
# of Intelligent Mode — a trader question and a founder question are different
# jobs and must engage visibly different boards.
# ═══════════════════════════════════════════════════════════════════════════

ENGAGEMENT_MODES = ("founder", "trader", "wealth", "operator")

# operator = scaling an existing company (blueprint's 5th engagement type); it
# runs the venture scaffold + founder dimensions with an ops-weighted roster.
_MODE_LABEL = {"founder": "🚀 Founder", "trader": "📈 Trader",
               "wealth": "💰 Wealth", "operator": "⚙️ Operator"}
_MODE_DESK = {"founder": "validate / build a venture", "trader": "evaluate a stock or position",
              "wealth": "grow / protect personal money", "operator": "scale an existing company"}

_TRADER_HINTS = re.compile(
    r"\b(stocks?|shares?|ticker|nifty|sensex|equit\w*|buy or sell|sell or sell|"
    r"go(ing)? long|short(ing)?|options?|calls?|puts?|futures?|deriv\w*|trade|trading|"
    r"position|entry|exit|breakout|support|resistance|candlestick|rsi|macd|"
    r"reliance|tcs|infosys|hdfc|aapl|tsla|nvda|btc|bitcoin|crypto|etf)\b", re.I)
_WEALTH_HINTS = re.compile(
    r"\b(salary|savings?|budget|retire\w*|fire|financial\s*independ\w*|"
    r"sip|mutual\s*fund|emergency\s*fund|rent\s*vs\s*buy|home\s*loan|emi|"
    r"pay\s*off\s*(my|the)?\s*debt|net\s*worth|corpus|pension|nps|ppf|fixed\s*deposit)\b", re.I)
_OPERATOR_HINTS = re.compile(
    r"\b(scal(e|ing)\s+(up|our|the|my)|our\s+(company|team|operations?|business|factory)|"
    r"we\s+(run|operate|already|have\s+\d)|existing\s+(company|business)|my\s+company|"
    r"headcount|reduce\s+churn|already\s+(launched|running|live|profitable)|"
    r"streamlin\w*|bottleneck|throughput|our\s+customers)\b", re.I)


def _convo_text(payload: dict) -> str:
    text = str(payload.get("situation") or "")
    for m in (payload.get("conversation") or []):
        text += " " + str(m.get("content") or m.get("text") or "")
    return text


def classify_engagement(payload: dict) -> str:
    """founder | trader | wealth | operator. The frontend Boss sends its own
    classification; this trusts a valid one, else re-derives deterministically."""
    given = str(payload.get("engagement_mode") or "").lower().strip()
    if given in ENGAGEMENT_MODES:
        return given
    if str(payload.get("symbol") or "").strip():
        return "trader"
    text = _convo_text(payload)
    if _TRADER_HINTS.search(text):
        return "trader"
    if _WEALTH_HINTS.search(text):
        return "wealth"
    if _OPERATOR_HINTS.search(text):
        return "operator"
    return "founder"


def _to_num(s: Any) -> float:
    try:
        return float(re.sub(r"[^\d.]", "", str(s)) or 0)
    except Exception:
        return 0.0


# ═══════════════════════════════════════════════════════════════════════════
# 🎩 BOSS — conversational intake (POST /api/intake + the pipeline's L0 head)
# ═══════════════════════════════════════════════════════════════════════════

# deterministic question ladder — the Boss still converses with ZERO keys
_BOSS_LADDER: list[tuple[str, str]] = [
    ("situation", "What decision or problem are you actually trying to solve? Tell me the way "
                  "you'd tell a trusted advisor — the real situation, not the polished version."),
    ("industry", "Which industry or space is this in, and where (city / country) will it play out?"),
    ("stage", "Where do things stand today — just an idea, something built, first revenue, or scaling?"),
    ("budget_band", "Roughly what capital can you commit (under ₹10L, ₹10L–1Cr, ₹1Cr+), and who is on the team?"),
    ("success", "Last one: what does success look like in 12 months — and what is the ONE thing "
                "you're most unsure about?"),
]

_BRIEF_FIELDS = ("situation", "industry", "geography", "stage", "budget_band", "team_size",
                 "uncertainty", "target_customer", "competitors", "revenue_model",
                 "success_criteria", "sensitivity", "symbol", "trading_style",
                 "monthly_income", "monthly_expenses")

_BOSS_SCHEMA = ('{"completeness": float (0-1, how complete the brief is), '
                '"engagement_mode": "founder"|"trader"|"wealth"|"operator" (classify the REAL job: '
                'founder=validate/build a venture · trader=evaluate a stock or position · '
                'wealth=grow/protect personal money (salary/savings/retirement) · '
                'operator=scale an EXISTING company), '
                '"next_question": str (ONE question, warm and specific — empty if complete), '
                '"missing": [str (what is still unknown)], '
                '"brief": {"situation": str (the REAL problem in <=80 words), "industry": str, '
                '"geography": str, "stage": str ("ideation"|"validation"|"mvp"|"traction"|"scaling"), '
                '"budget_band": str ("under_10L"|"10L_1Cr"|"1Cr_plus"), "team_size": str, '
                '"uncertainty": str, "target_customer": str, "competitors": str, '
                '"revenue_model": str, "success_criteria": str, '
                '"sensitivity": "public"|"confidential", '
                '"symbol": str (stock ticker — ONLY if trader, else ""), '
                '"trading_style": str (intraday|swing|position — ONLY if trader, else ""), '
                '"monthly_income": str (₹/month number — ONLY if wealth, else ""), '
                '"monthly_expenses": str (₹/month number — ONLY if wealth, else "")}}')


def _transcript(messages: list[dict[str, Any]], limit: int = 16) -> str:
    lines = []
    for m in messages[-limit:]:
        role = "CLIENT" if str(m.get("role", "user")) == "user" else "BOSS"
        text = str(m.get("content") or m.get("text") or "").strip()
        if text:
            lines.append(f"{role}: {text[:500]}")
    return "\n".join(lines)


def _demo_boss(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """Zero-key Boss: walk the deterministic ladder, one question per turn,
    and classify the engagement from keywords (no model needed)."""
    answers = [str(m.get("content") or m.get("text") or "").strip()
               for m in messages if str(m.get("role", "user")) == "user"]
    answers = [a for a in answers if a]
    n = len(answers)
    brief: dict[str, Any] = {"situation": answers[0] if answers else ""}
    mode = classify_engagement({"conversation": messages, "situation": brief["situation"]})
    if n >= 2:
        brief["industry"] = answers[1][:120]
    if n >= 3:
        low = answers[2].lower()
        brief["stage"] = next((s for s in ("ideation", "validation", "mvp", "traction", "scaling")
                               if s in low), "ideation" if "idea" in low else "validation")
    if n >= 4:
        low = answers[3].lower()
        brief["budget_band"] = ("1Cr_plus" if re.search(r"\b(1\s*cr|crore|1cr\+)", low)
                                else "10L_1Cr" if re.search(r"10\s*l|lakh", low) else "under_10L")
        brief["team_size"] = "solo" if "solo" in low or "alone" in low else "small_team"
    if n >= 5:
        brief["uncertainty"] = answers[4][:200]
        brief["success_criteria"] = answers[4][:200]
    complete = n >= len(_BOSS_LADDER)
    return {
        "complete": complete,
        "completeness": round(min(1.0, n / len(_BOSS_LADDER)), 2),
        "engagement_mode": mode,
        "question": "" if complete else _BOSS_LADDER[n][1],
        "missing": [k for k, _ in _BOSS_LADDER[n:]],
        "brief": {**brief, "engagement_mode": mode},
        "route": "deterministic ladder (no model reached)",
        "demo": True,
    }


async def boss_converse(messages: list[dict[str, Any]], llm: Gateway) -> dict[str, Any]:
    """One Boss turn: read the whole conversation so far, return either the
    next clarifying question or the finished Brief. Stateless by design —
    the client resends the transcript (keys are per-run, nothing persists)."""
    transcript = _transcript(messages)
    if not transcript:
        return {"complete": False, "completeness": 0.0, "engagement_mode": "",
                "question": _BOSS_LADDER[0][1],
                "missing": [k for k, _ in _BOSS_LADDER], "brief": {},
                "route": "opening", "demo": False}

    user_turns = sum(1 for m in messages if str(m.get("role", "user")) == "user")
    system = ("You are the Boss 🎩 of an AI advisory board — the ONLY agent that talks to the "
              "client. You NEVER give advice, opinions or analysis. You listen, clarify and "
              "capture. Jobs-to-be-done style: dig for the real problem behind the ask, the "
              "constraints, the success criteria, the risk posture and data sensitivity. "
              "CRUCIALLY: classify the engagement into one of four types — founder (validate or "
              "build a venture), trader (evaluate a stock/position), wealth (grow or protect "
              "personal money), operator (scale an existing company) — because the board that "
              "convenes depends on it. If it's a trader engagement, make sure you capture the "
              "stock/ticker; if wealth, capture monthly income and expenses. Ask exactly ONE "
              "next question at a time — warm, specific, never a form. When the brief is "
              "complete enough to hand to the board (completeness >= 0.75), stop asking and "
              "return the finished brief with next_question empty.")
    data, res = await llm.structured(
        "t3", system,
        f"CONVERSATION SO FAR:\n{transcript}\n\n"
        f"TASK: classify the engagement_mode, score completeness, extract the brief from what "
        f"the client actually said (never invent facts — empty string when unknown), list "
        f"what's still missing, and either ask the single best next question or declare the "
        f"brief complete.",
        _BOSS_SCHEMA, max_tokens=800, agent="boss",
    )
    if not data or not isinstance(data.get("brief"), dict):
        return _demo_boss(messages)

    brief = {k: str(data["brief"].get(k) or "")[:400] for k in _BRIEF_FIELDS}
    em = str(data.get("engagement_mode") or "").lower().strip()
    mode = em if em in ENGAGEMENT_MODES else classify_engagement({"conversation": messages})
    brief["engagement_mode"] = mode
    completeness = max(0.0, min(1.0, float(data.get("completeness") or 0.0)))
    # the Boss keeps asking until the brief is enough — but never traps the
    # client in an interview: after 6 answers it proceeds with the unknowns listed
    complete = (completeness >= 0.75 and user_turns >= 2) or user_turns >= 6
    return {
        "complete": complete,
        "completeness": round(completeness, 2),
        "engagement_mode": mode,
        "question": "" if complete else str(data.get("next_question") or _BOSS_LADDER[-1][1])[:300],
        "missing": [str(x)[:80] for x in (data.get("missing") or [])][:6],
        "brief": brief,
        "route": res.route,
        "demo": False,
    }


async def boss_brief(ctx: Ctx) -> None:
    """Pipeline head: distill the intake conversation into the raw payload so
    the whole L0 chain (parser → profiler → scope) builds on the REAL brief.
    Mode-aware: also lifts the trader ticker / wealth money figures the chosen
    pipeline's deterministic desks need."""
    aid, layer = "boss", "L0"
    mode = classify_engagement(ctx.state.raw)
    ctx.state.raw["engagement_mode"] = mode
    await ctx.emit.stage(aid, "queued", layer)
    await ctx.start(aid, layer)
    convo = ctx.state.raw.get("conversation") or []
    transcript = _transcript(convo)
    await ctx.emit.log(aid, f"engagement classified: {_MODE_LABEL.get(mode, mode)} "
                            f"— {_MODE_DESK.get(mode, '')}", "info")
    if not transcript:
        await ctx.emit.log(aid, "no intake conversation attached — using the written situation as the brief", "muted")
        await ctx.finish(aid, layer, {"verdict_line": f"Brief taken from the written intake · "
                                      f"{_MODE_LABEL.get(mode, mode)} engagement",
                                      "engagement_mode": mode, "handoff": "manager"})
        return

    await ctx.emit.log(aid, f"distilling a {len(convo)}-turn intake conversation into the Brief", "info")
    system = ("You are the Boss 🎩 — you ran the intake conversation; now write the handoff "
              f"Brief for the board. This is a {_MODE_LABEL.get(mode, mode)} engagement "
              f"({_MODE_DESK.get(mode, '')}). Capture the REAL problem (not the surface ask), "
              "constraints, success criteria and sensitivity. For a trader engagement capture the "
              "stock ticker + style; for wealth capture monthly income + expenses. Never invent "
              "facts; empty string when unknown.")
    user = (f"INTAKE CONVERSATION:\n{transcript}\n\nWritten situation field (may add detail): "
            f"{str(ctx.state.raw.get('situation') or '')[:400]}\n\n"
            "TASK: the structured handoff brief.")
    schema = ('{"situation": str (<=90 words, the real problem), "industry": str, "geography": str, '
              '"stage": str, "budget_band": str, "team_size": str, "uncertainty": str, '
              '"target_customer": str, "competitors": str, "revenue_model": str, '
              '"success_criteria": str, "sensitivity": "public"|"confidential", '
              '"symbol": str (ticker if trader else ""), "trading_style": str, '
              '"monthly_income": str (number if wealth else ""), "monthly_expenses": str}')
    await ctx.emit.prompt(aid, system, user)
    data, res = await ctx.llm.structured("t3", system, user, schema, max_tokens=650, agent=aid)

    out: dict[str, Any] = {"handoff": "manager", "engagement_mode": mode}
    if data:
        merged = []
        for k in _BRIEF_FIELDS:
            v = str(data.get(k) or "").strip()
            if v and not str(ctx.state.raw.get(k) or "").strip():
                ctx.state.raw[k] = v[:600]
                merged.append(k)
        # the distilled situation always wins — it's the whole point of the Boss
        if str(data.get("situation") or "").strip():
            ctx.state.raw["situation"] = str(data["situation"])[:900]
        # lift the numeric fields the trader / wealth desks need out of the chat
        if mode == "trader" and str(data.get("symbol") or "").strip():
            ctx.state.raw["symbol"] = re.sub(r"[^A-Za-z0-9.^-]", "", str(data["symbol"]).upper())[:16]
            if str(data.get("trading_style") or "").strip():
                ctx.state.raw["trading_style"] = str(data["trading_style"]).strip().lower()[:20]
        if mode == "wealth":
            if _to_num(data.get("monthly_income")) > 0:
                ctx.state.raw["monthly_income"] = _to_num(data.get("monthly_income"))
            if _to_num(data.get("monthly_expenses")) > 0:
                ctx.state.raw["monthly_expenses"] = _to_num(data.get("monthly_expenses"))
        out.update({"verdict_line": f"{_MODE_LABEL.get(mode, mode)} brief distilled from the "
                                    f"conversation — {len(merged) + 1} fields captured",
                    "brief": {k: str(data.get(k) or "")[:200] for k in _BRIEF_FIELDS if data.get(k)}})
        await ctx.emit.claim(aid, f"The real ask: {str(data.get('situation') or '')[:140]}", confidence=0.7)
        await ctx.emit.log(aid, f"handoff brief ready via {res.route}", "ok")
    else:
        out.update({"verdict_line": "Conversation attached but no model reachable — raw transcript "
                                    "handed to the parser as-is", "degraded": True})
        # even with zero keys the conversation still reaches the board
        ctx.state.raw["situation"] = (str(ctx.state.raw.get("situation") or "") +
                                      "\n\nINTAKE CONVERSATION:\n" + transcript)[:2400]
    await ctx.emit.partial("boss_brief",
                           {"engagement_mode": mode, **{k: ctx.state.raw.get(k, "") for k in _BRIEF_FIELDS}})
    await ctx.finish(aid, layer, out, res.route, res.tokens)


# ═══════════════════════════════════════════════════════════════════════════
# 🎼 MANAGER — dynamic routing over the whole pool, within the locked spine
# ═══════════════════════════════════════════════════════════════════════════

# the synthesis + grounding spine no plan may drop — MODE-AWARE (defense in
# depth: the scope_planner locks it in the picker, the Manager re-enforces here)
_FOUNDER_SPINE = {"web_researcher", "news_intel", "market_data", "macro_data", "rag_memory",
                  "market_analyst", "finance_modeler", "red_team", "fact_checker", "bias_auditor",
                  "weighing_engine", "verdict_composer", "scenario_planner", "negotiation_coach",
                  "storytelling", "visualizer", "reporter", "outcome_tracker"}
_TRADER_SPINE = {"news_intel", "market_data", "macro_data", "rag_memory", "technical_analyst",
                 "stock_analyst", "backtest_engineer", "quant_signals", "risk_manager",
                 "red_team", "fact_checker", "bias_auditor", "weighing_engine", "verdict_composer",
                 "scenario_planner", "negotiation_coach", "storytelling", "visualizer",
                 "reporter", "outcome_tracker"}
_WEALTH_SPINE = {"news_intel", "macro_data", "rag_memory", "salary_budget", "portfolio_allocator",
                 "fire_planner", "debt_banking", "red_team", "bias_auditor", "weighing_engine",
                 "verdict_composer", "scenario_planner", "negotiation_coach", "storytelling",
                 "visualizer", "reporter", "outcome_tracker"}
_SPINE = _FOUNDER_SPINE  # back-compat alias


def _spine(mode: str) -> set[str]:
    return (_TRADER_SPINE if mode == "trader" else _WEALTH_SPINE if mode == "wealth"
            else _FOUNDER_SPINE)


# the deterministic desks of OTHER modes can't be added into a founder pool
# (they need a ticker / salary numbers) — kept out of the additive pool
_POOL_EXCLUDED = {"boss", "manager", "stock_analyst", "technical_analyst", "quant_signals",
                  "risk_manager", "backtest_engineer", "options_desk", "microstructure",
                  "salary_budget", "portfolio_allocator", "fire_planner", "decision_graph"}


def _pool(mode: str = "founder") -> list[Any]:
    """The additive candidate pool for THIS engagement — the mode's own desks
    are already convened via its spine, so the pool is the cross-cutting lenses
    the Manager can pull in to sharpen the board for a specific brief."""
    excluded = _POOL_EXCLUDED | _spine(mode)
    return [m for m in ROSTER if m.implemented and m.id not in excluded]


async def manager_plan(ctx: Ctx) -> None:
    """Turn the mode's scope into a BRIEF-specific plan: add the lenses this
    exact situation needs, bench what it doesn't, give a reason per move. The
    engagement mode sets the base roster; the spine and the user's own picker
    choices are never overridden."""
    aid, layer = "manager", "L0"
    mode = classify_engagement(ctx.state.raw)
    spine = _spine(mode)
    await ctx.emit.stage(aid, "queued", layer)
    await ctx.start(aid, layer)
    scoped = list(ctx.state.scope)
    pool = _pool(mode)
    user_picked = bool(ctx.state.raw.get("agents_enabled"))
    depth = (ctx.state.raw.get("depth") or "board").lower()
    await ctx.emit.log(aid, f"routing a {_MODE_LABEL.get(mode, mode)} engagement "
                            f"({_MODE_DESK.get(mode, '')}) — mode-aware roster + spine locked", "info")

    candidates = "\n".join(f"- {m.id} ({m.layer}): {m.blurb}" for m in pool)
    schema = ('{"picks": [{"id": str (an agent id from the pool, not already convened), '
              '"reason": str (<=18 words — why THIS brief needs it)}], '
              '"drops": [{"id": str (a convened agent this brief does NOT need), '
              '"reason": str (<=14 words)}], '
              '"focus": str (<=30 words — the plan\'s center of gravity), '
              '"regulated": bool (does this brief touch legal/tax/financial/regulatory advice)}')
    system = ("You are the Manager 🎼 — the board's orchestrator. You do not analyse; you PLAN. "
              f"This is a {_MODE_LABEL.get(mode, mode)} engagement ({_MODE_DESK.get(mode, '')}). "
              "Given the brief and the currently convened board, route dynamically: add the "
              "specialists THIS specific situation needs (max 10), bench convened ones it "
              "genuinely doesn't (max 6). The synthesis + core spine is locked — never name it in "
              "drops. Every move needs a concrete reason tied to the brief.")
    user = (f"ENGAGEMENT: {mode}\nBRIEF: {str(ctx.state.brief)[:700]}\n"
            f"PROFILE: {str(ctx.state.profile)[:300]}\n"
            f"DEPTH: {depth}\nCONVENED ALREADY ({len(scoped)}): {', '.join(scoped)}\n\n"
            f"THE ADDITIVE POOL (cross-cutting lenses you may pull in):\n{candidates}\n\n"
            f"TASK: the routing plan for this brief.")
    await ctx.emit.prompt(aid, system, user)
    data, res = await ctx.llm.structured("t3", system, user, schema, max_tokens=800, agent=aid)

    pool_ids = {m.id for m in pool}
    picks: list[dict[str, str]] = []
    drops: list[dict[str, str]] = []
    focus = ""
    regulated = mode in ("trader", "wealth")   # financial engagements are regulated by nature
    if data:
        for p in (data.get("picks") or [])[:10]:
            if isinstance(p, dict) and p.get("id") in pool_ids and p["id"] not in scoped:
                picks.append({"id": str(p["id"]), "reason": str(p.get("reason") or "")[:120]})
        # the user's hand-picked board is sovereign — the Manager only ADDS then
        if not user_picked:
            for d in (data.get("drops") or [])[:6]:
                if isinstance(d, dict) and d.get("id") in scoped and d["id"] not in spine:
                    drops.append({"id": str(d["id"]), "reason": str(d.get("reason") or "")[:120]})
        focus = str(data.get("focus") or "")[:200]
        regulated = regulated or bool(data.get("regulated"))
        await ctx.emit.usage(aid, res.tokens, res.route)
    else:
        focus = (f"No model reachable — the {_MODE_LABEL.get(mode, mode)} board stands unchanged "
                 "(deterministic plan).")
        await ctx.emit.log(aid, "LLM unavailable — mode scope runs as planned (no dynamic routing)", "warn")

    for p in picks:
        scoped.append(p["id"])
        await ctx.emit.stage(p["id"], "queued", "")
        await ctx.emit.log(aid, f"＋ convening {p['id']} — {p['reason']}", "info")
    for d in drops:
        scoped.remove(d["id"])
        await ctx.emit.stage(d["id"], "skipped", "")
        await ctx.emit.log(aid, f"－ benching {d['id']} — {d['reason']}", "muted")
    ctx.state.scope = scoped
    if focus:
        await ctx.emit.log(aid, f"plan focus: {focus}", "info")
    await ctx.emit.collab(aid, [p["id"] for p in picks][:12] or scoped[:8])

    # the visible task graph — waves as they will actually execute
    from . import catalog
    l1 = [a for a in scoped if BY_ID.get(a) and BY_ID[a].layer == "L1"]
    l2 = [a for a in scoped if BY_ID.get(a) and BY_ID[a].layer == "L2"]
    plan = {
        "engagement_mode": mode,
        "mode_label": _MODE_LABEL.get(mode, mode),
        "focus": focus,
        "regulated": regulated,
        "picks": picks,
        "drops": drops,
        "spine_locked": sorted(spine & set(scoped)),
        "waves": {
            "grounding": l1,
            "analysis_wave1": [a for a in l2 if a in catalog.L2_FOUNDATIONAL],
            "analysis_wave2": [a for a in l2 if a not in catalog.L2_FOUNDATIONAL],
            "crucible": [a for a in scoped if BY_ID.get(a) and BY_ID[a].layer == "L3"],
            "synthesis": [a for a in scoped if BY_ID.get(a) and BY_ID[a].layer == "L4"],
        },
        "route": res.route if data else "deterministic",
    }
    ctx.state.rounds["manager_plan"] = plan
    await ctx.emit.partial("manager_plan", plan)
    await ctx.emit.partial("scope", scoped)
    await ctx.finish(aid, layer, {
        "verdict_line": (f"{_MODE_LABEL.get(mode, mode)} plan: {len(scoped)} specialists · "
                         f"+{len(picks)} routed in · −{len(drops)} benched · spine locked"),
        "engagement_mode": mode, "focus": focus, "regulated": regulated,
        "degraded": not bool(data),
    }, res.route, res.tokens)


# ═══════════════════════════════════════════════════════════════════════════
# ✅ QA GATE — blocking, with one re-dispatch cycle (runs BEFORE the reporter)
# ═══════════════════════════════════════════════════════════════════════════

_HARD = 0.75          # severity at/above which an issue blocks on its own
_MAX_REDISPATCH = 4   # agents re-dispatched per failed gate


def _claim_agent(claim: str) -> str:
    m = re.match(r"\s*\[([a-z_]+)\]", str(claim))
    return m.group(1) if m else ""


def _qa_issues(ctx: Ctx) -> list[dict[str, Any]]:
    """Deterministic issue sweep over the crucible's findings (t0 — no LLM)."""
    from .venture import _num
    issues: list[dict[str, Any]] = []
    fc = ctx.state.outputs.get("fact_checker") or {}
    for c in (fc.get("checks") or []):
        if not isinstance(c, dict):
            continue
        v = str(c.get("verdict") or "")
        if v in ("unsupported", "contradicted"):
            issues.append({"kind": "fact", "severity": 0.85 if v == "contradicted" else 0.6,
                           "agent": _claim_agent(c.get("claim", "")),
                           "note": f"{v}: {str(c.get('claim') or '')[:110]}"})
    for atk in (ctx.state.outputs.get("red_team") or {}).get("attacks") or []:
        if isinstance(atk, dict) and _num(atk.get("severity"), 0.0) >= _HARD:
            issues.append({"kind": "red_team", "severity": round(_num(atk.get("severity"), 0.8), 2),
                           "agent": str(atk.get("target_agent") or ""),
                           "note": str(atk.get("attack") or "")[:130]})
    for f in (ctx.state.outputs.get("bias_auditor") or {}).get("findings") or []:
        if isinstance(f, dict) and _num(f.get("severity"), 0.0) >= _HARD:
            issues.append({"kind": "bias", "severity": round(_num(f.get("severity"), 0.75), 2),
                           "agent": "user_framing",
                           "note": f"{f.get('bias')}: {str(f.get('note') or '')[:110]}"})
    if not isinstance(ctx.state.verdict.get("score"), (int, float)):
        issues.append({"kind": "verdict", "severity": 1.0, "agent": "verdict_composer",
                       "note": "no weighed verdict score exists — the deliverable has no spine"})
    return issues


def _qa_passes(issues: list[dict[str, Any]]) -> bool:
    fatal = [i for i in issues if i["severity"] >= 0.95]
    hard = [i for i in issues if i["severity"] >= _HARD]
    facts = [i for i in issues if i["kind"] == "fact"]
    return not fatal and len(hard) <= 2 and len(facts) <= 3


async def _redispatch(ctx: Ctx, aid: str, notes: list[str]) -> bool:
    """Send the QA gate's specific objections back to the responsible agent."""
    from .deliberate import _NARRATIVE_SCHEMA
    from .venture import _ANALYSIS_SCHEMA, _num
    prev = ctx.state.outputs.get(aid)
    meta = BY_ID.get(aid)
    if not isinstance(prev, dict) or meta is None or meta.tier == "t0":
        return False
    scored = isinstance(prev.get("score"), (int, float))
    await ctx.emit.stage(aid, "active", meta.layer)
    await ctx.emit.log(aid, "⟲ QA re-dispatch — the gate rejected parts of this analysis", "warn")
    system = (f"You are {meta.name} ('{aid}'). The QA gate REJECTED parts of your analysis — "
              "unsupported claims, or claims the crucible broke. Redo the flagged parts: ground "
              "every claim in the evidence provided or withdraw it. Lower your score/confidence "
              "if the objections stand. Never argue past the evidence.")
    user = (f"BRIEF: {str(ctx.state.brief)[:400]}\n"
            f"YOUR CURRENT FINDING: {str(prev.get('verdict_line') or '')[:160]}"
            + (f" (score {prev.get('score')}/10)\n" if scored else "\n")
            + "QA OBJECTIONS:\n" + "\n".join(f"- {n}" for n in notes[:5])
            + f"\n\nEVIDENCE BOARD:\n{ctx.state.evidence_digest(12, str(prev.get('verdict_line') or aid))}\n\n"
              f"TASK: your corrected finding as {meta.name}.")
    await ctx.emit.prompt(aid, system, user)
    data, res = await ctx.llm.structured(
        "t2", system, user, _ANALYSIS_SCHEMA if scored else _NARRATIVE_SCHEMA,
        max_tokens=650, agent=aid)
    if data and data.get("verdict_line"):
        fixed: dict[str, Any] = dict(prev)
        for k in ("verdict_line", "score", "confidence", "analysis",
                  "key_insights", "what_would_change", "assumptions"):
            if data.get(k) is not None:
                fixed[k] = data[k]
        if scored:
            fixed["score"] = max(0.0, min(10.0, _num(fixed.get("score"), 5.0)))
            fixed["confidence"] = max(0.05, min(0.95, _num(fixed.get("confidence"), 0.5)))
        fixed["qa_redispatched"] = True
        fixed["route"] = res.route
        await ctx.emit.usage(aid, res.tokens, res.route)
        await ctx.finish(aid, meta.layer, fixed)
        return True
    await ctx.emit.log(aid, "re-dispatch could not reach a model — original finding stands, flagged", "warn")
    await ctx.emit.stage(aid, "degraded" if prev.get("degraded") else "done", meta.layer)
    return False


async def qa_gate(ctx: Ctx, round_no: int = 1) -> bool:
    """The blocking gate. Runs after the crucible + weighing, BEFORE the
    reporter — so the deliverable is always written on a QA-cleaned board."""
    await ctx.emit.qa("started", round_=round_no)
    await ctx.emit.log("manager", f"QA gate (round {round_no}): fact traces, red-team severity, "
                                  "framing bias, verdict integrity", "info")
    issues = _qa_issues(ctx)
    if _qa_passes(issues):
        await ctx.emit.qa("passed", issues, round_no)
        await ctx.emit.log("manager", f"QA gate PASSED — {len(issues)} minor issue(s) on record", "ok")
        ctx.state.rounds[f"qa{round_no}"] = {"passed": True, "issues": issues[:12], "redispatched": []}
        return True

    await ctx.emit.qa("failed", issues, round_no)
    await ctx.emit.log("manager", f"QA gate FAILED — {len(issues)} issue(s); re-dispatching the "
                                  "responsible agents", "err")
    # group objections per responsible agent, re-dispatch the worst offenders
    per_agent: dict[str, list[str]] = {}
    for i in issues:
        a = i.get("agent") or ""
        if a and a in ctx.state.outputs and a not in ("verdict_composer", "user_framing"):
            per_agent.setdefault(a, []).append(i["note"])
    targets = sorted(per_agent, key=lambda a: -len(per_agent[a]))[:_MAX_REDISPATCH]
    redone = []
    for t in targets:
        if await _redispatch(ctx, t, per_agent[t]):
            redone.append(t)

    if redone:
        # the board changed — re-check facts, then re-weigh and re-sign with the
        # engagement's OWN weighing/verdict (trader ≠ wealth ≠ founder dimensions)
        from . import venture as v
        mode = classify_engagement(ctx.state.raw)
        if "fact_checker" in ctx.state.scope:
            await v.fact_checker(ctx)
        if mode == "trader":
            from . import markets as mk
            await mk.weighing_trader(ctx)
            await mk.verdict_trader(ctx)
        elif mode == "wealth":
            from . import wealth as wl
            await wl.weighing_wealth(ctx)
            await wl.verdict_wealth(ctx)
        else:
            await v.weighing_engine(ctx)
            await v.verdict_composer(ctx)
    issues2 = _qa_issues(ctx)
    passed = _qa_passes(issues2)
    await ctx.emit.qa("passed" if passed else "failed", issues2, round_no)
    await ctx.emit.log("manager",
                       f"QA re-check after re-dispatch: {'PASSED' if passed else 'still failing'} "
                       f"({len(issues2)} issue(s), {len(redone)} agent(s) redone)"
                       + ("" if passed else " — failures stay VISIBLE on the verdict, never hidden"),
                       "ok" if passed else "warn")
    ctx.state.rounds[f"qa{round_no}"] = {"passed": passed, "issues": issues2[:12], "redispatched": redone}
    if not passed:
        # honest degradation: the verdict carries the gate's objections openly
        ctx.state.verdict["qa_flag"] = (f"QA gate did not fully pass — {len(issues2)} open issue(s); "
                                        "read the issues list before acting")
    return passed


# ═══════════════════════════════════════════════════════════════════════════
# 🧑‍⚖️ HITL — the human approval gate for regulated content
# ═══════════════════════════════════════════════════════════════════════════

REGULATED_AGENTS = {"legal", "tax", "policy_compliance", "regulator", "optimization_predictor",
                    "banking", "fundraising_capital", "insurance_risk", "subsidies_schemes",
                    "cap_table", "debt_banking", "real_estate"}

DISCLAIMER = ("This output is research and decision-support, not professional, legal, tax, "
              "financial or investment advice. Regulated decisions require a licensed human.")


async def hitl_checkpoint(ctx: Ctx) -> dict[str, Any]:
    """Pause before the final deliverable when regulated content is present.
    approve → publish · reject → the report is withheld (verdict math stays,
    it's deterministic) · timeout → publish with an explicit UNREVIEWED mark."""
    mode = classify_engagement(ctx.state.raw)
    flagged = sorted(REGULATED_AGENTS & set(ctx.state.outputs))
    # a trader or wealth engagement IS financial/investment content by nature —
    # it always stops for review, even if no legal/tax specialist ran
    if mode in ("trader", "wealth") and mode not in flagged:
        flagged = [f"{mode}_desk", *flagged]
    alerts = [a for a in ((ctx.state.outputs.get("compliance_scan") or {}).get("alerts") or [])
              if isinstance(a, dict)]
    record: dict[str, Any] = {"regulated": bool(flagged or alerts), "sections": flagged,
                              "engagement_mode": mode, "decision": "not_required", "note": ""}
    if not record["regulated"]:
        ctx.state.rounds["hitl"] = record
        return record

    # every regulated run carries the disclaimer, reviewed or not
    ctx.state.verdict["disclaimer"] = DISCLAIMER

    if ctx.state.raw.get("hitl_auto_approve"):
        record["decision"] = "auto_approved"
        await ctx.emit.hitl("resumed", reason="auto-approve was pre-set for this run",
                            sections=flagged, decision="auto_approved")
        ctx.state.rounds["hitl"] = record
        return record

    timeout = float(ctx.state.raw.get("hitl_timeout") or 300)
    hitl.open_gate(ctx.state.run_id, {
        "sections": flagged,
        "verdict": {k: ctx.state.verdict.get(k) for k in ("score", "recommendation", "reasoning")},
        "alerts": alerts[:5],
        "regulated_lines": {a: str((ctx.state.outputs.get(a) or {}).get("verdict_line") or "")[:160]
                            for a in flagged},
    })
    await ctx.emit.hitl("pause",
                        reason=(f"regulated content from {len(flagged)} specialist(s) — a human must "
                                f"review before the final deliverable publishes (window: {int(timeout)}s)"),
                        sections=flagged)
    await ctx.emit.log("manager", f"⏸ HUMAN REVIEW: {', '.join(flagged)} produced regulated content. "
                                  f"Approve or reject in the review panel — the board waits "
                                  f"{int(timeout)}s, then publishes marked UNREVIEWED", "warn")
    result = await hitl.wait(ctx.state.run_id, timeout)
    record.update({"decision": result["decision"], "note": result.get("note", "")})

    if result["decision"] == "reject":
        note = result.get("note") or "no reason given"
        ctx.state.verdict["review_status"] = "rejected"
        rep = ctx.state.outputs.get("reporter")
        if isinstance(rep, dict) and rep.get("report_md"):
            rep["report_md"] = ("# Report withheld by human review\n\n"
                                f"The reviewer rejected the regulated sections of this run: {note}\n\n"
                                "The deterministic verdict math and every agent's individual finding "
                                f"remain visible above.\n\n> {DISCLAIMER}")
        await ctx.emit.log("manager", f"review REJECTED — report withheld ({note})", "err")
    elif result["decision"] == "timeout":
        ctx.state.verdict["review_status"] = "unreviewed_timeout"
        await ctx.emit.log("manager", "review window lapsed — publishing marked UNREVIEWED "
                                      "(the disclaimer applies in full)", "warn")
    else:
        ctx.state.verdict["review_status"] = "approved"
        await ctx.emit.log("manager", "review APPROVED — publishing the deliverable", "ok")

    await ctx.emit.hitl("resumed", sections=flagged, decision=result["decision"],
                        note=result.get("note", ""))
    ctx.state.rounds["hitl"] = record
    return record
