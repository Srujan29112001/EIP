"use client";

/** Results v4 — the Helix/Clinical density layer.
 * KPI tile row, key-findings grid, auto-detected insight bullets (harvested
 * from every specialist's key_insights), the full per-agent statistics table,
 * and cluster "domain screens" with progress bars.
 */

import { useMemo, useState } from "react";
import { Activity, Crosshair, Gauge as GaugeIcon, ListChecks, Table2 } from "lucide-react";
import { AGENTS, agentById } from "@/lib/agents";
import { useRun } from "@/lib/store";
import type { AgentOutput } from "@/lib/types";

const OK = "#9ae64a", WARN = "#fbbf24", ERR = "#fb7185", CYAN = "#22d3ee";
const scoreCls = (v: number) => (v >= 7 ? "text-ok" : v >= 4.5 ? "text-warn" : "text-err");

/* ── KPI tile row (Helix metric tiles) ────────────────────────────────────── */
export function KpiTiles() {
  const { verdict, board, agentOutputs, tokens, routes } = useRun();
  if (!verdict) return null;
  const claims = board.filter((b) => b.kind === "claim");
  const sourced = claims.filter((b) => b.source?.url).length;
  const scored = Object.values(agentOutputs).filter((o) => typeof o.score === "number");
  const avgConf = scored.length
    ? scored.reduce((s, o) => s + (typeof o.confidence === "number" ? o.confidence : 0.5), 0) / scored.length
    : 0;
  const attacks = board.filter((b) => b.kind === "conflict").length;
  const tiles = [
    { label: "specialists", value: String(Object.keys(agentOutputs).length), sub: "convened & done", cls: "text-cyan" },
    { label: "avg confidence", value: `${Math.round(avgConf * 100)}%`, sub: "self-reported, calibrated", cls: avgConf >= 0.6 ? "text-ok" : "text-warn" },
    { label: "evidence", value: String(claims.length), sub: `${sourced} live-sourced (${claims.length ? Math.round((sourced / claims.length) * 100) : 0}%)`, cls: "text-cyan" },
    { label: "attacks", value: String(attacks), sub: "red team, preserved", cls: attacks ? "text-err" : "text-ok" },
    { label: "compute", value: tokens > 999 ? `${(tokens / 1000).toFixed(1)}k` : String(tokens), sub: [...routes].length ? `${[...routes].length} routes` : "deterministic", cls: "text-slate-300" },
  ];
  return (
    <section className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-5">
      {tiles.map((t, i) => (
        <div key={t.label} className="panel-hover card-in glass rounded-2xl p-3 text-center">
          <div className={`font-display text-2xl font-bold ${t.cls}`}>{t.value}</div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-slate-400">{t.label}</div>
          {t.sub && <div className="mt-0.5 font-mono text-[10px] text-slate-400">{t.sub}</div>}
        </div>
      ))}
    </section>
  );
}

/* ── key findings grid (Helix KEY FINDINGS) ───────────────────────────────── */
export function KeyFindings() {
  const { verdict, agentOutputs } = useRun();
  if (!verdict?.dimensions) return null;
  const dimsSorted = Object.entries(verdict.dimensions).sort((a, b) => b[1] - a[1]);
  const scored = Object.entries(agentOutputs)
    .filter(([, o]) => typeof o.score === "number")
    .sort((a, b) => (b[1].score as number) - (a[1].score as number));
  if (!dimsSorted.length || !scored.length) return null;
  const [bestDim] = dimsSorted, worstDim = dimsSorted[dimsSorted.length - 1];
  const bull = scored[0], bear = scored[scored.length - 1];
  const topRisk = (verdict.risks ?? [])[0];
  const cards: { label: string; value: string; sub?: string; color: string }[] = [
    { label: "strongest dimension", value: `${bestDim[0]} · ${bestDim[1]}/10`, color: OK },
    { label: "weakest dimension", value: `${worstDim[0]} · ${worstDim[1]}/10`, sub: "fix this first", color: ERR },
    { label: "biggest believer", value: agentById(bull[0]).name, sub: `${bull[1].score}/10 — ${String(bull[1].verdict_line ?? "").slice(0, 60)}`, color: CYAN },
    { label: "biggest skeptic", value: agentById(bear[0]).name, sub: `${bear[1].score}/10 — ${String(bear[1].verdict_line ?? "").slice(0, 60)}`, color: WARN },
  ];
  if (topRisk) cards.push({ label: "top risk", value: String(topRisk.text).slice(0, 70), sub: `flagged by ${agentById(topRisk.source_agent).name}`, color: ERR });
  if (verdict.sensitivities?.[0]) cards.push({ label: "most sensitive to", value: String(verdict.sensitivities[0]).slice(0, 70), sub: "what would change the verdict", color: "#a78bfa" });
  return (
    <section>
      <h3 className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        <Crosshair size={13} /> Key findings
      </h3>
      <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-3">
        {cards.map((c, i) => (
          <div key={i} className="panel-hover card-in glass rounded-2xl p-3"
            style={{ borderLeftColor: c.color, borderLeftWidth: 3 }}>
            <div className="font-mono text-[10px] uppercase tracking-widest" style={{ color: c.color }}>{c.label}</div>
            <div className="mt-0.5 text-sm font-semibold text-slate-200">{c.value}</div>
            {c.sub && <div className="mt-0.5 text-[11px] text-slate-400">{c.sub}</div>}
          </div>
        ))}
      </div>
    </section>
  );
}

