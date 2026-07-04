"use client";

/** The chart kit — renders every spec the Visualizer agent emits.
 * Zero dependencies, native SVG tooltips, and a what-if multiplier slider on
 * any chart that declares one. Types: gauge, waterfall, bar, column, donut,
 * scatter, heatmap, candlestick, area, bullet, sparkline.
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
    <div className="panel-hover rounded-xl border border-line bg-panel p-4">
      <div className="mb-1 flex items-center gap-2">
        <span className="h-1.5 w-1.5 rounded-full" style={{ background: a.accent }} />
        <h4 className="text-sm font-semibold text-slate-200">{spec.title}</h4>
        <span className="ml-auto font-mono text-[9px] uppercase tracking-wider text-slate-600">{a.name}</span>
      </div>
      <p className="mb-2 text-xs leading-relaxed text-slate-400">{spec.insight}</p>
      <ChartBody spec={spec} mult={mult} />
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
    default: return <pre className="font-mono text-[10px] text-slate-500">{JSON.stringify(d).slice(0, 200)}</pre>;
  }
}

/* ── gauge (speedometer) ─────────────────────────────────────────────────── */
function Gauge({ d }: { d: { value: number; min: number; max: number; bands?: number[] } }) {
  const pct = (d.value - d.min) / (d.max - d.min || 1);
  const ang = -90 + pct * 180;
  const arc = (from: number, to: number, color: string) => {
    const a0 = ((from - 90) * Math.PI) / 180, a1 = ((to - 90) * Math.PI) / 180;
    const x0 = 110 + 80 * Math.sin(a0), y0 = 100 - 80 * Math.cos(a0);
    const x1 = 110 + 80 * Math.sin(a1), y1 = 100 - 80 * Math.cos(a1);
    return <path d={`M${x0},${y0} A80,80 0 0 1 ${x1},${y1}`} fill="none" stroke={color} strokeWidth="14" strokeLinecap="round" />;
  };
  const [b1, b2] = d.bands ?? [d.max * 0.45, d.max * 0.7];
  const toDeg = (v: number) => -90 + ((v - d.min) / (d.max - d.min || 1)) * 180;
  return (
    <svg viewBox="0 0 220 120" className="mx-auto w-full max-w-[260px]">
      {arc(-90, toDeg(b1), `${ERR}55`)}{arc(toDeg(b1), toDeg(b2), `${WARN}55`)}{arc(toDeg(b2), 90, `${OK}55`)}
      <line x1="110" y1="100" x2={110 + 62 * Math.sin((ang * Math.PI) / 180)} y2={100 - 62 * Math.cos((ang * Math.PI) / 180)}
        stroke="#e2e8f0" strokeWidth="2.5" strokeLinecap="round" />
      <circle cx="110" cy="100" r="5" fill={scoreColor(d.value, d.max)} />
      <text x="110" y="80" textAnchor="middle" style={{ font: "700 20px var(--font-jetbrains)", fill: scoreColor(d.value, d.max) }}>
        {d.value}
      </text>
      <text x="110" y="115" textAnchor="middle" className="fill-slate-500" style={{ font: "9px var(--font-jetbrains)" }}>
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
      <text x="26" y="93" textAnchor="end" className="fill-slate-500" style={{ font: "9px var(--font-jetbrains)" }}>{d.base}</text>
      {vals.map((v, i) => {
        const x = 45 + i * ((W - 80) / n);
        const up = v.delta >= 0;
        return (
          <g key={i}>
            <title>{`${v.label}: ${v.value} (${up ? "+" : ""}${v.delta.toFixed(1)} vs base)`}</title>
            <rect x={x} width={bw} y={up ? sy(v.delta) : 90} height={Math.max(2, Math.abs(sy(v.delta) - 90))}
              rx="3" fill={up ? OK : ERR} opacity="0.85" className="transition-all hover:opacity-100" />
            <text x={x + bw / 2} y={H - 28} textAnchor="middle" className="fill-slate-400" style={{ font: "8.5px var(--font-jetbrains)" }}>
              {v.label.slice(0, 11)}
            </text>
            <text x={x + bw / 2} y={up ? sy(v.delta) - 4 : sy(v.delta) + 12} textAnchor="middle"
              style={{ font: "9px var(--font-jetbrains)", fill: up ? OK : ERR }}>{v.value}</text>
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
    const rowH = 20, H = d.labels.length * rowH + 8;
    return (
      <svg viewBox={`0 0 560 ${H}`} className="w-full">
        {d.labels.map((l, i) => {
          const name = agentById(l).name !== "Board" || !l.includes("_") ? agentById(l).name : l;
          const w = (Math.abs(vals[i]) / maxV) * 360;
          return (
            <g key={i}>
              <title>{`${name}: ${vals[i].toFixed(1)}`}</title>
              <text x="150" y={i * rowH + 14} textAnchor="end" className="fill-slate-400" style={{ font: "9.5px var(--font-jetbrains)" }}>
                {name.slice(0, 22)}
              </text>
              <rect x="158" y={i * rowH + 5} width={Math.max(2, w)} height={rowH - 9} rx="3"
                fill={agentById(l).accent} opacity="0.85" className="transition-all hover:opacity-100" />
              <text x={162 + w} y={i * rowH + 14} style={{ font: "9px var(--font-jetbrains)", fill: "#94a3b8" }}>
                {vals[i].toFixed(1)}
              </text>
            </g>
          );
        })}
      </svg>
    );
  }
  const n = d.labels.length, W = 560, bw = Math.min(64, (W - 60) / n - 8);
  const lo = Math.min(0, ...vals), span = Math.max(...vals, 0) - lo || 1;
  const sy = (v: number) => 150 - ((v - lo) / span) * 130;
  return (
    <svg viewBox={`0 0 ${W} 185`} className="w-full">
      {lo < 0 && <line x1="20" x2={W - 10} y1={sy(0)} y2={sy(0)} stroke="rgba(148,163,184,0.25)" />}
      {d.labels.map((l, i) => {
        const x = 34 + i * ((W - 60) / n);
        const up = vals[i] >= 0;
        return (
          <g key={i}>
            <title>{`${l}: ${vals[i].toFixed(1)}`}</title>
            <rect x={x} width={bw} y={Math.min(sy(vals[i]), sy(0))} height={Math.max(3, Math.abs(sy(vals[i]) - sy(0)))}
              rx="3" fill={up ? CYAN : ERR} opacity="0.85" className="transition-all hover:opacity-100" />
            <text x={x + bw / 2} y={172} textAnchor="middle" className="fill-slate-400" style={{ font: "8.5px var(--font-jetbrains)" }}>
              {String(l).slice(0, 12)}
            </text>
            <text x={x + bw / 2} y={sy(vals[i]) + (up ? -4 : 11)} textAnchor="middle"
              style={{ font: "9px var(--font-jetbrains)", fill: up ? CYAN : ERR }}>{vals[i].toFixed(1)}</text>
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
      <text x="280" y="184" textAnchor="middle" className="fill-slate-500" style={{ font: "9px var(--font-jetbrains)" }}>{d.x_label}</text>
      <text x="14" y="90" className="fill-slate-500" style={{ font: "9px var(--font-jetbrains)" }} transform="rotate(-90 14 90)">{d.y_label}</text>
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
            <span className="font-mono text-[9px] text-slate-600">{agentById(r.group).name}</span>
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
          <text x="36" y={sy(v) + 3} textAnchor="end" className="fill-slate-500" style={{ font: "8px var(--font-jetbrains)" }}>
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
          <text x="532" y={sy(d.target) - 4} textAnchor="end" style={{ font: "9px var(--font-jetbrains)", fill: OK }}>
            target{hitYear != null ? ` · hit ~yr ${hitYear}` : " · not hit in 30y"}
          </text>
        </g>
      )}
      <text x="290" y="184" textAnchor="middle" className="fill-slate-500" style={{ font: "9px var(--font-jetbrains)" }}>{d.x_label}</text>
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
      <text x={`${sx(d.value)}%`} y="58" style={{ font: "9px var(--font-jetbrains)", fill: "#94a3b8" }}>you: {d.value}</text>
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
