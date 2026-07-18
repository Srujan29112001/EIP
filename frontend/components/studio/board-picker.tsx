"use client";

/** The Board Picker v2 — your company org-chart, alive.
 * The same flow-tree language as the live pipeline: layer columns, icon
 * nodes, wires that re-route to only connect the agents YOU convene.
 * Click a node to bench/convene it; use "brief" to hand any agent a
 * personal instruction it will read verbatim.
 */

import { useMemo, useState } from "react";
import { AGENTS, LAYER_LABELS, STAGE_IO, agentById, capsFor, type Layer } from "@/lib/agents";

const MANDATORY = new Set(["intake_parser", "context_profiler", "scope_planner",
  "rag_memory", "weighing_engine", "verdict_composer", "scenario_planner", "negotiation_coach",
  "storytelling", "visualizer", "reporter", "outcome_tracker"]);

const PULSE_ONLY = new Set(["web_researcher", "news_intel", "market_data", "macro_data", "doc_analyst",
  "market_analyst", "finance_modeler", "red_team", "fact_checker", "bias_auditor",
  ...MANDATORY]);
const BOARD_EXTRA = new Set(["competitor_intel", "market_research", "banking", "gtm_distribution",
  "legal", "tax", "policy_compliance", "industry_expert", "devils_advocate", "connecting_dots",
  "pricing_strategist", "cohort_retention", "sentiment_analyst",
  "product_ux", "fundraising_capital", "sales_revops", "customer_success", "brand_creative"]);

const HUMAN_WAVE = ["human_behaviour", "human_needs", "consumer_analysis", "production_ops",
  "philosophy_ethics", "money_happiness", "philanthropy_impact"];

const SYNTH = ["rag_memory", "weighing_engine", "verdict_composer", "scenario_planner",
  "negotiation_coach", "storytelling", "visualizer", "reporter", "outcome_tracker"];
const TRADER_CORE = ["news_intel", "market_data", "macro_data", "technical_analyst",
  "stock_analyst", "backtest_engineer", "quant_signals", "risk_manager",
  "fund_analyst", "options_desk", "microstructure", "red_team", "fact_checker",
  "bias_auditor", ...SYNTH];
const TRADER_BOARD = [...TRADER_CORE, "macroeconomist", "geopolitics", "trends", "regulator",
  "industry_expert", "market_research", "sentiment_analyst", "human_behaviour", "money_happiness",
  "philosophy_ethics"];
const TRADER_WAR = [...TRADER_CORE, "macroeconomist", "geopolitics", "trends", "regulator",
  "industry_expert", "market_research", "sentiment_analyst", "banking", "intl_markets", "esg_impact",
  "policy_compliance", "optimization_predictor", "supply_chain", "data_analytics", ...HUMAN_WAVE];
const TRADER_MANDATORY = new Set(["market_data", "technical_analyst", ...SYNTH]);

const WEALTH_CORE = ["news_intel", "macro_data", "salary_budget", "portfolio_allocator",
  "fire_planner", "debt_banking", "real_estate", "location_scout", "red_team",
  "bias_auditor", ...SYNTH];
const WEALTH_BOARD = [...WEALTH_CORE, "macroeconomist", "trends", "regulator", "fund_analyst",
  "market_research", "banking", "insurance_risk", "money_happiness", "human_needs",
  "philosophy_ethics", "philanthropy_impact"];
const WEALTH_WAR = [...WEALTH_CORE, "macroeconomist", "trends", "regulator", "fund_analyst",
  "market_research", "banking", "insurance_risk", "sentiment_analyst", "geopolitics", "intl_markets",
  "esg_impact", "optimization_predictor", "subsidies_schemes", ...HUMAN_WAVE];
const WEALTH_MANDATORY = new Set(["salary_budget", ...SYNTH]);

/* ── the Orchestra (Intelligent Mode) — mirror of backend agents/score.py ──
 * 62 players across 11 movements; depth gates which analytical families join
 * (Pulse: Framing+Research+Analysis · Board: +Legal+Commercial+Human ·
 * War Room: +Technology = everything). QA + Delivery always run. */
