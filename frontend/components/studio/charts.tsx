"use client";

/** EIP chart engine — zero-dependency interactive SVG (Helix idiom).
 * One shared time-series component powers every simulation chart: past line,
 * projected future line, uncertainty cone, hover crosshair with tooltip.
 */

import { useMemo, useRef, useState } from "react";

export interface SeriesPoint {
  x: number;        // ordinal position (index or month offset)
  y: number;
  label?: string;   // e.g. a date for the tooltip
}

export interface Cone {
  points: { x: number; lo: number; hi: number }[];
  color?: string;
}

export function TimeSeries({
  past, future, cone, height = 220, color = "#22d3ee", futureColor = "#a78bfa",
  yLabel = "", zeroLine = false, markerX,
}: {
  past: SeriesPoint[];
  future?: SeriesPoint[];
  cone?: Cone;
  height?: number;
  color?: string;
  futureColor?: string;
  yLabel?: string;
  zeroLine?: boolean;
  markerX?: number | null;   // e.g. the month cash hits zero
}) {
  const W = 640, H = height, PAD = { l: 46, r: 12, t: 14, b: 22 };
  const [hover, setHover] = useState<{ px: number; pt: SeriesPoint; isFuture: boolean } | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const all = useMemo(() => {
    const pts = [...past, ...(future ?? [])];
    const ys = [...pts.map((p) => p.y),
      ...(cone?.points.flatMap((c) => [c.lo, c.hi]) ?? []),
      ...(zeroLine ? [0] : [])];
    const xs = pts.map((p) => p.x);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    let minY = Math.min(...ys), maxY = Math.max(...ys);
    if (minY === maxY) { minY -= 1; maxY += 1; }
    const padY = (maxY - minY) * 0.08;
    return { minX, maxX, minY: minY - padY, maxY: maxY + padY };
  }, [past, future, cone, zeroLine]);

  const sx = (x: number) => PAD.l + ((x - all.minX) / (all.maxX - all.minX || 1)) * (W - PAD.l - PAD.r);
  const sy = (y: number) => PAD.t + (1 - (y - all.minY) / (all.maxY - all.minY || 1)) * (H - PAD.t - PAD.b);

  const path = (pts: SeriesPoint[]) => pts.map((p, i) => `${i ? "L" : "M"}${sx(p.x).toFixed(1)},${sy(p.y).toFixed(1)}`).join(" ");
  const area = (pts: SeriesPoint[]) =>
    `${path(pts)} L${sx(pts[pts.length - 1].x).toFixed(1)},${sy(all.minY)} L${sx(pts[0].x).toFixed(1)},${sy(all.minY)} Z`;

  const conePath = useMemo(() => {
    if (!cone?.points.length) return "";
    const up = cone.points.map((c, i) => `${i ? "L" : "M"}${sx(c.x).toFixed(1)},${sy(c.hi).toFixed(1)}`).join(" ");
    const down = [...cone.points].reverse().map((c) => `L${sx(c.x).toFixed(1)},${sy(c.lo).toFixed(1)}`).join(" ");
    return `${up} ${down} Z`;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cone, all]);

  const onMove = (e: React.MouseEvent) => {
    const svg = svgRef.current;
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    const px = ((e.clientX - rect.left) / rect.width) * W;
    const pool = [...past.map((p) => ({ p, f: false })), ...(future ?? []).map((p) => ({ p, f: true }))];
    if (!pool.length) return;
    const best = pool.reduce((a, b) => (Math.abs(sx(b.p.x) - px) < Math.abs(sx(a.p.x) - px) ? b : a));
    setHover({ px: sx(best.p.x), pt: best.p, isFuture: best.f });
  };

  const yTicks = useMemo(() => {
    const n = 4, out: number[] = [];
    for (let i = 0; i <= n; i++) out.push(all.minY + ((all.maxY - all.minY) * i) / n);
    return out;
  }, [all]);

  return (
    <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} className="w-full select-none"
      onMouseMove={onMove} onMouseLeave={() => setHover(null)}>
      {yTicks.map((t, i) => (
        <g key={i}>
          <line x1={PAD.l} x2={W - PAD.r} y1={sy(t)} y2={sy(t)} stroke="rgba(148,163,184,0.09)" />
          <text x={PAD.l - 6} y={sy(t) + 3} textAnchor="end" className="fill-slate-500"
            style={{ font: "9px var(--font-jetbrains)" }}>
            {Math.abs(t) >= 1000 ? `${(t / 1000).toFixed(1)}k` : t.toFixed(Math.abs(all.maxY) < 20 ? 1 : 0)}
          </text>
        </g>
      ))}
      {zeroLine && all.minY < 0 && (
        <line x1={PAD.l} x2={W - PAD.r} y1={sy(0)} y2={sy(0)} stroke="#fb7185" strokeDasharray="4 3" strokeOpacity="0.5" />
      )}
      {yLabel && (
        <text x={PAD.l} y={10} className="fill-slate-500" style={{ font: "9px var(--font-jetbrains)" }}>{yLabel}</text>
      )}

      {/* uncertainty cone under the lines */}
      {conePath && <path d={conePath} fill={cone?.color ?? futureColor} opacity="0.13" />}

      {/* past: area + line */}
      {past.length > 1 && (
        <>
          <path d={area(past)} fill={color} opacity="0.07" />
          <path d={path(past)} fill="none" stroke={color} strokeWidth="2" />
        </>
      )}

      {/* future: dashed line, seeded from the last past point */}
      {future && future.length > 0 && past.length > 0 && (
        <path d={path([past[past.length - 1], ...future])} fill="none" stroke={futureColor}
          strokeWidth="2" strokeDasharray="5 4" />
      )}

      {/* now divider */}
      {future && future.length > 0 && past.length > 0 && (
        <g>
          <line x1={sx(past[past.length - 1].x)} x2={sx(past[past.length - 1].x)}
            y1={PAD.t} y2={H - PAD.b} stroke="rgba(148,163,184,0.25)" strokeDasharray="2 3" />
          <text x={sx(past[past.length - 1].x) + 4} y={PAD.t + 8} className="fill-slate-500"
            style={{ font: "8px var(--font-jetbrains)" }}>now</text>
        </g>
      )}

      {/* event marker (e.g. cash-out month) */}
      {markerX != null && (
        <g>
          <line x1={sx(markerX)} x2={sx(markerX)} y1={PAD.t} y2={H - PAD.b}
            stroke="#fb7185" strokeWidth="1.5" strokeOpacity="0.7" />
          <circle cx={sx(markerX)} cy={PAD.t + 5} r="3" fill="#fb7185" />
        </g>
      )}

      {/* hover crosshair + tooltip */}
      {hover && (
        <g>
          <line x1={hover.px} x2={hover.px} y1={PAD.t} y2={H - PAD.b} stroke="rgba(255,255,255,0.18)" />
          <circle cx={hover.px} cy={sy(hover.pt.y)} r="3.5"
            fill={hover.isFuture ? futureColor : color} stroke="#04060f" strokeWidth="1.5" />
          <g transform={`translate(${Math.min(hover.px + 8, W - 150)}, ${PAD.t + 4})`}>
            <rect width="142" height="34" rx="6" fill="#0a1020" stroke="rgba(148,163,184,0.25)" />
            <text x="8" y="14" className="fill-slate-400" style={{ font: "9px var(--font-jetbrains)" }}>
              {hover.pt.label ?? `t = ${hover.pt.x}`}{hover.isFuture ? " · projected" : ""}
            </text>
            <text x="8" y="27" style={{ font: "700 11px var(--font-jetbrains)", fill: hover.isFuture ? futureColor : color }}>
              {hover.pt.y >= 1000 ? hover.pt.y.toLocaleString(undefined, { maximumFractionDigits: 0 }) : hover.pt.y.toFixed(2)}
            </text>
          </g>
        </g>
      )}
    </svg>
  );
}

/** Compact labelled slider used by every simulator. */
export function SimSlider({ label, value, min, max, step, onChange, fmt }: {
  label: string; value: number; min: number; max: number; step: number;
  onChange: (v: number) => void; fmt?: (v: number) => string;
}) {
  return (
    <label className="block">
      <span className="flex justify-between font-mono text-[10px] uppercase tracking-wider text-slate-500">
        {label} <span className="text-cyan">{fmt ? fmt(value) : value}</span>
      </span>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={(e) => onChange(Number(e.target.value))} className="w-full accent-[#06b6d4]" />
    </label>
  );
}
