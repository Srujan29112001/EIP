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
  // L2 — Domain analysis (violet family for venture cluster)
  { id: "market_analyst", name: "Market Analyst", layer: "L2", cluster: "venture", blurb: "Market size, growth, competition — sourced", accent: "#8b5cf6" },
  { id: "finance_modeler", name: "Finance Modeler", layer: "L2", cluster: "venture", blurb: "Unit economics, runway, breakeven — real math", accent: "#a78bfa" },
  // L3 — Crucible (red/orange family)
  { id: "red_team", name: "Red Team", layer: "L3", cluster: "crucible", blurb: "Attacks the thesis with evidence", accent: "#fb7185" },
  // L4 — Synthesis (gold family)
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
