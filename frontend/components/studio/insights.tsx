"use client";

/** Results v3 surfaces: the chart gallery (Visualizer output), the smart
 * insight grid (one card per specialist, ~30 on a War Room run), and the
 * Reporter's full decision report.
 */

import { useState } from "react";
import { BarChart3, ChevronDown, FileText, Lightbulb } from "lucide-react";
import { AGENTS, agentById } from "@/lib/agents";
import { useRun } from "@/lib/store";
import type { AgentOutput } from "@/lib/types";
import { AgentSim } from "./agent-sim";
import { ChartCard, type ChartSpec } from "./chart-kit";

/* ── chart gallery — every insight, visualized ────────────────────────────── */
export function ChartGallery({ charts: chartsProp, title }: {
  charts?: ChartSpec[]; title?: string } = {}) {
  const storeCharts = useRun((s) => s.charts) as unknown as ChartSpec[];
  const charts = chartsProp ?? storeCharts;
  if (!charts?.length) return null;
  return (
    <section>
      <h3 className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        <BarChart3 size={13} /> {title ?? `The insight gallery — ${charts.length} interactive charts`}
      </h3>
      <div className="grid gap-3 lg:grid-cols-2">
        {charts.map((c) => <ChartCard key={c.id} spec={c} />)}
      </div>
    </section>
  );
}

