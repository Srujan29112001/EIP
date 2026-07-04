"""The agent catalog — one map of every convocable specialist.

LENS_AGENTS need only the shared blackboard (brief + evidence), so they are
safe to convene in ANY mode. Input-bound deterministic agents (runway math,
OHLCV chain, salary math) stay wired inside their home pipelines.
"""
from __future__ import annotations

from . import board, human, markets, wealth

# blackboard-only lenses — mode-agnostic by construction
LENS_AGENTS = {
    **{k: f for k, f in board.BOARD_AGENTS.items()
       if k not in ("devils_advocate", "connecting_dots")},
    **board.WORLD_WAVE,
    **human.HUMAN_AGENTS,
    "fund_analyst": markets.fund_analyst,
    "options_desk": markets.options_desk,
    "microstructure": markets.microstructure,
    "debt_banking": wealth.debt_banking,
    "real_estate": wealth.real_estate,
    "location_scout": wealth.location_scout,
}

HUMAN_WAVE = list(human.HUMAN_AGENTS.keys())
WORLD_WAVE = list(board.WORLD_WAVE.keys())
VENTURE_WAVE = [k for k in board.BOARD_AGENTS if k not in ("devils_advocate", "connecting_dots")]

# extra lens agents convened per depth, per mode (beyond each mode's core desk)
TRADER_EXTRA = {
    "board": ["macroeconomist", "geopolitics", "trends", "regulator", "industry_expert",
              "human_behaviour", "money_happiness", "philosophy_ethics"],
    "war_room": ["macroeconomist", "geopolitics", "trends", "regulator", "industry_expert",
                 "intl_markets", "esg_impact", "policy_compliance", "optimization_predictor",
                 *HUMAN_WAVE],
}
WEALTH_EXTRA = {
    "board": ["macroeconomist", "trends", "regulator", "fund_analyst",
              "money_happiness", "human_needs", "philosophy_ethics", "philanthropy_impact"],
    "war_room": ["macroeconomist", "trends", "regulator", "fund_analyst", "geopolitics",
                 "intl_markets", "esg_impact", "optimization_predictor", "subsidies_schemes",
                 *HUMAN_WAVE],
}
