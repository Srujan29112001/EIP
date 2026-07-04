"use client";

/** The Board Picker v2 — your company org-chart, alive.
 * The same flow-tree language as the live pipeline: layer columns, icon
 * nodes, wires that re-route to only connect the agents YOU convene.
 * Click a node to bench/convene it; use "brief" to hand any agent a
 * personal instruction it will read verbatim.
 */

import { useMemo, useState } from "react";
import { AGENTS, LAYER_LABELS, agentById, type Layer } from "@/lib/agents";

const MANDATORY = new Set(["intake_parser", "context_profiler", "scope_planner",
  "weighing_engine", "verdict_composer", "visualizer", "reporter"]);

const PULSE_ONLY = new Set(["web_researcher", "news_intel", "market_data", "macro_data", "doc_analyst",
  "market_analyst", "finance_modeler", "red_team", "fact_checker", "bias_auditor",
  ...MANDATORY]);
const BOARD_EXTRA = new Set(["competitor_intel", "gtm_distribution", "legal", "tax",
  "policy_compliance", "industry_expert", "devils_advocate", "connecting_dots"]);

const TRADER_ROSTER = ["news_intel", "market_data", "macro_data", "technical_analyst",
  "stock_analyst", "backtest_engineer", "quant_signals", "risk_manager",
  "fund_analyst", "options_desk", "microstructure", "red_team", "fact_checker",
  "bias_auditor", "weighing_engine", "verdict_composer", "visualizer", "reporter"];
const TRADER_MANDATORY = new Set(["market_data", "technical_analyst", "weighing_engine",
  "verdict_composer", "visualizer", "reporter"]);

const WEALTH_ROSTER = ["news_intel", "macro_data", "salary_budget", "portfolio_allocator",
  "fire_planner", "debt_banking", "real_estate", "location_scout", "red_team",
  "bias_auditor", "weighing_engine", "verdict_composer", "visualizer", "reporter"];
const WEALTH_MANDATORY = new Set(["salary_budget", "weighing_engine", "verdict_composer",
  "visualizer", "reporter"]);

const LAYERS: Layer[] = ["L0", "L1", "L2", "L3", "L4"];

