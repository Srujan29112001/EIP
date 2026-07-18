"use client";

/** Per-agent visualization + what-if — shown when you expand an agent's
 * "full analysis" in Smart Insights. Every specialist gets its own chart
 * (score vs its dimension vs the board) and a live simulator (drag its score,
 * watch the whole verdict move through the weighing math).
 */

import { useMemo, useState } from "react";
import { agentById } from "@/lib/agents";
import { dimAgentsMap, dimForAgent } from "@/lib/dimensions";
import { useRun } from "@/lib/store";
import type { AgentOutput } from "@/lib/types";
import { SimSlider } from "./charts";
import { weightsFor } from "./sim-charts";

const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));
const barColor = (v: number) => (v >= 7 ? "#9ae64a" : v >= 4.5 ? "#fbbf24" : "#fb7185");

export function AgentSim({ agentId }: { agentId: string }) {
  const { agentOutputs, verdict } = useRun();
  const out = agentOutputs[agentId] as AgentOutput | undefined;
  const [override, setOverride] = useState<number | null>(null);

  const a = agentById(agentId);
  const score = typeof out?.score === "number" ? out.score : null;
  const dims = verdict?.dimensions ?? {};
  const overall = verdict?.score ?? 0;

  const boardAvg = useMemo(() => {
    const scored = Object.values(agentOutputs).filter((o) => typeof o.score === "number");
    return scored.length ? scored.reduce((s, o) => s + (o.score as number), 0) / scored.length : 5;
  }, [agentOutputs]);

  if (score === null) return null;
  const dim = dimForAgent(agentId, dims);

  // what-if: change THIS agent's score → shift its dimension → shift the verdict
  const newScore = override ?? score;
  let projected = overall, delta = 0, newDim: number | null = null;
  if (dim) {
    const peers = dimAgentsMap(dims)[dim].filter((id) => typeof agentOutputs[id]?.score === "number");
    const n = Math.max(1, peers.length);
    const w = weightsFor(dims)[dim] ?? 0;
    const curDim = dims[dim] ?? 5;
    newDim = clamp(curDim + (newScore - score) / n, 0, 10);
    projected = clamp(overall - curDim * w + newDim * w, 0, 10);
    delta = projected - overall;
  }

  // the chart: this agent vs its dimension vs the board average
  const bars: { label: string; value: number }[] = [
    { label: a.name.slice(0, 16), value: override ?? score },
    ...(dim ? [{ label: `${dim} (dimension)`, value: newDim ?? dims[dim] ?? 5 }] : []),
    { label: "board average", value: Math.round(boardAvg * 10) / 10 },
  ];

  return (
    <div className="mt-2 space-y-2 rounded-lg border border-line bg-ink/40 p-2.5">
      {/* comparison chart */}
      <div>
        <div className="mb-1 font-mono text-[10px] uppercase tracking-widest text-slate-400">
          how this specialist compares
        </div>
        <div className="space-y-1">
          {bars.map((b, i) => (
            <div key={i} className="flex items-center gap-2">
              <span className="w-28 shrink-0 truncate text-right font-mono text-[10px] text-slate-400">{b.label}</span>
              <span className="h-3 flex-1 overflow-hidden rounded bg-slate-800">
                <span className="block h-full rounded transition-all duration-300"
                  style={{ width: `${b.value * 10}%`, background: barColor(b.value) }} />
              </span>
              <span className="w-8 shrink-0 font-mono text-[10px]" style={{ color: barColor(b.value) }}>{b.value.toFixed(1)}</span>
            </div>
          ))}
        </div>
      </div>

      {/* the sourced/estimate numbers this agent used, as chips */}
      {Array.isArray(out?.numbers_used) && out!.numbers_used!.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {out!.numbers_used!.slice(0, 6).map((num, i) => {
            const sourced = String(num.source ?? "").startsWith("http");
            return (
              <span key={i} className={`rounded border px-1.5 py-0.5 font-mono text-[10px] ${
                sourced ? "border-cyan/30 bg-cyan/5 text-cyan" : "border-warn/30 bg-warn/5 text-warn"}`}>
                {num.figure}{sourced ? "" : " · est"}
              </span>
            );
          })}
        </div>
      )}

      {/* what-if simulator */}
      {dim ? (
        <div className="rounded-md border border-line bg-panel-2 p-2">
          <SimSlider label={`what if ${a.name} scored`} value={override ?? score} min={0} max={10} step={0.1}
            onChange={setOverride} fmt={(v) => `${v.toFixed(1)}/10`} />
          <div className="mt-1 flex items-center justify-between font-mono text-[10px]">
            <span className="text-slate-400">→ verdict {projected.toFixed(1)}/10</span>
            <span className={delta > 0.02 ? "text-ok" : delta < -0.02 ? "text-err" : "text-slate-400"}>
              {delta >= 0 ? "▲ +" : "▼ "}{delta.toFixed(2)} via {dim}
            </span>
            {override !== null && (
              <button onClick={() => setOverride(null)} className="text-slate-400 hover:text-cyan">↺ reset</button>
            )}
          </div>
        </div>
      ) : (
        <p className="font-mono text-[10px] text-slate-400">
          This specialist shapes the verdict qualitatively (crucible / synthesis) — it isn&apos;t weighted into a single dimension.
        </p>
      )}
    </div>
  );
}
