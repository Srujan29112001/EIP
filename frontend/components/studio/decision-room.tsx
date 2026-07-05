"use client";

import { AlertTriangle, ArrowRight, Download, FileJson, FileText, GraduationCap, Lightbulb, Mic, Network, Scale } from "lucide-react";
import { NeuralMap } from "@/components/graph/neural-map";
import { agentById } from "@/lib/agents";
import { buildMarkdown, download, printPdf } from "@/lib/export";
import { buildGraph } from "@/lib/graph-data";
import { useRun } from "@/lib/store";
import { AskBoard } from "./ask-board";
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
  const { verdict, radar, tokens, routes, board, brief, agentOutputs, collabs, story, crossInsights, compliance } = useRun();

  const exportMd = () =>
    download("eip-decision.md", buildMarkdown({ brief, verdict, board, agentOutputs, tokens, routes }));
  const exportJson = () =>
    download("eip-decision.json",
      JSON.stringify({ brief, verdict, board, agentOutputs }, null, 2), "application/json");
  const exportPdf = () => printPdf({ brief, verdict, board, agentOutputs, tokens, routes });

  if (!verdict) {
    return (
      <div className="rounded-xl border border-line bg-panel p-6 text-sm text-slate-500">
        The Decision Room fills in as the synthesis layer completes…
      </div>
    );
  }
  const band = BAND_STYLE[verdict.recommendation] ?? BAND_STYLE.CONDITIONAL_GO;
  const sourced = board.filter((b) => b.kind === "claim" && b.source?.url).length;

  return (
    <div className="space-y-4 pb-4">
      <QualityBanner />
      <DegradedNotice />

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
      <section className={`rounded-xl border p-5 ${band.cls}`}>
        <div className="flex flex-wrap items-baseline justify-between gap-3">
          <div>
            <div className="font-mono text-[11px] uppercase tracking-widest opacity-70">Weighted verdict</div>
            <div className="font-display text-4xl font-bold">
              {verdict.score}<span className="text-xl opacity-60">/10</span>
            </div>
          </div>
          <div className="rounded-lg border border-current px-4 py-2 font-display text-lg font-bold">
            {band.label}
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
        <section className="rounded-xl border border-line bg-gradient-to-br from-panel to-[#1a1330] p-5">
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
      <div className="grid gap-4 md:grid-cols-2">
        <section className="rounded-xl border border-line bg-panel p-4">
          <h3 className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
            <Scale size={13} /> Dimension radar
          </h3>
          <Radar dims={radar?.dimensions ?? verdict.dimensions} />
        </section>
        <section className="rounded-xl border border-line bg-panel p-4">
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
      <div className="grid gap-4 md:grid-cols-2">
        <section className="rounded-xl border border-line bg-panel p-4">
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
        <section className="rounded-xl border border-line bg-panel p-4">
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

      {/* cross-pollination — how the specialists' findings connect (A2A synthesis) */}
      {crossInsights && ((crossInsights.connections?.length ?? 0) > 0 || (crossInsights.emergent?.length ?? 0) > 0) && (
        <section className="rounded-xl border border-line bg-panel p-4">
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
      <ChartGallery />
      <SmartInsights />
      <AgentTable />

      {/* the simulation layer — bend every insight and watch the math move */}
      <RunwaySim />
      <MarketSim />
      <ScoreSim />

      {/* the Reporter's full document */}
      <ReportSection />

      {/* the decision graph — this run as a living neural map */}
      <section className="rounded-xl border border-line bg-panel p-4">
        <h3 className="mb-3 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
          <Network size={13} /> The Decision Graph — everything the board produced
        </h3>
        <NeuralMap {...buildGraph({ brief, board, agentOutputs, verdict, collabs })} height={460} />
      </section>

      <AskBoard />

      <p className="pb-2 text-center font-mono text-[10px] text-slate-600">
        EIP provides analytics and education, not investment advice. Decisions and outcomes are yours.
      </p>
    </div>
  );
}