export function BoardPicker({ mode, depth, enabled, onChange, agentContext, onContext }: {
  mode: "founder" | "trader" | "wealth";
  depth: "pulse" | "board" | "war_room";
  enabled: string[];
  onChange: (ids: string[]) => void;
  agentContext: Record<string, string>;
  onContext: (ctx: Record<string, string>) => void;
}) {
  const [briefFor, setBriefFor] = useState<string | null>(null);

  const { roster, mandatory } = useMemo(() => {
    if (mode === "trader") {
      return { roster: AGENTS.filter((a) => TRADER_ROSTER.includes(a.id)), mandatory: TRADER_MANDATORY };
    }
    if (mode === "wealth") {
      return { roster: AGENTS.filter((a) => WEALTH_ROSTER.includes(a.id)), mandatory: WEALTH_MANDATORY };
    }
    const inDepth = (id: string) => depth === "war_room" ? true
      : depth === "board" ? PULSE_ONLY.has(id) || BOARD_EXTRA.has(id)
      : PULSE_ONLY.has(id);
    return { roster: AGENTS.filter((a) => inDepth(a.id)), mandatory: MANDATORY };
  }, [mode, depth]);

  const isOn = (id: string) => enabled.length === 0 || enabled.includes(id) || mandatory.has(id);
  const toggle = (id: string) => {
    if (mandatory.has(id)) { setBriefFor(briefFor === id ? null : id); return; }
    const current = enabled.length === 0 ? roster.map((a) => a.id) : [...enabled];
    const next = current.includes(id) ? current.filter((x) => x !== id) : [...current, id];
    onChange(next.length >= roster.length ? [] : next);
    setBriefFor(id);
  };

  // ── flow layout (same geometry as the live pipeline tree) ────────────────
  const cols = LAYERS.map((l) => roster.filter((a) => a.layer === l));
  const W = 940, ROW = 52, PAD_T = 46;
  const H = PAD_T + Math.max(...cols.map((c) => c.length), 1) * ROW + 26;
  const colX = (i: number) => 90 + i * ((W - 180) / (LAYERS.length - 1));
  const pos = new Map<string, { x: number; y: number }>();
  cols.forEach((agents, ci) => {
    const offset = ((agents.length - 1) * ROW) / 2;
    agents.forEach((a, ri) => pos.set(a.id, { x: colX(ci), y: PAD_T + (H - PAD_T) / 2 - offset + ri * ROW - 26 }));
  });

  // wires only between CONVENED agents — bench someone and the board rewires
  const edges: { from: string; to: string; live: boolean }[] = [];
  for (let i = 0; i < LAYERS.length - 1; i++) {
    const fromOn = cols[i].filter((a) => isOn(a.id));
    for (let j = i + 1; j < LAYERS.length; j++) {
      const toOn = cols[j].filter((a) => isOn(a.id));
      if (!toOn.length) continue;
      for (const f of fromOn) for (const t of toOn) edges.push({ from: f.id, to: t.id, live: true });
      break; // connect to the next non-empty convened layer only
    }
  }

  const onCount = roster.filter((a) => isOn(a.id)).length;
  const briefAgent = briefFor ? agentById(briefFor) : null;
  const briefedCount = Object.values(agentContext).filter((v) => v?.trim()).length;

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-slate-500">
        <span>{onCount}/{roster.length} convened{briefedCount ? ` · ${briefedCount} briefed` : ""}</span>
        <span className="text-slate-600">click a node to bench/convene · click again to brief it</span>
        {enabled.length > 0 && (
          <button onClick={() => onChange([])} className="ml-auto text-slate-500 hover:text-cyan">↺ everyone back on</button>
        )}
      </div>

      <div className="overflow-x-auto rounded-xl border border-line bg-ink/50 p-2">
        <svg viewBox={`0 0 ${W} ${H}`} className="min-w-[760px] w-full">
          {LAYERS.map((l, i) => cols[i].length > 0 && (
            <text key={l} x={colX(i)} y={20} textAnchor="middle" className="fill-slate-500"
              style={{ font: "700 10px var(--font-jetbrains)", letterSpacing: "0.14em" }}>
              {l} · {LAYER_LABELS[l].toUpperCase()}
            </text>
          ))}

          {/* wires — living connections between convened agents */}
          {edges.map(({ from, to }, i) => {
            const p1 = pos.get(from), p2 = pos.get(to);
            if (!p1 || !p2) return null;
            const mx = (p1.x + p2.x) / 2;
            return (
              <path key={i}
                d={`M${p1.x + 15},${p1.y} C${mx},${p1.y} ${mx},${p2.y} ${p2.x - 15},${p2.y}`}
                fill="none" stroke="rgba(34,211,238,0.22)" strokeWidth="1"
                className="transition-all duration-500" />
            );
          })}

          {/* nodes — icon chips */}
          {roster.map((a) => {
            const p = pos.get(a.id);
            if (!p) return null;
            const on = isOn(a.id);
            const locked = mandatory.has(a.id);
            const briefed = Boolean(agentContext[a.id]?.trim());
            return (
              <g key={a.id} onClick={() => toggle(a.id)} className="cursor-pointer">
                <title>{locked ? `${a.name} — core, always runs (click to brief)` : `${a.name} — ${a.blurb}`}</title>
                {on && (
                  <circle cx={p.x} cy={p.y} r={16} fill={a.accent} opacity="0.14"
                    className="transition-all duration-300" />
                )}
                <circle cx={p.x} cy={p.y} r={13} fill={on ? "#0d1428" : "#0a0f1a"}
                  stroke={on ? a.accent : "#334155"} strokeWidth={on ? 1.8 : 1}
                  strokeDasharray={on ? undefined : "3 2"}
                  className="transition-all duration-300"
                  style={on ? { filter: `drop-shadow(0 0 6px ${a.accent}66)` } : undefined} />
                <text x={p.x} y={p.y + 4.5} textAnchor="middle" style={{ font: "12px sans-serif", opacity: on ? 1 : 0.35 }}>
                  {a.icon}
                </text>
                {briefed && <circle cx={p.x + 11} cy={p.y - 10} r="3.5" fill="#9ae64a" stroke="#04060f" strokeWidth="1" />}
                {locked && (
                  <text x={p.x} y={p.y - 17} textAnchor="middle" className="fill-slate-600" style={{ font: "7px var(--font-jetbrains)" }}>CORE</text>
                )}
                <text x={p.x} y={p.y + 27} textAnchor="middle"
                  style={{ font: "8.5px var(--font-jetbrains)", fill: on ? "#cbd5e1" : "#475569",
                           textDecoration: on ? "none" : "line-through" }}>
                  {a.name.length > 17 ? a.name.slice(0, 16) + "…" : a.name}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* per-agent brief */}
      {briefAgent && isOn(briefAgent.id) && (
        <div className="mt-2 rounded-lg border p-3" style={{ borderColor: `${briefAgent.accent}55`, background: `${briefAgent.accent}0a` }}>
          <div className="mb-1.5 flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider">
            <span className="text-sm">{briefAgent.icon}</span>
            <span style={{ color: briefAgent.accent }}>brief {briefAgent.name} directly</span>
            <span className="text-slate-600">it reads this verbatim before analysing</span>
            <button onClick={() => setBriefFor(null)} className="ml-auto text-slate-500 hover:text-white">✕</button>
          </div>
          <textarea
            value={agentContext[briefAgent.id] ?? ""}
            onChange={(e) => onContext({ ...agentContext, [briefAgent.id]: e.target.value })}
            rows={2} maxLength={500}
            placeholder={`e.g. "focus on Karnataka regulations only" · "assume we already have FSSAI licence"`}
            className="w-full resize-none rounded-md border border-line bg-ink/70 p-2 text-xs outline-none focus:border-cyan/60" />
        </div>
      )}
    </div>
  );
}
