"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, ArrowRight, Download, FileJson, FileText, GraduationCap, Lightbulb, Mic, Network, Repeat, Scale } from "lucide-react";
import { NeuralMap } from "@/components/graph/neural-map";
import { agentById } from "@/lib/agents";
import { buildMarkdown, download, printPdf } from "@/lib/export";
import { buildGraph } from "@/lib/graph-data";
import { useRun } from "@/lib/store";
import { AskBoard } from "./ask-board";
import { AboveBeyondPanel, ManagerPlanPanel, QaGatePanel, RulingsPanel } from "./intelligent-panels";
import { OrchestraView } from "./orchestra-view";
import { ChartGallery, ReportSection, SmartInsights } from "./insights";
import { AgentTable, DegradedNotice, DomainScreens, InsightBullets, KeyFindings, KpiTiles, QualityBanner } from "./results-v4";
import { Disagreements } from "./disagreements";
import { Radar } from "./radar";
import { MarketSim, RunwaySim, ScoreSim } from "./sim-charts";
import { TradeDesk } from "./trade-desk";

const BAND_STYLE: Record<string, { label: string; cls: string }> = {
  GO: { label: "GO", cls: "text-ok border-ok/40 bg-ok/10" },
  CONDITIONAL_GO: { label: "PROCEED WITH CAUTION", cls: "text-warn border-warn/40 bg-warn/10" },
  NO_GO: { label: "NO-GO (as framed)", cls: "text-err border-err/40 bg-err/10" },
};