const ORCH_ALL = new Set([
  // 02 framing · 03 research · 04 analysis (always convened)
  "intake_parser", "context_profiler", "scope_planner",
  "web_researcher", "news_intel", "market_data", "macro_data", "competitor_intel",
  "regulator", "trends", "intl_markets", "geopolitics",
  "market_analyst", "finance_modeler", "macroeconomist", "consumer_analysis", "weighing_engine",
  // 05 strategy
  "industry_expert", "business_model", "gtm_distribution", "marketing_strategy",
  "production_ops", "hr_talent", "banking", "supply_chain",
  // 06 legal & fiscal
  "legal", "tax", "policy_compliance", "subsidies_schemes", "optimization_predictor",
  "patent_ip", "insurance_risk",
  // 07 technology (war room)
  "ai_ml_strategist", "data_analytics", "software_architecture", "product_ux",
  "cybersecurity_privacy", "deep_tech",
  // 08 commercial & growth
  "fundraising_capital", "sales_revops", "pricing_strategist", "customer_success",
  "partnerships_bd", "brand_creative", "pr_communications", "community_ecosystem",
  // 09 human & meaning
  "human_behaviour", "human_needs", "philosophy_ethics", "money_happiness",
  "philanthropy_impact", "esg_impact", "founder_coaching",
  // 10 adversarial QA · 11 delivery (always convened)
  "red_team", "fact_checker", "bias_auditor", "devils_advocate",
  "connecting_dots", "storytelling", "visualizer", "reporter", "verdict_composer",
]);
const ORCH_BOARD_ONLY = new Set([
  "legal", "tax", "policy_compliance", "subsidies_schemes", "optimization_predictor",
  "patent_ip", "insurance_risk", "fundraising_capital", "sales_revops", "pricing_strategist",
  "customer_success", "partnerships_bd", "brand_creative", "pr_communications",
  "community_ecosystem", "human_behaviour", "human_needs", "philosophy_ethics",
  "money_happiness", "philanthropy_impact", "esg_impact", "founder_coaching",
]);
const ORCH_WAR_ONLY = new Set(["ai_ml_strategist", "data_analytics", "software_architecture",
  "product_ux", "cybersecurity_privacy", "deep_tech"]);
const ORCH_MANDATORY = ["intake_parser", "context_profiler", "scope_planner", "weighing_engine",
  "red_team", "fact_checker", "bias_auditor", "connecting_dots", "verdict_composer",
  "storytelling", "visualizer", "reporter"];

const LAYERS: Layer[] = ["L0", "L1", "L2", "L3", "L4"];