/* ── smart insights — one card per specialist ─────────────────────────────── */
export function SmartInsights() {
  const outputs = useRun((s) => s.agentOutputs);
  const [open, setOpen] = useState<string | null>(null);
  const rows = AGENTS.filter((a) =>
    outputs[a.id]?.verdict_line &&
    !["weighing_engine", "verdict_composer", "visualizer", "reporter",
      "intake_parser", "context_profiler", "scope_planner"].includes(a.id));
  if (rows.length < 1) return null;

  return (
    <section>
      <h3 className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        <Lightbulb size={13} /> Smart insights — every specialist&apos;s finding ({rows.length})
      </h3>
      <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-3">
        {rows.map((a) => {
          const out = outputs[a.id] as AgentOutput;
          const score = typeof out.score === "number" ? out.score : null;
          const conf = typeof out.confidence === "number" ? out.confidence : null;
          const isOpen = open === a.id;
          return (
            <div key={a.id}
              className="panel-hover flex flex-col card-in rounded-2xl border border-line bg-panel p-3"
              style={{ borderTopColor: `${a.accent}66`, borderTopWidth: 2 }}>
              <div className="flex items-center gap-2">
                <span className="text-base">{a.icon}</span>
                <span className="truncate font-mono text-[10px] uppercase tracking-wider" style={{ color: a.accent }}>
                  {a.name}
                </span>
                <span className="rounded bg-panel-2 px-1 py-0.5 font-mono text-[10px] uppercase text-slate-400">{a.cluster}</span>
                {out.degraded ? (
                  <span title={String(out.degraded_reason ?? "no LLM reached this agent")}
                    className="rounded-full border border-warn/40 bg-warn/10 px-1.5 py-0.5 font-mono text-[10px] text-warn">
                    reduced depth
                  </span>
                ) : null}
                {score !== null && (
                  <span className="ml-auto shrink-0 rounded-full border px-2 py-0.5 font-mono text-[10px] font-bold"
                    style={{ color: score >= 7 ? "#9ae64a" : score >= 4.5 ? "#fbbf24" : "#fb7185",
                             borderColor: `${a.accent}44` }}>
                    {score}/10
                  </span>
                )}
              </div>
              <p className="mt-1.5 text-xs leading-relaxed text-slate-300">{out.verdict_line}</p>
              {conf !== null && (
                <div className="mt-2 flex items-center gap-1.5">
                  <span className="h-1 flex-1 overflow-hidden rounded bg-slate-800">
                    <span className="block h-full rounded" style={{ width: `${Math.round(conf * 100)}%`, background: a.accent }} />
                  </span>
                  <span className="font-mono text-[10px] text-slate-400">{Math.round(conf * 100)}%</span>
                </div>
              )}
              <button onClick={() => setOpen(isOpen ? null : a.id)}
                className="mt-2 flex items-center gap-1 font-mono text-[10px] uppercase tracking-wider text-slate-400 hover:text-cyan">
                full analysis · chart · what-if <ChevronDown size={10} className={`transition ${isOpen ? "rotate-180" : ""}`} />
              </button>
              {isOpen && (
                <div className="mt-1.5 space-y-1.5 border-t border-line pt-1.5">
                  {out.degraded && (
                    <p className="rounded border border-warn/30 bg-warn/5 p-1.5 text-[10px] leading-relaxed text-warn/90">
                      ⚠ ran on its deterministic core only — {String(out.degraded_reason ?? "no LLM reached this agent")}
                    </p>
                  )}
                  {out.analysis ? (
                    <p className="text-[11px] leading-relaxed text-slate-400">{String(out.analysis)}</p>
                  ) : null}
                  {out.what_would_change ? (
                    <p className="text-[10px] text-slate-400">
                      <span className="font-mono uppercase tracking-wider text-cyan/70">flips my score: </span>
                      {String(out.what_would_change)}
                    </p>
                  ) : null}
                  {Array.isArray(out.assumptions) && out.assumptions.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {out.assumptions.slice(0, 3).map((s, i) => (
                        <span key={i} className="rounded border border-warn/25 bg-warn/5 px-1.5 py-0.5 font-mono text-[10px] text-warn/90">
                          assumes: {String(s).slice(0, 50)}
                        </span>
                      ))}
                    </div>
                  )}
                  {/* per-agent chart + what-if simulator */}
                  <AgentSim agentId={a.id} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}

/* ── the reporter's full document ─────────────────────────────────────────── */
export function ReportSection({ report: reportProp, title }: {
  report?: string; title?: string } = {}) {
  const storeReport = useRun((s) => s.report);
  const [expanded, setExpanded] = useState(false);
  const report = reportProp ?? storeReport;
  if (!report) return null;
  return (
    <section className="glass card-in rounded-2xl p-4">
      <h3 className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        <FileText size={13} /> {title ?? "The full decision report — by the Reporter"}
      </h3>
      <div className={`relative overflow-hidden ${expanded ? "" : "max-h-72"}`}>
        <Markdown text={report} />
        {!expanded && (
          <div className="pointer-events-none absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-panel to-transparent" />
        )}
      </div>
      <button onClick={() => setExpanded((v) => !v)}
        className="mt-2 font-mono text-[10px] uppercase tracking-wider text-cyan hover:underline">
        {expanded ? "collapse" : "read the full report"}
      </button>
    </section>
  );
}

/** Minimal markdown renderer — headings, bold, bullets, numbers. */
function Markdown({ text }: { text: string }) {
  const lines = text.split("\n");
  return (
    <div className="space-y-1.5 text-[13px] leading-relaxed text-slate-300">
      {lines.map((raw, i) => {
        const line = raw.trimEnd();
        if (!line.trim()) return <div key={i} className="h-1" />;
        if (line.startsWith("### ")) return <h5 key={i} className="pt-1 font-display text-sm font-bold text-slate-200">{inline(line.slice(4))}</h5>;
        if (line.startsWith("## ")) return <h4 key={i} className="pt-2 font-display text-base font-bold text-slate-100">{inline(line.slice(3))}</h4>;
        if (line.startsWith("# ")) return <h3 key={i} className="font-display text-lg font-bold text-white">{inline(line.slice(2))}</h3>;
        if (/^[-*] /.test(line)) return <div key={i} className="flex gap-2 pl-1"><span className="text-cyan">•</span><span>{inline(line.slice(2))}</span></div>;
        const num = line.match(/^(\d+)\. (.*)/);
        if (num) return <div key={i} className="flex gap-2 pl-1"><span className="font-mono text-cyan">{num[1]}.</span><span>{inline(num[2])}</span></div>;
        return <p key={i}>{inline(line)}</p>;
      })}
    </div>
  );
}

function inline(s: string): React.ReactNode {
  const parts = s.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((p, i) =>
    p.startsWith("**") && p.endsWith("**")
      ? <strong key={i} className="font-semibold text-slate-100">{p.slice(2, -2)}</strong>
      : p);
}
