"use client";

/** The chart kit — renders every spec the Visualizer agent emits.
 * Zero dependencies, native SVG tooltips, animated motion (draw-in lines,
 * sweeping rings, staggered fades), and a what-if multiplier slider on any
 * chart that declares one. Types: gauge, waterfall, bar, column, donut,
 * scatter, heatmap, candlestick, area, bullet, line (multi-series), radial,
 * pyramid, funnel, histogram, sparkline.
 */

import { useState } from "react";
import { agentById } from "@/lib/agents";
import { SimSlider } from "./charts";

export interface ChartSpec {
  id: string;
  type: string;
  title: string;
  insight: string;
  source_agent: string;
  data: Record<string, unknown>;
  whatif?: { label: string; min: number; max: number; step: number };
}

const OK = "#9ae64a", WARN = "#fbbf24", ERR = "#fb7185", CYAN = "#22d3ee", BRAND = "#6d64a3";
const scoreColor = (v: number, max = 10) => (v / max >= 0.7 ? OK : v / max >= 0.45 ? WARN : ERR);

export function ChartCard({ spec }: { spec: ChartSpec }) {
  const [mult, setMult] = useState(1);
  const a = agentById(spec.source_agent);
  return (
    <div className="panel-hover card-in flex flex-col rounded-2xl border border-line bg-panel p-4">
      <div className="mb-1 flex items-center gap-2">
        <span className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: a.accent }} />
        <h4 className="min-w-0 truncate font-mono text-[11px] uppercase tracking-widest text-muted">{spec.title}</h4>
        <span className="ml-auto shrink-0 font-mono text-[10px] uppercase tracking-wider text-slate-400">{a.name}</span>
      </div>
      <p className="mb-2 text-xs leading-relaxed text-slate-400">{spec.insight}</p>
      <div className="flex min-h-[190px] flex-1 flex-col justify-center">
        <ChartBody spec={spec} mult={mult} />
      </div>
      {spec.whatif && (
        <div className="mt-2">
          <SimSlider label={spec.whatif.label} value={mult} min={spec.whatif.min}
            max={spec.whatif.max} step={spec.whatif.step} onChange={setMult}
            fmt={(v) => `${v.toFixed(2)}×`} />
        </div>
      )}
    </div>
  );
}

function ChartBody({ spec, mult }: { spec: ChartSpec; mult: number }) {
  const d = spec.data as never;
  switch (spec.type) {
    case "gauge": return <Gauge d={d} />;
    case "waterfall": return <Waterfall d={d} mult={mult} />;
    case "bar": return <Bars d={d} horizontal mult={mult} />;
    case "column": return <Bars d={d} mult={mult} />;
    case "donut": return <Donut d={d} />;
    case "scatter": return <Scatter d={d} />;
    case "heatmap": return <Heatmap d={d} />;
    case "candlestick": return <Candles d={d} mult={mult} />;
    case "area": return <Area d={d} mult={mult} />;
    case "bullet": return <Bullet d={d} />;
    case "line": return <MultiLine d={d} mult={mult} />;
    case "radial": return <Radial d={d} />;
    case "pyramid": case "funnel": return <Pyramid d={d} funnel={spec.type === "funnel"} />;
    case "histogram": return <Histogram d={d} mult={mult} />;
    default: return <pre className="font-mono text-[10px] text-slate-400">{JSON.stringify(d).slice(0, 200)}</pre>;
  }
}

/** shared motion styles — draw-in lines, sweeping rings, staggered fades */
function AnimStyle() {
  return (
    <style>{`
      @keyframes ckfade { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
      @keyframes ckdraw { to { stroke-dashoffset: 0; } }
      @keyframes cksweep { from { stroke-dashoffset: var(--ck-c); } to { stroke-dashoffset: var(--ck-o); } }
      .ck-a { opacity: 0; animation: ckfade .5s ease-out forwards; }
      .ck-draw { stroke-dasharray: 1; stroke-dashoffset: 1; animation: ckdraw 1.1s ease-out forwards; }
      .ck-sweep { animation: cksweep 1s ease-out forwards; }
    `}</style>
  );
}

