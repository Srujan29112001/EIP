"""Technical analysis engine — pure pandas, zero LLM (tier t0).

Hand-rolled classics (no pandas-ta dependency): SMA/EMA, RSI, MACD,
Bollinger, ATR, swing support/resistance. Every reading returns a
bullish/bearish/neutral verdict so the UI can render it directly, and
`summary()` folds them into deterministic trend/momentum scores.
"""
from __future__ import annotations

from typing import Any

import pandas as pd


def sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n).mean()


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    delta = close.diff()
    up = delta.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    down = (-delta.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = up / down.replace(0, 1e-9)
    return 100 - 100 / (1 + rs)


def macd(close: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    line = ema(close, 12) - ema(close, 26)
    signal = ema(line, 9)
    return line, signal, line - signal


def bollinger(close: pd.Series, n: int = 20, k: float = 2.0) -> tuple[pd.Series, pd.Series, pd.Series]:
    mid = sma(close, n)
    sd = close.rolling(n).std()
    return mid + k * sd, mid, mid - k * sd


def atr(high: pd.Series, low: pd.Series, close: pd.Series, n: int = 14) -> pd.Series:
    prev = close.shift()
    tr = pd.concat([high - low, (high - prev).abs(), (low - prev).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def swing_levels(close: pd.Series, lookback: int = 60) -> tuple[float, float]:
    """Nearest meaningful support/resistance from recent swing extremes."""
    window = close.tail(lookback)
    return float(window.min()), float(window.max())


def summary(df: pd.DataFrame) -> dict[str, Any]:
    """df: columns Open/High/Low/Close/Volume, daily. Returns the full read."""
    c = df["Close"]
    last = float(c.iloc[-1])
    s20, s50 = sma(c, 20), sma(c, 50)
    s200 = sma(c, 200) if len(c) >= 200 else None
    r = rsi(c)
    m_line, m_sig, m_hist = macd(c)
    bb_u, bb_m, bb_l = bollinger(c)
    a = atr(df["High"], df["Low"], c)
    sup, res = swing_levels(c)

    readings: list[dict[str, Any]] = []

    def add(name: str, value: str, read: str, note: str = "") -> None:
        readings.append({"name": name, "value": value, "read": read, "note": note})

    # trend stack
    above20 = last > float(s20.iloc[-1])
    above50 = last > float(s50.iloc[-1])
    above200 = bool(s200 is not None and last > float(s200.iloc[-1]))
    stack = (float(s20.iloc[-1]) > float(s50.iloc[-1]))
    add("price vs SMA20", f"{'above' if above20 else 'below'} ({s20.iloc[-1]:.1f})",
        "bullish" if above20 else "bearish")
    add("price vs SMA50", f"{'above' if above50 else 'below'} ({s50.iloc[-1]:.1f})",
        "bullish" if above50 else "bearish")
    if s200 is not None:
        add("price vs SMA200", "above" if above200 else "below",
            "bullish" if above200 else "bearish", "long-term trend filter")
    add("SMA20 vs SMA50", "golden stack" if stack else "dead stack",
        "bullish" if stack else "bearish")

    # momentum
    rsi_v = float(r.iloc[-1])
    add("RSI(14)", f"{rsi_v:.0f}",
        "bearish" if rsi_v > 70 else "bullish" if rsi_v < 30 else
        "bullish" if rsi_v >= 55 else "bearish" if rsi_v <= 45 else "neutral",
        "overbought >70 · oversold <30")
    macd_up = float(m_hist.iloc[-1]) > 0
    add("MACD histogram", f"{m_hist.iloc[-1]:+.2f}", "bullish" if macd_up else "bearish")

    # volatility / bands
    atr_pct = float(a.iloc[-1]) / last * 100
    width = (float(bb_u.iloc[-1]) - float(bb_l.iloc[-1])) / float(bb_m.iloc[-1]) * 100
    add("ATR(14)", f"{atr_pct:.1f}% of price",
        "neutral", "position sizing input")
    band_pos = (last - float(bb_l.iloc[-1])) / max(float(bb_u.iloc[-1]) - float(bb_l.iloc[-1]), 1e-9)
    add("Bollinger position", f"{band_pos * 100:.0f}% of band (width {width:.1f}%)",
        "bearish" if band_pos > 0.95 else "bullish" if band_pos < 0.05 else "neutral")

    # deterministic scores (0-10)
    trend_score = 5.0 + (1.2 if above20 else -1.2) + (1.2 if above50 else -1.2) \
        + (1.0 if above200 else (-1.0 if s200 is not None else 0.0)) + (0.6 if stack else -0.6)
    momentum_score = 5.0 + (1.5 if macd_up else -1.5) \
        + (1.5 if 55 <= rsi_v <= 70 else -1.5 if 30 <= rsi_v <= 45 else
           -0.5 if rsi_v > 70 else 0.5 if rsi_v < 30 else 0.0)
    clamp = lambda v: round(max(0.5, min(9.5, v)), 1)  # noqa: E731

    bullish = sum(1 for x in readings if x["read"] == "bullish")
    bearish = sum(1 for x in readings if x["read"] == "bearish")
    return {
        "last": round(last, 2),
        "readings": readings,
        "trend_score": clamp(trend_score),
        "momentum_score": clamp(momentum_score),
        "atr_pct": round(atr_pct, 2),
        "support": round(sup, 2),
        "resistance": round(res, 2),
        "bullish": bullish,
        "bearish": bearish,
        "bias": "bullish" if bullish - bearish >= 2 else "bearish" if bearish - bullish >= 2 else "mixed",
    }
