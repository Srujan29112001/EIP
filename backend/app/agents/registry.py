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
    # L0 — Orchestration (Intelligent Mode: the Advisory Engine pair)
    AgentMeta("boss", "Boss", "L0", "gateway", "t3", "Conversational intake — a real dialogue distilled into the structured Brief", True),
    AgentMeta("manager", "Manager", "L0", "gateway", "t3", "Dynamic orchestrator — plans the board from the whole pool, within the guaranteed spine", True),
    # L0 — Gateway
    AgentMeta("intake_parser", "Intake Parser", "L0", "gateway", "t1", "Turns your words into a structured brief", True),
    AgentMeta("context_profiler", "Context Profiler", "L0", "gateway", "t1", "Works out who is asking — stage, capital, risk", True),
    AgentMeta("scope_planner", "Scope Planner", "L0", "gateway", "t1", "Decides which specialists to convene", True),
    # L1 — Grounding
    AgentMeta("web_researcher", "Web Researcher", "L1", "grounding", "t2", "Live web evidence — competitors, markets, claims", True),
    AgentMeta("news_intel", "News Intelligence", "L1", "grounding", "t2", "What is happening right now in this space", True),
    AgentMeta("market_data", "Market Data", "L1", "grounding", "t0", "Live prices & fundamentals (NSE/BSE/global, True)"),
    AgentMeta("macro_data", "Macro Data", "L1", "grounding", "t0", "GDP, inflation, rates from official series", True),
    AgentMeta("doc_analyst", "Document Analyst", "L1", "grounding", "t2", "Reads your pitch deck, plan, contracts", True),
    AgentMeta("sentiment_analyst", "Sentiment Analyst", "L1", "grounding", "t2", "Social/news sentiment as a live demand signal", True),
    AgentMeta("rag_memory", "RAG Memory", "L1", "grounding", "t0", "Indexes the board — every specialist retrieves its own most-relevant evidence", True),
    # L2 — Venture
    AgentMeta("market_analyst", "Market Analyst", "L2", "venture", "t2", "Market size, growth, competition — sourced", True),
    AgentMeta("market_research", "Market Research", "L2", "venture", "t2", "Primary demand signals — surveys, search, cohort pull", True),
    AgentMeta("finance_modeler", "Finance Modeler", "L2", "venture", "t2", "Unit economics, runway, breakeven — real math", True),
    AgentMeta("banking", "Banker & Capital", "L2", "venture", "t2", "Loans, working capital, schemes, investor-grade capital stack", True),
    AgentMeta("competitor_intel", "Competitor Intelligence", "L2", "venture", "t2", "Positioning map and moat analysis", True),
    AgentMeta("business_model", "Business Model", "L2", "venture", "t2", "Canvas analysis + model recommendation", True),
    AgentMeta("gtm_distribution", "GTM & Distribution", "L2", "venture", "t2", "Channels, launch sequence, CAC reality", True),
    AgentMeta("marketing_strategy", "Marketing Strategist", "L2", "venture", "t2", "Brand, acquisition, growth loops", True),
    AgentMeta("legal", "Legal", "L2", "venture", "t2", "Contracts, structure, IP exposure", True),
    AgentMeta("tax", "Tax (India-first, True)", "L2", "venture", "t2", "GST, income tax, optimization"),
    AgentMeta("policy_compliance", "Policy & Compliance", "L2", "venture", "t2", "Acts, rules, compliance calendar", True),
    AgentMeta("regulator", "Regulator Analysis", "L2", "venture", "t2", "SEBI / RBI / CCI / FSSAI exposure", True),
    AgentMeta("subsidies_schemes", "Subsidies & Schemes", "L2", "venture", "t2", "Government money you are leaving on the table", True),
    AgentMeta("pricing_strategist", "Pricing Strategist", "L2", "venture", "t2", "Van-Westendorp / value-based pricing, WTP bands", True),
    AgentMeta("supply_chain", "Supply-Chain Analyst", "L2", "venture", "t2", "Input dependency, single-source fragility, logistics cost", True),
    AgentMeta("cap_table", "Cap-Table Modeler", "L2", "venture", "t2", "Round math, ESOP, dilution across scenarios", True),
    AgentMeta("patent_ip", "Patent / IP Scout", "L2", "venture", "t2", "Prior-art & freedom-to-operate signals", True),
    AgentMeta("insurance_risk", "Insurance & Risk-Transfer", "L2", "venture", "t2", "What's insurable, what liability to transfer", True),
    AgentMeta("ai_ml_strategist", "AI & ML Strategist", "L2", "venture", "t3", "AI feasibility, build-vs-buy, data moats, AI governance", True),
    AgentMeta("data_analytics", "Data Science & Analytics", "L2", "venture", "t2", "Metric tree, instrumentation, what's honestly predictable", True),
    AgentMeta("software_architecture", "Software Architecture", "L2", "venture", "t3", "Technical feasibility, build cost/time, the scaling wall", True),
    AgentMeta("product_ux", "Product & UX Design", "L2", "venture", "t2", "The core loop, PMF signals, onboarding friction", True),
    AgentMeta("cybersecurity_privacy", "Cybersecurity & Privacy", "L2", "venture", "t2", "Threat model, privacy-by-design, certification readiness", True),
    AgentMeta("fundraising_capital", "Fundraising & Capital", "L2", "venture", "t2", "Round strategy, investor match, terms to never sign", True),
    AgentMeta("sales_revops", "Sales & Revenue Ops", "L2", "venture", "t2", "Sales motion, pipeline math, comp that doesn't backfire", True),
    AgentMeta("partnerships_bd", "Partnerships & BD", "L2", "venture", "t2", "Alliances, deal structures, what never to exclusivity away", True),
    AgentMeta("community_ecosystem", "Community & Ecosystem", "L2", "venture", "t2", "Turns users into a compounding network and moat (Orchestra player)", True),
    AgentMeta("brand_creative", "Brand & Creative", "L2", "venture", "t2", "Identity, naming, the positioning territory to own", True),
    AgentMeta("pr_communications", "PR & Communications", "L2", "venture", "t2", "Media angles, the outlets that matter, crisis comms", True),
    AgentMeta("industry_expert", "Industry Expert", "L2", "venture", "t2", "Sector-specific dynamics and benchmarks", True),
    AgentMeta("hr_talent", "HR & Talent", "L2", "venture", "t2", "Team, salaries, hiring plan", True),
    AgentMeta("optimization_predictor", "Optimization Predictor", "L2", "venture", "t2", "Legal/tax optimizations and their risks", True),
    # L2 — Markets
    AgentMeta("stock_analyst", "Stock Analyst", "L2", "markets", "t2", "Fundamentals + narrative for any listed company", True),
    AgentMeta("technical_analyst", "Technical Analyst", "L2", "markets", "t0", "40+ indicators, multi-timeframe — pure math", True),
    AgentMeta("quant_signals", "Quant Signals", "L2", "markets", "t0", "Regime detection, volatility, probability cones", True),
    AgentMeta("risk_manager", "Risk Manager", "L2", "markets", "t0", "Position sizing, exposure, stop discipline", True),
    AgentMeta("options_desk", "Options & Derivatives", "L2", "markets", "t2", "Chains, greeks, defined-risk structures", True),
    AgentMeta("fund_analyst", "Fund Analyst", "L2", "markets", "t2", "Mutual funds, ETFs, hedge strategies", True),
    AgentMeta("microstructure", "HFT / Microstructure", "L2", "markets", "t2", "Educational — how the plumbing works", True),
    AgentMeta("backtest_engineer", "Backtest Engineer", "L2", "markets", "t0", "Every signal proves itself on history first", True),
    # L2 — Wealth
    AgentMeta("salary_budget", "Salary & Budget", "L2", "wealth", "t2", "Cashflow, savings rate, budget design", True),
    AgentMeta("portfolio_allocator", "Portfolio Allocator", "L2", "wealth", "t0", "Asset allocation for your goals & risk", True),
    AgentMeta("debt_banking", "Debt & Banking", "L2", "wealth", "t2", "Loans, credit, banking products", True),
    AgentMeta("fire_planner", "FIRE / Goal Planner", "L2", "wealth", "t0", "When does money stop being the constraint", True),
    AgentMeta("real_estate", "Real Estate", "L2", "wealth", "t2", "Property, REITs, rent-vs-buy math", True),
    AgentMeta("location_scout", "Location Opportunity Scout", "L2", "wealth", "t2", "Money & venture opportunities where you are", True),
    # L2 — World
    AgentMeta("macroeconomist", "Macroeconomist", "L2", "world", "t2", "Rates, inflation, cycles — what it means for you", True),
    AgentMeta("geopolitics", "Geopolitics", "L2", "world", "t2", "Conflicts, sanctions, supply chains", True),
    AgentMeta("intl_markets", "International Markets", "L2", "world", "t2", "Cross-border expansion and exposure", True),
    AgentMeta("trends", "Trends & Weak Signals", "L2", "world", "t2", "What is emerging before it is obvious", True),
    AgentMeta("esg_impact", "ESG & Impact", "L2", "world", "t2", "Sustainability, ethics, impact economics", True),
    AgentMeta("sustainability_accountant", "Sustainability Accountant", "L2", "world", "t2", "Carbon/impact quantified into cost & moat", True),
    AgentMeta("deep_tech", "Emerging / Deep Tech", "L2", "world", "t2", "Frontier-tech maturity (TRL) and realistic feasibility", True),
    # L2 — Human layer (blueprint: behaviour, needs, consumer, production, philosophy, money-happiness, philanthropy)
    AgentMeta("human_behaviour", "Human Behaviour", "L2", "human", "t2", "How real people will actually behave toward this", True),
    AgentMeta("human_needs", "Human Needs", "L2", "human", "t2", "Does this serve a real, durable need (Maslow)", True),
    AgentMeta("consumer_analysis", "Consumer Analysis", "L2", "human", "t2", "Segments, willingness to pay, purchase journey", True),
    AgentMeta("production_ops", "Production & Ops", "L2", "human", "t2", "Making the thing: inputs, capacity, fragility", True),
    AgentMeta("philosophy_ethics", "Philosophy & Ethics", "L2", "human", "t3", "The examined view — stakeholders, second-order effects", True),
    AgentMeta("money_happiness", "Money & Happiness", "L2", "human", "t2", "Will this actually buy a better life", True),
    AgentMeta("philanthropy_impact", "Philanthropy & Impact", "L2", "human", "t2", "Where doing good compounds the mission", True),
    AgentMeta("cohort_retention", "Cohort / Retention Analyst", "L2", "human", "t2", "Retention curves, LTV by cohort, churn drivers", True),
    AgentMeta("customer_success", "Customer Success & Retention", "L2", "human", "t2", "Onboarding, activation, expansion, churn saves — the operating plan", True),
    AgentMeta("founder_coaching", "Founder Coaching & Org", "L2", "human", "t2", "The founder's leverage, decision hygiene, org & culture for scale", True),
    # L3 — Crucible
    AgentMeta("red_team", "Red Team", "L3", "crucible", "t3", "Attacks the thesis with evidence", True),
    AgentMeta("devils_advocate", "Devil's Advocate", "L3", "crucible", "t3", "Steel-mans the NO case", True),
    AgentMeta("bias_auditor", "Bias Auditor", "L3", "crucible", "t3", "Names the biases in your framing", True),
    AgentMeta("fact_checker", "Fact Checker", "L3", "crucible", "t2", "Spot-checks claims against the evidence board", True),
    # L4 — Synthesis
    AgentMeta("connecting_dots", "Connecting Dots", "L4", "synthesis", "t3", "Cross-domain patterns and second-order effects", True),
    AgentMeta("cross_pollinate", "Cross-Pollinator", "L4", "synthesis", "t3", "Every specialist read against every other — synergies & tensions", True),
    AgentMeta("compliance_scan", "Compliance Sentinel", "L4", "synthesis", "t0", "Deterministic regulatory red-flag scan — nothing missed", True),
    AgentMeta("storytelling", "Storyteller", "L4", "synthesis", "t3", "Turns the verdict into a pitch — hook, narrative, one-liner", True),
    AgentMeta("scenario_planner", "Scenario Planner", "L4", "synthesis", "t0", "Monte-Carlo the verdict — P10/P50/P90 + what breaks it", True),
    AgentMeta("negotiation_coach", "Negotiation Coach", "L4", "synthesis", "t3", "BATNA, anchor, concessions for the next conversation", True),
    AgentMeta("weighing_engine", "Weighing Engine", "L4", "synthesis", "t0", "Deterministic scoring — disagreement preserved", True),
    AgentMeta("verdict_composer", "Verdict Composer", "L4", "synthesis", "t3", "The decision document, with sensitivities", True),
    AgentMeta("visualizer", "Visualizer", "L4", "synthesis", "t2", "Best-fit interactive charts for every insight", True),
    AgentMeta("reporter", "Reporter", "L4", "synthesis", "t3", "The full written decision report", True),
    # L5 — Memory
    AgentMeta("decision_graph", "Decision Graph", "L5", "memory", "t0", "Every run becomes memory you can see"),
    AgentMeta("outcome_tracker", "Outcome Tracker", "L5", "memory", "t0", "Graded outcomes → GO hit-rate calibration + learned weights", True),
]

BY_ID: dict[str, AgentMeta] = {a.id: a for a in ROSTER}
IMPLEMENTED: list[str] = [a.id for a in ROSTER if a.implemented]