/* ── auto-detected insight bullets (harvested key_insights) ──────────────── */
export function InsightBullets() {
  const agentOutputs = useRun((s) => s.agentOutputs);
  const items = useMemo(() => {
    const out: { agent: string; text: string }[] = [];
    for (const [aid, o] of Object.entries(agentOutputs)) {
      const ins = (o as AgentOutput).key_insights;
      if (Array.isArray(ins)) for (const t of ins.slice(0, 2)) out.push({ agent: aid, text: String(t) });
    }
    return out.slice(0, 18);
  }, [agentOutputs]);
  if (items.length < 1) return null;
  return (
    <section className="glass card-in rounded-2xl p-4">
      <h3 className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        <ListChecks size={13} /> Key insights · auto-detected across the board ({items.length})
      </h3>
      <div className="grid gap-1.5 md:grid-cols-2">
        {items.map((x, i) => {
          const a = agentById(x.agent);
          return (
            <div key={i} className="flex items-start gap-2 rounded-lg bg-panel-2 px-2.5 py-1.5 text-xs leading-relaxed">
              <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: a.accent }} />
              <span className="text-slate-300">{x.text}
                <span className="ml-1.5 font-mono text-[10px] text-slate-400">— {a.name}</span>
              </span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

/* ── the board as a statistics table (Helix significance-table idiom) ─────── */
export function AgentTable() {
  const agentOutputs = useRun((s) => s.agentOutputs);
  const [sortBy, setSortBy] = useState<"score" | "confidence">("score");
  const rows = Object.entries(agentOutputs)
    .filter(([, o]) => typeof o.score === "number")
    .sort((a, b) => ((b[1][sortBy] as number) ?? 0) - ((a[1][sortBy] as number) ?? 0));
  if (rows.length < 2) return null;
  return (
    <section className="glass card-in rounded-2xl p-4">
      <h3 className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        <Table2 size={13} /> The board, in numbers · click headers to sort
      </h3>
      <div className="scroll-thin max-h-96 overflow-auto">
        <table className="w-full min-w-[640px] font-mono text-[11px]">
          <thead className="sticky top-0 bg-panel">
            <tr className="border-b border-line text-left text-slate-400">
              <th className="py-1.5 pr-2 font-normal">specialist</th>
              <th className="pr-2 font-normal">cluster</th>
              <th className="cursor-pointer pr-2 font-normal hover:text-cyan" onClick={() => setSortBy("score")}>
                score {sortBy === "score" ? "▾" : ""}</th>
              <th className="cursor-pointer pr-2 font-normal hover:text-cyan" onClick={() => setSortBy("confidence")}>
                conf {sortBy === "confidence" ? "▾" : ""}</th>
              <th className="font-normal">finding</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(([aid, o]) => {
              const a = agentById(aid);
              const s = o.score as number;
              return (
                <tr key={aid} className="border-b border-line/40 align-top hover:bg-white/[0.02]">
                  <td className="whitespace-nowrap py-1.5 pr-2">
                    <span className="mr-1">{a.icon}</span>
                    <span style={{ color: a.accent }}>{a.name}</span>
                  </td>
                  <td className="pr-2 text-slate-400">{a.cluster}</td>
                  <td className={`pr-2 font-bold ${scoreCls(s)}`}>{s}</td>
                  <td className="pr-2 text-slate-400">
                    {typeof o.confidence === "number" ? `${Math.round(o.confidence * 100)}%` : "—"}
                  </td>
                  <td className="max-w-[300px] pr-1 text-slate-400">{String(o.verdict_line ?? "").slice(0, 90)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

/* ── domain screens: cluster averages as progress bars (Clinical idiom) ───── */
export function DomainScreens() {
  const agentOutputs = useRun((s) => s.agentOutputs);
  const clusters = useMemo(() => {
    const acc: Record<string, { total: number; n: number; accent: string }> = {};
    for (const a of AGENTS) {
      const o = agentOutputs[a.id];
      if (!o || typeof o.score !== "number") continue;
      (acc[a.cluster] ??= { total: 0, n: 0, accent: a.accent }).total += o.score;
      acc[a.cluster].n += 1;
    }
    return Object.entries(acc)
      .map(([k, v]) => ({ cluster: k, avg: v.total / v.n, n: v.n, accent: v.accent }))
      .sort((a, b) => b.avg - a.avg);
  }, [agentOutputs]);
  if (clusters.length < 1) return null;
  return (
    <section className="glass card-in rounded-2xl p-4">
      <h3 className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        <Activity size={13} /> Domain screens · average read per cluster
      </h3>
      <div className="grid gap-x-6 gap-y-2 md:grid-cols-2">
        {clusters.map((c) => (
          <div key={c.cluster}>
            <div className="flex justify-between font-mono text-[10px]">
              <span className="uppercase tracking-wider text-slate-400">{c.cluster} <span className="text-slate-400">· {c.n} agents</span></span>
              <span className={scoreCls(c.avg)}>{c.avg.toFixed(1)}/10</span>
            </div>
            <div className="mt-1 h-2 overflow-hidden rounded-full bg-slate-800">
              <div className="h-full rounded-full transition-all duration-700"
                style={{ width: `${c.avg * 10}%`, background: `linear-gradient(90deg, ${c.accent}66, ${c.accent})` }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ── reduced-depth notice — honest about which agents didn't get an LLM ──── */
export function DegradedNotice() {
  const { agentStatus, agentOutputs } = useRun();
  const degraded = AGENTS.filter((a) =>
    agentStatus[a.id] === "degraded" || (agentOutputs[a.id] as AgentOutput | undefined)?.degraded);
  const ran = Object.keys(agentOutputs).length;
  if (!degraded.length) return null;
  const reason = (agentOutputs[degraded[0].id] as AgentOutput | undefined)?.degraded_reason
    ?? "no LLM reached these agents — every configured key was rate-limited or missing.";
  return (
    <details className="rounded-2xl border border-warn/40 bg-warn/5 p-1">
      <summary className="flex cursor-pointer items-center gap-2 rounded-xl px-3 py-2 transition hover:bg-warn/10">
        <span className="text-sm">⚠</span>
        <span className="font-mono text-[11px] uppercase tracking-widest text-warn">
          {degraded.length} of {ran} specialists ran reduced-depth — details
        </span>
      </summary>
      <div className="px-3 pb-2.5">
      <p className="mt-1 text-xs leading-relaxed text-slate-400">
        These agents produced a deterministic-core answer but couldn&apos;t get AI narration: <span className="text-slate-300">{reason}</span>
      </p>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {degraded.map((a) => (
          <span key={a.id} className="inline-flex items-center gap-1 rounded border border-warn/30 bg-warn/10 px-1.5 py-0.5 font-mono text-[10px] text-warn">
            <span>{a.icon}</span> {a.name}
          </span>
        ))}
      </div>
      <p className="mt-2 font-mono text-[10px] text-slate-400">
        Fix: add more API keys in the engine step (up to 16 per provider — they rotate automatically), or re-run at a lighter depth.
      </p>
      </div>
    </details>
  );
}

/* ── verdict-quality banner (Helix model-quality banner) ─────────────────── */
export function QualityBanner() {
  const { verdict, board, agentOutputs } = useRun();
  if (!verdict) return null;
  const claims = board.filter((b) => b.kind === "claim");
  const sourcedPct = claims.length ? Math.round((claims.filter((b) => b.source?.url).length / claims.length) * 100) : 0;
  const llmRuns = Object.values(agentOutputs).filter((o) => o.route && o.route !== "none").length;
  const grade = sourcedPct >= 60 && llmRuns >= 5 ? ["Strong evidence base", OK]
    : sourcedPct >= 35 ? ["Workable evidence — verify the flagged estimates", WARN]
    : ["Thin evidence — treat as directional only", ERR];
  return (
    <div className="flex flex-wrap items-center gap-2 rounded-xl border p-3"
      style={{ borderColor: `${grade[1]}55`, background: `${grade[1]}0d` }}>
      <GaugeIcon size={15} style={{ color: grade[1] }} />
      <span className="text-sm font-semibold" style={{ color: grade[1] }}>{grade[0]}</span>
      <span className="font-mono text-[10px] text-slate-400">
        {sourcedPct}% of claims live-sourced · {llmRuns} AI-narrated specialists · dissent preserved, never averaged away
      </span>
    </div>
  );
}
