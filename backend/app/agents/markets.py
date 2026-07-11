"""Phase-4 markets cluster — the Trading Co-Pilot.

Design rules (MASTER_PLAN §5, SEBI-shaped):
- deterministic cores do the math; LLMs only narrate on top of it
- a signal that hasn't survived a backtest on this symbol's own history
  is never shown (Backtest Engineer runs before Quant Signals speaks)
- output language is SETUP QUALITY and probability cones — never
  "buy this", never point predictions, never execution
"""
from __future__ import annotations

from typing import Any

import pandas as pd

from ..engine import backtest as bt
from ..engine import indicators as ta
from ..grounding import market
from .base import Ctx
from .venture import _num


def _df(ohlcv: list[list[Any]]) -> pd.DataFrame:
    df = pd.DataFrame(ohlcv, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    return df.set_index("Date")


# ── L1: market history (t0 — the trader's evidence base) ─────────────────────

async def market_history(ctx: Ctx) -> None:
    aid, layer = "market_data", "L1"
    await ctx.start(aid, layer)
    raw = ctx.state.raw
    symbol = market.resolve_symbol(raw.get("symbol", ""), raw.get("geography", "India"))
    await ctx.emit.log(aid, f"⌕ yfinance: {symbol} · 2y daily + fundamentals", "code")
    data = await market.full_history(symbol)
    if not data:
        await ctx.emit.log(aid, f"no data for {symbol} — check the symbol (NSE needs .NS)", "err")
        await ctx.fail(aid, layer, "symbol unresolved")
        return

    info = data["info"]
    closes = [row[4] for row in data["ohlcv"]]
    last, first = closes[-1], closes[0]
    ret = (last / first - 1) * 100
    name = info.get("longName", symbol)
    src = {"url": data["source_url"], "name": "Yahoo Finance"}

    await ctx.emit.claim(aid, f"{name}: last {last} · {len(closes)}d return {ret:+.1f}%", source=src, confidence=0.9)
    ctx.state.evidence.append({"text": f"PRICE: {name} last {last}, 2y {ret:+.1f}%", "source": src, "agent": aid})
    for label, key, fmt in (("P/E (trailing)", "trailingPE", "{:.1f}"), ("P/B", "priceToBook", "{:.1f}"),
                            ("beta", "beta", "{:.2f}"), ("revenue growth", "revenueGrowth", "{:.1%}"),
                            ("profit margin", "profitMargins", "{:.1%}")):
        if key in info:
            try:
                text = f"{label}: {fmt.format(float(info[key]))}"
            except (TypeError, ValueError):
                continue
            await ctx.emit.claim(aid, f"{name} {text}", source=src, confidence=0.85)
            ctx.state.evidence.append({"text": f"FUNDAMENTAL: {name} {text}", "source": src, "agent": aid})

    # weekly series → the MarketSim chart (same shape founder mode uses)
    weekly = [[row[0], row[4]] for row in data["ohlcv"][::5]]
    daily = pd.Series(closes).pct_change().dropna()
    vol = float(daily.std()) * (252 ** 0.5) * 100 if len(daily) > 10 else 20.0
    pulse = {"symbol": symbol, "label": name, "last": last, "series": weekly,
             "ret_1y_pct": round(ret / 2, 1), "ret_3m_pct": 0.0,
             "volatility_pct": round(vol, 1), "source_url": data["source_url"]}

    out = {"pulses": [pulse], "ohlcv": data["ohlcv"], "info": info, "symbol": symbol, "name": name}
    ctx.state.brief.setdefault("industry", info.get("industry", info.get("sector", "")))
    await ctx.emit.log(aid, f"{len(data['ohlcv'])} sessions + {len(info)} fundamentals on the board", "ok")
    await ctx.finish(aid, layer, out)


# ── L2: technical analyst (t0 — pure math) ───────────────────────────────────

async def technical_analyst(ctx: Ctx) -> None:
    aid, layer = "technical_analyst", "L2"
    await ctx.start(aid, layer)
    md = ctx.state.outputs.get("market_data", {})
    if not md.get("ohlcv"):
        await ctx.fail(aid, layer, "no price history to analyse")
        return
    s = ta.summary(_df(md["ohlcv"]))
    await ctx.emit.log(aid, "no LLM in this stage — indicator math only", "muted")
    for r in s["readings"]:
        kind = "ok" if r["read"] == "bullish" else "err" if r["read"] == "bearish" else "info"
        await ctx.emit.log(aid, f"{r['name']:<20} {r['value']} → {r['read']}", kind)
    await ctx.emit.log(aid, f"support ≈ {s['support']} · resistance ≈ {s['resistance']} · ATR {s['atr_pct']}%", "code")
    await ctx.emit.claim(
        aid, f"Technical read: {s['bias']} ({s['bullish']} bullish vs {s['bearish']} bearish signals) — "
             f"trend {s['trend_score']}/10, momentum {s['momentum_score']}/10", confidence=0.75)
    s["verdict_line"] = f"{s['bias']} bias · trend {s['trend_score']}/10 · momentum {s['momentum_score']}/10"
    s["score"] = s["trend_score"]
    s["confidence"] = 0.75
    await ctx.finish(aid, layer, s)


# ── L2: backtest engineer (t0) ────────────────────────────────────────────────

async def backtest_engineer(ctx: Ctx) -> None:
    aid, layer = "backtest_engineer", "L2"
    await ctx.start(aid, layer)
    md = ctx.state.outputs.get("market_data", {})
    if not md.get("ohlcv"):
        await ctx.fail(aid, layer, "no history")
        return
    await ctx.emit.log(aid, "every strategy proves itself on THIS symbol's history before anyone cites it", "muted")
    results = bt.backtest_all(_df(md["ohlcv"]))
    for r in results:
        kind = "ok" if r["beats_buy_hold"] else "warn"
        await ctx.emit.log(
            aid, f"{r['strategy']}: {r['trades']} trades · hit {r['hit_rate']}% · "
                 f"{r['strategy_return_pct']:+.1f}% vs B&H {r['buy_hold_return_pct']:+.1f}% · "
                 f"maxDD {r['max_drawdown_pct']}% ({r['sample_note']})", kind)
    best = max(results, key=lambda r: r["strategy_return_pct"])
    await ctx.emit.claim(
        aid, f"Backtests (2y, no costs): best {best['strategy']} {best['strategy_return_pct']:+.1f}% "
             f"({best['trades']} trades, hit {best['hit_rate']}%) vs buy&hold {best['buy_hold_return_pct']:+.1f}%",
        confidence=0.7)
    await ctx.finish(aid, layer, {"results": results,
                                  "verdict_line": f"best strategy on history: {best['strategy']} "
                                                  f"({best['strategy_return_pct']:+.1f}%)"})


# ── L2: quant signals (t0 — the ensemble, only after the backtest) ───────────

async def quant_signals(ctx: Ctx) -> None:
    aid, layer = "quant_signals", "L2"
    await ctx.start(aid, layer)
    tech = ctx.state.outputs.get("technical_analyst", {})
    tests = ctx.state.outputs.get("backtest_engineer", {}).get("results", [])
    if not tech or not tests:
        await ctx.fail(aid, layer, "needs technicals + backtests first")
        return

    votes = {
        "trend": 1 if tech.get("trend_score", 5) >= 6 else -1 if tech.get("trend_score", 5) <= 4 else 0,
        "momentum": 1 if tech.get("momentum_score", 5) >= 6 else -1 if tech.get("momentum_score", 5) <= 4 else 0,
        "history": 1 if any(t["beats_buy_hold"] and t["trades"] >= 5 for t in tests) else 0,
    }
    score = sum(votes.values())
    agreement = sum(1 for v in votes.values() if v == max(votes.values(), key=abs, default=0) and v != 0)
    setup = ("constructive" if score >= 2 else "cautiously constructive" if score == 1
             else "deteriorating" if score <= -2 else "mixed")
    for k, v in votes.items():
        await ctx.emit.log(aid, f"vote · {k}: {'+' if v > 0 else ''}{v}", "code")
    await ctx.emit.log(aid, f"regime: {'trending' if abs(votes['trend']) else 'ranging'} · "
                            f"volatility {tech.get('atr_pct', '?')}%/day", "info")
    await ctx.emit.claim(
        aid, f"Setup quality: {setup.upper()} ({score:+d} of 3 votes, agreement {agreement}/3) — "
             "probability read, not a recommendation", confidence=0.6 + 0.1 * agreement)
    await ctx.finish(aid, layer, {
        "verdict_line": f"setup: {setup} ({score:+d}/3 votes)",
        "setup": setup, "votes": votes, "signal_score": score,
        "score": round(5.0 + score * 1.5, 1), "confidence": round(0.6 + 0.1 * agreement, 2),
    })


# ── L2: risk manager (t0 — always-on survival math) ──────────────────────────

async def risk_manager(ctx: Ctx) -> None:
    aid, layer = "risk_manager", "L2"
    await ctx.start(aid, layer)
    raw = ctx.state.raw
    tech = ctx.state.outputs.get("technical_analyst", {})
    md = ctx.state.outputs.get("market_data", {})
    capital = _num(raw.get("capital"), 100000.0)
    risk_pct = max(0.25, min(_num(raw.get("risk_pct"), 1.0), 5.0))
    last = _num(tech.get("last") or (md.get("pulses") or [{}])[0].get("last"), 0.0)
    atr_pct = _num(tech.get("atr_pct"), 2.0)
    if last <= 0:
        await ctx.fail(aid, layer, "no price")
        return

    risk_amount = capital * risk_pct / 100
    stop_dist = last * (2 * atr_pct / 100)              # 2×ATR stop
    qty = int(risk_amount / stop_dist) if stop_dist > 0 else 0
    position = qty * last
    await ctx.emit.log(aid, "no LLM in this stage — position sizing math only", "muted")
    await ctx.emit.log(aid, f"capital ₹{capital:,.0f} · risk/trade {risk_pct}% = ₹{risk_amount:,.0f}", "code")
    await ctx.emit.log(aid, f"2×ATR stop ≈ ₹{stop_dist:,.1f} below entry → size {qty} shares (₹{position:,.0f})", "code")
    if position > capital * 0.5:
        await ctx.emit.log(aid, "⚠ position would exceed 50% of capital — concentration risk", "warn")
    await ctx.emit.claim(
        aid, f"If you traded this setup: max loss ₹{risk_amount:,.0f} ({risk_pct}%), "
             f"{qty} shares, stop ≈ {last - stop_dist:,.1f}. This trade risks "
             f"{risk_pct}% of your capital.", confidence=0.9)
    await ctx.finish(aid, layer, {
        "verdict_line": f"{qty} shares max · stop {last - stop_dist:,.1f} · risk ₹{risk_amount:,.0f}",
        "capital": capital, "risk_pct": risk_pct, "qty": qty,
        "stop": round(last - stop_dist, 2), "position_value": round(position, 2),
        "max_loss": round(risk_amount, 2),
        "score": 7.0 if position <= capital * 0.5 else 4.0, "confidence": 0.9,
    })


# ── L2: stock analyst (t2 — fundamentals narrative over the evidence) ────────

async def stock_analyst(ctx: Ctx) -> None:
    from .venture import _scored_analysis  # local import avoids cycle at module load
    aid, layer = "stock_analyst", "L2"
    await ctx.start(aid, layer)
    md = ctx.state.outputs.get("market_data", {})
    info = md.get("info", {})
    pe = info.get("trailingPE")
    det = 5.0 if pe is None else 7.0 if _num(pe, 30) < 18 else 3.5 if _num(pe, 30) > 45 else 5.5
    fallback = {
        "verdict_line": f"P/E screen only: {pe if pe is not None else 'n/a'}",
        "score": det, "confidence": 0.35,
        "analysis": "Deterministic valuation screen from fundamentals. Add a key/model for a full read.",
        "assumptions": ["P/E vs broad-market band proxies valuation"], "numbers_used": [],
    }
    out = await _scored_analysis(
        ctx, aid,
        f"You are an equity analyst covering {md.get('name', 'this company')}. Fundamentals, "
        "competitive position, what the market is pricing in. Never predict a price.",
        "Assess the company's quality and valuation from the fundamentals and news on the evidence "
        "board. Score 0-10 for VALUE (10 = excellent business at a fair or cheap price).", fallback)
    await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
    await ctx.finish(aid, layer, out)


# ── L2: fund analyst / options desk / microstructure (education lenses) ──────

async def fund_analyst(ctx: Ctx) -> None:
    from .venture import _scored_analysis
    aid, layer = "fund_analyst", "L2"
    await ctx.start(aid, layer)
    fallback = {"verdict_line": "Fund comparison needs a model — index-first principle applies",
                "score": 6.0, "confidence": 0.3,
                "analysis": "Default principle: low-cost index funds beat most active funds after fees; "
                            "check expense ratio, tracking error, AUM before anything else.",
                "assumptions": [], "numbers_used": []}
    out = await _scored_analysis(
        ctx, aid,
        "You are a mutual-fund and hedge-strategy analyst (India-first: index funds, flexicap, ELSS; "
        "hedge strategies as education only).",
        "For someone interested in this symbol/sector: how funds give the same exposure with less "
        "single-stock risk, which fund CATEGORY fits (never a specific scheme pick), and what a hedge "
        "fund would do differently (education). Score 0-10 for fund-route attractiveness vs direct stock.",
        fallback)
    await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
    await ctx.finish(aid, layer, out)


async def options_desk(ctx: Ctx) -> None:
    from .venture import _scored_analysis
    aid, layer = "options_desk", "L2"
    await ctx.start(aid, layer)
    await ctx.emit.log(aid, "education only — defined-risk structures, never naked positions", "muted")
    tech = ctx.state.outputs.get("technical_analyst", {})
    fallback = {"verdict_line": "Options education needs a model", "score": 5.0, "confidence": 0.25,
                "analysis": "Principle: buy defined-risk (spreads), never sell naked; theta decays you, "
                            "IV crush around events.", "assumptions": [], "numbers_used": []}
    out = await _scored_analysis(
        ctx, aid,
        "You are an options educator (NSE F&O context). You explain defined-risk structures that fit a "
        "view — you never recommend a trade, never naked selling.",
        f"Given the technical read (bias: {tech.get('bias', 'mixed')}, ATR {tech.get('atr_pct', '?')}%/day, "
        f"support {tech.get('support', '?')} / resistance {tech.get('resistance', '?')}): explain which "
        "defined-risk structure MATCHES that view and its max loss/gain shape, as education. "
        "Score 0-10 for how options-suitable this underlying is (liquidity, IV regime).", fallback)
    await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
    await ctx.finish(aid, layer, out)


async def microstructure(ctx: Ctx) -> None:
    from .venture import _scored_analysis
    aid, layer = "microstructure", "L2"
    await ctx.start(aid, layer)
    await ctx.emit.log(aid, "education: how the plumbing works — retail cannot out-speed HFT and shouldn't try", "muted")
    fallback = {"verdict_line": "Microstructure read needs a model", "score": 5.0, "confidence": 0.2,
                "analysis": "Principle: retail edge is time horizon, not speed. Use limit orders, avoid "
                            "open/close auctions volatility, mind impact costs.", "assumptions": [], "numbers_used": []}
    out = await _scored_analysis(
        ctx, aid,
        "You are a market-microstructure educator: HFT, spreads, slippage, order types — teaching a "
        "retail trader what the plumbing means for THEM.",
        "Explain what microstructure means for trading this symbol at retail size: realistic slippage, "
        "best order type, one mistake HFTs profit from. Score 0-10 for execution friendliness.", fallback)
    await ctx.emit.claim(aid, out["verdict_line"], confidence=out["confidence"])
    await ctx.finish(aid, layer, out)


# ── L4: trader weighing (t0) + verdict ────────────────────────────────────────

async def weighing_trader(ctx: Ctx) -> None:
    aid, layer = "weighing_engine", "L4"
    await ctx.start(aid, layer)
    await ctx.emit.log(aid, "no LLM in this stage — weighted evidence math only", "muted")
    o = ctx.state.outputs

    def penalty(target: str) -> float:
        return sum(_num(a.get("severity"), 0.5) for a in ctx.state.conflicts
                   if isinstance(a, dict) and a.get("target_agent") == target) * 0.8

    def sc(aid_: str, default: float = 5.0) -> float:
        out = o.get(aid_, {})
        return max(0.5, _num(out.get("score"), default) - penalty(aid_))

    tech = o.get("technical_analyst", {})
    dims = {
        "Trend": sc("technical_analyst"),
        "Momentum": max(0.5, _num(tech.get("momentum_score"), 5.0)),
        "Value": sc("stock_analyst"),
        "History": sc("quant_signals"),
        "RiskFit": sc("risk_manager"),
    }
    # human layer (board/war_room depth): trading is a psychology game too
    hvals = [_num(o[i].get("score"), -1) for i in
             ("human_behaviour", "money_happiness", "philosophy_ethics")
             if isinstance(o.get(i), dict) and isinstance(o[i].get("score"), (int, float))]
    if hvals:
        dims["Psychology"] = max(0.5, sum(hvals) / len(hvals))
    dims = {k: round(min(10.0, v), 1) for k, v in dims.items()}
    ctx.state.dimensions = dims
    base_w = {"Trend": 0.25, "Momentum": 0.2, "Value": 0.2, "History": 0.2,
              "RiskFit": 0.15, "Psychology": 0.12}
    weights = {k: base_w[k] for k in dims if k in base_w}
    try:   # learned weights from the graded track record (bounded ±15%)
        from ..memory.store import dimension_calibration
        learned = await dimension_calibration()
        if learned:
            weights = {k: w * learned.get(k, 1.0) for k, w in weights.items()}
            await ctx.emit.log(aid, "learned weights active (graded outcomes): "
                               + ", ".join(f"{k}×{v}" for k, v in learned.items() if k in weights), "info")
    except Exception:
        pass
    tw = sum(weights.values()) or 1.0
    overall = round(sum(dims[k] * (w / tw) for k, w in weights.items()), 1)
    for k, v in dims.items():
        await ctx.emit.log(aid, f"{k:<10} {v}/10", "code")
    await ctx.emit.log(aid, f"setup quality {overall}/10 · dissent: {len(ctx.state.conflicts)} attacks", "info")
    await ctx.emit.partial("radar", {"dimensions": dims, "overall": overall})
    await ctx.finish(aid, layer, {"dimensions": dims, "overall": overall, "dissent": ctx.state.conflicts})


_TRADE_VERDICT_SCHEMA = (
    '{"recommendation": "FAVOURABLE_SETUP"|"MIXED_SETUP"|"UNFAVOURABLE_SETUP", '
    '"reasoning": str (3 sentences, cite the evidence), "sensitivities": [str x3], '
    '"risks": [{"text": str, "source_agent": str, "severity": float}], '
    '"opportunities": [{"text": str, "source_agent": str}], '
    '"next_steps": [str x4 — study/paper-trade actions, never order instructions], '
    '"teach": str (2 sentences: how to think about this class of trade)}')


async def verdict_trader(ctx: Ctx) -> None:
    aid, layer = "verdict_composer", "L4"
    await ctx.start(aid, layer)
    w = ctx.state.outputs.get("weighing_engine", {})
    overall = _num(w.get("overall"), 5.0)
    band = ("FAVOURABLE_SETUP" if overall >= 7 else
            "MIXED_SETUP" if overall >= 4.5 else "UNFAVOURABLE_SETUP")
    await ctx.emit.log(aid, "EIP describes setup quality — the decision, and the outcome, are yours", "muted")
    q = ctx.state.outputs.get("quant_signals", {})
    r = ctx.state.outputs.get("risk_manager", {})
    fallback = {
        "recommendation": band,
        "reasoning": f"Setup quality {overall}/10 from deterministic cores "
                     f"({q.get('setup', 'mixed')} signals). Add a model/key for full reasoning.",
        "sensitivities": ["Trend persistence", "Backtest sample size", "Volatility regime"],
        "risks": [{"text": a.get("attack", ""), "source_agent": "red_team",
                   "severity": _num(a.get("severity"), 0.5)} for a in ctx.state.conflicts[:4]],
        "opportunities": [],
        "next_steps": ["Paper-trade this setup for 10 occurrences before risking money",
                       "Re-run after the next earnings/major news event",
                       "Compare the same setup on 2 peer stocks",
                       "Read the backtest caveats — no costs/slippage are modelled"],
        "teach": "A good setup is a probability edge, not a promise. Position sizing — not prediction — "
                 "is what keeps traders alive.",
    }
    data, res = await ctx.llm.structured(
        "t3",
        "You compose an educational trading decision document. You may NOT change the numeric setup "
        "score (deterministic), may NOT tell the user to buy or sell, may NOT predict prices. "
        "Describe setup quality, key levels, invalidation, and what would change the read.",
        f"SYMBOL: {ctx.state.outputs.get('market_data', {}).get('name', '')}\n"
        f"DIMENSIONS: {ctx.state.dimensions} → setup {overall}/10 ({band})\n"
        f"QUANT: {q.get('verdict_line', '')} · RISK PLAN: {r.get('verdict_line', '')}\n"
        f"ATTACKS: {[str(a.get('attack', ''))[:120] for a in ctx.state.conflicts[:3]]}\n"
        f"EVIDENCE:\n{ctx.state.evidence_digest(10)}",
        _TRADE_VERDICT_SCHEMA, max_tokens=1000, agent=aid,
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
    await ctx.emit.log(aid, f"SETUP: {verdict['recommendation']} · {overall}/10", "ok")
    await ctx.emit.partial("verdict", verdict)
    await ctx.finish(aid, layer, verdict)