export function BoardPicker({ mode, depth, enabled, onChange, agentContext, onContext }: {
  mode: "founder" | "trader" | "wealth" | "intelligent";
  depth: "pulse" | "board" | "war_room";
  enabled: string[];
  onChange: (ids: string[]) => void;
  agentContext: Record<string, string>;
  onContext: (ctx: Record<string, string>) => void;
}) {
  const [briefFor, setBriefFor] = useState<string | null>(null);

  const { roster, mandatory } = useMemo(() => {
    if (mode === "trader") {
      const list = depth === "war_room" ? TRADER_WAR : depth === "board" ? TRADER_BOARD : TRADER_CORE;
      return { roster: AGENTS.filter((a) => list.includes(a.id)), mandatory: TRADER_MANDATORY };
    }
    if (mode === "wealth") {
      const list = depth === "war_room" ? WEALTH_WAR : depth === "board" ? WEALTH_BOARD : WEALTH_CORE;
      return { roster: AGENTS.filter((a) => list.includes(a.id)), mandatory: WEALTH_MANDATORY };
    }
    // Orchestra-only ids never appear in the founder/trader/wealth boards —
    // they belong exclusively to Intelligent Mode
    const ORCH_ONLY = new Set(["boss", "manager", "community_ecosystem"]);
    const inDepth = (id: string) => ORCH_ONLY.has(id) ? false
      : depth === "war_room" ? true
      : depth === "board" ? PULSE_ONLY.has(id) || BOARD_EXTRA.has(id) || HUMAN_WAVE.includes(id)
      : PULSE_ONLY.has(id);
    const base = AGENTS.filter((a) => inDepth(a.id));
    // Intelligent Mode = the Orchestra: the 62 players (each conducting its
    // junior instruments) + the 🎩 Boss / 🎼 Manager pair, always locked. You can
    // bench or brief any non-mandatory player; the Manager casts depth on top.
    if (mode === "intelligent") {
      const orchDepth = (id: string) =>
        depth === "war_room" ? ORCH_ALL.has(id)
        : depth === "board" ? ORCH_ALL.has(id) && !ORCH_WAR_ONLY.has(id)
        : ORCH_ALL.has(id) && !ORCH_WAR_ONLY.has(id) && !ORCH_BOARD_ONLY.has(id);
      const orch = AGENTS.filter((a) => a.id === "boss" || a.id === "manager");
      return {
        roster: [...orch, ...AGENTS.filter((a) => orchDepth(a.id))],
        mandatory: new Set(["boss", "manager", ...ORCH_MANDATORY]),
      };
    }
    return { roster: base, mandatory: MANDATORY };
  }, [mode, depth]);

  const isOn = (id: string) => enabled.length === 0 || enabled.includes(id) || mandatory.has(id);
  const toggle = (id: string) => {
    if (mandatory.has(id)) return;
    const current = enabled.length === 0 ? roster.map((a) => a.id) : [...enabled];
    const next = current.includes(id) ? current.filter((x) => x !== id) : [...current, id];
    onChange(next.length >= roster.length ? [] : next);
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

  // the golden A2A mesh — same neural wiring the live pipeline shows: within
  // each layer (L1+), every CONVENED agent talks to every other. Shown here so
  // you see the communication fabric you are convening, in every mode.
  const peerEdges: { from: string; to: string }[] = [];
  cols.forEach((col, ci) => {
    if (ci === 0) return;   // L0 gateway is a sequence
    const on = col.filter((a) => isOn(a.id));
    for (let a = 0; a < on.length; a++) {
      for (let b = a + 1; b < on.length; b++) peerEdges.push({ from: on[a].id, to: on[b].id });
    }
  });

  const onCount = roster.filter((a) => isOn(a.id)).length;
  const briefAgent = briefFor ? agentById(briefFor) : null;
  const briefedCount = Object.values(agentContext).filter((v) => v?.trim()).length;

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-slate-400">
        <span>{onCount}/{roster.length} convened{briefedCount ? ` · ${briefedCount} briefed` : ""}</span>
        <span className="text-slate-400">click a node → its capability card, brief box & bench/convene</span>
        {enabled.length > 0 && (
          <button onClick={() => onChange([])} className="ml-auto text-slate-400 hover:text-cyan">↺ everyone back on</button>
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

          {/* the golden agent↔agent mesh — bench someone and their arcs vanish */}
          {peerEdges.map(({ from, to }, i) => {
            const p1 = pos.get(from), p2 = pos.get(to);
            if (!p1 || !p2) return null;
            const dy = Math.abs(p2.y - p1.y);
            const bulge = Math.min(120, 24 + dy * 0.45);
            const side = i % 2 === 0 ? -1 : 1;
            const edgeX = side < 0 ? -13 : 13;
            const cx = p1.x + side * bulge;
            const cy = (p1.y + p2.y) / 2;
            return (
              <path key={`peer${i}`}
                d={`M${p1.x + edgeX},${p1.y} Q${cx},${cy} ${p2.x + edgeX},${p2.y}`}
                fill="none" stroke="#fbbf24" strokeOpacity="0.2" strokeWidth="0.8"
                strokeLinecap="round" className="transition-all duration-500" />
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
              <g key={a.id} onClick={() => setBriefFor(briefFor === a.id ? null : a.id)} className="cursor-pointer">
                <title>{locked ? `${a.name} — core, always runs (click for its card)` : `${a.name} — ${a.blurb}`}</title>
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

      {/* the selected agent: capability card + direct brief */}
      {briefAgent && (() => {
        const caps = capsFor(briefAgent.id);
        const io = STAGE_IO[briefAgent.id];
        const on = isOn(briefAgent.id);
        const locked = mandatory.has(briefAgent.id);
        return (
        <div className="mt-2 rounded-lg border p-3" style={{ borderColor: `${briefAgent.accent}55`, background: `${briefAgent.accent}0a` }}>
          <div className="mb-2 flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider">
            <span className="text-base">{briefAgent.icon}</span>
            <span className="text-sm normal-case font-sans font-semibold tracking-normal" style={{ color: briefAgent.accent }}>
              {briefAgent.name}
            </span>
            <span className="rounded bg-panel-2 px-1.5 py-0.5 text-[10px] text-slate-400">{briefAgent.layer} · {briefAgent.cluster}</span>
            {locked ? (
              <span className="rounded border border-line px-2 py-0.5 text-[10px] text-slate-400">core · always runs</span>
            ) : (
              <button onClick={() => toggle(briefAgent.id)}
                className={`rounded border px-2 py-0.5 text-[10px] transition ${
                  on ? "border-err/50 text-err hover:bg-err/10" : "border-ok/50 text-ok hover:bg-ok/10"}`}>
                {on ? "bench this agent" : "convene this agent"}
              </button>
            )}
            <button onClick={() => setBriefFor(null)} className="ml-auto text-slate-400 hover:text-white">✕</button>
          </div>

          <div className="mb-2 grid gap-2 text-[11px] leading-relaxed md:grid-cols-3">
            <div>
              <div className="mb-0.5 font-mono text-[10px] uppercase tracking-widest text-slate-400">what it does</div>
              <p className="text-slate-300">{briefAgent.blurb}.</p>
              {io && (
                <div className="mt-1 space-y-0.5 font-mono text-[10px]">
                  <div className="text-slate-400">⇥ in: <span className="text-slate-400">{io.in}</span></div>
                  <div className="text-slate-400">⇤ out: <span className="text-slate-400">{io.out}</span></div>
                </div>
              )}
            </div>
            <div>
              <div className="mb-0.5 font-mono text-[10px] uppercase tracking-widest text-slate-400">talks to</div>
              <ul className="space-y-0.5 text-slate-400">
                {caps.talks_to.slice(0, 4).map((t, i) => <li key={i}>↔ {t}</li>)}
              </ul>
            </div>
            <div>
              <div className="mb-0.5 font-mono text-[10px] uppercase tracking-widest text-slate-400">sub-agents</div>
              {caps.subagents.length ? (
                <ul className="space-y-0.5 text-slate-400">
                  {caps.subagents.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              ) : <p className="text-slate-400">works solo on the shared board</p>}
            </div>
          </div>

          {/* tools & data access — the additive tech layer for this specialist */}
          <div className="mb-2">
            <div className="mb-1 font-mono text-[10px] uppercase tracking-widest text-slate-400">tools & data access</div>
            <div className="flex flex-wrap gap-1">
              {caps.tools.map((t, i) => (
                <span key={i} className="rounded border border-line bg-panel px-1.5 py-0.5 font-mono text-[10px] text-slate-300">
                  {t}
                </span>
              ))}
            </div>
          </div>

          <div className="mb-1 font-mono text-[10px] uppercase tracking-widest" style={{ color: briefAgent.accent }}>
            brief it directly — it reads this verbatim before analysing
          </div>
          <textarea
            value={agentContext[briefAgent.id] ?? ""}
            onChange={(e) => onContext({ ...agentContext, [briefAgent.id]: e.target.value })}
            rows={2} maxLength={500}
            placeholder={`e.g. "focus on Karnataka regulations only" · "assume we already have FSSAI licence"`}
            className="w-full resize-none rounded-md border border-line bg-ink/70 p-2 text-xs outline-none focus:border-cyan/60" />
        </div>
        );
      })()}
    </div>
  );
}
