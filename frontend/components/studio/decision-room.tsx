"use client";

import { AlertTriangle, ArrowRight, Download, FileJson, GraduationCap, Lightbulb, Network, Scale } from "lucide-react";
import { NeuralMap } from "@/components/graph/neural-map";
import { agentById } from "@/lib/agents";
import { buildMarkdown, download } from "@/lib/export";
import { buildGraph } from "@/lib/graph-data";
import { useRun } from "@/lib/store";
import { AgentAccordion } from "./agent-accordion";
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
  const { verdict, radar, tokens, routes, board, brief, agentOutputs } = useRun();

  const exportMd = () =>
    download("eip-decision.md", buildMarkdown({ brief, verdict, board, agentOutputs, tokens, routes }));
  const exportJson = () =>
    download("eip-decision.json",
      JSON.stringify({ brief, verdict, board, agentOutputs }, null, 2), "application/json");

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
    <div className="scroll-thin max-h-[74vh] space-y-4 overflow-y-auto pr-1">
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
          </span>
        </div>
      </section>

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

      <Disagreements />
      <TradeDesk />

      {/* the simulation layer — bend every insight and watch the math move */}
      <RunwaySim />
      <MarketSim />
      <ScoreSim />

      <AgentAccordion />

      {/* the decision graph — this run as a living neural map */}
      <section className="rounded-xl border border-line bg-panel p-4">
        <h3 className="mb-3 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
          <Network size={13} /> The Decision Graph — everything the board produced
        </h3>
        <NeuralMap {...buildGraph({ brief, board, agentOutputs, verdict })} height={460} />
      </section>

      <p className="pb-2 text-center font-mono text-[10px] text-slate-600">
        EIP provides analytics and education, not investment advice. Decisions and outcomes are yours.
      </p>
    </div>
  );
}
