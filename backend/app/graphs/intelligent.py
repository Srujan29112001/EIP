"""Intelligent Mode — the Advisory Engine (the 4th mode).

This is NOT a fourth pipeline. It is the meta-layer the blueprint describes
(final-2.html Diagram 4 · Playbook Upgrade B): the 🎩 Boss runs a conversation
and CLASSIFIES the engagement — Founder, Trader, Wealth or Operator — and the
🎼 Manager then routes to THAT engagement's real board and deterministic cores.
A trader question and a founder question are different jobs, so they engage
visibly different pipelines.

So `run_intelligent` classifies, then DELEGATES to the matching pipeline with
`advisory=True`. Each pipeline, seeing that flag, runs the Advisory-Engine
wrappers on top of its normal flow:
    🎩 boss_brief   — distil the conversation into the brief (+ lift the ticker
                      / money figures the trader / wealth desks need)
    🎼 manager_plan — brief-specific dynamic routing within the mode's spine
    ✅ qa_gate       — blocking accuracy gate + re-dispatch, BEFORE the reporter
    🧑‍⚖️ hitl        — human review of regulated content before publish

Operator maps onto the venture scaffold (scaling a company is still venture
analysis) with an ops-weighted Manager roster.
"""
from __future__ import annotations

from ..agents.orchestra import classify_engagement, _MODE_LABEL, _MODE_DESK
from ..core.events import Emitter
from .trading import run_trading
from .venture import run_venture
from .wealth import run_wealth


async def run_intelligent(run_id: str, payload: dict, emitter: Emitter) -> None:
    # the Boss's classification (sent by the frontend intake) decides the board;
    # fall back to a deterministic keyword classifier for API callers
    mode = classify_engagement(payload)
    payload = {**payload, "advisory": True, "engagement_mode": mode, "mode": mode}
    await emitter.log("boss",
                      f"🎩 Intelligent Mode · engagement classified as {_MODE_LABEL.get(mode, mode)} "
                      f"({_MODE_DESK.get(mode, '')}) — routing to that board with the dynamic "
                      "Manager, a blocking QA gate, and human review of regulated content", "info")
    pipeline = (run_trading if mode == "trader"
                else run_wealth if mode == "wealth"
                else run_venture)   # founder + operator both use the venture scaffold
    await pipeline(run_id, payload, emitter)
