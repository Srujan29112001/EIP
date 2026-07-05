/** Which agents feed which radar dimension — the client mirror of the backend
 * weighing engines (venture / markets / wealth). Drives per-agent what-if:
 * changing an agent's score shifts its dimension, which shifts the verdict.
 */

const FOUNDER: Record<string, string[]> = {
  Market: ["market_analyst", "market_research", "competitor_intel", "industry_expert", "trends", "consumer_analysis"],
  Economics: ["finance_modeler", "tax", "subsidies_schemes", "banking"],
  Execution: ["gtm_distribution", "business_model", "marketing_strategy", "hr_talent", "production_ops"],
  Regulatory: ["policy_compliance", "legal", "regulator"],
  HumanFit: ["human_behaviour", "human_needs", "money_happiness", "philosophy_ethics", "philanthropy_impact"],
};

const TRADER: Record<string, string[]> = {
  Trend: ["technical_analyst"],
  Momentum: ["technical_analyst"],
  Value: ["stock_analyst"],
  History: ["quant_signals"],
  RiskFit: ["risk_manager"],
  Psychology: ["human_behaviour", "money_happiness", "philosophy_ethics"],
};

const WEALTH: Record<string, string[]> = {
  Cashflow: ["salary_budget"],
  Allocation: ["portfolio_allocator"],
  GoalFit: ["fire_planner"],
  DebtHealth: ["debt_banking"],
  Opportunity: ["real_estate", "location_scout"],
  LifeFit: ["money_happiness", "human_needs", "philosophy_ethics", "philanthropy_impact"],
};

export function dimAgentsMap(dims: Record<string, number>): Record<string, string[]> {
  return "Trend" in dims ? TRADER : "Cashflow" in dims ? WEALTH : FOUNDER;
}

/** the radar dimension an agent contributes to, or null (crucible/synthesis). */
export function dimForAgent(id: string, dims: Record<string, number>): string | null {
  for (const [d, ids] of Object.entries(dimAgentsMap(dims))) {
    if (ids.includes(id) && d in dims) return d;
  }
  return null;
}
