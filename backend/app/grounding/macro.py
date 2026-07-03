"""Official macro series from the World Bank API — key-free, fail-soft.

Every figure returned carries its indicator id and a citable URL, so macro
numbers land on the evidence board fully sourced (Constitution #1).
"""
from __future__ import annotations

from typing import Any

import httpx

COUNTRY = {"India": "IND", "US": "USA", "Europe": "EMU", "Global": "WLD", "SEA": "IDN"}

INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": "GDP growth (annual %)",
    "FP.CPI.TOTL.ZG": "Inflation, consumer prices (annual %)",
    "FR.INR.LEND": "Lending interest rate (%)",
    "SL.UEM.TOTL.ZS": "Unemployment (% of labour force)",
}


async def series(geography: str) -> list[dict[str, Any]]:
    """Latest non-null value per indicator: [{name, value, year, source_url}]."""
    iso = COUNTRY.get(geography, "IND")
    out: list[dict[str, Any]] = []
    try:
        async with httpx.AsyncClient(timeout=15.0) as c:
            for code, name in INDICATORS.items():
                url = f"https://api.worldbank.org/v2/country/{iso}/indicator/{code}"
                r = await c.get(url, params={"format": "json", "per_page": 6})
                if r.status_code != 200:
                    continue
                body = r.json()
                rows = body[1] if isinstance(body, list) and len(body) > 1 and body[1] else []
                latest = next((row for row in rows if row.get("value") is not None), None)
                if latest:
                    out.append({
                        "indicator": code,
                        "name": name,
                        "value": round(float(latest["value"]), 2),
                        "year": latest.get("date", ""),
                        "country": iso,
                        "source_url": f"https://data.worldbank.org/indicator/{code}?locations={iso}",
                    })
    except Exception:
        return out  # partial results are still evidence
    return out
