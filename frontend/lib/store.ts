"use client";

/** Run state — a zustand store fed one SSE event at a time (lib/api.consumeRun). */

import { create } from "zustand";
import type {
  AgentOutput, BoardItem, ComplianceAlerts, CrossInsights, FinanceCore, HitlState, InstrumentResult, LogKind, ManagerPlan, QaEvent, RadarData, ResultSetData, RoundsData, RunEvent, StageStatus, Story, TaskGraph, Verdict,
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
  /** agent id → highest deliberation round completed (drives the ✓✓ badges) */
  roundsDone: Record<string, number>;
  crossInsights: CrossInsights | null;
  compliance: ComplianceAlerts | null;
  rounds: RoundsData | null;
  /** round number → the COMPLETE published result set for that round */
  resultSets: Record<number, ResultSetData>;
  story: Story | null;
  charts: Record<string, unknown>[];
  report: string | null;
  tokens: number;
  routes: Set<string>;
  fatal: string | null;
  /** Intelligent Mode (Advisory Engine) */
  managerPlan: ManagerPlan | null;
  bossBrief: Record<string, string> | null;
  qa: QaEvent[];
  hitl: HitlState | null;
  /** agents that could not reach ANY model (deterministic core only) */
  noLlm: Record<string, boolean>;
  /** Intelligent Mode = the Orchestra: the Manager's task graph + per-player instruments */
  taskGraph: TaskGraph | null;
  instruments: Record<string, InstrumentResult[]>;
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
  roundsDone: {} as Record<string, number>,
  crossInsights: null as CrossInsights | null,
  compliance: null as ComplianceAlerts | null,
  rounds: null as RoundsData | null,
  resultSets: {} as Record<number, ResultSetData>,
  story: null as Story | null,
  charts: [] as Record<string, unknown>[],
  report: null as string | null,
  tokens: 0,
  routes: new Set<string>(),
  fatal: null,
  managerPlan: null as ManagerPlan | null,
  bossBrief: null as Record<string, string> | null,
  qa: [] as QaEvent[],
  hitl: null as HitlState | null,
  noLlm: {} as Record<string, boolean>,
  taskGraph: null as TaskGraph | null,
  instruments: {} as Record<string, InstrumentResult[]>,
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
        case "round":
          return { roundsDone: { ...s.roundsDone, [e.agent]: Math.max(e.round, s.roundsDone[e.agent] ?? 0) } };
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
          if (e.section === "rounds") return { rounds: e.data as RoundsData };
          if (e.section === "result_set") {
            const rs = e.data as ResultSetData;
            return { resultSets: { ...s.resultSets, [rs.round]: rs } };
          }
          if (e.section === "report") return { report: e.data as string };
          if (e.section === "run_id") return { runId: e.data as string };
          if (e.section === "manager_plan") return { managerPlan: e.data as ManagerPlan };
          if (e.section === "boss_brief") return { bossBrief: e.data as Record<string, string> };
          if (e.section === "task_graph") return { taskGraph: e.data as TaskGraph };
          if (e.section === "agent_output") {
            const d = e.data as { agent: string; output: AgentOutput };
            return { agentOutputs: { ...s.agentOutputs, [d.agent]: d.output } };
          }
          return {};
        }
        case "usage":
          return { tokens: s.tokens + (e.tokens || 0), routes: new Set(s.routes).add(e.route) };
        case "qa":
          return { qa: [...s.qa, { status: e.status, round: e.round, issues: e.issues }] };
        case "hitl":
          return { hitl: { status: e.status, reason: e.reason, sections: e.sections,
                           decision: e.decision, note: e.note } };
        case "skipped_no_llm":
          return { noLlm: { ...s.noLlm, [e.agent]: true } };
        case "instrument": {
          const prev = s.instruments[e.player] ?? [];
          const row: InstrumentResult = { name: e.name, skill: e.skill, finding: e.finding, status: e.status };
          // replace-by-name so re-emits update in place, else append
          const i = prev.findIndex((r) => r.name === e.name);
          const next = i >= 0 ? prev.map((r, j) => (j === i ? row : r)) : [...prev, row];
          return { instruments: { ...s.instruments, [e.player]: next } };
        }
        case "done":
          return { phase: "done" as const, runId: e.run_id };
        case "fatal":
          return { phase: "done" as const, fatal: e.message };
        default:
          return {};
      }
    }),
}));
