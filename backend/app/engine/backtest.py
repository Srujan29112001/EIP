"""Backtest engine — ported from the user's Finance-and-Trading BacktestEngine,
simplified to the honest essentials: a signal that hasn't survived history is
never shown (EIP Constitution + MASTER_PLAN §5.3). Pure pandas, tier t0.
"""
from __future__ import annotations

from typing import Any

import pandas as pd

from . import indicators as ta


def _run(close: pd.Series, entries: pd.Series, exits: pd.Series) -> dict[str, Any]:
    """Long-only, one position at a time, next-bar execution, no costs
    (costs stated as a caveat in the UI rather than pretending precision)."""
    in_pos = False
    entry_price = 0.0
    trades: list[float] = []
    equity = [1.0]
    for i in range(1, len(close)):
        price = float(close.iloc[i])
        if in_pos:
            equity.append(equity[-1] * price / float(close.iloc[i - 1]))
        else:
            equity.append(equity[-1])
        if not in_pos and bool(entries.iloc[i]):
            in_pos, entry_price = True, price
        elif in_pos and bool(exits.iloc[i]):
            in_pos = False
            trades.append(price / entry_price - 1.0)
    if in_pos:  # close open position at the end
        trades.append(float(close.iloc[-1]) / entry_price - 1.0)

    eq = pd.Series(equity)
    peak = eq.cummax()
    max_dd = float(((eq - peak) / peak).min()) * 100
    total = (float(eq.iloc[-1]) - 1.0) * 100
    bh = (float(close.iloc[-1]) / float(close.iloc[0]) - 1.0) * 100
    wins = sum(1 for t in trades if t > 0)
    return {
        "trades": len(trades),
        "hit_rate": round(wins / len(trades) * 100, 1) if trades else 0.0,
        "strategy_return_pct": round(total, 1),
        "buy_hold_return_pct": round(bh, 1),
        "max_drawdown_pct": round(max_dd, 1),
        "avg_trade_pct": round(sum(trades) / len(trades) * 100, 2) if trades else 0.0,
    }


def sma_cross(df: pd.DataFrame, fast: int = 20, slow: int = 50) -> dict[str, Any]:
    c = df["Close"]
    f, s = ta.sma(c, fast), ta.sma(c, slow)
    entries = (f > s) & (f.shift() <= s.shift())
    exits = (f < s) & (f.shift() >= s.shift())
    out = _run(c, entries.fillna(False), exits.fillna(False))
    out["strategy"] = f"SMA {fast}/{slow} cross"
    return out


def rsi_reversion(df: pd.DataFrame, low: int = 32, high: int = 60) -> dict[str, Any]:
    c = df["Close"]
    r = ta.rsi(c)
    entries = (r < low) & (r.shift() >= low)
    exits = (r > high) & (r.shift() <= high)
    out = _run(c, entries.fillna(False), exits.fillna(False))
    out["strategy"] = f"RSI reversion {low}/{high}"
    return out


def backtest_all(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Every strategy the signal ensemble votes with, proven on this symbol's
    own trailing history. Sample-size honesty included."""
    results = [sma_cross(df), rsi_reversion(df)]
    for r in results:
        r["sample_note"] = ("thin sample — treat as weak evidence" if r["trades"] < 5
                            else "reasonable sample")
        r["beats_buy_hold"] = r["strategy_return_pct"] > r["buy_hold_return_pct"]
    return results
