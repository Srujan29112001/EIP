/** Shared types — the client half of the SSE contract (backend/app/core/events.py). */

export type StageStatus = "queued" | "active" | "done" | "degraded" | "error" | "skipped";
export type LogKind = "info" | "code" | "ok" | "err" | "warn" | "muted";

export interface EngineSelection {
  compute: "auto" | "local" | "cloud" | "hybrid" | "demo";
  provider: string;
  api_key: string;
  model: string;
  /** provider id → API key (multi-BYOK; never persisted server-side) */
  api_keys: Record<string, string>;
  /** provider id → up to 5 keys, rotated when one is exhausted mid-run */
  api_keys_multi: Record<string, string[]>;
  /** agent id → "provider:model" per-agent override */
  agent_routes: Record<string, string>;
  /** tier → "provider:model" — set when the user picks an explicit model so
   * it's honored at every tier (highest routing precedence on the backend) */
  routes: Record<string, string>;
  temperature: number | null;
  max_tokens_cap: number;
}

export interface IntakeForm {
  mode: "founder" | "trader" | "wealth";
  situation: string;
  industry: string;
  geography: string;
  stage: string;
  budget_band: string;
  team_size: string;
  uncertainty: string;
  depth: "pulse" | "board" | "war_room";
  /** empty = the full scope for the chosen depth; else the hand-picked board */
  agents_enabled: string[];
  /** founder extras */
  target_customer: string;
  competitors: string;
  revenue_model: string;
  /** trader mode */
  symbol: string;
  trading_style: "intraday" | "swing" | "position" | "options_edu";
  capital: number;
  risk_pct: number;
  thesis: string;
  existing_position: number;
  /** wealth mode */
  monthly_income: number;
  monthly_expenses: number;
  current_savings: number;
  age: number;
  risk_appetite: "conservative" | "moderate" | "aggressive";
  city: string;
  goals: string;
  dependents: number;
  current_debt: number;
  monthly_sip: number;
  /** document intelligence — extracted via POST /api/extract */
  documents: { name: string; text: string }[];
  /** per-agent user briefs from the board picker */
  agent_context: Record<string, string>;
  engine: EngineSelection;
}

export interface Source {
  url?: string;
  name?: string;
  date?: string;
}

/** One entry in the Boardroom feed (claims, conflicts, bias flags, debate turns). */
export interface BoardItem {
  kind: "claim" | "conflict" | "bias" | "debate";
  agent: string;
  text: string;
  vs?: string;
  confidence?: number;
  source?: Source | null;
  round?: number;
  stance?: "attack" | "rebuttal" | "concession";
}

export interface RadarData {
  dimensions: Record<string, number>;
  overall: number;
}

/** Deterministic finance core — the client-side What-If simulator re-runs this math. */
export interface FinanceCore {
  capital_lakhs: number;
  burn_lakhs_pm: number;
  runway_months: number;
  team: number;
}

/** Loose shape of one agent's structured output (streamed via partial:agent_output). */
export type AgentOutput = {
  verdict_line?: string;
  score?: number;
  confidence?: number;
  analysis?: string;
  key_insights?: string[];
  what_would_change?: string;
  assumptions?: string[];
  numbers_used?: { figure: string; source: string }[];
  route?: string;
  degraded?: boolean;
  degraded_reason?: string;
} & Record<string, unknown>;

/** The Compliance Sentinel's ranked red-flags (partial:compliance_alerts). */
export interface ComplianceAlert {
  agent: string;
  severity: "high" | "medium" | "low";
  text: string;
  action?: string;
  score?: number | null;
}
export interface ComplianceAlerts {
  alerts: ComplianceAlert[];
  high: number;
}

/** The Cross-Pollinator's inter-agent map (partial:cross_insights). */
export interface CrossInsights {
  connections?: { a: string; b: string; type: "synergy" | "tension"; insight: string }[];
  emergent?: string[];
  degraded?: boolean;
}

/** The Storyteller's pitch narrative (partial:story). */
export interface Story {
  hook?: string;
  narrative?: string;
  one_liner?: string;
  three_beats?: string[];
}

export interface Verdict {
  score: number;
  band: string;
  recommendation: string;
  reasoning: string;
  dimensions: Record<string, number>;
  sensitivities?: string[];
  risks?: { text: string; source_agent: string; severity?: number }[];
  opportunities?: { text: string; source_agent?: string }[];
  next_steps?: string[];
  teach?: string;
}

/** Every event shape the backend emits over SSE — field names must match exactly. */
export type RunEvent =
  | { type: "stage"; agent: string; status: StageStatus; layer: string }
  | { type: "log"; agent: string; kind: LogKind; text: string }
  | { type: "prompt"; agent: string; system: string; user: string }
  | { type: "collab"; agent: string; peers: string[] }
  | { type: "claim"; agent: string; claim: { text: string; source?: Source | null; confidence: number } }
  | { type: "conflict"; a: string; b: string; topic: string }
  | { type: "debate"; agent: string; round: number; stance: "attack" | "rebuttal" | "concession"; text: string }
  | { type: "bias"; target: string; bias: string; note: string }
  | { type: "partial"; section: string; data: unknown }
  | { type: "usage"; agent: string; tokens: number; route: string }
  | { type: "done"; run_id: string }
  | { type: "fatal"; message: string };
