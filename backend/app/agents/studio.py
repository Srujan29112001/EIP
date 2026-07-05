"""The studio agents (Helix pattern): Visualizer + Reporter.

Visualizer (L4, t0+t2): turns the run's REAL numbers into chart specs the
frontend renders interactively — one chart per insight, best-fit type chosen
from the taxonomy (bar/column/line/area/donut/waterfall/gauge/scatter/
heatmap/candlestick/bullet/sparkline). Deterministic charts come straight
from state; the LLM may add extra insight charts ONLY from evidence figures.

Reporter (L4, t3): the long-form decision report — sectioned markdown built
from every agent's output, with a deterministic assembly fallback.
"""
from __future__ import annotations

import asyncio
from typing import Any

from .base import Ctx
from .venture import _num

Chart = dict[str, Any]


def _chart(id_: str, type_: str, title: str, insight: str, source: str,
           data: dict[str, Any], whatif: dict[str, Any] | None = None) -> Chart:
    c = {"id": id_, "type": type_, "title": title, "insight": insight,
         "source_agent": source, "data": data}
    if whatif:
        c["whatif"] = whatif
    return c


def _deterministic_charts(ctx: Ctx) -> list[Chart]:
    o = ctx.state.outputs
    dims = ctx.state.dimensions or {}
    verdict = ctx.state.verdict or {}
    charts: list[Chart] = []

    # gauge — the verdict itself
    overall = _num(verdict.get("score") or (o.get("weighing_engine", {}) or {}).get("overall"), 0)
    if overall:
        charts.append(_chart("gauge_overall", "gauge", "The verdict, as a dial",
                             f"The weighted board score is {overall}/10 — deterministic math, not vibes.",
                             "weighing_engine", {"value": overall, "min": 0, "max": 10,
                                                 "bands": [4.5, 7.0]}))

    # waterfall — how the dimensions build the score
    if dims:
        weights_map = {"Market": 0.25, "Economics": 0.25, "Regulatory": 0.125, "Evidence": 0.10,
                       "Execution": 0.125, "Timing": 0.15} if "Regulatory" in dims else None
        steps = [{"label": k, "value": round(v, 1)} for k, v in dims.items()]
        charts.append(_chart("waterfall_dims", "waterfall", "How the score is built",
                             "Each dimension pushes the verdict up or down from the neutral 5.0 line.",
                             "weighing_engine", {"base": 5.0, "steps": steps},
                             {"label": "weight emphasis", "min": 0.5, "max": 1.5, "step": 0.05}))
        _ = weights_map

    # column — the verdict's dimensions, exact values beside the radar
    if dims:
        charts.append(_chart("col_dims", "column", "Every dimension, scored",
                             "The radar shows the shape; this shows the exact number each dimension "
                             "earned. Below 4.5 (red) is what drags the verdict down.",
                             "weighing_engine",
                             {"labels": list(dims.keys()), "values": [round(v, 1) for v in dims.values()],
                              "max": 10}))

    # bar — every scoring agent ranked (the board, compared)
    scored = [(aid, _num(out.get("score"), -1), _num(out.get("confidence"), 0.5))
              for aid, out in o.items()
              if isinstance(out, dict) and isinstance(out.get("score"), (int, float))
              and aid not in ("weighing_engine",)]
    scored = [s for s in scored if s[1] >= 0]
    if len(scored) >= 3:
        scored.sort(key=lambda s: -s[1])
        charts.append(_chart("bar_agents", "bar", "The board, ranked",
                             f"{len(scored)} specialists scored this decision — the spread IS the story: "
                             "tight agreement means confidence, wide spread means open questions.",
                             "connecting_dots",
                             {"labels": [s[0] for s in scored], "values": [s[1] for s in scored],
                              "max": 10}))
        # scatter — confidence vs score (who is sure, who is guessing)
        charts.append(_chart("scatter_conf", "scatter", "Conviction map",
                             "Top-right = confident and positive. Bottom-right = positive but unsure — "
                             "treat those scores as soft.",
                             "fact_checker",
                             {"points": [{"x": s[1], "y": round(s[2] * 100), "label": s[0]} for s in scored],
                              "x_label": "score /10", "y_label": "confidence %"}))

    # donut — evidence quality split
    ev = ctx.state.evidence
    if ev:
        sourced = sum(1 for e in ev if (e.get("source") or {}).get("url"))
        docs = sum(1 for e in ev if str(e.get("agent")) == "doc_analyst")
        unsourced = max(0, len(ev) - sourced - docs)
        charts.append(_chart("donut_evidence", "donut", "What the verdict stands on",
                             f"{len(ev)} evidence items: live-sourced beats agent-claimed beats estimated.",
                             "fact_checker",
                             {"slices": [{"label": "live sourced", "value": sourced, "color": "#22d3ee"},
                                         {"label": "your documents", "value": docs, "color": "#0ea5e9"},
                                         {"label": "unsourced", "value": unsourced, "color": "#fbbf24"}]}))

    # heatmap — risk severity × source
    risks = (verdict.get("risks") or [])[:8]
    if risks:
        charts.append(_chart("heat_risks", "heatmap", "Risk heat",
                             "Every risk, by severity — the red cells are what the red team would "
                             "attack first if this were their money.",
                             "red_team",
                             {"rows": [{"label": str(r.get("text", ""))[:60],
                                        "value": round(_num(r.get("severity"), 0.5), 2),
                                        "group": str(r.get("source_agent", "board"))} for r in risks]}))

    # mode-specific
    md = o.get("market_data", {})
    if md.get("ohlcv"):  # trader: candlestick + backtest columns
        charts.append(_chart("candle_price", "candlestick", "Price action (real OHLC)",
                             "The last ~120 sessions, straight from the exchange feed.",
                             "market_data", {"ohlc": md["ohlcv"][-120:]},
                             {"label": "sessions shown", "min": 30, "max": 240, "step": 10}))
        tests = (o.get("backtest_engineer", {}) or {}).get("results") or []
        if tests:
            charts.append(_chart("col_backtests", "column", "Strategies vs just holding",
                                 "A signal earns the right to exist only by beating history — "
                                 "here is the proof of work.",
                                 "backtest_engineer",
                                 {"labels": [t["strategy"] for t in tests] + ["buy & hold"],
                                  "values": [t["strategy_return_pct"] for t in tests]
                                  + [tests[0]["buy_hold_return_pct"]]}))
    sb = o.get("salary_budget", {})
    if sb.get("savings_rate") is not None:  # wealth: budget donut + FIRE line + bullet
        income = _num(ctx.state.raw.get("monthly_income"), 0)
        expenses = _num(ctx.state.raw.get("monthly_expenses"), 0)
        if income > 0:
            charts.append(_chart("donut_budget", "donut", "Where the salary goes",
                                 f"Savings rate {sb['savings_rate']}% — the single number that decides "
                                 "your financial future.",
                                 "salary_budget",
                                 {"slices": [{"label": "expenses", "value": round(expenses), "color": "#fb7185"},
                                             {"label": "surplus (invests)", "value": round(max(0, income - expenses)),
                                              "color": "#9ae64a"}]}))
            charts.append(_chart("bullet_savings", "bullet", "Savings rate vs benchmarks",
                                 "20% sustains, 30% builds wealth — where do you sit?",
                                 "salary_budget",
                                 {"value": _num(sb.get("savings_rate"), 0), "target": 30,
                                  "bands": [10, 20, 30], "max": 60}))
        fp = o.get("fire_planner", {})
        if fp.get("fire_number"):
            surplus = max(0.0, income - expenses)
            corpus = _num(ctx.state.raw.get("current_savings"), 0)
            series, r = [], 0.05 / 12
            for m in range(0, 361, 6):
                series.append({"x": round(m / 12, 1), "y": round(corpus)})
                for _i in range(6):
                    corpus = corpus * (1 + r) + surplus
            charts.append(_chart("line_fire", "area", "The road to your FIRE number",
                                 f"Corpus growth at 5% real returns toward ₹{_num(fp['fire_number'], 0):,.0f}.",
                                 "fire_planner",
                                 {"points": series, "x_label": "years", "y_label": "corpus ₹",
                                  "target": _num(fp.get("fire_number"), 0)},
                                 {"label": "monthly surplus ×", "min": 0.5, "max": 2.5, "step": 0.1}))
    return charts


