"""Specialist model routing — the right KIND of model for each agent's job.

A general chat model is a decent analyst, a mediocre mathematician and a
verbose parser. This module classifies every agent by the *kind* of thinking
its task demands and maps each class to the best-fitting model on every
provider, so a run stops sending quant work and poetry to the same brain:

  reasoning   deep multi-step judgment      → reasoning-tuned flagships (R1/QwQ/o4/2.5-pro)
  quant       math, markets, simulations    → reasoning/math models
  research    breadth: retrieve + synthesize→ strong general flagships
  creative    narrative, persuasion, pitch  → strong general flagships
  extraction  parse, structure, classify    → fast cheap siblings

Resolution order in the gateway (highest wins):
  user's explicit per-agent route → user's explicit model pick →
  specialist model for the agent's class (when cfg.specialized) →
  tier default. Routing is STRICT: the resolved model is the only one tried —
  if it fails, the agent reports the reason (no silent sibling/provider swap).
Agents not listed fall through to tier defaults untouched.
"""
from __future__ import annotations

# ── agent → class ─────────────────────────────────────────────────────────────
SPECIALIZATION: dict[str, str] = {
    # deep multi-step judgment (crucible, verdicts, law & policy, geopolitics)
    "boss": "reasoning", "manager": "reasoning",
    "red_team": "reasoning", "devils_advocate": "reasoning",
    "bias_auditor": "reasoning", "fact_checker": "reasoning",
    "connecting_dots": "reasoning", "cross_pollinate": "reasoning",
    "verdict_composer": "reasoning",
    "legal": "reasoning", "tax": "reasoning", "policy_compliance": "reasoning",
    "regulator": "reasoning", "patent_ip": "reasoning", "insurance_risk": "reasoning",
    "cybersecurity_privacy": "reasoning", "philosophy_ethics": "reasoning",
    "macroeconomist": "reasoning", "geopolitics": "reasoning",
    "industry_expert": "reasoning", "deep_tech": "reasoning",
    # math, markets, models, simulations
    "finance_modeler": "quant", "quant_signals": "quant",
    "technical_analyst": "quant", "backtest_engineer": "quant",
    "options_desk": "quant", "microstructure": "quant",
    "risk_manager": "quant", "stock_analyst": "quant", "fund_analyst": "quant",
    "salary_budget": "quant", "portfolio_allocator": "quant",
    "fire_planner": "quant", "debt_banking": "quant", "real_estate": "quant",
    "cap_table": "quant", "optimization_predictor": "quant",
    "data_analytics": "quant", "scenario_planner": "quant",
    "weighing_engine": "quant",
    # breadth: retrieve, compare, synthesize a domain
    "market_analyst": "research", "market_research": "research",
    "competitor_intel": "research", "business_model": "research",
    "banking": "research", "subsidies_schemes": "research",
    "pricing_strategist": "research", "supply_chain": "research",
    "fundraising_capital": "research", "sales_revops": "research",
    "partnerships_bd": "research", "hr_talent": "research",
    "ai_ml_strategist": "research", "software_architecture": "research",
    "intl_markets": "research", "trends": "research",
    "esg_impact": "research", "sustainability_accountant": "research",
    "location_scout": "research", "human_needs": "research",
    "consumer_analysis": "research", "production_ops": "research",
    "money_happiness": "research", "philanthropy_impact": "research",
    "cohort_retention": "research", "customer_success": "research",
    "human_behaviour": "research",
    # narrative, persuasion, coaching
    "storytelling": "creative", "reporter": "creative",
    "negotiation_coach": "creative", "brand_creative": "creative",
    "pr_communications": "creative", "marketing_strategy": "creative",
    "gtm_distribution": "creative", "community_ecosystem": "creative",
    "founder_coaching": "creative", "product_ux": "creative",
    # parse, structure, classify — fast and cheap wins
    "intake_parser": "extraction", "context_profiler": "extraction",
    "scope_planner": "extraction", "web_researcher": "extraction",
    "news_intel": "extraction", "doc_analyst": "extraction",
    "sentiment_analyst": "extraction", "rag_memory": "extraction",
    "visualizer": "extraction", "compliance_scan": "extraction",
    "decision_graph": "extraction", "outcome_tracker": "extraction",
}

# ── provider → class → model ─────────────────────────────────────────────────
# Chosen from each provider's live catalog (probe /models before changing —
# a wrong id now fails VISIBLY instead of silently swapping models).
SPECIALIST_MODELS: dict[str, dict[str, str]] = {
    "groq": {
        "reasoning": "openai/gpt-oss-120b",
        "quant": "qwen/qwen3.6-27b",
        "research": "llama-3.3-70b-versatile",
        "creative": "llama-3.3-70b-versatile",
        "extraction": "llama-3.1-8b-instant",
    },
    "anthropic": {
        "reasoning": "claude-sonnet-4-5",
        "quant": "claude-sonnet-4-5",
        "research": "claude-haiku-4-5",
        "creative": "claude-sonnet-4-5",
        "extraction": "claude-haiku-4-5",
    },
    "openai": {
        "reasoning": "o4-mini",
        "quant": "o4-mini",
        "research": "gpt-5-mini",
        "creative": "gpt-5-mini",
        "extraction": "gpt-5-mini",
    },
    "google": {
        "reasoning": "gemini-2.5-pro",
        "quant": "gemini-2.5-pro",
        "research": "gemini-2.5-flash",
        "creative": "gemini-2.5-flash",
        "extraction": "gemini-2.5-flash-lite",
    },
    "deepseek": {
        "reasoning": "deepseek-reasoner",
        "quant": "deepseek-reasoner",
        "research": "deepseek-chat",
        "creative": "deepseek-chat",
        "extraction": "deepseek-chat",
    },
    "openrouter": {
        "reasoning": "deepseek/deepseek-r1",
        "quant": "deepseek/deepseek-r1",
        "research": "deepseek/deepseek-chat",
        "creative": "deepseek/deepseek-chat",
        "extraction": "deepseek/deepseek-chat",
    },
    "mistral": {
        "reasoning": "magistral-medium-latest",
        "quant": "magistral-medium-latest",
        "research": "mistral-large-latest",
        "creative": "mistral-large-latest",
        "extraction": "mistral-small-latest",
    },
    "xai": {
        "reasoning": "grok-4",
        "quant": "grok-4",
        "research": "grok-3-mini",
        "creative": "grok-4",
        "extraction": "grok-3-mini",
    },
}


def specialist_model(agent: str, provider: str) -> str:
    """The class-fit model for this agent on this provider, or "" (→ tier default)."""
    cls = SPECIALIZATION.get(agent, "")
    if not cls:
        return ""
    return SPECIALIST_MODELS.get(provider, {}).get(cls, "")


def specialization_of(agent: str) -> str:
    return SPECIALIZATION.get(agent, "")
