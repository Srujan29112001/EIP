"use client";

/** Custom SVG radar (Helix idiom — no chart library), now interactive:
 * hover an axis to see which agents contributed that dimension's score. */

import { useState } from "react";
import { agentById } from "@/lib/agents";
import { useRun } from "@/lib/store";

/** which agents feed each dimension — mirror of the backend weighing engine */
const DIM_SOURCES: Record<string, string[]> = {
  Market: ["market_analyst", "competitor_intel", "industry_expert"],
  Economics: ["finance_modeler", "tax"],
  Regulatory: ["policy_compliance", "legal"],
  Evidence: ["web_researcher", "news_intel", "market_data", "macro_data", "fact_checker"],
  Execution: ["gtm_distribution"],
  Timing: ["macro_data", "market_data"],
};

export function Radar({ dims }: { dims: Record<string, number> }) {
  const [focus, setFocus] = useState<string | null>(null);
  const outputs = useRun((s) => s.agentOutputs);
  const entries = Object.entries(dims);
  const n = entries.length;
  if (n < 3) return null;
  const cx = 140, cy = 130, R = 95;

  const pt = (i: number, v: number) => {
    const ang = (Math.PI * 2 * i) / n - Math.PI / 2;
    return [cx + Math.cos(ang) * R * (v / 10), cy + Math.sin(ang) * R * (v / 10)] as const;
  };
  const poly = entries.map(([, v], i) => pt(i, v).join(",")).join(" ");
  const color = (v: number) => (v >= 7 ? "#9ae64a" : v >= 4 ? "#fbbf24" : "#fb7185");

  const focusSources = focus
    ? (DIM_SOURCES[focus] ?? []).filter((id) => outputs[id])
    : [];

  return (
    <div>
      <svg viewBox="0 0 280 260" className="w-full max-w-sm" onMouseLeave={() => setFocus(null)}>
        {[2.5, 5, 7.5, 10].map((r) => (
          <polygon key={r}
            points={entries.map((_, i) => pt(i, r).join(",")).join(" ")}
            fill="none" stroke="rgba(148,163,184,0.12)" strokeWidth="1" />
        ))}
        {entries.map(([k], i) => {
          const [x, y] = pt(i, 10);
          return <line key={i} x1={cx} y1={cy} x2={x} y2={y}
            stroke={focus === k ? "rgba(6,182,212,0.5)" : "rgba(148,163,184,0.12)"} />;
        })}
        <polygon points={poly} fill="rgba(109,100,163,0.25)" stroke="#6d64a3" strokeWidth="2" />
        {entries.map(([k, v], i) => {
          const [x, y] = pt(i, v);
          const [lx, ly] = pt(i, 12.4);
          const hot = focus === k;
          return (
            <g key={k} onMouseEnter={() => setFocus(k)} className="cursor-pointer">
              {/* generous invisible hit area per axis */}
              <circle cx={lx} cy={ly - 3} r="16" fill="transparent" />
              <circle cx={x} cy={y} r={hot ? 5 : 3.5} fill={color(v)}
                style={{ transition: "r 0.15s", filter: hot ? `drop-shadow(0 0 6px ${color(v)})` : undefined }} />
              <text x={lx} y={ly} textAnchor="middle"
                className={hot ? "fill-cyan" : "fill-slate-400"}
                style={{ font: `${hot ? "700 " : ""}10px var(--font-jetbrains)`, transition: "fill 0.15s" }}>
                {k} {v}
              </text>
            </g>
          );
        })}
      </svg>
      <div className="min-h-[2.4rem]">
        {focus ? (
          <div className="flex flex-wrap items-center gap-1.5 font-mono text-[10px]">
            <span className="uppercase tracking-wider text-slate-500">{focus} scored by:</span>
            {focusSources.length ? focusSources.map((id) => {
              const a = agentById(id);
              const out = outputs[id];
              return (
                <span key={id} className="rounded border px-1.5 py-0.5"
                  style={{ color: a.accent, borderColor: `${a.accent}44` }}>
                  {a.name}{typeof out?.score === "number" ? ` ${out.score}` : ""}
                </span>
              );
            }) : <span className="text-slate-600">computed deterministically</span>}
          </div>
        ) : (
          <p className="font-mono text-[10px] text-slate-600">hover an axis → who scored it</p>
        )}
      </div>
    </div>
  );
}