export function DecisionRoom() {
  const { verdict, radar, tokens, routes, board, brief, agentOutputs, collabs, story, crossInsights, compliance, rounds, resultSets, managerPlan, qa, hitl, noLlm, taskGraph } = useRun();
  const twoRounds = Boolean(resultSets[1] && resultSets[2]);
  const intelligent = Boolean(managerPlan || qa.length || hitl || taskGraph);
  const noLlmCount = Object.keys(noLlm).length;

  const exportMd = () =>
    download("eip-decision.md", buildMarkdown({ brief, verdict, board, agentOutputs, tokens, routes }));
  const exportJson = () =>
    download("eip-decision.json",
      JSON.stringify({ brief, verdict, board, agentOutputs }, null, 2), "application/json");
  const exportPdf = () => printPdf({ brief, verdict, board, agentOutputs, tokens, routes });

  if (!verdict) {
    return (
      <div className="glass flex items-center gap-3 rounded-2xl p-6 text-sm text-slate-500">
        <span className="typing-dots"><span /><span /><span /></span>
        The Decision Room fills in as the synthesis layer completes…
      </div>
    );
  }
  const band = BAND_STYLE[verdict.recommendation] ?? BAND_STYLE.CONDITIONAL_GO;
  const sourced = board.filter((b) => b.kind === "claim" && b.source?.url).length;

  const navItems = [
    { id: "dr-verdict", label: "⚖ Verdict" },
    ...(story && (story.narrative || story.one_liner) ? [{ id: "dr-pitch", label: "🎙 Pitch" }] : []),
    { id: "dr-radar", label: "📡 Radar" },
    { id: "dr-risks", label: "⚠ Risks" },
    ...(rounds && (rounds.deltas?.length ?? 0) > 0 ? [{ id: "dr-rounds", label: "🔁 Deliberation" }] : []),
    { id: "dr-charts", label: "📊 Charts" },
    { id: "dr-agents", label: "🧠 Agents" },
    { id: "dr-graph", label: "🌐 3D Graph" },
    { id: "dr-ask", label: "💬 Ask the Board" },
  ];

  return (
    <div className="space-y-4 pb-4">
      <QualityBanner />
      <DegradedNotice />
      {/* screen connections — sticky spy-nav over the whole decision room */}
      <SectionNav items={navItems} />

      {/* ═══ Intelligent Mode — the Advisory Engine's audit trail ═══ */}
      {intelligent && (
        <div className="space-y-3 rounded-xl border border-brand/30 bg-brand/[0.03] p-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-display text-sm font-bold text-slate-100">🎩 Advisory Engine · run audit</span>
            {hitl && (
              <span className={`rounded border px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-wider ${
                hitl.decision === "approve" || hitl.decision === "auto_approved"
                  ? "border-ok/40 bg-ok/10 text-ok"
                  : hitl.decision === "reject" ? "border-err/40 bg-err/10 text-err"
                  : "border-warn/40 bg-warn/10 text-warn"}`}>
                review: {hitl.decision || "pending"}
              </span>
            )}
            {noLlmCount > 0 && (
              <span className="rounded border border-warn/40 bg-warn/10 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-wider text-warn">
                {noLlmCount} agent{noLlmCount > 1 ? "s" : ""} deterministic-only (no LLM reached)
              </span>
            )}
          </div>
          <ManagerPlanPanel />
          <QaGatePanel />
        </div>
      )}

      {/* 🌟 the Advisory Engine's signature deliverable sections */}
      <AboveBeyondPanel />
      <RulingsPanel />

      {/* the two-tier orchestra — players & the instruments each one played */}
      {taskGraph && (
        <details className="rounded-xl border border-brand/30 bg-brand/[0.02] p-1">
          <summary className="cursor-pointer px-3 py-2 font-mono text-[11px] uppercase tracking-wider text-brand">
            🎼 the orchestra that played — {taskGraph.n_players} players · {taskGraph.n_instruments} instruments
          </summary>
          <div className="p-2"><OrchestraView /></div>
        </details>
      )}

      {/* ═══ THE TWO RESULT SETS — round 1 in full, then round 2 under it ═══ */}
      {twoRounds && (
        <>
          <div className="flex items-center gap-3">
            <span className="rounded-lg border border-ok/40 bg-ok/10 px-3 py-1.5 font-mono text-[11px] font-bold uppercase tracking-widest text-ok">
              Round 1 — independent analysis
            </span>
            <span className="h-px flex-1 bg-line" />
          </div>
          <RoundOneResults data={resultSets[1]} />
          <div className="mt-2 flex items-center gap-3">
            <span className="rounded-lg border border-[#fbbf24]/50 bg-[#fbbf24]/10 px-3 py-1.5 font-mono text-[11px] font-bold uppercase tracking-widest text-[#fbbf24]">
              Round 2 — after full-board deliberation (final)
            </span>
            <span className="h-px flex-1 bg-line" />
          </div>
          <ComparativePanel r1={resultSets[1]} r2={resultSets[2]} />
        </>
      )}

      {/* the bottom line — conclusions & recommendations, composed deterministically */}
      <BottomLine verdict={verdict} outputs={agentOutputs} />

      {/* predictions under uncertainty + the negotiation playbook */}
      <div className="grid gap-4 lg:grid-cols-2">
        <ScenarioPanel out={agentOutputs["scenario_planner"]} />
        <NegotiationPanel out={agentOutputs["negotiation_coach"]} />
      </div>

      {/* compliance alerts — the regulatory red-flags, elevated so nothing is missed */}
      {compliance && compliance.alerts.length > 0 && (
        <section className={`rounded-xl border p-4 ${compliance.high > 0 ? "border-err/40 bg-err/10" : "border-warn/40 bg-warn/10"}`}>
          <h3 className={`mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest ${compliance.high > 0 ? "text-err" : "text-warn"}`}>
            <AlertTriangle size={13} /> Compliance sentinel — {compliance.alerts.length} flag{compliance.alerts.length > 1 ? "s" : ""}
            {compliance.high > 0 && <span className="rounded bg-err/20 px-1.5 py-0.5 text-[9px]">{compliance.high} HIGH</span>}
          </h3>
          <ul className="space-y-1.5">
            {compliance.alerts.map((a, i) => (
              <li key={i} className="flex items-start gap-2 text-xs">
                <span className={`mt-0.5 rounded px-1.5 py-0.5 font-mono text-[8px] uppercase ${
                  a.severity === "high" ? "bg-err/25 text-err" : a.severity === "medium" ? "bg-warn/25 text-warn" : "bg-panel-2 text-slate-400"}`}>
                  {a.severity}
                </span>
                <span className="text-slate-200">
                  {a.text}
                  <span className="ml-1.5 font-mono text-[9px] text-slate-500">— {agentById(a.agent).name}</span>
                </span>
              </li>
            ))}
          </ul>
          <p className="mt-2 font-mono text-[9px] text-slate-500">
            Deterministic scan — education, not legal advice. Verify each against the current official source.
          </p>
        </section>
      )}

      <KpiTiles />
      {/* verdict card */}
      <section id="dr-verdict" className={`card-in scroll-mt-24 rounded-2xl border p-5 ${band.cls}`}>
        <div className="flex flex-wrap items-center gap-5">
          <AnimatedGauge value={verdict.score} />
          <div className="min-w-0 flex-1">
            <div className="font-mono text-[11px] uppercase tracking-widest opacity-70">Weighted verdict</div>
            <div className="mt-1 font-hero text-3xl font-bold md:text-4xl">{band.label}</div>
          </div>
        </div>
        <p className="mt-3 text-sm leading-relaxed text-slate-200">{verdict.reasoning}</p>
        <div className="mt-3 flex flex-wrap items-center gap-3 font-mono text-[10px] text-slate-400">
          <span>
            {sourced} externally sourced claims · {tokens.toLocaleString()} tokens ·{" "}
            {[...routes].join(", ") || "deterministic cores only"}
          </span>
          <span className="ml-auto flex gap-2">
            <button onClick={exportMd}
              className="flex items-center gap-1 rounded border border-line px-2 py-1 text-slate-300 transition hover:border-cyan/60 hover:text-cyan">
              <Download size={11} /> Markdown
            </button>
            <button onClick={exportJson}
              className="flex items-center gap-1 rounded border border-line px-2 py-1 text-slate-300 transition hover:border-cyan/60 hover:text-cyan">
              <FileJson size={11} /> JSON
            </button>
            <button onClick={exportPdf}
              className="flex items-center gap-1 rounded border border-line px-2 py-1 text-slate-300 transition hover:border-cyan/60 hover:text-cyan">
              <FileText size={11} /> PDF
            </button>
          </span>
        </div>
      </section>

      {/* the Storyteller's pitch — the honest narrative for this decision */}
      {story && (story.narrative || story.one_liner) && (
        <section id="dr-pitch" className="card-in scroll-mt-24 rounded-2xl border border-line bg-gradient-to-br from-panel/90 to-[#1a1330] p-5 backdrop-blur-sm">
          <h3 className="mb-3 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
            <Mic size={13} className="text-[#fca5a5]" /> The pitch — as the Storyteller would tell it
          </h3>
          {story.one_liner && (
            <p className="font-display text-lg font-semibold leading-snug text-slate-100">“{story.one_liner}”</p>
          )}
          {story.hook && story.hook !== story.one_liner && (
            <p className="mt-1 text-sm italic text-[#fca5a5]">{story.hook}</p>
          )}
          {story.narrative && (
            <p className="mt-3 text-sm leading-relaxed text-slate-300">{story.narrative}</p>
          )}
          {Array.isArray(story.three_beats) && story.three_beats.length > 0 && (
            <div className="mt-4 grid gap-2 sm:grid-cols-3">
              {story.three_beats.slice(0, 3).map((b, i) => (
                <div key={i} className="rounded-lg border border-line bg-panel-2 p-3">
                  <div className="mb-1 font-mono text-[9px] uppercase tracking-widest text-[#fca5a5]">
                    {["Problem", "Insight", "Why now"][i] ?? `Beat ${i + 1}`}
                  </div>
                  <p className="text-xs leading-relaxed text-slate-300">{b}</p>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* radar + sensitivities */}
      <div id="dr-radar" className="scroll-mt-24 grid gap-4 md:grid-cols-2">
        <section className="glass card-in rounded-2xl p-4">
          <h3 className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
            <Scale size={13} /> Dimension radar
          </h3>
          <Radar dims={radar?.dimensions ?? verdict.dimensions} />
        </section>
        <section className="glass card-in rounded-2xl p-4">
          <h3 className="mb-2 font-mono text-[11px] uppercase tracking-widest text-muted">
            What would change this verdict
          </h3>
          <ul className="space-y-2 text-sm">
            {(verdict.sensitivities ?? []).map((s, i) => (
              <li key={i} className="flex gap-2 text-slate-300">
                <span className="font-mono text-cyan">{i + 1}.</span> {s}
              </li>
            ))}
          </ul>
          {verdict.teach && (
            <p className="mt-4 flex gap-2 rounded-lg bg-panel-2 p-3 text-xs leading-relaxed text-slate-400">
              <GraduationCap size={14} className="mt-0.5 shrink-0 text-brand" /> {verdict.teach}
            </p>
          )}
        </section>
      </div>

      {/* risks & opportunities */}
      <div id="dr-risks" className="scroll-mt-24 grid gap-4 md:grid-cols-2">
        <section className="glass card-in rounded-2xl p-4">
          <h3 className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-err">
            <AlertTriangle size={13} /> Risk register
          </h3>
          <ul className="space-y-2">
            {(verdict.risks ?? []).map((r, i) => (
              <li key={i} className="rounded-lg border border-line bg-panel-2 p-2.5 text-xs">
                <span className="mr-2 rounded px-1.5 py-0.5 font-mono text-[9px]"
                  style={{ color: agentById(r.source_agent).accent, border: `1px solid ${agentById(r.source_agent).accent}44` }}>
                  {agentById(r.source_agent).name}
                </span>
                <span className="text-slate-300">{r.text}</span>
              </li>
            ))}
          </ul>
        </section>
        <section className="glass card-in rounded-2xl p-4">
          <h3 className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-ok">
            <Lightbulb size={13} /> Opportunities & next steps
          </h3>
          <ul className="space-y-2">
            {(verdict.opportunities ?? []).map((o, i) => (
              <li key={`o${i}`} className="rounded-lg border border-line bg-panel-2 p-2.5 text-xs text-slate-300">
                {o.text}
              </li>
            ))}
            {(verdict.next_steps ?? []).map((s, i) => (
              <li key={`s${i}`} className="flex gap-2 p-1 text-xs text-slate-300">
                <ArrowRight size={12} className="mt-0.5 shrink-0 text-cyan" /> {s}
              </li>
            ))}
          </ul>
        </section>
      </div>

      {/* two-round deliberation — round 1 independent, round 2 all-to-all re-read */}
      {rounds && (rounds.deltas?.length ?? 0) > 0 && (() => {
        const movers = [...rounds.deltas]
          .filter((d) => Math.abs(d.delta) >= 0.1)
          .sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta))
          .slice(0, 12);
        return (
          <section id="dr-rounds" className="glass card-in scroll-mt-24 rounded-2xl p-4">
            <h3 className="mb-1 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
              <Repeat size={13} className="text-[#fbbf24]" /> Two-round deliberation — how the board changed its mind
            </h3>
            <p className="mb-2 text-[11px] text-slate-500">
              Round 1: every layer ran independently. Round 2: L1 → L2 → L3 re-ran with the <b>full board</b> visible —
              {" "}{rounds.refined} refined their analysis, {rounds.revised} revised their score.
            </p>
            {rounds.verdict1 && rounds.verdict2 && (
              <div className="mb-3 flex flex-wrap items-center gap-2 rounded-lg border border-line bg-panel-2 px-3 py-2 text-xs">
                <span className="font-mono text-[9px] uppercase tracking-widest text-slate-500">the two verdicts</span>
                <span className="text-slate-300">
                  Round 1: <b>{rounds.verdict1.score}/10</b> {String(rounds.verdict1.recommendation ?? "").replaceAll("_", " ")}
                </span>
                <ArrowRight size={11} className="text-[#fbbf24]" />
                <span className="text-slate-100">
                  After deliberation: <b>{rounds.verdict2.score}/10</b> {String(rounds.verdict2.recommendation ?? "").replaceAll("_", " ")}
                </span>
                {typeof rounds.verdict1.score === "number" && typeof rounds.verdict2.score === "number" && (
                  <span className={`rounded px-1.5 py-0.5 font-mono text-[9px] ${
                    rounds.verdict2.score >= rounds.verdict1.score ? "bg-ok/15 text-ok" : "bg-err/15 text-err"}`}>
                    {rounds.verdict2.score > rounds.verdict1.score ? "+" : ""}{(rounds.verdict2.score - rounds.verdict1.score).toFixed(1)}
                  </span>
                )}
              </div>
            )}
            {movers.length > 0 ? (
              <div className="grid gap-1.5 sm:grid-cols-2">
                {movers.map((d) => {
                  const a = agentById(d.agent);
                  return (
                    <div key={d.agent} className="flex items-center gap-2 rounded-lg border border-line bg-panel-2 px-2.5 py-1.5 text-xs">
                      <span className="truncate" style={{ color: a.accent }}>{a.icon} {a.name}</span>
                      <span className="ml-auto font-mono text-[10px] text-slate-500">{d.before}</span>
                      <ArrowRight size={10} className="shrink-0 text-slate-600" />
                      <span className="font-mono text-[11px] text-slate-200">{d.after}</span>
                      <span className={`rounded px-1 py-0.5 font-mono text-[9px] ${
                        d.delta > 0 ? "bg-ok/15 text-ok" : "bg-err/15 text-err"}`}>
                        {d.delta > 0 ? "+" : ""}{d.delta}
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="rounded-lg border border-ok/30 bg-ok/5 p-2.5 text-xs text-slate-300">
                All {rounds.deltas.length} specialists held their scores after reading the full board — strong convergence:
                the round-1 reads survived full-board scrutiny.
              </p>
            )}
            <p className="mt-2 font-mono text-[9px] text-slate-500">
              Unmoved scores = the specialist read everyone and stood firm (convergence). Movement = new context genuinely mattered.
            </p>
          </section>
        );
      })()}

      {/* cross-pollination — how the specialists' findings connect (A2A synthesis) */}
      {crossInsights && ((crossInsights.connections?.length ?? 0) > 0 || (crossInsights.emergent?.length ?? 0) > 0) && (
        <section className="glass card-in rounded-2xl p-4">
          <h3 className="mb-1 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
            <Network size={13} className="text-[#fbbf24]" /> Cross-pollination — how the specialists connect
          </h3>
          <p className="mb-3 text-[11px] text-slate-500">
            Every specialist read against every other — where their findings reinforce (synergy) or collide (tension).
          </p>
          {(crossInsights.connections?.length ?? 0) > 0 && (
            <div className="grid gap-2 sm:grid-cols-2">
              {crossInsights.connections!.map((c, i) => {
                const syn = c.type === "synergy";
                return (
                  <div key={i} className={`rounded-lg border p-2.5 text-xs ${syn ? "border-ok/30 bg-ok/5" : "border-warn/30 bg-warn/5"}`}>
                    <div className="mb-1 flex flex-wrap items-center gap-1 font-mono text-[10px]">
                      <span style={{ color: agentById(c.a).accent }}>{agentById(c.a).icon} {agentById(c.a).name}</span>
                      <span className={syn ? "text-ok" : "text-warn"}>{syn ? "⇄" : "⚡"}</span>
                      <span style={{ color: agentById(c.b).accent }}>{agentById(c.b).icon} {agentById(c.b).name}</span>
                      <span className={`ml-auto rounded px-1.5 py-0.5 text-[8px] uppercase ${syn ? "bg-ok/15 text-ok" : "bg-warn/15 text-warn"}`}>{c.type}</span>
                    </div>
                    <p className="leading-relaxed text-slate-300">{c.insight}</p>
                  </div>
                );
              })}
            </div>
          )}
          {(crossInsights.emergent?.length ?? 0) > 0 && (
            <div className="mt-3">
              <div className="mb-1.5 font-mono text-[9px] uppercase tracking-widest text-[#fbbf24]">Emergent — only visible across the whole board</div>
              <ul className="space-y-1.5">
                {crossInsights.emergent!.map((e, i) => (
                  <li key={i} className="flex gap-2 text-xs text-slate-300">
                    <Lightbulb size={12} className="mt-0.5 shrink-0 text-[#fbbf24]" /> {e}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {/* results v4 — the density layer */}
      <KeyFindings />
      <InsightBullets />
      <DomainScreens />

      <Disagreements />
      <TradeDesk />

      {/* the Visualizer's gallery + every specialist's finding */}
      <div id="dr-charts" className="scroll-mt-24 space-y-4">
        <ChartGallery />
        <SmartInsights />
      </div>
      <div id="dr-agents" className="scroll-mt-24">
        <AgentTable />
      </div>

      {/* the simulation layer — bend every insight and watch the math move */}
      <RunwaySim />
      <MarketSim />
      <ScoreSim />

      {/* the Reporter's full document */}
      <ReportSection />

      {/* the decision graph — this run as a living neural map */}
      <section id="dr-graph" className="glass card-in scroll-mt-24 rounded-2xl p-4">
        <h3 className="mb-3 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
          <Network size={13} /> The Decision Graph — everything the board produced
        </h3>
        <NeuralMap {...buildGraph({ brief, board, agentOutputs, verdict, collabs })} height={460} />
      </section>

      <div id="dr-ask" className="scroll-mt-24">
        <AskBoard />
      </div>

      <p className="pb-2 text-center font-mono text-[10px] text-slate-600">
        EIP provides analytics and education, not investment advice. Decisions and outcomes are yours.
      </p>
    </div>
  );
}

/* ── the verdict dial — the conic fill sweeps in on mount ─────────────────── */
function AnimatedGauge({ value }: { value: unknown }) {
  const [pct, setPct] = useState(0);
  useEffect(() => {
    const target = Math.max(0, Math.min(100, Number(value) * 10 || 0));
    const id = requestAnimationFrame(() => requestAnimationFrame(() => setPct(target)));
    return () => cancelAnimationFrame(id);
  }, [value]);
  return (
    <div className="gauge-ring grid h-24 w-24 shrink-0 place-items-center rounded-full"
      style={{ "--pct": pct } as React.CSSProperties}>
      <div className="text-center">
        <div className="font-hero text-3xl font-bold leading-none text-slate-100">{String(value)}</div>
        <div className="mt-0.5 font-mono text-[9px] uppercase tracking-wider opacity-60">/ 10</div>
      </div>
    </div>
  );
}

/* ── screen connections — sticky scroll-spy across the decision room ──────── */
function SectionNav({ items }: { items: { id: string; label: string }[] }) {
  const [active, setActive] = useState(items[0]?.id ?? "");
  const key = items.map((i) => i.id).join(",");
  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) => {
        for (const e of entries) if (e.isIntersecting) { setActive(e.target.id); return; }
      },
      { rootMargin: "-15% 0px -75% 0px" },
    );
    for (const it of items) {
      const el = document.getElementById(it.id);
      if (el) obs.observe(el);
    }
    return () => obs.disconnect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);
  return (
    <nav className="glass scroll-thin sticky top-2 z-30 flex gap-1 overflow-x-auto rounded-2xl p-1.5">
      {items.map((it) => (
        <button key={it.id}
          onClick={() => document.getElementById(it.id)?.scrollIntoView({ behavior: "smooth", block: "start" })}
          className={`shrink-0 rounded-lg px-3 py-1.5 font-mono text-[10px] uppercase tracking-wider transition ${
            active === it.id
              ? "bg-panel-2 text-cyan shadow-[0_0_16px_-6px_rgba(34,211,238,0.6)]"
              : "text-slate-500 hover:text-slate-300"}`}>
          {it.label}
        </button>
      ))}
    </nav>
  );
}

/* ── the ROUND-1 result set, published in full above the final results ────── */
import type { AgentOutput as AO, ResultSetData, Verdict as V } from "@/lib/types";
import type { ChartSpec } from "./chart-kit";

/* ── comparative analysis — round 1 vs round 2, dimension by dimension ────── */
function ComparativePanel({ r1, r2 }: { r1: ResultSetData; r2: ResultSetData }) {
  const d1 = r1.dimensions ?? {}, d2 = r2.dimensions ?? {};
  const keys = Object.keys(d2).filter((k) => k in d1);
  if (!keys.length) return null;
  const v1s = Number(r1.verdict?.score ?? 0), v2s = Number(r2.verdict?.score ?? 0);
  return (
    <section className="glass card-in rounded-2xl p-4">
      <h3 className="mb-1 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        <Scale size={13} className="text-[#fbbf24]" /> Comparative analysis — what deliberation changed
      </h3>
      <p className="mb-3 text-[11px] text-slate-500">
        Verdict {v1s}/10 → <b className="text-slate-300">{v2s}/10</b>
        {r1.story?.one_liner && r2.story?.one_liner && r1.story.one_liner !== r2.story.one_liner
          ? " · the pitch itself was rewritten after the board read itself." : ""}
      </p>
      <div className="space-y-1.5">
        {keys.map((k) => {
          const a = Number(d1[k] ?? 0), b = Number(d2[k] ?? 0), delta = +(b - a).toFixed(1);
          return (
            <div key={k} className="flex items-center gap-2 text-xs">
              <span className="w-24 shrink-0 font-mono text-[10px] text-slate-400">{k}</span>
              <div className="relative h-2.5 flex-1 overflow-hidden rounded bg-panel-2">
                <div className="absolute inset-y-0 left-0 rounded bg-slate-600/60" style={{ width: `${a * 10}%` }} />
                <div className="absolute inset-y-0 left-0 rounded bg-[#fbbf24]/80 transition-all duration-700"
                  style={{ width: `${b * 10}%`, mixBlendMode: "screen" }} />
              </div>
              <span className="w-16 shrink-0 text-right font-mono text-[10px] text-slate-400">{a} → <b className="text-slate-200">{b}</b></span>
              <span className={`w-10 shrink-0 rounded px-1 text-center font-mono text-[9px] ${
                delta > 0 ? "bg-ok/15 text-ok" : delta < 0 ? "bg-err/15 text-err" : "bg-panel-2 text-slate-500"}`}>
                {delta > 0 ? "+" : ""}{delta}
              </span>
            </div>
          );
        })}
      </div>
      <p className="mt-2 font-mono text-[9px] text-slate-500">
        grey = round-1 score · gold = after deliberation. The gap IS the value of the second round.
      </p>
    </section>
  );
}

/* ── the bottom line — conclusions & recommendations in one place ──────────── */
function BottomLine({ verdict, outputs }: { verdict: V | null; outputs: Record<string, AO> }) {
  if (!verdict) return null;
  const sc = outputs["scenario_planner"] ?? {};
  const nc = outputs["negotiation_coach"] ?? {};
  const topRisk = (verdict.risks ?? [])[0];
  const steps = (verdict.next_steps ?? []).slice(0, 3);
  return (
    <section className="rounded-xl border border-cyan/30 bg-gradient-to-br from-panel to-[#0c1a2e] p-4">
      <h3 className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-cyan">
        <Lightbulb size={13} /> The bottom line — conclusions, predictions, recommendations
      </h3>
      <div className="grid gap-2 text-xs sm:grid-cols-2">
        <div className="rounded-lg border border-line bg-panel-2 p-2.5">
          <div className="mb-1 font-mono text-[9px] uppercase tracking-widest text-slate-500">Conclusion</div>
          <p className="text-slate-200"><b>{verdict.score}/10 · {String(verdict.recommendation ?? "").replaceAll("_", " ")}</b>
            {typeof sc.p10 === "number" && <span className="text-slate-400"> — and under 1,000 simulated futures it stays between <b>{String(sc.p10)}</b> and <b>{String(sc.p90)}</b> (P50 {String(sc.p50)}).</span>}
          </p>
        </div>
        <div className="rounded-lg border border-line bg-panel-2 p-2.5">
          <div className="mb-1 font-mono text-[9px] uppercase tracking-widest text-slate-500">Prediction</div>
          <p className="text-slate-200">
            {typeof sc.prob_go === "number"
              ? <>P(GO) <b className="text-ok">{Math.round(Number(sc.prob_go) * 100)}%</b> · P(NO-GO) <b className="text-err">{Math.round(Number(sc.prob_nogo ?? 0) * 100)}%</b>{sc.breaks_it ? <> — the case most often breaks on <b>{String(sc.breaks_it)}</b>.</> : "."}</>
              : "Run at Board depth for the Monte-Carlo prediction band."}
          </p>
        </div>
        {topRisk && (
          <div className="rounded-lg border border-err/25 bg-err/5 p-2.5">
            <div className="mb-1 font-mono text-[9px] uppercase tracking-widest text-err">Guard against</div>
            <p className="text-slate-300">{topRisk.text}</p>
          </div>
        )}
        <div className="rounded-lg border border-ok/25 bg-ok/5 p-2.5">
          <div className="mb-1 font-mono text-[9px] uppercase tracking-widest text-ok">Recommended first moves</div>
          {steps.length ? (
            <ol className="list-decimal space-y-0.5 pl-4 text-slate-300">{steps.map((s, i) => <li key={i}>{s}</li>)}</ol>
          ) : <p className="text-slate-400">See the report's 30-60-90 plan.</p>}
          {typeof nc.anchor === "string" && nc.anchor && (
            <p className="mt-1.5 text-[11px] text-slate-400">Next conversation, open at: <b className="text-slate-200">{nc.anchor}</b></p>
          )}
        </div>
      </div>
    </section>
  );
}

/* ── predictions under uncertainty (Scenario Planner) ──────────────────────── */
function ScenarioPanel({ out }: { out?: AO }) {
  if (!out || typeof out.p50 !== "number") return null;
  const tiles: [string, string, string][] = [
    ["P10 · bad luck", String(out.p10), "text-err"],
    ["P50 · expected", String(out.p50), "text-slate-100"],
    ["P90 · good luck", String(out.p90), "text-ok"],
  ];
  return (
    <section className="glass card-in rounded-2xl p-4">
      <h3 className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        🎲 Predictions under uncertainty — {String(out.draws ?? 1000)} simulated futures
      </h3>
      <div className="grid grid-cols-3 gap-2">
        {tiles.map(([l, v, cls]) => (
          <div key={l} className="rounded-lg border border-line bg-panel-2 p-2 text-center">
            <div className={`font-display text-xl font-bold ${cls}`}>{v}</div>
            <div className="font-mono text-[8.5px] uppercase tracking-wider text-slate-500">{l}</div>
          </div>
        ))}
      </div>
      <div className="mt-2 flex flex-wrap gap-2 font-mono text-[10px]">
        <span className="rounded bg-ok/15 px-2 py-1 text-ok">P(GO) {Math.round(Number(out.prob_go ?? 0) * 100)}%</span>
        <span className="rounded bg-err/15 px-2 py-1 text-err">P(NO-GO) {Math.round(Number(out.prob_nogo ?? 0) * 100)}%</span>
        {typeof out.breaks_it === "string" && out.breaks_it ? (
          <span className="rounded bg-warn/15 px-2 py-1 text-warn">breaks on: {out.breaks_it}</span>
        ) : null}
      </div>
      <p className="mt-2 font-mono text-[9px] text-slate-500">
        Deterministic Monte-Carlo over the board's own scores — uncertainty width comes from the board's confidence.
      </p>
    </section>
  );
}

/* ── the negotiation playbook (Negotiation Coach) ───────────────────────────── */
function NegotiationPanel({ out }: { out?: AO }) {
  if (!out || out.degraded || !out.batna) return null;
  return (
    <section className="glass card-in rounded-2xl p-4">
      <h3 className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        🤝 The next conversation — negotiation playbook
        {typeof out.counterparty === "string" && out.counterparty ? (
          <span className="rounded bg-panel-2 px-1.5 py-0.5 text-[9px] normal-case text-slate-400">vs {out.counterparty}</span>
        ) : null}
      </h3>
      <div className="space-y-1.5 text-xs">
        <p><span className="font-mono text-[9px] uppercase tracking-widest text-cyan">Anchor · </span><span className="text-slate-200">{String(out.anchor ?? "")}</span></p>
        <p><span className="font-mono text-[9px] uppercase tracking-widest text-slate-500">BATNA · </span><span className="text-slate-300">{String(out.batna)}</span></p>
        {Array.isArray(out.concessions) && out.concessions.length > 0 && (
          <p><span className="font-mono text-[9px] uppercase tracking-widest text-slate-500">Give, in order · </span>
            <span className="text-slate-300">{(out.concessions as string[]).join(" → ")}</span></p>
        )}
        {typeof out.walk_away === "string" && out.walk_away ? (
          <p><span className="font-mono text-[9px] uppercase tracking-widest text-err">Walk away if · </span><span className="text-slate-300">{out.walk_away}</span></p>
        ) : null}
      </div>
    </section>
  );
}

function RoundOneResults({ data }: { data: ResultSetData }) {
  const v = data.verdict ?? {};
  const band = BAND_STYLE[String(v.recommendation)] ?? BAND_STYLE.CONDITIONAL_GO;
  const dims = data.dimensions ?? {};
  return (
    <div className="space-y-3 rounded-xl border border-ok/20 bg-panel/60 p-3">
      {/* the round-1 verdict */}
      <section className={`card-in rounded-2xl border p-4 ${band.cls}`}>
        <div className="flex flex-wrap items-baseline justify-between gap-3">
          <div>
            <div className="font-mono text-[10px] uppercase tracking-widest opacity-70">Round-1 verdict</div>
            <div className="font-display text-3xl font-bold">
              {String(v.score ?? "—")}<span className="text-lg opacity-60">/10</span>
            </div>
          </div>
          <div className="rounded-lg border border-current px-3 py-1.5 font-display text-base font-bold">{band.label}</div>
        </div>
        {typeof v.reasoning === "string" && v.reasoning && (
          <p className="mt-2 text-sm leading-relaxed text-slate-200">{v.reasoning}</p>
        )}
        {Object.keys(dims).length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5 font-mono text-[10px]">
            {Object.entries(dims).map(([k, val]) => (
              <span key={k} className="rounded border border-line bg-panel-2 px-1.5 py-0.5 text-slate-300">
                {k} {Number(val).toFixed(1)}
              </span>
            ))}
          </div>
        )}
      </section>

      {/* the round-1 pitch */}
      {data.story && (data.story.one_liner || data.story.narrative) && (
        <section className="glass rounded-2xl p-3">
          <div className="mb-1 font-mono text-[10px] uppercase tracking-widest text-muted">Round-1 pitch</div>
          {data.story.one_liner && <p className="font-display text-sm font-semibold text-slate-100">“{data.story.one_liner}”</p>}
          {data.story.narrative && <p className="mt-1.5 text-xs leading-relaxed text-slate-400">{data.story.narrative}</p>}
        </section>
      )}

      {/* round-1 cross-links + compliance, compact */}
      {((data.cross?.connections?.length ?? 0) > 0 || (data.compliance?.length ?? 0) > 0) && (
        <div className="flex flex-wrap gap-2 font-mono text-[10px]">
          {(data.cross?.connections?.length ?? 0) > 0 && (
            <span className="rounded border border-line bg-panel-2 px-2 py-1 text-slate-400">
              {data.cross!.connections!.length} cross-links found in round 1
            </span>
          )}
          {(data.compliance?.length ?? 0) > 0 && (
            <span className="rounded border border-warn/30 bg-warn/10 px-2 py-1 text-warn">
              {data.compliance!.length} compliance flag{data.compliance!.length > 1 ? "s" : ""}
            </span>
          )}
        </div>
      )}

      {/* the round-1 chart gallery + report, in full */}
      <ChartGallery charts={(data.charts ?? []) as unknown as ChartSpec[]}
        title={`Round-1 insight gallery — ${data.charts?.length ?? 0} charts`} />
      {data.report && <ReportSection report={data.report} title="The round-1 decision report" />}
    </div>
  );
}
