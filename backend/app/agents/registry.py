"""The full agent roster (MASTER_PLAN §3.2). `implemented` flips as phases land.

This registry is mirrored by frontend/lib/agents.ts — ids, layers and accents
must stay in sync (they drive the pipeline rail and event rendering).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentMeta:
    id: str
    name: str
    layer: str          # L0..L5
    cluster: str        # gateway|grounding|venture|markets|wealth|world|crucible|synthesis|memory
    tier: str           # t0 (deterministic) | t1 | t2 | t3
    blurb: str
    implemented: bool = False


ROSTER: list[AgentMeta] = [
    # L0 — Gateway
    AgentMeta("intake_parser", "Intake Parser", "L0", "gateway", "t1", "Turns your words into a structured brief", True),
    AgentMeta("context_profiler", "Context Profiler", "L0", "gateway", "t1", "Works out who is asking — stage, capital, risk", True),
    AgentMeta("scope_planner", "Scope Planner", "L0", "gateway", "t1", "Decides which specialists to convene", True),
    # L1 — Grounding
    AgentMeta("web_researcher", "Web Researcher", "L1", "grounding", "t2", "Live web evidence — competitors, markets, claims", True),
    AgentMeta("news_intel", "News Intelligence", "L1", "grounding", "t2", "What is happening right now in this space", True),
    AgentMeta("market_data", "Market Data", "L1", "grounding", "t0", "Live prices & fundamentals (NSE/BSE/global, True)"),
    AgentMeta("macro_data", "Macro Data", "L1", "grounding", "t0", "GDP, inflation, rates from official series", True),
    AgentMeta("doc_analyst", "Document Analyst", "L1", "grounding", "t2", "Reads your pitch deck, plan, contracts"),
    # L2 — Venture
    AgentMeta("market_analyst", "Market Analyst", "L2", "venture", "t2", "Market size, growth, competition — sourced", True),
    AgentMeta("finance_modeler", "Finance Modeler", "L2", "venture", "t2", "Unit economics, runway, breakeven — real math", True),
    AgentMeta("competitor_intel", "Competitor Intelligence", "L2", "venture", "t2", "Positioning map and moat analysis", True),
    AgentMeta("business_model", "Business Model", "L2", "venture", "t2", "Canvas analysis + model recommendation"),
    AgentMeta("gtm_distribution", "GTM & Distribution", "L2", "venture", "t2", "Channels, launch sequence, CAC reality", True),
    AgentMeta("marketing_strategy", "Marketing Strategist", "L2", "venture", "t2", "Brand, acquisition, growth loops"),
    AgentMeta("legal", "Legal", "L2", "venture", "t2", "Contracts, structure, IP exposure", True),
    AgentMeta("tax", "Tax (India-first, True)", "L2", "venture", "t2", "GST, income tax, optimization"),
    AgentMeta("policy_compliance", "Policy & Compliance", "L2", "venture", "t2", "Acts, rules, compliance calendar", True),
    AgentMeta("regulator", "Regulator Analysis", "L2", "venture", "t2", "SEBI / RBI / CCI / FSSAI exposure"),
    AgentMeta("subsidies_schemes", "Subsidies & Schemes", "L2", "venture", "t2", "Government money you are leaving on the table"),
    AgentMeta("industry_expert", "Industry Expert", "L2", "venture", "t2", "Sector-specific dynamics and benchmarks", True),
    AgentMeta("hr_talent", "HR & Talent", "L2", "venture", "t2", "Team, salaries, hiring plan"),
    AgentMeta("optimization_predictor", "Optimization Predictor", "L2", "venture", "t2", "Legal/tax optimizations and their risks"),
    # L2 — Markets
    AgentMeta("stock_analyst", "Stock Analyst", "L2", "markets", "t2", "Fundamentals + narrative for any listed company"),
    AgentMeta("technical_analyst", "Technical Analyst", "L2", "markets", "t0", "40+ indicators, multi-timeframe — pure math"),
    AgentMeta("quant_signals", "Quant Signals", "L2", "markets", "t0", "Regime detection, volatility, probability cones"),
    AgentMeta("risk_manager", "Risk Manager", "L2", "markets", "t0", "Position sizing, exposure, stop discipline"),
    AgentMeta("options_desk", "Options & Derivatives", "L2", "markets", "t2", "Chains, greeks, defined-risk structures"),
    AgentMeta("fund_analyst", "Fund Analyst", "L2", "markets", "t2", "Mutual funds, ETFs, hedge strategies"),
    AgentMeta("microstructure", "HFT / Microstructure", "L2", "markets", "t2", "Educational — how the plumbing works"),
    AgentMeta("backtest_engineer", "Backtest Engineer", "L2", "markets", "t0", "Every signal proves itself on history first"),
    # L2 — Wealth
    AgentMeta("salary_budget", "Salary & Budget", "L2", "wealth", "t2", "Cashflow, savings rate, budget design"),
    AgentMeta("portfolio_allocator", "Portfolio Allocator", "L2", "wealth", "t0", "Asset allocation for your goals & risk"),
    AgentMeta("debt_banking", "Debt & Banking", "L2", "wealth", "t2", "Loans, credit, banking products"),
    AgentMeta("fire_planner", "FIRE / Goal Planner", "L2", "wealth", "t0", "When does money stop being the constraint"),
    AgentMeta("real_estate", "Real Estate", "L2", "wealth", "t2", "Property, REITs, rent-vs-buy math"),
    AgentMeta("location_scout", "Location Opportunity Scout", "L2", "wealth", "t2", "Money & venture opportunities where you are"),
    # L2 — World
    AgentMeta("macroeconomist", "Macroeconomist", "L2", "world", "t2", "Rates, inflation, cycles — what it means for you"),
    AgentMeta("geopolitics", "Geopolitics", "L2", "world", "t2", "Conflicts, sanctions, supply chains"),
    AgentMeta("intl_markets", "International Markets", "L2", "world", "t2", "Cross-border expansion and exposure"),
    AgentMeta("trends", "Trends & Weak Signals", "L2", "world", "t2", "What is emerging before it is obvious"),
    AgentMeta("esg_impact", "ESG & Impact", "L2", "world", "t2", "Sustainability, ethics, impact economics"),
    # L3 — Crucible
    AgentMeta("red_team", "Red Team", "L3", "crucible", "t3", "Attacks the thesis with evidence", True),
    AgentMeta("devils_advocate", "Devil's Advocate", "L3", "crucible", "t3", "Steel-mans the NO case", True),
    AgentMeta("bias_auditor", "Bias Auditor", "L3", "crucible", "t3", "Names the biases in your framing", True),
    AgentMeta("fact_checker", "Fact Checker", "L3", "crucible", "t2", "Spot-checks claims against the evidence board", True),
    # L4 — Synthesis
    AgentMeta("connecting_dots", "Connecting Dots", "L4", "synthesis", "t3", "Cross-domain patterns and second-order effects", True),
    AgentMeta("weighing_engine", "Weighing Engine", "L4", "synthesis", "t0", "Deterministic scoring — disagreement preserved", True),
    AgentMeta("verdict_composer", "Verdict Composer", "L4", "synthesis", "t3", "The decision document, with sensitivities", True),
    # L5 — Memory
    AgentMeta("decision_graph", "Decision Graph", "L5", "memory", "t0", "Every run becomes memory you can see"),
]

BY_ID: dict[str, AgentMeta] = {a.id: a for a in ROSTER}
IMPLEMENTED: list[str] = [a.id for a in ROSTER if a.implemented]