/* ── gauge (speedometer) ─────────────────────────────────────────────────── */
function Gauge({ d }: { d: { value: number; min: number; max: number; bands?: number[] } }) {
  const pct = Math.max(0, Math.min(1, (d.value - d.min) / (d.max - d.min || 1)));
  const arc = (from: number, to: number, color: string, w = 16, cap: "round" | "butt" = "round") => {
    const a0 = ((from - 90) * Math.PI) / 180, a1 = ((to - 90) * Math.PI) / 180;
    const x0 = 110 + 82 * Math.sin(a0), y0 = 104 - 82 * Math.cos(a0);
    const x1 = 110 + 82 * Math.sin(a1), y1 = 104 - 82 * Math.cos(a1);
    return <path d={`M${x0},${y0} A82,82 0 ${to - from > 180 ? 1 : 0} 1 ${x1},${y1}`}
      fill="none" stroke={color} strokeWidth={w} strokeLinecap={cap} />;
  };
  const color = scoreColor(d.value, d.max);
  const ang = -90 + pct * 180;
  return (
    <svg viewBox="0 0 220 132" className="mx-auto w-full max-w-[300px]">
      {arc(-90, 90, "rgba(148,163,184,0.16)")}
      {pct > 0.005 && arc(-90, Math.max(-89, ang), color)}
      <line x1="110" y1="104" x2={110 + 58 * Math.sin((ang * Math.PI) / 180)} y2={104 - 58 * Math.cos((ang * Math.PI) / 180)}
        stroke="#e2e8f0" strokeWidth="2" strokeLinecap="round" opacity="0.7" />
      <circle cx="110" cy="104" r="5" fill={color} />
      <text x="110" y="78" textAnchor="middle" style={{ font: "700 26px var(--font-jetbrains)", fill: color }}>
        {d.value}
      </text>
      <text x="110" y="126" textAnchor="middle" className="fill-slate-400" style={{ font: "10px var(--font-jetbrains)" }}>
        of {d.max}
      </text>
    </svg>
  );
}

/* ── waterfall ───────────────────────────────────────────────────────────── */
function Waterfall({ d, mult }: { d: { base: number; steps: { label: string; value: number }[] }; mult: number }) {
  const W = 560, H = 180, n = d.steps.length, bw = Math.min(70, (W - 80) / n - 10);
  const vals = d.steps.map((s) => ({ ...s, delta: (s.value - d.base) * mult }));
  const maxAbs = Math.max(...vals.map((v) => Math.abs(v.delta)), 1);
  const sy = (delta: number) => 90 - (delta / maxAbs) * 60;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full">
      <line x1="30" x2={W - 10} y1="90" y2="90" stroke="rgba(148,163,184,0.25)" strokeDasharray="3 3" />
      <text x="26" y="93" textAnchor="end" className="fill-slate-400" style={{ font: "10px var(--font-jetbrains)" }}>{d.base}</text>
      {vals.map((v, i) => {
        const x = 45 + i * ((W - 80) / n);
        const up = v.delta >= 0;
        return (
          <g key={i}>
            <title>{`${v.label}: ${v.value} (${up ? "+" : ""}${v.delta.toFixed(1)} vs base)`}</title>
            <rect x={x} width={bw} y={up ? sy(v.delta) : 90} height={Math.max(2, Math.abs(sy(v.delta) - 90))}
              rx="3" fill={up ? OK : ERR} opacity="0.85" className="transition-all hover:opacity-100" />
            <text x={x + bw / 2} y={H - 28} textAnchor="middle" className="fill-slate-400" style={{ font: "10px var(--font-jetbrains)" }}>
              {v.label.slice(0, 11)}
            </text>
            <text x={x + bw / 2} y={up ? sy(v.delta) - 4 : sy(v.delta) + 12} textAnchor="middle"
              style={{ font: "10px var(--font-jetbrains)", fill: up ? OK : ERR }}>{v.value}</text>
          </g>
        );
      })}
    </svg>
  );
}

