"use client";

/** THE EVIDENCE WALL — the boardroom as a living case file.
 *
 * Every claim, conflict, debate blow and bias flag the agents throw at each
 * other, pinned to a filterable wall: a stat strip up top, accent-railed
 * evidence cards below, battles stretched full-width for drama.
 */

import { useState } from "react";
import { ExternalLink, Flame, Link2, Swords } from "lucide-react";
import { agentById } from "@/lib/agents";
import { useRun } from "@/lib/store";

/** Scraped source URLs are untrusted — a malformed one must not crash the tab. */
function safeHost(url: string): string {
  try {
    return new URL(url).hostname;
  } catch {
    return url.slice(0, 40);
  }
}

type Filter = "all" | "claim" | "conflict" | "debate" | "bias";

export function Boardroom() {
  const board = useRun((s) => s.board);
  const [filter, setFilter] = useState<Filter>("all");

  const claims = board.filter((b) => b.kind === "claim");
  const sourced = claims.filter((b) => b.source?.url).length;
  const counts: Record<Filter, number> = {
    all: board.length,
    claim: claims.length,
    conflict: board.filter((b) => b.kind === "conflict").length,
    debate: board.filter((b) => b.kind === "debate").length,
    bias: board.filter((b) => b.kind === "bias").length,
  };
  const visible = board
    .map((b, i) => ({ b, i }))
    .filter(({ b }) => filter === "all" || (b.kind ?? "claim") === filter
      || (filter === "claim" && !["conflict", "debate", "bias"].includes(b.kind ?? "")));

  if (board.length === 0) {
    return (
      <div className="glass card-in flex items-center gap-3 rounded-2xl p-5 text-xs text-slate-500">
        <span className="typing-dots"><span /><span /><span /></span>
        Claims, conflicts and bias flags appear here as agents talk to each other.
      </div>
    );
  }

  return (
    <div className="space-y-3 pb-4">
      {/* ── the case-file header: live stats + filters ── */}
      <div className="glass card-in rounded-2xl p-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-mono text-[10px] uppercase tracking-[0.25em] text-cyan">Evidence wall</span>
          <span className="rounded-full border border-cyan/30 bg-cyan/10 px-2 py-0.5 font-mono text-[10px] text-cyan">
            {counts.claim} claims
          </span>
          <span className="rounded-full border border-ok/30 bg-ok/10 px-2 py-0.5 font-mono text-[10px] text-ok">
            <Link2 size={9} className="mr-1 inline" />
            {claims.length ? Math.round((sourced / claims.length) * 100) : 0}% live-sourced
          </span>
          {counts.conflict > 0 && (
            <span className="rounded-full border border-err/30 bg-err/10 px-2 py-0.5 font-mono text-[10px] text-err">
              <Swords size={9} className="mr-1 inline" />{counts.conflict} challenges
            </span>
          )}
          {counts.bias > 0 && (
            <span className="rounded-full border border-warn/30 bg-warn/10 px-2 py-0.5 font-mono text-[10px] text-warn">
              <Flame size={9} className="mr-1 inline" />{counts.bias} bias flags
            </span>
          )}
          <span className="ml-auto flex gap-1">
            {(["all", "claim", "conflict", "debate", "bias"] as const).map((fk) => (
              <button key={fk} onClick={() => setFilter(fk)}
                className={`rounded-lg px-2.5 py-1 font-mono text-[9px] uppercase tracking-wider transition ${
                  filter === fk
                    ? "bg-panel-2 text-cyan shadow-[0_0_14px_-5px_rgba(34,211,238,0.6)]"
                    : "text-slate-500 hover:text-slate-300"}`}>
                {fk}{counts[fk] ? ` ${counts[fk]}` : ""}
              </button>
            ))}
          </span>
        </div>
      </div>

      {/* ── the wall ── */}
      <div className="grid gap-2 md:grid-cols-2">
        {visible.map(({ b, i }) => {
          const a = agentById(b.agent);
          if (b.kind === "conflict") {
            return (
              <div key={i}
                className="card-in relative overflow-hidden rounded-2xl border border-err/30 bg-err/5 p-3.5 text-xs md:col-span-2">
                <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,rgba(251,113,133,0.08),transparent_55%)]" />
                <div className="relative mb-1.5 flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-err">
                  <span className="grid h-6 w-6 place-items-center rounded-lg border border-err/40 bg-err/10">
                    <Swords size={12} />
                  </span>
                  <span style={{ color: a.accent }}>{a.icon} {a.name}</span>
                  <span className="text-err">challenges</span>
                  <span style={{ color: agentById(b.vs ?? "").accent }}>
                    {agentById(b.vs ?? "").icon} {agentById(b.vs ?? "").name}
                  </span>
                </div>
                <p className="relative leading-relaxed text-slate-300">{b.text}</p>
              </div>
            );
          }
          if (b.kind === "debate") {
            const style = b.stance === "attack"
              ? { border: "border-err/30", bg: "bg-err/5", tag: "text-err", label: "⚔ attacks" }
              : b.stance === "concession"
                ? { border: "border-warn/30", bg: "bg-warn/5", tag: "text-warn", label: "concedes" }
                : { border: "border-cyan/30", bg: "bg-cyan/5", tag: "text-cyan", label: "rebuts" };
            return (
              <div key={i}
                className={`card-in rounded-2xl border ${style.border} ${style.bg} p-3.5 text-xs md:col-span-2 md:ml-10`}>
                <div className={`mb-1.5 flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider ${style.tag}`}>
                  <span className="h-1.5 w-1.5 rounded-full" style={{ background: a.accent }} />
                  {a.icon} {a.name} {style.label} · debate round {b.round}
                </div>
                <p className="leading-relaxed text-slate-300">{b.text}</p>
              </div>
            );
          }
          if (b.kind === "bias") {
            return (
              <div key={i} className="card-in rounded-2xl border border-warn/30 bg-warn/5 p-3.5 text-xs md:col-span-2">
                <div className="mb-1.5 flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-warn">
                  <span className="grid h-6 w-6 place-items-center rounded-lg border border-warn/40 bg-warn/10">
                    <Flame size={12} />
                  </span>
                  bias flag · {b.agent}
                </div>
                <p className="leading-relaxed text-slate-300">{b.text}</p>
              </div>
            );
          }
          return (
            <div key={i}
              className="card-in scan-on-hover relative rounded-2xl border border-line bg-panel/80 p-3.5 text-xs backdrop-blur-sm transition hover:-translate-y-0.5"
              style={{ borderLeftColor: a.accent, borderLeftWidth: 3, animationDelay: `${Math.min(i % 8, 6) * 45}ms` }}>
              <div className="mb-1 flex items-center justify-between">
                <span className="font-mono text-[10px] uppercase tracking-wider" style={{ color: a.accent }}>
                  {a.icon} {a.name}
                </span>
                {typeof b.confidence === "number" && (
                  <span className="flex items-center gap-1.5 font-mono text-[10px] text-slate-500">
                    <span className="inline-block h-1 w-10 overflow-hidden rounded-full bg-slate-800">
                      <span className="block h-full rounded-full"
                        style={{ width: `${Math.round(b.confidence * 100)}%`, background: a.accent }} />
                    </span>
                    {Math.round(b.confidence * 100)}%
                  </span>
                )}
              </div>
              <p className="leading-relaxed text-slate-300">{b.text}</p>
              {b.source?.url && (
                <a href={b.source.url} target="_blank" rel="noreferrer"
                  className="mt-1.5 inline-flex items-center gap-1 rounded-full border border-cyan/25 bg-cyan/5 px-2 py-0.5 font-mono text-[10px] text-cyan transition hover:border-cyan/60">
                  <ExternalLink size={10} /> {b.source.name || safeHost(b.source.url)}
                </a>
              )}
              {!b.source?.url && b.kind === "claim" && (
                <span className="mt-1.5 inline-block rounded-full bg-slate-800 px-2 py-0.5 font-mono text-[9px] text-warn">
                  agent claim — not externally sourced
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
