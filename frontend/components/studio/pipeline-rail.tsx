"use client";

import { AGENTS, LAYER_LABELS } from "@/lib/agents";
import { useRun } from "@/lib/store";
import type { StageStatus } from "@/lib/types";

const DOT: Record<StageStatus, string> = {
  queued: "bg-slate-600",
  active: "bg-cyan",
  done: "bg-ok",
  degraded: "bg-warn",
  error: "bg-err",
  skipped: "bg-slate-700",
};

export function PipelineRail() {
  const status = useRun((s) => s.agentStatus);
  const scope = useRun((s) => s.scope);
  const roundsDone = useRun((s) => s.roundsDone);
  const layers = ["L0", "L1", "L2", "L3", "L4", "L5"] as const;
  // only the convened board belongs in the rail — the full registry is 55+
  const convened = new Set(["intake_parser", "context_profiler", "scope_planner", ...scope]);

  return (
    <aside className="scroll-thin glass sticky top-4 max-h-[calc(100vh-2rem)] overflow-y-auto rounded-2xl p-4">
      <h3 className="mb-3 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        <span className="pulse-ring h-1.5 w-1.5 rounded-full bg-cyan" style={{ "--ring": "#22d3ee" } as React.CSSProperties} />
        Intelligence layers
      </h3>
      {layers.map((layer) => {
        const agents = AGENTS.filter((a) => a.layer === layer &&
          (scope.length === 0 || convened.has(a.id) || status[a.id]));
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
                    <span className={`ml-auto font-mono text-[9px] ${st === "degraded" ? "text-warn" : "text-slate-600"}`}>
                      {st === "done" && (roundsDone[a.id] ?? 0) >= 2 ? (
                        <span title="round 1 + round 2 (deliberation) complete">
                          <span className="text-ok">✓</span><span className="text-[#fbbf24]">✓</span>
                        </span>
                      ) : st === "degraded" ? "no-LLM" : st}
                    </span>
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
