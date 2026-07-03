"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Network } from "lucide-react";
import { NeuralMap } from "@/components/graph/neural-map";
import { getRun, listRuns, type RunSummary } from "@/lib/api";
import { buildGraph, type GEdge, type GNode } from "@/lib/graph-data";
import type { AgentOutput, BoardItem, Verdict } from "@/lib/types";

/** Rebuild board items from a persisted run's state (evidence + conflicts). */
function boardFromState(state: Record<string, unknown>): BoardItem[] {
  const out: BoardItem[] = [];
  for (const e of (state.evidence as { text: string; source?: { url?: string }; agent: string }[]) ?? []) {
    out.push({ kind: "claim", agent: e.agent, text: e.text, source: e.source, confidence: 0.6 });
  }
  for (const c of (state.conflicts as { target_agent?: string; attack?: string }[]) ?? []) {
    out.push({ kind: "conflict", agent: "red_team", vs: c.target_agent, text: c.attack ?? "" });
  }
  return out;
}

export default function GraphPage() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [sel, setSel] = useState<string>("");
  const [graph, setGraph] = useState<{ nodes: GNode[]; edges: GEdge[] } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listRuns().then((r) => {
      setRuns(r);
      if (r.length) setSel(r[0].id);
      else setLoading(false);
    });
  }, []);

  useEffect(() => {
    if (!sel) return;
    setLoading(true);
    getRun(sel).then((rec) => {
      if (rec?.state) {
        const st = rec.state as Record<string, unknown>;
        setGraph(buildGraph({
          brief: (st.brief as Record<string, unknown>) ?? null,
          board: boardFromState(st),
          agentOutputs: (st.outputs as Record<string, AgentOutput>) ?? {},
          verdict: (st.verdict as Verdict) ?? null,
        }));
      }
      setLoading(false);
    });
  }, [sel]);

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <nav className="mb-8 flex items-center justify-between">
        <Link href="/" className="font-display text-lg font-bold">EIP<span className="text-cyan">.</span></Link>
        <span className="flex gap-2">
          <Link href="/history" className="rounded-lg px-3 py-2 font-mono text-xs uppercase tracking-wider text-slate-500 hover:text-cyan">History</Link>
          <Link href="/studio" className="rounded-lg border border-line px-4 py-2 font-mono text-xs uppercase tracking-wider text-slate-300 transition hover:border-cyan/60 hover:text-cyan">Open Studio →</Link>
        </span>
      </nav>

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <h1 className="flex items-center gap-2 font-display text-2xl font-bold">
          <Network size={20} className="text-cyan" /> The Decision Graph
        </h1>
        {runs.length > 0 && (
          <select value={sel} onChange={(e) => setSel(e.target.value)}
            className="ml-auto max-w-sm rounded-md border border-line bg-panel-2 px-3 py-1.5 text-xs outline-none focus:border-cyan/60">
            {runs.map((r) => (
              <option key={r.id} value={r.id}>
                {new Date(r.created_at).toLocaleDateString()} · {r.score?.toFixed?.(1)}/10 · {r.situation.slice(0, 60)}
              </option>
            ))}
          </select>
        )}
      </div>
      <p className="mb-5 max-w-2xl text-sm text-slate-400">
        Every run becomes memory: agents, sourced claims, risks and arguments orbiting the decision.
        Drag to explore, click any node, or light it up with a question.
      </p>

      {loading && <div className="rounded-xl border border-line bg-panel p-8 text-center font-mono text-xs text-slate-500 animate-pulse">mapping the decision…</div>}
      {!loading && !graph && (
        <div className="rounded-xl border border-line bg-panel p-8 text-center text-sm text-slate-500">
          No runs yet — convene your first board in the <Link href="/studio" className="text-cyan hover:underline">Studio</Link>.
        </div>
      )}
      {!loading && graph && <NeuralMap nodes={graph.nodes} edges={graph.edges} height={560} />}
    </div>
  );
}
