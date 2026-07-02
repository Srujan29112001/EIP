"use client";

/** Custom SVG radar (Helix idiom — no chart library). */
export function Radar({ dims }: { dims: Record<string, number> }) {
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

  return (
    <svg viewBox="0 0 280 260" className="w-full max-w-sm">
      {[2.5, 5, 7.5, 10].map((r) => (
        <polygon key={r}
          points={entries.map((_, i) => pt(i, r).join(",")).join(" ")}
          fill="none" stroke="rgba(148,163,184,0.12)" strokeWidth="1" />
      ))}
      {entries.map((_, i) => {
        const [x, y] = pt(i, 10);
        return <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="rgba(148,163,184,0.12)" />;
      })}
      <polygon points={poly} fill="rgba(109,100,163,0.25)" stroke="#6d64a3" strokeWidth="2" />
      {entries.map(([k, v], i) => {
        const [x, y] = pt(i, v);
        const [lx, ly] = pt(i, 12.4);
        return (
          <g key={k}>
            <circle cx={x} cy={y} r="3.5" fill={color(v)} />
            <text x={lx} y={ly} textAnchor="middle" className="fill-slate-400"
              style={{ font: "10px var(--font-jetbrains)" }}>
              {k} {v}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
