/** The agent registry — the client mirror of backend/app/agents/registry.py.
 *
 * Only implemented agents are listed (they drive the pipeline rail and the
 * landing-page "live" counts); new agents are appended as backend phases land.
 * ids, layers and accents must stay in sync with the backend registry.
 */

export type Layer = "L0" | "L1" | "L2" | "L3" | "L4" | "L5";

export interface AgentInfo {
  id: string;
  name: string;
  layer: Layer;
  cluster: string;
  blurb: string;
  accent: string;
}

export const LAYER_LABELS: Record<Layer, string> = {
  L0: "Gateway",
  L1: "Grounding",
  L2: "Domain analysis",
  L3: "The Crucible",
  L4: "Synthesis",
  L5: "Memory",
};

/** Accent families per layer (globals.css tokens), shaded per agent for identity. */
export const AGENTS: AgentInfo[] = [
  // L0 — Gateway (slate family)
  { id: "intake_parser", name: "Intake Parser", layer: "L0", cluster: "gateway", blurb: "Turns your words into a structured brief", accent: "#94a3b8" },
  { id: "context_profiler", name: "Context Profiler", layer: "L0", cluster: "gateway", blurb: "Works out who is asking — stage, capital, risk", accent: "#a8b6c8" },
  { id: "scope_planner", name: "Scope Planner", layer: "L0", cluster: "gateway", blurb: "Decides which specialists to convene", accent: "#8494ab" },
  // L1 — Grounding (cyan family)
  { id: "web_researcher", name: "Web Researcher", layer: "L1", cluster: "grounding", blurb: "Live web evidence — competitors, markets, claims", accent: "#22d3ee" },
  { id: "news_intel", name: "News Intelligence", layer: "L1", cluster: "grounding", blurb: "What is happening right now in this space", accent: "#67e8f9" },
  { id: "market_data", name: "Market Data", layer: "L1", cluster: "grounding", blurb: "Live prices & index pulse (NSE/global)", accent: "#06b6d4" },
  { id: "macro_data", name: "Macro Data", layer: "L1", cluster: "grounding", blurb: "GDP, inflation, rates from official series", accent: "#38bdf8" },
  // L2 — Domain analysis (violet family for venture cluster)
  { id: "market_analyst", name: "Market Analyst", layer: "L2", cluster: "venture", blurb: "Market size, growth, competition — sourced", accent: "#8b5cf6" },
  { id: "finance_modeler", name: "Finance Modeler", layer: "L2", cluster: "venture", blurb: "Unit economics, runway, breakeven — real math", accent: "#a78bfa" },
  { id: "competitor_intel", name: "Competitor Intelligence", layer: "L2", cluster: "venture", blurb: "Positioning map, moats, whitespace", accent: "#7c3aed" },
  { id: "gtm_distribution", name: "GTM & Distribution", layer: "L2", cluster: "venture", blurb: "Channels, launch sequence, CAC reality", accent: "#9333ea" },
  { id: "legal", name: "Legal", layer: "L2", cluster: "venture", blurb: "Structure, contracts, IP exposure", accent: "#c084fc" },
  { id: "tax", name: "Tax (India-first)", layer: "L2", cluster: "venture", blurb: "GST, exemptions, legitimate optimization", accent: "#a855f7" },
  { id: "policy_compliance", name: "Policy & Compliance", layer: "L2", cluster: "venture", blurb: "Acts, licences, compliance calendar", accent: "#8b5cf6" },
  { id: "industry_expert", name: "Industry Expert", layer: "L2", cluster: "venture", blurb: "Insider benchmarks and failure modes", accent: "#6d28d9" },
  // L2 — Markets cluster (green family — the Trading Co-Pilot)
  { id: "technical_analyst", name: "Technical Analyst", layer: "L2", cluster: "markets", blurb: "Indicators, levels, multi-signal read — pure math", accent: "#34d399" },
  { id: "stock_analyst", name: "Stock Analyst", layer: "L2", cluster: "markets", blurb: "Fundamentals + what the market is pricing in", accent: "#6ee7b7" },
  { id: "backtest_engineer", name: "Backtest Engineer", layer: "L2", cluster: "markets", blurb: "Every signal proves itself on history first", accent: "#10b981" },
  { id: "quant_signals", name: "Quant Signals", layer: "L2", cluster: "markets", blurb: "Regime + ensemble vote → setup quality", accent: "#2dd4bf" },
  { id: "risk_manager", name: "Risk Manager", layer: "L2", cluster: "markets", blurb: "Position sizing, stops, exposure — always on", accent: "#059669" },
  // L3 — Crucible (red/orange family)
  { id: "red_team", name: "Red Team", layer: "L3", cluster: "crucible", blurb: "Attacks the thesis with evidence", accent: "#fb7185" },
  { id: "fact_checker", name: "Fact Checker", layer: "L3", cluster: "crucible", blurb: "Every claim must trace to the evidence board", accent: "#f97316" },
  { id: "bias_auditor", name: "Bias Auditor", layer: "L3", cluster: "crucible", blurb: "Names the biases in your framing", accent: "#fbbf24" },
  { id: "devils_advocate", name: "Devil's Advocate", layer: "L3", cluster: "crucible", blurb: "Steel-mans the NO case", accent: "#f43f5e" },
  // L4 — Synthesis (gold family)
  { id: "connecting_dots", name: "Connecting Dots", layer: "L4", cluster: "synthesis", blurb: "Cross-domain patterns and weak signals", accent: "#fde047" },
  { id: "weighing_engine", name: "Weighing Engine", layer: "L4", cluster: "synthesis", blurb: "Deterministic scoring — disagreement preserved", accent: "#eab308" },
  { id: "verdict_composer", name: "Verdict Composer", layer: "L4", cluster: "synthesis", blurb: "The decision document, with sensitivities", accent: "#facc15" },
];

const BY_ID = new Map(AGENTS.map((a) => [a.id, a]));

const UNKNOWN: AgentInfo = {
  id: "unknown", name: "Board", layer: "L4", cluster: "synthesis",
  blurb: "", accent: "#64748b",
};

/** Never throws — unknown ids (e.g. future agents, "user_framing") get a neutral identity. */
export function agentById(id: string): AgentInfo {
  return BY_ID.get(id) ?? { ...UNKNOWN, id: id || "unknown", name: id ? prettify(id) : "Board" };
}

function prettify(id: string): string {
  return id.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
