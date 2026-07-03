/** Shared types — the client half of the SSE contract (backend/app/core/events.py). */

export type StageStatus = "queued" | "active" | "done" | "error" | "skipped";
export type LogKind = "info" | "code" | "ok" | "err" | "warn" | "muted";

export interface EngineSelection {
  compute: "auto" | "local" | "cloud" | "hybrid" | "demo";
  provider: string;
  api_key: string;
  model: string;
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
  engine: EngineSelection;
}

export interface Source {
  url?: string;
  name?: string;
  date?: string;
}

/** One entry in the Boardroom feed (claims, conflicts, bias flags). */
export interface BoardItem {
  kind: "claim" | "conflict" | "bias";
  agent: string;
  text: string;
  vs?: string;
  confidence?: number;
  source?: Source | null;
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
  assumptions?: string[];
  numbers_used?: { figure: string; source: string }[];
  route?: string;
} & Record<string, unknown>;

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
  | { type: "claim"; agent: string; claim: { text: string; source?: Source | null; confidence: number } }
  | { type: "conflict"; a: string; b: string; topic: string }
  | { type: "bias"; target: string; bias: string; note: string }
  | { type: "partial"; section: string; data: unknown }
  | { type: "usage"; agent: string; tokens: number; route: string }
  | { type: "done"; run_id: string }
  | { type: "fatal"; message: string };
