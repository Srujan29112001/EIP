"use client";

import { useState } from "react";
import { ChevronDown, Link2 } from "lucide-react";
import { AGENTS } from "@/lib/agents";
import { useRun } from "@/lib/store";
import type { AgentOutput } from "@/lib/types";

/** Per-agent insight cards: one-line verdict, confidence bar, full analysis,
 * and every number tagged sourced vs ESTIMATE (Constitution #1 made visible). */
export function AgentAccordion() {
  const outputs = useRun((s) => s.agentOutputs);
  const [open, setOpen] = useState<string | null>(null);

  // stable roster order; skip agents whose output is pure plumbing
  const rows = AGENTS.filter((a) => outputs[a.id] && !["intake_parser", "scope_planner"].includes(a.id));
  if (!rows.length) return null;

  return (
    <section className="glass card-in rounded-2xl p-4">
      <h3 className="mb-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        Agent-by-agent insights
      </h3>
      <div className="space-y-1.5">
        {rows.map((a) => {
          const out = outputs[a.id] as AgentOutput;
          const conf = typeof out.confidence === "number" ? out.confidence : null;
          const line = out.verdict_line
            ?? (typeof out.unsupported === "number" ? `${out.unsupported} claims failed verification` : null)
            ?? (Array.isArray(out.findings) ? `${out.findings.length} bias flags on your framing` : null)
            ?? (Array.isArray(out.pulses) ? `${out.pulses.length} live market series` : null)
            ?? (Array.isArray(out.series) ? `${out.series.length} official macro indicators` : null)
            ?? summary(out);
          const isOpen = open === a.id;
          return (
            <div key={a.id} className="rounded-lg border border-line bg-panel-2">
              <button onClick={() => setOpen(isOpen ? null : a.id)}
                className="flex w-full items-center gap-2 p-2.5 text-left text-xs">
                <span className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: a.accent }} />
                <span className="shrink-0 font-mono text-[10px] uppercase tracking-wider" style={{ color: a.accent }}>
                  {a.name}
                </span>
                <span className="truncate text-slate-400">{line}</span>
                {conf !== null && (
                  <span className="ml-auto flex shrink-0 items-center gap-1.5">
                    <span className="h-1 w-14 overflow-hidden rounded bg-slate-800">
                      <span className="block h-full rounded"
                        style={{ width: `${Math.round(conf * 100)}%`, background: a.accent }} />
                    </span>
                    <span className="font-mono text-[9px] text-slate-500">{Math.round(conf * 100)}%</span>
                  </span>
                )}
                <ChevronDown size={13} className={`shrink-0 text-slate-600 transition ${isOpen ? "rotate-180" : ""}`} />
              </button>
              {isOpen && (
                <div className="border-t border-line p-3 text-xs leading-relaxed text-slate-300">
                  {typeof out.score === "number" && (
                    <div className="mb-1 font-mono text-[10px] text-slate-500">
                      score {out.score}/10{out.route ? ` · via ${out.route}` : ""}
                    </div>
                  )}
                  {out.analysis && <p>{out.analysis}</p>}
                  {Array.isArray(out.assumptions) && out.assumptions.length > 0 && (
                    <div className="mt-2">
                      <div className="font-mono text-[10px] uppercase tracking-wider text-slate-500">assumptions</div>
                      <ul className="mt-1 list-inside list-disc text-slate-400">
                        {out.assumptions.map((x, i) => <li key={i}>{x}</li>)}
                      </ul>
                    </div>
                  )}
                  {Array.isArray(out.numbers_used) && out.numbers_used.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {out.numbers_used.map((n, i) => {
                        const sourced = String(n.source ?? "").startsWith("http");
                        return sourced ? (
                          <a key={i} href={n.source} target="_blank" rel="noreferrer"
                            className="inline-flex items-center gap-1 rounded border border-cyan/30 bg-cyan/5 px-1.5 py-0.5 font-mono text-[10px] text-cyan hover:underline">
                            <Link2 size={9} /> {n.figure}
                          </a>
                        ) : (
                          <span key={i}
                            className="rounded border border-warn/30 bg-warn/5 px-1.5 py-0.5 font-mono text-[10px] text-warn">
                            {n.figure} · ESTIMATE
                          </span>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}

function summary(out: AgentOutput): string {
  const j = JSON.stringify(out);
  return j.length > 90 ? j.slice(0, 90) + "…" : j;
}
