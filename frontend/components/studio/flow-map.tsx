"use client";

/** The Flow Map — the whole agent workflow as a living tree. Data streams
 * left → right through the five intelligence layers; edges pulse while the
 * downstream agent works; click any node for its live status and output.
 */

import { useMemo, useState } from "react";
import { AGENTS, LAYER_LABELS, PEERS, agentById, type Layer } from "@/lib/agents";
import { useRun } from "@/lib/store";
import type { AgentOutput } from "@/lib/types";

const LAYERS: Layer[] = ["L0", "L1", "L2", "L3", "L4"];

export function FlowMap({ onFocus }: { onFocus?: (id: string) => void }) {
  const { agentStatus, scope, agentOutputs, collabs } = useRun();
  const [sel, setSel] = useState<string | null>(null);

  const active = useMemo(() => {
    const ids = scope.length
      ? ["intake_parser", "context_profiler", "scope_planner", ...scope]
      : AGENTS.map((a) => a.id);
    const set = new Set(ids);
    return AGENTS.filter((a) => set.has(a.id));
  }, [scope]);

  // layout: one column per layer, agents stacked vertically
  const W = 900, ROW = 46, PAD_T = 54;
  const cols = LAYERS.map((l) => active.filter((a) => a.layer === l));
  const H = PAD_T + Math.max(...cols.map((c) => c.length), 1) * ROW + 20;
  const colX = (i: number) => 80 + i * ((W - 160) / (LAYERS.length - 1));
  const pos = new Map<string, { x: number; y: number }>();
  cols.forEach((agents, ci) => {
    agents.forEach((a, ri) => {
      const offset = ((cols[ci].length - 1) * ROW) / 2;
      pos.set(a.id, { x: colX(ci), y: PAD_T + H / 2 - PAD_T / 2 - offset + ri * ROW - 20 });
    });
  });

  // edges: every agent feeds the next layer's agents (the shared blackboard flow)
  const edges: { from: string; to: string }[] = [];
  for (let i = 0; i < LAYERS.length - 1; i++) {
    for (const a of cols[i]) for (const b of cols[i + 1]) edges.push({ from: a.id, to: b.id });
  }

  // A2A mesh: expert ↔ expert links (venture.PEERS), so specialists visibly
  // build on EACH OTHER — not just funnel into the common grounding/crucible
  // agents. `live` = the collab actually fired this run (bright gold); else the
  // wiring is latent (faint gold). Deduped, undirected.
  const activeIds = new Set(active.map((a) => a.id));
  const peerSeen = new Set<string>();
  const peerEdges: { from: string; to: string; live: boolean }[] = [];
  for (const a of active) {
    const declared = PEERS[a.id] ?? [];
    const livePeers = collabs[a.id] ?? [];
    for (const p of new Set([...declared, ...livePeers])) {
      if (!activeIds.has(p) || p === a.id) continue;
      const key = a.id < p ? `${a.id}|${p}` : `${p}|${a.id}`;
      if (peerSeen.has(key)) continue;
      peerSeen.add(key);
      const live = livePeers.includes(p) || (collabs[p] ?? []).includes(a.id);
      peerEdges.push({ from: p, to: a.id, live });
    }
  }

  const status = (id: string) => agentStatus[id] ?? "queued";
  const selAgent = sel ? agentById(sel) : null;
  const selOut = sel ? (agentOutputs[sel] as AgentOutput | undefined) : undefined;

  return (
    <div className="space-y-3">
      <div className="overflow-x-auto rounded-xl border border-line bg-panel p-2">
        <svg viewBox={`0 0 ${W} ${H}`} className="min-w-[720px] w-full">
          <defs>
            <style>{`@keyframes flowdash { to { stroke-dashoffset: -14; } }`}</style>
          </defs>

          {/* layer headers */}
          {LAYERS.map((l, i) => (
            <g key={l}>
              <text x={colX(i)} y={22} textAnchor="middle" className="fill-slate-500"
                style={{ font: "700 10px var(--font-jetbrains)", letterSpacing: "0.15em" }}>
                {l} · {LAYER_LABELS[l].toUpperCase()}
              </text>
              <line x1={colX(i)} x2={colX(i)} y1={30} y2={H - 8} stroke="rgba(148,163,184,0.05)" />
            </g>
          ))}

          {/* edges */}
          {edges.map(({ from, to }, i) => {
            const p1 = pos.get(from), p2 = pos.get(to);
            if (!p1 || !p2) return null;
            const fromDone = status(from) === "done";
            const toActive = status(to) === "active";
            const mx = (p1.x + p2.x) / 2;
            return (
              <path key={i}
                d={`M${p1.x + 12},${p1.y} C${mx},${p1.y} ${mx},${p2.y} ${p2.x - 12},${p2.y}`}
                fill="none"
                stroke={toActive ? "#22d3ee" : fromDone ? "rgba(34,211,238,0.13)" : "rgba(148,163,184,0.06)"}
                strokeWidth={toActive ? 1.6 : 0.8}
                strokeDasharray={toActive ? "6 8" : undefined}
                style={toActive ? { animation: "flowdash 0.7s linear infinite" } : undefined}
              />
            );
          })}

          {/* A2A mesh — expert ↔ expert arcs (gold), bowed out of the column so
              you can SEE specialists building on each other, not just the
              common agents. Bright = it fired this run; faint = latent wiring. */}
          {peerEdges.map(({ from, to, live }, i) => {
            const p1 = pos.get(from), p2 = pos.get(to);
            if (!p1 || !p2) return null;
            const dy = Math.abs(p2.y - p1.y);
            const bulge = Math.min(150, 34 + dy * 0.5);
            // same column → bow left of the column; cross-column → bow left of the midpoint
            const cx = (p1.x === p2.x ? p1.x : (p1.x + p2.x) / 2) - bulge;
            const cy = (p1.y + p2.y) / 2;
            return (
              <path key={`peer${i}`}
                d={`M${p1.x - 11},${p1.y} Q${cx},${cy} ${p2.x - 11},${p2.y}`}
                fill="none"
                stroke="#fbbf24"
                strokeOpacity={live ? 0.9 : 0.2}
                strokeWidth={live ? 1.9 : 1}
                strokeLinecap="round"
                strokeDasharray={live ? "5 6" : undefined}
                style={live ? { animation: "flowdash 0.9s linear infinite" } : undefined}
              />
            );
          })}

          {/* nodes — icon chips that glow while working */}
          {active.map((a) => {
            const p = pos.get(a.id);
            if (!p) return null;
            const st = status(a.id);
            return (
              <g key={a.id} onClick={() => { setSel(sel === a.id ? null : a.id); onFocus?.(a.id); }}
                className="cursor-pointer">
                <title>{`${a.name} · ${st} — click for inputs/outputs`}</title>
                {st === "active" && (
                  <circle cx={p.x} cy={p.y} r={16} fill="none" stroke={a.accent} strokeOpacity={0.5}>
                    <animate attributeName="r" values="13;20;13" dur="1.4s" repeatCount="indefinite" />
                    <animate attributeName="stroke-opacity" values="0.6;0;0.6" dur="1.4s" repeatCount="indefinite" />
                  </circle>
                )}
                <circle cx={p.x} cy={p.y} r={sel === a.id ? 14 : 12}
                  fill="#0d1428"
                  stroke={st === "queued" ? "#334155" : a.accent}
                  strokeWidth={st === "active" ? 2 : 1.4}
                  strokeDasharray={st === "skipped" ? "3 2" : undefined}
                  style={st === "active" || st === "done"
                    ? { filter: `drop-shadow(0 0 ${st === "active" ? 9 : 4}px ${a.accent}${st === "active" ? "cc" : "55"})` }
                    : undefined}
                  className="transition-all duration-300" />
                <text x={p.x} y={p.y + 4} textAnchor="middle"
                  style={{ font: "11px sans-serif", opacity: st === "queued" || st === "skipped" ? 0.35 : 1 }}>
                  {a.icon}
                </text>
                {st === "done" && (
                  <g>
                    <circle cx={p.x + 10} cy={p.y - 9} r="4.5" fill="#9ae64a" />
                    <text x={p.x + 10} y={p.y - 6.5} textAnchor="middle" style={{ font: "700 6.5px sans-serif", fill: "#04060f" }}>✓</text>
                  </g>
                )}
                {st === "degraded" && (
                  <g>
                    <circle cx={p.x + 10} cy={p.y - 9} r="4.5" fill="#fbbf24" />
                    <text x={p.x + 10} y={p.y - 6} textAnchor="middle" style={{ font: "700 7px sans-serif", fill: "#04060f" }}>!</text>
                  </g>
                )}
                {st === "error" && (
                  <g>
                    <circle cx={p.x + 10} cy={p.y - 9} r="4.5" fill="#fb7185" />
                    <text x={p.x + 10} y={p.y - 6} textAnchor="middle" style={{ font: "700 7px sans-serif", fill: "#04060f" }}>!</text>
                  </g>
                )}
                <text x={p.x} y={p.y + 26} textAnchor="middle"
                  style={{ font: "9px var(--font-jetbrains)", fill: st === "queued" ? "#475569" : "#cbd5e1" }}>
                  {a.name.length > 18 ? a.name.slice(0, 17) + "…" : a.name}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* selected node detail */}
      {selAgent && (
        <div className="rounded-xl border border-line bg-panel p-4 text-xs">
          <div className="mb-1 flex items-center gap-2">
            <span className="h-2 w-2 rounded-full" style={{ background: selAgent.accent }} />
            <span className="font-semibold" style={{ color: selAgent.accent }}>{selAgent.name}</span>
            <span className="font-mono text-[10px] text-slate-500">{selAgent.layer} · {status(selAgent.id)}</span>
            <button onClick={() => setSel(null)} className="ml-auto text-slate-500 hover:text-white">✕</button>
          </div>
          <p className="text-slate-400">{selAgent.blurb}</p>
          {selOut?.verdict_line && (
            <p className="mt-2 rounded-lg bg-panel-2 p-2 text-slate-300">
              <span className="font-mono text-[9px] uppercase text-slate-500">output › </span>{selOut.verdict_line}
              {typeof selOut.score === "number" && <span className="ml-2 font-mono" style={{ color: selAgent.accent }}>{selOut.score}/10</span>}
            </p>
          )}
        </div>
      )}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[10px] text-slate-600">
        <span className="flex items-center gap-1.5">
          <svg width="20" height="6"><line x1="0" y1="3" x2="20" y2="3" stroke="#22d3ee" strokeOpacity="0.5" strokeWidth="1.4" /></svg>
          layer-to-layer flow
        </span>
        <span className="flex items-center gap-1.5">
          <svg width="20" height="6"><line x1="0" y1="3" x2="20" y2="3" stroke="#fbbf24" strokeOpacity="0.85" strokeWidth="1.6" strokeDasharray="4 3" /></svg>
          agent ↔ agent (experts building on each other{peerEdges.some((e) => e.live) ? " — live" : ""})
        </span>
        <span>Pulsing = communicating now.</span>
      </div>
    </div>
  );
}
