"use client";

/** Run state — a zustand store fed one SSE event at a time (lib/api.consumeRun). */

import { create } from "zustand";
import type {
  AgentOutput, BoardItem, FinanceCore, LogKind, RadarData, RunEvent, StageStatus, Verdict,
} from "./types";

export type RunPhase = "intake" | "running" | "done";

interface RunStore {
  phase: RunPhase;
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
  tokens: number;
  routes: Set<string>;
  fatal: string | null;
  begin: () => void;
  apply: (e: RunEvent) => void;
  reset: () => void;
}

const EMPTY = {
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
        case "claim":
          return {
            board: [...s.board, {
              kind: "claim" as const, agent: e.agent, text: e.claim.text,
              confidence: e.claim.confidence, source: e.claim.source,
            }],
          };
        case "conflict":
          return { board: [...s.board, { kind: "conflict" as const, agent: e.a, vs: e.b, text: e.topic }] };
        case "bias":
          return { board: [...s.board, { kind: "bias" as const, agent: e.target, text: `${e.bias} — ${e.note}` }] };
        case "partial": {
          if (e.section === "verdict") return { verdict: e.data as Verdict };
          if (e.section === "radar") return { radar: e.data as RadarData };
          if (e.section === "brief") return { brief: e.data as Record<string, unknown> };
          if (e.section === "scope") return { scope: e.data as string[] };
          if (e.section === "finance_core") return { financeCore: e.data as FinanceCore };
          if (e.section === "agent_output") {
            const d = e.data as { agent: string; output: AgentOutput };
            return { agentOutputs: { ...s.agentOutputs, [d.agent]: d.output } };
          }
          return {};
        }
        case "usage":
          return { tokens: s.tokens + (e.tokens || 0), routes: new Set(s.routes).add(e.route) };
        case "done":
          return { phase: "done" as const };
        case "fatal":
          return { phase: "done" as const, fatal: e.message };
        default:
          return {};
      }
    }),
}));
