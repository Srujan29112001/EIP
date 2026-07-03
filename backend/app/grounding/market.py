"""Live market pulse via yfinance — key-free, fail-soft (returns {} / []).

Founder mode uses this as *timing context* (index momentum, sector proxy);
Trader mode (Phase 4) will build its full data plane on the same module.
"""
from __future__ import annotations

import asyncio
from typing import Any

# Indian sector proxies that resolve reliably on Yahoo Finance. Keys are matched
# against the brief's industry/keywords; NIFTY 50 is always fetched as baseline.
SECTOR_TICKERS: dict[str, tuple[str, str]] = {
    "pharma": ("SUNPHARMA.NS", "Sun Pharma (pharma proxy)"),
    "health": ("APOLLOHOSP.NS", "Apollo Hospitals (healthcare proxy)"),
    "supplement": ("DABUR.NS", "Dabur (ayurveda/FMCG-wellness proxy)"),
    "ayurved": ("DABUR.NS", "Dabur (ayurveda/FMCG-wellness proxy)"),
    "food": ("NESTLEIND.NS", "Nestlé India (packaged foods proxy)"),
    "snack": ("BRITANNIA.NS", "Britannia (snacking proxy)"),
    "fmcg": ("HINDUNILVR.NS", "Hindustan Unilever (FMCG proxy)"),
    "beauty": ("HINDUNILVR.NS", "Hindustan Unilever (FMCG proxy)"),
    "fashion": ("TRENT.NS", "Trent (retail/fashion proxy)"),
    "retail": ("DMART.NS", "DMart (retail proxy)"),
    "ecommerce": ("NYKAA.NS", "Nykaa (D2C/e-commerce proxy)"),
    "d2c": ("NYKAA.NS", "Nykaa (D2C/e-commerce proxy)"),
    "fintech": ("PAYTM.NS", "Paytm (fintech proxy)"),
    "bank": ("HDFCBANK.NS", "HDFC Bank (banking proxy)"),
    "software": ("TCS.NS", "TCS (IT services proxy)"),
    "saas": ("TCS.NS", "TCS (IT services proxy)"),
    "tech": ("INFY.NS", "Infosys (tech proxy)"),
    "auto": ("MARUTI.NS", "Maruti Suzuki (auto proxy)"),
    "ev": ("TATAMOTORS.NS", "Tata Motors (EV/auto proxy)"),
    "energy": ("RELIANCE.NS", "Reliance (energy proxy)"),
    "solar": ("ADANIGREEN.NS", "Adani Green (renewables proxy)"),
    "logistics": ("DELHIVERY.NS", "Delhivery (logistics proxy)"),
    "hotel": ("INDHOTEL.NS", "Indian Hotels (hospitality proxy)"),
    "travel": ("INDIGO.NS", "IndiGo (travel proxy)"),
    "real estate": ("DLF.NS", "DLF (real-estate proxy)"),
    "education": ("NIITLTD.NS", "NIIT (education proxy)"),
}

INDEX = {"India": ("^NSEI", "NIFTY 50"), "US": ("^GSPC", "S&P 500"),
         "Europe": ("^STOXX50E", "EURO STOXX 50"), "Global": ("^GSPC", "S&P 500 (global proxy)"),
         "SEA": ("^STI", "Straits Times Index")}


def _pulse_sync(symbol: str, label: str) -> dict[str, Any]:
    import yfinance as yf
    hist = yf.Ticker(symbol).history(period="1y", auto_adjust=True)
    if hist.empty or len(hist) < 30:
        return {}
    close = hist["Close"]
    last = float(close.iloc[-1])
    ret_1y = (last / float(close.iloc[0]) - 1.0) * 100
    ret_3m = (last / float(close.iloc[-63]) - 1.0) * 100 if len(close) > 63 else 0.0
    # annualised volatility from daily returns
    daily = close.pct_change().dropna()
    vol = float(daily.std()) * (252 ** 0.5) * 100 if len(daily) > 10 else 0.0
    # ~weekly sampled series → the frontend's interactive past/future chart
    weekly = close.iloc[::5]
    series = [[idx.strftime("%Y-%m-%d"), round(float(val), 2)] for idx, val in weekly.items()][-60:]
    return {
        "symbol": symbol, "label": label, "last": round(last, 2),
        "ret_1y_pct": round(ret_1y, 1), "ret_3m_pct": round(ret_3m, 1),
        "volatility_pct": round(vol, 1),
        "series": series,
        "source_url": f"https://finance.yahoo.com/quote/{symbol}",
    }


async def pulse(symbol: str, label: str) -> dict[str, Any]:
    try:
        return await asyncio.wait_for(asyncio.to_thread(_pulse_sync, symbol, label), timeout=25)
    except Exception:
        return {}


def sector_for(text: str) -> tuple[str, str] | None:
    lower = text.lower()
    for key, pair in SECTOR_TICKERS.items():
        if key in lower:
            return pair
    return None
