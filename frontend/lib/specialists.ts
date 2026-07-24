/** Frontend mirror of backend/app/core/specialists.py — KEEP IN SYNC.
 *
 * Each agent is classified by the KIND of thinking its task demands
 * (reasoning · quant · code · research · creative · extraction), and each
 * provider maps every class to its best-fitting model (verified July 2026 —
 * real code specialists: Codestral, Qwen-Coder, DeepSeek-V4). The gateway
 * resolves: explicit per-agent route → per-class route → explicit model pick →
 * specialist model → tier default. When unpinned, code/reasoning agents PREFER
 * OpenRouter (widest catalog of fine-tunes) if keyed. Routing is STRICT — the
 * resolved model is the only one tried; failures surface their reason.
 * NOTE: true domain-expert LLMs (finance/legal) aren't API-served; these are
 * the best *task-matched* general/specialist models available.
 */

export type SpecClass = "reasoning" | "quant" | "code" | "research" | "creative" | "extraction";

export const CLASS_META: Record<SpecClass, { icon: string; label: string; blurb: string }> = {
  reasoning: { icon: "🧠", label: "Deep reasoning", blurb: "crucible attacks, verdicts, law & policy — multi-step judgment" },
  quant: { icon: "📐", label: "Quant & math", blurb: "financial models, indicators, simulations — numbers must be right" },
  code: { icon: "💻", label: "Code & engineering", blurb: "architecture, security, data pipelines — code-tuned models" },
  research: { icon: "🔎", label: "Research & synthesis", blurb: "market landscapes, comparisons — breadth over depth" },
  creative: { icon: "🎨", label: "Narrative & persuasion", blurb: "the pitch, the report, negotiation scripts" },
  extraction: { icon: "⚡", label: "Parse & structure", blurb: "intake, scraping, classification — fast and cheap wins" },
};

export const SPECIALIZATION: Record<string, SpecClass> = {
  boss: "reasoning", manager: "reasoning",
  red_team: "reasoning", devils_advocate: "reasoning",
  bias_auditor: "reasoning", fact_checker: "reasoning",
  connecting_dots: "reasoning", cross_pollinate: "reasoning",
  verdict_composer: "reasoning",
  legal: "reasoning", tax: "reasoning", policy_compliance: "reasoning",
  regulator: "reasoning", patent_ip: "reasoning", insurance_risk: "reasoning",
  cybersecurity_privacy: "code", philosophy_ethics: "reasoning",
  macroeconomist: "reasoning", geopolitics: "reasoning",
  industry_expert: "reasoning", deep_tech: "code",
  finance_modeler: "quant", quant_signals: "quant",
  technical_analyst: "quant", backtest_engineer: "code",
  options_desk: "quant", microstructure: "quant",
  risk_manager: "quant", stock_analyst: "quant", fund_analyst: "quant",
  salary_budget: "quant", portfolio_allocator: "quant",
  fire_planner: "quant", debt_banking: "quant", real_estate: "quant",
  cap_table: "quant", optimization_predictor: "quant",
  data_analytics: "code", scenario_planner: "quant",
  weighing_engine: "quant",
  market_analyst: "research", market_research: "research",
  competitor_intel: "research", business_model: "research",
  banking: "research", subsidies_schemes: "research",
  pricing_strategist: "research", supply_chain: "research",
  fundraising_capital: "research", sales_revops: "research",
  partnerships_bd: "research", hr_talent: "research",
  ai_ml_strategist: "code", software_architecture: "code",
  intl_markets: "research", trends: "research",
  esg_impact: "research", sustainability_accountant: "research",
  location_scout: "research", human_needs: "research",
  consumer_analysis: "research", production_ops: "research",
  money_happiness: "research", philanthropy_impact: "research",
  cohort_retention: "research", customer_success: "research",
  human_behaviour: "research",
  storytelling: "creative", reporter: "creative",
  negotiation_coach: "creative", brand_creative: "creative",
  pr_communications: "creative", marketing_strategy: "creative",
  gtm_distribution: "creative", community_ecosystem: "creative",
  founder_coaching: "creative", product_ux: "creative",
  intake_parser: "extraction", context_profiler: "extraction",
  scope_planner: "extraction", web_researcher: "extraction",
  news_intel: "extraction", doc_analyst: "extraction",
  sentiment_analyst: "extraction", rag_memory: "extraction",
  visualizer: "extraction", compliance_scan: "extraction",
  decision_graph: "extraction", outcome_tracker: "extraction",
};

export const SPECIALIST_MODELS: Record<string, Record<SpecClass, string>> = {
  groq: {
    reasoning: "openai/gpt-oss-120b", quant: "qwen/qwen3.6-27b", code: "qwen/qwen3.6-27b",
    research: "llama-3.3-70b-versatile", creative: "llama-3.3-70b-versatile",
    extraction: "llama-3.1-8b-instant",
  },
  openrouter: {
    reasoning: "deepseek/deepseek-r1", quant: "deepseek/deepseek-r1", code: "qwen/qwen3-coder-plus",
    research: "deepseek/deepseek-chat", creative: "deepseek/deepseek-chat",
    extraction: "openai/gpt-oss-20b",
  },
  deepseek: {
    reasoning: "deepseek-v4-pro", quant: "deepseek-v4-pro", code: "deepseek-v4-pro",
    research: "deepseek-v4-flash", creative: "deepseek-v4-flash", extraction: "deepseek-v4-flash",
  },
  mistral: {
    reasoning: "magistral-medium-2506", quant: "magistral-medium-2506", code: "codestral-latest",
    research: "mistral-large-latest", creative: "mistral-large-latest", extraction: "mistral-small-latest",
  },
  anthropic: {
    reasoning: "claude-opus-4-8", quant: "claude-sonnet-4-6", code: "claude-sonnet-4-6",
    research: "claude-haiku-4-5", creative: "claude-sonnet-4-6", extraction: "claude-haiku-4-5",
  },
  google: {
    reasoning: "gemini-3-pro-preview", quant: "gemini-3-pro-preview", code: "gemini-3-pro-preview",
    research: "gemini-3.6-flash", creative: "gemini-3.6-flash", extraction: "gemini-3.5-flash-lite",
  },
  openai: {
    reasoning: "gpt-5.5", quant: "gpt-5.5", code: "gpt-5.5",
    research: "gpt-5.5", creative: "gpt-5.5", extraction: "gpt-5.4-nano",
  },
  xai: {
    reasoning: "grok-4", quant: "grok-4", code: "grok-4",
    research: "grok-3-mini", creative: "grok-4", extraction: "grok-3-mini",
  },
};

export function specialistModel(agentId: string, provider: string): string {
  const cls = SPECIALIZATION[agentId];
  if (!cls) return "";
  return SPECIALIST_MODELS[provider]?.[cls] ?? "";
}
