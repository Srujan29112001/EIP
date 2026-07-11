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

    # column — the deliberation: how each specialist's score moved after the
    # all-to-all round-2 read (the golden-arc pass, made visible as a chart)
    rd = ctx.state.rounds or {}
    dl = [d for d in (rd.get("deltas") or []) if isinstance(d, dict)]
    if dl:
        moved = sorted(dl, key=lambda d: -abs(_num(d.get("delta"), 0.0)))[:10]
        charts.append(_chart("col_deliberation", "column", "The board, after deliberation",
                             f"{rd.get('revised', 0)} of {len(dl)} specialists revised their score "
                             "after reading the FULL board in round 2 — convergence is confidence, "
                             "movement is where new context mattered.",
                             "weighing_engine",
                             {"labels": [f"{d['agent']} ({'+' if d['delta'] >= 0 else ''}{d['delta']})"
                                         for d in moved],
                              "values": [_num(d.get("after"), 0.0) for d in moved], "max": 10}))

    # the Scenario Planner's Monte-Carlo, three ways: distribution histogram,
    # probability rings, and the P10/P50/P90 columns
    sc = o.get("scenario_planner", {}) or {}
    if isinstance(sc.get("p50"), (int, float)):
        if isinstance(sc.get("bins"), list) and sc["bins"]:
            charts.append(_chart("hist_scenarios", "histogram", "1,000 simulated verdicts",
                                 "The full distribution of the Monte-Carlo draws — a tight peak means "
                                 "a stable verdict; a fat left tail is the risk you are actually carrying.",
                                 "scenario_planner",
                                 {"bins": sc["bins"], "start": _num(sc.get("bin_start"), 0.0),
                                  "step": _num(sc.get("bin_step"), 0.714), "marker": _num(sc.get("p50"), 0),
                                  "marker_label": f"P50 {sc.get('p50')}", "x_label": "simulated verdict score /10"}))
        ev_n = len(ctx.state.evidence)
        sourced_pct = (100.0 * sum(1 for e in ctx.state.evidence if (e.get("source") or {}).get("url"))
                       / ev_n) if ev_n else 0.0
        confs = [_num(v.get("confidence"), 0) for v in o.values()
                 if isinstance(v, dict) and isinstance(v.get("confidence"), (int, float))]
        avg_conf = (sum(confs) / len(confs) * 100) if confs else 0.0
        charts.append(_chart("radial_probs", "radial", "The odds, at a glance",
                             "Three rings: the probability this clears GO, the board's own calibrated "
                             "confidence, and how much of the evidence is live-sourced.",
                             "scenario_planner",
                             {"rings": [{"label": "P(GO) — clears 7/10", "value": _num(sc.get("prob_go"), 0) * 100},
                                        {"label": "board confidence", "value": avg_conf},
                                        {"label": "evidence live-sourced", "value": sourced_pct}]}))
        charts.append(_chart("col_scenarios", "column", "The verdict under uncertainty",
                             f"{sc.get('draws', 1000)} Monte-Carlo draws around the board's scores: "
                             f"P(GO) {int(_num(sc.get('prob_go'), 0) * 100)}%, "
                             f"P(NO-GO) {int(_num(sc.get('prob_nogo'), 0) * 100)}%"
                             + (f" — the case most often breaks on {sc['breaks_it']}." if sc.get("breaks_it") else "."),
                             "scenario_planner",
                             {"labels": ["P10 (bad luck)", "P50 (expected)", "P90 (good luck)"],
                              "values": [_num(sc.get("p10"), 0), _num(sc.get("p50"), 0),
                                         _num(sc.get("p90"), 0)], "max": 10}))

    # line — round 1 vs round 2, dimension by dimension (the deliberation, charted)
    r1dims = ((ctx.state.rounds or {}).get("results", {}).get("1", {}) or {}).get("dimensions") or {}
    if r1dims and dims and any(abs(_num(r1dims.get(k), 0) - _num(v, 0)) >= 0.05 for k, v in dims.items()):
        labels = [k for k in dims if k in r1dims]
        charts.append(_chart("line_rounds", "line", "Round 1 vs round 2, dimension by dimension",
                             "Where the board moved after reading itself — divergence between the lines "
                             "is exactly where deliberation changed the case.",
                             "weighing_engine",
                             {"labels": labels,
                              "series": [{"name": "round 1", "values": [round(_num(r1dims[k], 0), 1) for k in labels]},
                                         {"name": "round 2 (final)", "values": [round(_num(dims[k], 0), 1) for k in labels]}],
                              "max": 10},
                             {"label": "round-2 emphasis", "min": 0.7, "max": 1.3, "step": 0.05}))

    # pyramid — the board's consensus shape (bullish / neutral / bearish)
    if len(scored) >= 5:
        bullish = sum(1 for s in scored if s[1] >= 7.0)
        bearish = sum(1 for s in scored if s[1] < 4.5)
        neutral = len(scored) - bullish - bearish
        charts.append(_chart("pyr_consensus", "pyramid", "The shape of the board's consensus",
                             "How the specialists split — a heavy bearish base means the dissent is "
                             "structural, not one loud voice.",
                             "cross_pollinate",
                             {"levels": [{"label": "bullish (≥7)", "value": bullish, "color": "#9ae64a"},
                                         {"label": "neutral", "value": neutral, "color": "#22d3ee"},
                                         {"label": "bearish (<4.5)", "value": bearish, "color": "#fb7185"}]}))

    # donut — how the specialists connect (cross-pollination synergies vs tensions)
    conns = (o.get("cross_pollinate", {}) or {}).get("connections") or []
    if conns:
        syn = sum(1 for c in conns if isinstance(c, dict) and c.get("type") == "synergy")
        ten = len(conns) - syn
        charts.append(_chart("donut_crosslinks", "donut", "How the specialists connect",
                             f"{len(conns)} cross-links between specialists — synergy reinforces the case, "
                             "tension is where the board disagrees.",
                             "cross_pollinate",
                             {"slices": [{"label": "synergy", "value": syn, "color": "#9ae64a"},
                                         {"label": "tension", "value": ten, "color": "#fbbf24"}]}))

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
    await ctx.finish(aid, layer, {"verdict_line": f"{len(charts)} charts rendered",
                                  "count": len(charts), "charts": charts})


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
    lines = {k: str(v.get("verdict_line")) for k, v in o.items()
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

    # ── the real reason this agent kept starving: PROMPT SIZE, not just quota.
    # With ~36 specialists the findings block alone can blow a free tier's
    # per-request token ceiling — then EVERY key fails on EVERY retry, no
    # matter how many keys or how long we cool down. So the ladder now shrinks
    # the INPUT step by step (fewer findings, shorter lines, less evidence),
    # and the final rung SPLITS the report into two small calls and stitches.
    def findings_block(cap: int, width: int) -> str:
        items = list(lines.items())
        if len(items) > cap:
            # keep the most informative findings: strongest deviations from neutral
            def dev(kv: tuple) -> float:
                s = o.get(kv[0], {}).get("score")
                return abs(float(s) - 5.0) if isinstance(s, (int, float)) else 0.0
            items = sorted(items, key=dev, reverse=True)[:cap]
        return "\n".join(f"- {k}: {v[:width]}" for k, v in items)

    rd = ctx.state.rounds or {}
    v1 = rd.get("verdict1")
    rounds_note = (f"\nROUND-1 VERDICT (before deliberation): {v1}" if v1 else "")
    core = (f"BRIEF: {str(ctx.state.brief)[:600]}\n"
            f"VERDICT: { {k: verdict.get(k) for k in ('score', 'recommendation', 'reasoning', 'sensitivities')} }"
            f"{rounds_note}\n"
            f"RISKS: {[str(r.get('text'))[:100] for r in (verdict.get('risks') or [])[:6]]}\n")
    system = ("You are the board's reporter. Write the decision report a paying client would expect: "
              "specific, sourced from the agent findings given, honest about dissent. Never invent "
              "numbers; cite agents by name. Markdown only.")

    # (tier, max_out, findings cap, line width, evidence items, cooldown)
    ladder = [("t3", 1600, 40, 100, 10, 0.0), ("t3", 1400, 22, 80, 8, 10.0),
              ("t2", 1200, 22, 80, 6, 12.0), ("t2", 1000, 14, 60, 4, 14.0)]
    report = None
    for tier, cap, n_find, width, n_ev, wait in ladder:
        if wait:
            await ctx.emit.log(aid, f"report attempt failed — shrinking the prompt, cooling {wait:.0f}s, retrying on {tier}", "warn")
            await asyncio.sleep(wait)
        user = (core + f"AGENT FINDINGS:\n{findings_block(n_find, width)}\n"
                + f"TOP EVIDENCE:\n{ctx.state.evidence_digest(n_ev, 'verdict decision risks ' + str(ctx.state.brief.get('summary', ''))[:80])}")
        data, res = await ctx.llm.structured(tier, system, user, _REPORT_SCHEMA, max_tokens=cap, agent=aid)
        candidate = (data or {}).get("report_markdown")
        if candidate and len(str(candidate)) > 300:
            report = str(candidate)
            await ctx.emit.usage(aid, res.tokens, res.route)
            await ctx.emit.log(aid, f"report written · {len(report):,} chars via {res.route}", "ok")
            break

    if report is None:
        # last resort before deterministic: SPLIT the report into two small
        # calls (half the findings each, tiny prompts) and stitch the halves
        await ctx.emit.log(aid, "single-call report impossible — splitting into two smaller passes", "warn")
        half_schema = '{"section_markdown": str (markdown for ONLY the requested sections, 250-450 words)}'
        asks = [("## Executive summary / ## What the evidence says / ## Domain findings",
                 findings_block(12, 60)),
                ("## Risks & dissent / ## The plan: 30-60-90 days / ## What would change this verdict",
                 findings_block(8, 60))]
        parts: list[str] = []
        for section_ask, fb in asks:
            data, res = await ctx.llm.structured(
                "t2", system, core + f"AGENT FINDINGS:\n{fb}\n\nWRITE ONLY THESE SECTIONS: {section_ask}",
                half_schema, max_tokens=700, agent=aid)
            part = (data or {}).get("section_markdown")
            if part and len(str(part)) > 150:
                parts.append(str(part))
                await ctx.emit.usage(aid, res.tokens, res.route)
        if parts:
            title = f"# Decision report — {str(ctx.state.brief.get('summary', ''))[:100]}\n\n"
            report = title + "\n\n".join(parts)
            await ctx.emit.log(aid, f"report stitched from {len(parts)} split passes · {len(report):,} chars", "ok")

    degraded = report is None
    if degraded:
        report = fallback_report()
        await ctx.emit.log(aid, "LLM unavailable after full ladder + split — deterministic report assembly", "warn")
    await ctx.emit.partial("report", str(report))
    await ctx.finish(aid, layer, {"verdict_line": "full decision report ready",
                                  "chars": len(str(report)), "degraded": degraded,
                                  "report_md": str(report)})
