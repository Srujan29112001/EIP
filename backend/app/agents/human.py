"""The human layer — the seven agents that ask whether the numbers serve a
human life, not just a spreadsheet. Present in ALL three modes: a venture, a
trade and a savings plan are all ultimately decisions by and about people.

Ports the spirit of the legacy generation's human_behaviour / human_needs /
philosophy_ethics / money_happiness / philanthropy agents onto the new
blackboard contract.
"""
from __future__ import annotations

from .base import Ctx
from .board import _lens


async def human_behaviour(ctx: Ctx) -> None:
    await _lens(ctx, "human_behaviour",
        "You are a behavioural psychologist of markets and customers: buying triggers, habit loops, "
        "loss aversion, status signalling, friction points. You analyse how REAL people will behave "
        "toward this decision's product/asset/plan — not how a rational agent would.",
        "Predict the human behaviour that decides this outcome: the 2 psychological forces working "
        "FOR it, the 2 working AGAINST it, and the single behavioural design change with the biggest "
        "payoff. Score 0-10 for behavioural tailwind.",
        "Behavioural read needs a model — no deterministic prior")


async def human_needs(ctx: Ctx) -> None:
    await _lens(ctx, "human_needs",
        "You are a human-needs analyst (Maslow, Max-Neef): does this serve a real, durable need — "
        "physiological, safety, belonging, esteem, self-actualisation — or a transient want?",
        "Map this decision to the needs hierarchy: which need it truly serves, how durable that need "
        "is through a downturn, and whether the need is felt strongly enough to be paid for. "
        "Score 0-10 for need-realness.",
        "Needs mapping needs a model", 5.5)


async def consumer_analysis(ctx: Ctx) -> None:
    await _lens(ctx, "consumer_analysis",
        "You are a consumer-insights analyst: segments, willingness to pay, purchase journey, "
        "switching costs, review culture. India-first when the geography says so.",
        "Profile the real consumer here: the 2 segments most likely to pay, their willingness-to-pay "
        "band [ESTIMATE unless evidenced], where they discover and decide, and the switching cost "
        "keeping them where they are. Score 0-10 for consumer pull.",
        "Consumer profile needs a model")


async def production_ops(ctx: Ctx) -> None:
    await _lens(ctx, "production_ops",
        "You are a production and operations analyst: making the thing, sourcing, unit costs, "
        "capacity, quality control, supply-chain fragility.",
        "Lay out the production reality: the critical inputs and where they come from, the step most "
        "likely to break at 10× volume, and one cost lever. Score 0-10 for production feasibility.",
        "Ops read needs a model", 5.5)


async def philosophy_ethics(ctx: Ctx) -> None:
    await _lens(ctx, "philosophy_ethics",
        "You are the board's philosopher: ethics, stakeholder effects, second-order consequences, "
        "and whether the decision is one the decider will be proud of in ten years. Practical "
        "philosophy, not sermon.",
        "Give the examined view: who bears the costs of this succeeding, the strongest ethical "
        "objection stated fairly, and the version of this decision the decider respects most. "
        "Score 0-10 for ethical soundness.",
        "The examined view needs a model", 6.0)


async def money_happiness(ctx: Ctx) -> None:
    await _lens(ctx, "money_happiness",
        "You are a money-and-wellbeing analyst (hedonic adaptation, time-vs-money research, FIRE "
        "psychology): will this decision actually buy a better life for this specific person?",
        "Assess the happiness math: what this costs in time/stress vs what it buys in security/"
        "freedom, where hedonic adaptation will erase the gain, and the cheapest change that buys "
        "the most wellbeing. Score 0-10 for life-fit.",
        "Life-fit read needs a model", 6.0)


async def philanthropy_impact(ctx: Ctx) -> None:
    await _lens(ctx, "philanthropy_impact",
        "You are an impact and philanthropy analyst: social return, giving strategies, NGO "
        "partnerships, and where doing good compounds the mission commercially.",
        "Find the impact angle: the social good this could genuinely create, one giving/partnership "
        "structure that fits (CSR, 1% pledge, NGO alliance), and where impact becomes a moat rather "
        "than a cost. Score 0-10 for impact leverage.",
        "Impact read needs a model", 5.5)


HUMAN_AGENTS = {
    "human_behaviour": human_behaviour,
    "human_needs": human_needs,
    "consumer_analysis": consumer_analysis,
    "production_ops": production_ops,
    "philosophy_ethics": philosophy_ethics,
    "money_happiness": money_happiness,
    "philanthropy_impact": philanthropy_impact,
}