_LLM_CHART_SCHEMA = (
    '{"charts": [{"type": "bar"|"column"|"donut", "title": str, '
    '"insight": str (<=30 words, the so-what), "source_agent": str, '
    '"labels": [str], "values": [number]} x2-4]}')


async def visualizer(ctx: Ctx) -> None:
    aid, layer = "visualizer", "L4"
    await ctx.start(aid, layer)
    await ctx.emit.log(aid, "picking the best chart for every insight — real numbers only", "muted")
    charts = _deterministic_charts(ctx)
    await ctx.emit.log(aid, f"{len(charts)} charts built from run state (deterministic)", "code")

    # LLM extras: only figures already on the evidence board may be charted
    figures = [e["text"] for e in ctx.state.evidence
               if any(c.isdigit() for c in e.get("text", ""))][:18]
    if figures:
        data, res = await ctx.llm.structured(
            "t2",
            "You are a data visualizer. Build 2-4 SIMPLE comparison charts strictly from the figures "
            "provided — never invent numbers, skip a chart rather than guess. Values must be plain "
            "numbers extracted from the text.",
            "FIGURES ON THE EVIDENCE BOARD:\n" + "\n".join(figures),
            _LLM_CHART_SCHEMA, max_tokens=800, agent=aid)
        extra = (data or {}).get("charts") or []
        ok = 0
        for i, c in enumerate(extra):
            if (isinstance(c, dict) and c.get("type") in ("bar", "column", "donut")
                    and isinstance(c.get("labels"), list) and isinstance(c.get("values"), list)
                    and len(c["labels"]) == len(c["values"]) and 1 < len(c["labels"]) <= 8):
                try:
                    values = [float(v) for v in c["values"]]
                except (TypeError, ValueError):
                    continue
                payload = ({"slices": [{"label": str(l)[:40], "value": v}
                                       for l, v in zip(c["labels"], values)]}
                           if c["type"] == "donut" else
                           {"labels": [str(l)[:40] for l in c["labels"]], "values": values})
                charts.append(_chart(f"llm_{i}", c["type"], str(c.get("title", "Insight"))[:70],
                                     str(c.get("insight", ""))[:200],
                                     str(c.get("source_agent", "visualizer")), payload))
                ok += 1
        if ok:
            await ctx.emit.usage(aid, res.tokens, res.route)
            await ctx.emit.log(aid, f"+{ok} insight charts from evidence figures", "ok")
        else:
            await ctx.emit.log(aid, "no clean figures for extra charts — deterministic set stands", "info")

    await ctx.emit.partial("charts", charts)
    await ctx.emit.log(aid, f"{len(charts)} interactive charts → Decision Room", "ok")
    await ctx.finish(aid, layer, {"verdict_line": f"{len(charts)} charts rendered", "count": len(charts)})