/* ── bars / columns ──────────────────────────────────────────────────────── */
function Bars({ d, horizontal = false, mult }: {
  d: { labels: string[]; values: number[]; max?: number }; horizontal?: boolean; mult: number;
}) {
  const vals = d.values.map((v) => v * mult);
  const maxV = d.max ?? Math.max(...vals.map(Math.abs), 1);
  if (horizontal) {
    const rowH = 28, H = d.labels.length * rowH + 10, BARX = 168, BARW = 350;
    return (
      <svg viewBox={`0 0 560 ${H}`} className="w-full">
        {d.labels.map((l, i) => {
          const name = agentById(l).name !== "Board" || !l.includes("_") ? agentById(l).name : l;
          const w = (Math.abs(vals[i]) / maxV) * BARW;
          return (
            <g key={i}>
              <title>{`${name}: ${vals[i].toFixed(1)}`}</title>
              <text x={BARX - 10} y={i * rowH + 18} textAnchor="end" className="fill-slate-400" style={{ font: "10px var(--font-jetbrains)" }}>
                {name.slice(0, 24)}
              </text>
              <rect x={BARX} y={i * rowH + 7} width={BARW} height={rowH - 13} rx="4" fill="rgba(148,163,184,0.1)" />
              <rect x={BARX} y={i * rowH + 7} width={Math.max(3, w)} height={rowH - 13} rx="4"
                fill={agentById(l).accent} opacity="0.9" className="transition-all hover:opacity-100" />
              <text x={BARX + BARW + 8} y={i * rowH + 18} style={{ font: "10px var(--font-jetbrains)", fill: "#cbd5e1" }}>
                {vals[i].toFixed(1)}
              </text>
            </g>
          );
        })}
      </svg>
    );
  }
  const n = d.labels.length, W = 560;
  const bw = Math.max(36, Math.min(88, (W - 120) / n - 18));
  const gap = Math.min(46, bw * 0.5);
  const total = n * bw + (n - 1) * gap;
  const startX = (W - total) / 2;
  const lo = Math.min(0, ...vals), span = Math.max(...vals, 0) - lo || 1;
  const sy = (v: number) => 150 - ((v - lo) / span) * 126;
  return (
    <svg viewBox={`0 0 ${W} 188`} className="w-full">
      {[0.25, 0.5, 0.75, 1].map((f) => (
        <line key={f} x1="24" x2={W - 24} y1={sy(lo + f * span)} y2={sy(lo + f * span)} stroke="rgba(148,163,184,0.09)" />
      ))}
      <line x1="24" x2={W - 24} y1={sy(Math.max(0, lo))} y2={sy(Math.max(0, lo))} stroke="rgba(148,163,184,0.3)" />
      {d.labels.map((l, i) => {
        const x = startX + i * (bw + gap);
        const up = vals[i] >= 0;
        return (
          <g key={i}>
            <title>{`${l}: ${vals[i].toFixed(1)}`}</title>
            <rect x={x} width={bw} y={Math.min(sy(vals[i]), sy(0))} height={Math.max(3, Math.abs(sy(vals[i]) - sy(0)))}
              rx="4" fill={up ? CYAN : ERR} opacity="0.9" className="transition-all hover:opacity-100" />
            <text x={x + bw / 2} y={174} textAnchor="middle" className="fill-slate-400" style={{ font: "10px var(--font-jetbrains)" }}>
              {String(l).slice(0, 12)}
            </text>
            <text x={x + bw / 2} y={sy(vals[i]) + (up ? -6 : 13)} textAnchor="middle"
              style={{ font: "600 10.5px var(--font-jetbrains)", fill: up ? CYAN : ERR }}>{vals[i].toFixed(1)}</text>
          </g>
        );
      })}
    </svg>
  );
}

