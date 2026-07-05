"use client";

/** Run state — a zustand store fed one SSE event at a time (lib/api.consumeRun). */

import { create } from "zustand";
import type {
  AgentOutput, BoardItem, ComplianceAlerts, CrossInsights, FinanceCore, LogKind, RadarData, RunEvent, StageStatus, Story, Verdict,
} from "./types";

export type RunPhase = "intake" | "running" | "done";

interface RunStore {
  phase: RunPhase;
  runId: string | null;
  agentStatus: Record<string, StageStatus>;
  logs: { agent: string; kind: LogKind; text: string }[];
  board: BoardItem[];
  brief: Record<string, unknown> | null;
  scope: string[];
  radar: RadarData | null;
  verdict: Verdict | null;
  agentOutputs: Record<string, AgentOutput>;
  financeCore: FinanceCore | null;
  prompts: Record<string, { system: string; user: string }>;
  /** agent id → the colleagues it built on (A2A collab events) */
  collabs: Record<string, string[]>;
  crossInsights: CrossInsights | null;
  compliance: ComplianceAlerts | null;
  story: Story | null;
  charts: Record<string, unknown>[];
  report: string | null;
  tokens: number;
  routes: Set<string>;
  fatal: string | null;
  begin: () => void;
  apply: (e: RunEvent) => void;
  reset: () => void;
}

const EMPTY = {
  runId: null as string | null,
  agentStatus: {} as Record<string, StageStatus>,
  logs: [],
  board: [],
  brief: null,
  scope: [],
  radar: null,
  verdict: null,
  agentOutputs: {},
  financeCore: null,
  prompts: {},
  collabs: {} as Record<string, string[]>,
  crossInsights: null as CrossInsights | null,
  compliance: null as ComplianceAlerts | null,
  story: null as Story | null,
  charts: [] as Record<string, unknown>[],
  report: null as string | null,
  tokens: 0,
  routes: new Set<string>(),
  fatal: null,
};

export const useRun = create<RunStore>((set) => ({
  phase: "intake",
  ...EMPTY,

  begin: () => set({ phase: "running", ...EMPTY, routes: new Set() }),
  reset: () => set({ phase: "intake", ...EMPTY, routes: new Set() }),

  apply: (e) =>
    set((s) => {
      switch (e.type) {
        case "stage":
          return { agentStatus: { ...s.agentStatus, [e.agent]: e.status } };
        case "log":
          return { logs: [...s.logs, { agent: e.agent, kind: e.kind, text: e.text }] };
        case "prompt":
          return { prompts: { ...s.prompts, [e.agent]: { system: e.system, user: e.user } } };
        case "collab":
          return { collabs: { ...s.collabs, [e.agent]: e.peers } };
        case "claim":
          return {
            board: [...s.board, {
              kind: "claim" as const, agent: e.agent, text: e.claim.text,
              confidence: e.claim.confidence, source: e.claim.source,
            }],
          };
        case "conflict":
          return { board: [...s.board, { kind: "conflict" as const, agent: e.a, vs: e.b, text: e.topic }] };
        case "debate":
          return { board: [...s.board, {
            kind: "debate" as const, agent: e.agent, text: e.text, round: e.round, stance: e.stance,
          }] };
        case "bias":
          return { board: [...s.board, { kind: "bias" as const, agent: e.target, text: `${e.bias} — ${e.note}` }] };
        case "partial": {
          if (e.section === "verdict") return { verdict: e.data as Verdict };
          if (e.section === "radar") return { radar: e.data as RadarData };
          if (e.section === "brief") return { brief: e.data as Record<string, unknown> };
          if (e.section === "scope") return { scope: e.data as string[] };
          if (e.section === "finance_core") return { financeCore: e.data as FinanceCore };
          if (e.section === "charts") return { charts: e.data as Record<string, unknown>[] };
          if (e.section === "story") return { story: e.data as Story };
          if (e.section === "cross_insights") return { crossInsights: e.data as CrossInsights };
          if (e.section === "compliance_alerts") return { compliance: e.data as ComplianceAlerts };
          if (e.section === "report") return { report: e.data as string };
          if (e.section === "agent_output") {
            const d = e.data as { agent: string; output: AgentOutput };
            return { agentOutputs: { ...s.agentOutputs, [d.agent]: d.output } };
          }
          return {};
        }
        case "usage":
          return { tokens: s.tokens + (e.tokens || 0), routes: new Set(s.routes).add(e.route) };
        case "done":
          return { phase: "done" as const, runId: e.run_id };
        case "fatal":
          return { phase: "done" as const, fatal: e.message };
        default:
          return {};
      }
    }),
}));