_REPORT_SCHEMA = ('{"report_markdown": str (a complete decision report in markdown, 600-1000 words: '
                  '## Executive summary / ## What the evidence says / ## Domain findings (one bullet '
                  'per agent, cite them) / ## Risks & dissent / ## The plan: 30-60-90 days / '
                  '## What would change this verdict)}')


async def reporter(ctx: Ctx) -> None:
    aid, layer = "reporter", "L4"
    await ctx.start(aid, layer)
    await ctx.emit.log(aid, "writing the full decision report from every agent's output", "muted")
    o = ctx.state.outputs
    verdict = ctx.state.verdict or {}
    lines = {k: v.get("verdict_line") for k, v in o.items()
             if isinstance(v, dict) and v.get("verdict_line")}

    def fallback_report() -> str:
        md = [f"# Decision report — {str(ctx.state.brief.get('summary', ''))[:100]}",
              "", f"**Verdict: {verdict.get('recommendation', '—')} · {verdict.get('score', '—')}/10**",
              "", str(verdict.get("reasoning", "")), "", "## Every specialist's one-line finding", ""]
        md += [f"- **{k}**: {v}" for k, v in lines.items()]
        md += ["", "## Risks", ""]
        md += [f"- {r.get('text', '')}" for r in (verdict.get("risks") or [])[:6]]
        md += ["", "## Next steps", ""]
        md += [f"1. {s}" for s in (verdict.get("next_steps") or [])[:6]]
        md += ["", "_Deterministic assembly — add a model/key for the narrated report._"]
        return "\n".join(md)

    system = ("You are the board's reporter. Write the decision report a paying client would expect: "
              "specific, sourced from the agent findings given, honest about dissent. Never invent "
              "numbers; cite agents by name. Markdown only.")
    user = (f"BRIEF: {ctx.state.brief}\nVERDICT: { {k: verdict.get(k) for k in ('score', 'recommendation', 'reasoning', 'sensitivities')} }\n"
            f"AGENT FINDINGS: {lines}\n"
            f"RISKS: {[r.get('text') for r in (verdict.get('risks') or [])[:6]]}\n"
            f"TOP EVIDENCE:\n{ctx.state.evidence_digest(12)}")

    # The report is the single biggest LLM call and runs dead-last, when every
    # per-minute key quota is most likely spent — the #1 reason it starved.
    # A retry ladder rescues it: escalating cooldowns (Groq/Gemini refresh per
    # minute) and a drop to the faster tier so we still get NARRATION, never
    # just deterministic assembly, whenever any key has a shred of quota left.
    ladder = [("t3", 1800, 0.0), ("t3", 1600, 12.0), ("t2", 1400, 14.0), ("t2", 1100, 16.0)]
    report = None
    for tier, cap, wait in ladder:
        if wait:
            await ctx.emit.log(aid, f"report starved — cooling {wait:.0f}s for quota, retrying on {tier}", "warn")
            await asyncio.sleep(wait)
        data, res = await ctx.llm.structured(tier, system, user, _REPORT_SCHEMA, max_tokens=cap, agent=aid)
        candidate = (data or {}).get("report_markdown")
        if candidate and len(str(candidate)) > 300:
            report = str(candidate)
            await ctx.emit.usage(aid, res.tokens, res.route)
            await ctx.emit.log(aid, f"report written · {len(report):,} chars via {res.route}", "ok")
            break
    degraded = report is None
    if degraded:
        report = fallback_report()
        await ctx.emit.log(aid, "LLM unavailable after full retry ladder — deterministic report assembly", "warn")
    await ctx.emit.partial("report", str(report))
    await ctx.finish(aid, layer, {"verdict_line": "full decision report ready",
                                  "chars": len(str(report)), "degraded": degraded})