/* ── donut ───────────────────────────────────────────────────────────────── */
function Donut({ d }: { d: { slices: { label: string; value: number; color?: string }[] } }) {
  const total = d.slices.reduce((s, x) => s + Math.max(0, x.value), 0) || 1;
  const palette = [CYAN, BRAND, OK, WARN, ERR, "#38bdf8", "#a78bfa"];
  let acc = 0;
  return (
    <div className="flex flex-wrap items-center justify-center gap-4">
      <svg viewBox="0 0 120 120" className="h-36 w-36">
        {d.slices.map((s, i) => {
          const frac = Math.max(0, s.value) / total;
          const a0 = acc * 2 * Math.PI - Math.PI / 2;
          acc += frac;
          const a1 = acc * 2 * Math.PI - Math.PI / 2;
          const large = frac > 0.5 ? 1 : 0;
          const p = (a: number, r: number) => `${60 + r * Math.cos(a)},${60 + r * Math.sin(a)}`;
          return (
            <path key={i}
              d={`M${p(a0, 52)} A52,52 0 ${large} 1 ${p(a1, 52)} L${p(a1, 30)} A30,30 0 ${large} 0 ${p(a0, 30)} Z`}
              fill={s.color ?? palette[i % palette.length]} opacity="0.9" className="transition-opacity hover:opacity-100">
              <title>{`${s.label}: ${s.value.toLocaleString()} (${Math.round(frac * 100)}%)`}</title>
            </path>
          );
        })}
        <text x="60" y="64" textAnchor="middle" style={{ font: "700 11px var(--font-jetbrains)", fill: "#cbd5e1" }}>
          {total >= 1000 ? `${(total / 1000).toFixed(0)}k` : total}
        </text>
      </svg>
      <div className="space-y-1">
        {d.slices.map((s, i) => (
          <div key={i} className="flex items-center gap-1.5 font-mono text-[10px] text-slate-400">
            <span className="h-2 w-2 rounded-sm" style={{ background: s.color ?? palette[i % palette.length] }} />
            {s.label} · {Math.round((Math.max(0, s.value) / total) * 100)}%
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── scatter (conviction map) ────────────────────────────────────────────── */
function Scatter({ d }: { d: { points: { x: number; y: number; label: string }[]; x_label: string; y_label: string } }) {
  const xs = d.points.map((p) => p.x), ys = d.points.map((p) => p.y);
  const xMin = Math.min(...xs, 0), xMax = Math.max(...xs, 10), yMin = Math.min(...ys, 0), yMax = Math.max(...ys, 100);
  const sx = (x: number) => 40 + ((x - xMin) / (xMax - xMin || 1)) * 480;
  const sy = (y: number) => 160 - ((y - yMin) / (yMax - yMin || 1)) * 130;
  return (
    <svg viewBox="0 0 560 190" className="w-full">
      <line x1="40" x2="520" y1="160" y2="160" stroke="rgba(148,163,184,0.2)" />
      <line x1="40" x2="40" y1="20" y2="160" stroke="rgba(148,163,184,0.2)" />
      <text x="280" y="184" textAnchor="middle" className="fill-slate-400" style={{ font: "10px var(--font-jetbrains)" }}>{d.x_label}</text>
      <text x="14" y="90" className="fill-slate-400" style={{ font: "10px var(--font-jetbrains)" }} transform="rotate(-90 14 90)">{d.y_label}</text>
      {d.points.map((p, i) => {
        const a = agentById(p.label);
        return (
          <g key={i} className="cursor-pointer">
            <title>{`${a.name}: ${p.x}/10 at ${p.y}% confidence`}</title>
            <circle cx={sx(p.x)} cy={sy(p.y)} r="5.5" fill={a.accent} opacity="0.85" className="transition-all hover:r-7 hover:opacity-100" />
          </g>
        );
      })}
    </svg>
  );
}

/* ── heatmap (risk rows) ─────────────────────────────────────────────────── */
function Heatmap({ d }: { d: { rows: { label: string; value: number; group: string }[] } }) {
  return (
    <div className="space-y-1">
      {d.rows.map((r, i) => {
        const heat = Math.max(0, Math.min(1, r.value));
        return (
          <div key={i} className="flex items-center gap-2" title={`severity ${(heat * 100).toFixed(0)}%`}>
            <span className="h-5 rounded-sm transition-all hover:scale-x-105"
              style={{ width: `${18 + heat * 82}%`, background: `color-mix(in srgb, ${ERR} ${Math.round(heat * 100)}%, ${WARN}33)` }} />
            <span className="min-w-0 flex-1 truncate text-[11px] text-slate-400">{r.label}</span>
            <span className="font-mono text-[10px] text-slate-400">{agentById(r.group).name}</span>
          </div>
        );
      })}
    </div>
  );
}

/* ── candlestick (real OHLC) ─────────────────────────────────────────────── */
function Candles({ d, mult }: { d: { ohlc: [string, number, number, number, number, number][] }; mult: number }) {
  const n = Math.max(10, Math.min(d.ohlc.length, Math.round(120 * mult)));
  const rows = d.ohlc.slice(-n);
  const lo = Math.min(...rows.map((r) => r[3])), hi = Math.max(...rows.map((r) => r[2]));
  const sy = (v: number) => 12 + (1 - (v - lo) / (hi - lo || 1)) * 150;
  const W = 560, cw = Math.max(1.6, (W - 50) / rows.length - 1.2);
  return (
    <svg viewBox={`0 0 ${W} 190`} className="w-full">
      {[lo, (lo + hi) / 2, hi].map((v, i) => (
        <g key={i}>
          <line x1="40" x2={W - 6} y1={sy(v)} y2={sy(v)} stroke="rgba(148,163,184,0.09)" />
          <text x="36" y={sy(v) + 3} textAnchor="end" className="fill-slate-400" style={{ font: "10px var(--font-jetbrains)" }}>
            {v.toFixed(0)}
          </text>
        </g>
      ))}
      {rows.map((r, i) => {
        const [date, o, h, l, c] = r;
        const x = 42 + i * ((W - 50) / rows.length);
        const up = c >= o;
        return (
          <g key={i}>
            <title>{`${date} · O${o} H${h} L${l} C${c}`}</title>
            <line x1={x + cw / 2} x2={x + cw / 2} y1={sy(h)} y2={sy(l)} stroke={up ? OK : ERR} strokeWidth="0.8" />
            <rect x={x} width={cw} y={sy(Math.max(o, c))} height={Math.max(1, Math.abs(sy(o) - sy(c)))}
              fill={up ? OK : ERR} opacity="0.9" />
          </g>
        );
      })}
    </svg>
  );
}

/* ── area (growth curve with target line) ────────────────────────────────── */
function Area({ d, mult }: { d: { points: { x: number; y: number }[]; x_label: string; y_label: string; target?: number }; mult: number }) {
  const pts = d.points.map((p, i) => ({ x: p.x, y: i === 0 ? p.y : p.y * mult }));
  const hi = Math.max(...pts.map((p) => p.y), d.target ?? 0);
  const sx = (x: number) => 46 + (x / (pts[pts.length - 1].x || 1)) * 490;
  const sy = (y: number) => 160 - (y / (hi || 1)) * 140;
  const path = pts.map((p, i) => `${i ? "L" : "M"}${sx(p.x).toFixed(1)},${sy(p.y).toFixed(1)}`).join(" ");
  const hitYear = d.target ? pts.find((p) => p.y >= d.target!)?.x : undefined;
  return (
    <svg viewBox="0 0 560 190" className="w-full">
      <path d={`${path} L${sx(pts[pts.length - 1].x)},160 L46,160 Z`} fill={CYAN} opacity="0.1" />
      <path d={path} fill="none" stroke={CYAN} strokeWidth="2" />
      {d.target && (
        <g>
          <line x1="46" x2="536" y1={sy(d.target)} y2={sy(d.target)} stroke={OK} strokeDasharray="5 4" strokeOpacity="0.6" />
          <text x="532" y={sy(d.target) - 4} textAnchor="end" style={{ font: "10px var(--font-jetbrains)", fill: OK }}>
            target{hitYear != null ? ` · hit ~yr ${hitYear}` : " · not hit in 30y"}
          </text>
        </g>
      )}
      <text x="290" y="184" textAnchor="middle" className="fill-slate-400" style={{ font: "10px var(--font-jetbrains)" }}>{d.x_label}</text>
    </svg>
  );
}

/* ── bullet (actual vs target) ───────────────────────────────────────────── */
function Bullet({ d }: { d: { value: number; target: number; bands: number[]; max: number } }) {
  const sx = (v: number) => (v / (d.max || 1)) * 100;
  return (
    <svg viewBox="0 0 560 64" className="w-full">
      <rect x="0" y="18" width={`${sx(d.bands[0])}%`} height="22" fill={`${ERR}33`} rx="3" />
      <rect x={`${sx(d.bands[0])}%`} y="18" width={`${sx(d.bands[1] - d.bands[0])}%`} height="22" fill={`${WARN}33`} />
      <rect x={`${sx(d.bands[1])}%`} y="18" width={`${sx(d.max - d.bands[1])}%`} height="22" fill={`${OK}22`} />
      <rect x="0" y="24" width={`${sx(d.value)}%`} height="10" rx="2" fill={scoreColor(d.value, d.max)}>
        <title>{`actual: ${d.value}`}</title>
      </rect>
      <line x1={`${sx(d.target)}%`} x2={`${sx(d.target)}%`} y1="12" y2="46" stroke="#e2e8f0" strokeWidth="2">
        <title>{`target: ${d.target}`}</title>
      </line>
      <text x={`${sx(d.value)}%`} y="58" style={{ font: "10px var(--font-jetbrains)", fill: "#94a3b8" }}>you: {d.value}</text>
    </svg>
  );
}

/** Tiny inline sparkline for insight cards. */
export function Sparkline({ values, color = CYAN }: { values: number[]; color?: string }) {
  if (values.length < 2) return null;
  const lo = Math.min(...values), hi = Math.max(...values);
  const pts = values.map((v, i) =>
    `${(i / (values.length - 1)) * 80},${18 - ((v - lo) / (hi - lo || 1)) * 16}`).join(" ");
  return (
    <svg viewBox="0 0 80 20" className="h-4 w-20">
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" />
    </svg>
  );
}

/* ── multi-series line (animated draw-in) — e.g. round 1 vs round 2 ────────── */
function MultiLine({ d, mult }: {
  d: { labels: string[]; series: { name: string; values: number[]; color?: string }[]; max?: number };
  mult: number;
}) {
  const W = 560, H = 190, PADL = 34, PADB = 30;
  const palette = [CYAN, WARN, OK, BRAND, ERR];
  const series = (d.series ?? []).map((s, si) => ({
    ...s,
    color: s.color ?? palette[si % palette.length],
    // the what-if slider bends the LAST series (the "current" one)
    values: s.values.map((v) => (si === d.series.length - 1 ? v * mult : v)),
  }));
  const all = series.flatMap((s) => s.values);
  if (!all.length) return null;
  const hi = d.max ?? Math.max(...all, 1), lo = Math.min(0, ...all);
  const sx = (i: number) => PADL + (i / Math.max(1, d.labels.length - 1)) * (W - PADL - 14);
  const sy = (v: number) => H - PADB - ((v - lo) / (hi - lo || 1)) * (H - PADB - 18);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full">
      <AnimStyle />
      {[0.25, 0.5, 0.75, 1].map((f) => (
        <line key={f} x1={PADL} x2={W - 14} y1={sy(lo + f * (hi - lo))} y2={sy(lo + f * (hi - lo))}
          stroke="rgba(148,163,184,0.12)" />
      ))}
      {series.map((s, si) => (
        <g key={si}>
          <polyline className="ck-draw" pathLength={1} style={{ animationDelay: `${si * 0.25}s` }}
            points={s.values.map((v, i) => `${sx(i)},${sy(v)}`).join(" ")}
            fill="none" stroke={s.color} strokeWidth="2.2" strokeLinejoin="round" />
          {s.values.map((v, i) => (
            <circle key={i} className="ck-a" style={{ animationDelay: `${0.3 + i * 0.05}s` }}
              cx={sx(i)} cy={sy(v)} r="3" fill={s.color}>
              <title>{`${s.name} · ${d.labels[i]}: ${v.toFixed(1)}`}</title>
            </circle>
          ))}
        </g>
      ))}
      {d.labels.map((l, i) => (
        <text key={i} x={sx(i)} y={H - 10} textAnchor="middle" className="fill-slate-400"
          style={{ font: "10px var(--font-jetbrains)" }}>{String(l).slice(0, 10)}</text>
      ))}
      {series.map((s, si) => (
        <g key={`lg${si}`} className="ck-a" style={{ animationDelay: `${0.2 + si * 0.1}s` }}>
          <rect x={PADL + si * 130} y={4} width="10" height="3" fill={s.color} rx="1.5" />
          <text x={PADL + si * 130 + 14} y={9} style={{ font: "10px var(--font-jetbrains)", fill: "#94a3b8" }}>{s.name}</text>
        </g>
      ))}
    </svg>
  );
}

/* ── radial progress rings (animated sweep) — probabilities at a glance ────── */
function Radial({ d }: { d: { rings: { label: string; value: number; color?: string }[] } }) {
  const palette = [OK, CYAN, WARN, BRAND];
  const rings = (d.rings ?? []).slice(0, 4);
  return (
    <div className="flex flex-wrap items-center justify-center gap-5">
      <svg viewBox="0 0 130 130" className="h-40 w-40">
        <AnimStyle />
        {rings.map((r, i) => {
          const rad = 54 - i * 13;
          const c = 2 * Math.PI * rad;
          const off = c * (1 - Math.max(0, Math.min(100, r.value)) / 100);
          return (
            <g key={i}>
              <circle cx="65" cy="65" r={rad} fill="none" stroke="rgba(148,163,184,0.12)" strokeWidth="9" />
              <circle className="ck-sweep" cx="65" cy="65" r={rad} fill="none"
                stroke={r.color ?? palette[i % palette.length]} strokeWidth="9" strokeLinecap="round"
                strokeDasharray={c} strokeDashoffset={off}
                style={{ ["--ck-c" as never]: `${c}`, ["--ck-o" as never]: `${off}`,
                         transform: "rotate(-90deg)", transformOrigin: "65px 65px",
                         animationDelay: `${i * 0.15}s` }}>
                <title>{`${r.label}: ${Math.round(r.value)}%`}</title>
              </circle>
            </g>
          );
        })}
        {rings[0] && (
          <text x="65" y="70" textAnchor="middle"
            style={{ font: "700 17px var(--font-jetbrains)", fill: rings[0].color ?? OK }}>
            {Math.round(rings[0].value)}%
          </text>
        )}
      </svg>
      <ul className="space-y-1.5">
        {rings.map((r, i) => (
          <li key={i} className="flex items-center gap-2 text-xs text-slate-300">
            <span className="h-2 w-2 rounded-full" style={{ background: r.color ?? palette[i % palette.length] }} />
            {r.label} — <b>{Math.round(r.value)}%</b>
          </li>
        ))}
      </ul>
    </div>
  );
}

/* ── pyramid / funnel (staggered) — e.g. board consensus, TAM→SAM→SOM ──────── */
function Pyramid({ d, funnel = false }: {
  d: { levels: { label: string; value: number; color?: string }[] }; funnel?: boolean;
}) {
  const palette = [OK, CYAN, WARN, BRAND, ERR];
  const levels = funnel ? (d.levels ?? []) : [...(d.levels ?? [])];
  const maxV = Math.max(...levels.map((l) => Math.abs(l.value)), 1);
  const H = levels.length * 34 + 8, W = 560;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full">
      <AnimStyle />
      {levels.map((l, i) => {
        const frac = Math.max(0.12, Math.abs(l.value) / maxV);
        const topW = funnel
          ? Math.max(0.12, Math.abs(levels[Math.max(0, i - 1)]?.value ?? l.value) / maxV) * 300
          : (i === 0 ? frac : Math.max(0.12, Math.abs(levels[i - 1].value) / maxV)) * 300;
        const botW = frac * 300;
        const y = i * 34 + 4, cx = 190;
        return (
          <g key={i} className="ck-a" style={{ animationDelay: `${i * 0.12}s` }}>
            <title>{`${l.label}: ${l.value.toLocaleString()}`}</title>
            <path d={`M${cx - topW / 2},${y} L${cx + topW / 2},${y} L${cx + botW / 2},${y + 26} L${cx - botW / 2},${y + 26} Z`}
              fill={l.color ?? palette[i % palette.length]} opacity="0.85" className="transition-opacity hover:opacity-100" />
            <text x={cx + 175} y={y + 17} style={{ font: "10px var(--font-jetbrains)", fill: "#cbd5e1" }}>
              {l.label.slice(0, 26)} — <tspan style={{ fill: l.color ?? palette[i % palette.length] }}>{l.value.toLocaleString()}</tspan>
            </text>
          </g>
        );
      })}
    </svg>
  );
}

/* ── histogram (distribution) — e.g. 1000 simulated verdicts ───────────────── */
function Histogram({ d, mult }: {
  d: { bins: number[]; start: number; step: number; marker?: number; marker_label?: string; x_label?: string };
  mult: number;
}) {
  const bins = (d.bins ?? []).map((b) => b * mult);
  if (!bins.length) return null;
  const W = 560, H = 170, maxB = Math.max(...bins, 1), bw = (W - 60) / bins.length;
  const sx = (v: number) => 30 + ((v - d.start) / (d.step * bins.length || 1)) * (W - 60);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full">
      <AnimStyle />
      {bins.map((b, i) => (
        <g key={i} className="ck-a" style={{ animationDelay: `${i * 0.04}s` }}>
          <title>{`${(d.start + i * d.step).toFixed(1)}–${(d.start + (i + 1) * d.step).toFixed(1)}: ${Math.round(b)}`}</title>
          <rect x={30 + i * bw + 1} y={140 - (b / maxB) * 118} width={Math.max(2, bw - 2)}
            height={Math.max(1, (b / maxB) * 118)} rx="2" fill={CYAN} opacity="0.75"
            className="transition-opacity hover:opacity-100" />
        </g>
      ))}
      {typeof d.marker === "number" && (
        <g className="ck-a" style={{ animationDelay: "0.5s" }}>
          <line x1={sx(d.marker)} x2={sx(d.marker)} y1="14" y2="142" stroke={WARN} strokeWidth="2" strokeDasharray="4 3" />
          <text x={sx(d.marker) + 4} y="22" style={{ font: "10px var(--font-jetbrains)", fill: WARN }}>
            {d.marker_label ?? `P50 ${d.marker}`}
          </text>
        </g>
      )}
      {[0, Math.floor(bins.length / 2), bins.length - 1].map((i) => (
        <text key={i} x={30 + i * bw + bw / 2} y={H - 12} textAnchor="middle" className="fill-slate-400"
          style={{ font: "10px var(--font-jetbrains)" }}>{(d.start + i * d.step).toFixed(1)}</text>
      ))}
      {d.x_label && <text x={W / 2} y={H - 1} textAnchor="middle" className="fill-slate-400"
        style={{ font: "10px var(--font-jetbrains)" }}>{d.x_label}</text>}
    </svg>
  );
}
