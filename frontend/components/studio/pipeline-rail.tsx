"use client";

import { AGENTS, LAYER_LABELS } from "@/lib/agents";
import { useRun } from "@/lib/store";
import type { StageStatus } from "@/lib/types";

const DOT: Record<StageStatus, string> = {
  queued: "bg-slate-600",
  active: "bg-cyan",
  done: "bg-ok",
  error: "bg-err",
  skipped: "bg-slate-700",
};

export function PipelineRail() {
  const status = useRun((s) => s.agentStatus);
  const layers = ["L0", "L1", "L2", "L3", "L4", "L5"] as const;

  return (
    <aside className="scroll-thin sticky top-4 max-h-[calc(100vh-2rem)] overflow-y-auto rounded-xl border border-line bg-panel p-4">
      <h3 className="mb-3 font-mono text-[11px] uppercase tracking-widest text-muted">Intelligence layers</h3>
      {layers.map((layer) => {
        const agents = AGENTS.filter((a) => a.layer === layer);
        if (!agents.length) return null;
        return (
          <div key={layer} className="mb-4">
            <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-slate-500">
              {layer} · {LAYER_LABELS[layer]}
            </div>
            <ul className="space-y-1">
              {agents.map((a) => {
                const st = status[a.id] ?? "queued";
                return (
                  <li key={a.id} style={{ "--glow": a.accent } as React.CSSProperties}
                    className={`flex items-center gap-2 rounded-md border px-2.5 py-1.5 text-xs transition ${
                      st === "active" ? "glow-active border-cyan/40 bg-panel-2" : "border-transparent"}`}>
                    <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${DOT[st]}`} />
                    <span className="truncate" style={{ color: st === "queued" ? "#64748b" : a.accent }}>
                      {a.name}
                    </span>
                    <span className="ml-auto font-mono text-[9px] text-slate-600">{st}</span>
                  </li>
                );
              })}
            </ul>
          </div>
        );
      })}
    </aside>
  );
}
