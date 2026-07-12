"use client";

/** 🎼 The Orchestra — Intelligent Mode's signature two-tier view.
 *
 * The Manager's task graph (movements → players), where every player expands to
 * its junior INSTRUMENTS lighting up as each one reports. This is the whole
 * point of Intelligent Mode: not a flat list of agents, but an orchestra where
 * every expert conducts its own section.
 */

import { useState } from "react";
import { useRun } from "@/lib/store";
import type { StageStatus, TaskGraphPlayer } from "@/lib/types";

const STATUS_DOT: Record<StageStatus, string> = {
  queued: "bg-slate-600",
  active: "bg-cyan animate-pulse",
  done: "bg-ok",
  degraded: "bg-warn",
  error: "bg-err",
  skipped: "bg-slate-700",
};

export function OrchestraView() {
  const taskGraph = useRun((s) => s.taskGraph);
  const instruments = useRun((s) => s.instruments);
  const agentStatus = useRun((s) => s.agentStatus);
  if (!taskGraph) return null;

  const playedInst = Object.values(instruments).reduce((n, arr) => n + arr.filter((i) => i.finding && !i.finding.startsWith("(no model")).length, 0);

  return (
    <div className="space-y-3">
      <div className="rounded-xl border border-brand/40 bg-gradient-to-b from-brand/5 to-panel p-4">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-lg">🎼</span>
          <h3 className="font-display text-sm font-bold text-slate-100">The Orchestra — the Manager&apos;s score</h3>
          {taskGraph.regulated && (
            <span className="rounded border border-err/40 bg-err/10 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-wider text-err">
              regulated · human review
            </span>
          )}
          <span className="ml-auto font-mono text-[10px] text-muted">
            {taskGraph.movements.length} movements · {taskGraph.n_players} players ·{" "}
            <span className="text-brand">{playedInst}/{taskGraph.n_instruments}</span> instruments played
          </span>
        </div>
        {taskGraph.focus && <p className="mt-2 text-xs leading-relaxed text-slate-400">{taskGraph.focus}</p>}
      </div>

      {taskGraph.movements.map((mv) => (
        <div key={mv.id} className="rounded-xl border border-line bg-panel p-3">
          <div className="mb-2 flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-sm" style={{ background: mv.color }} />
            <span className="font-mono text-[11px] uppercase tracking-wider text-slate-300">
              {mv.id} · {mv.name}
            </span>
            <span className="font-mono text-[10px] text-slate-600">{mv.players.length} players</span>
          </div>
          <div className="grid gap-2 md:grid-cols-2">
            {mv.players.map((p) => (
              <PlayerCard key={p.id} player={p} color={mv.color}
                status={agentStatus[p.id] ?? "queued"}
                insts={instruments[p.id] ?? []} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function PlayerCard({ player, color, status, insts }: {
  player: TaskGraphPlayer;
  color: string;
  status: StageStatus;
  insts: { name: string; skill: string; finding: string; status: string }[];
}) {
  const [open, setOpen] = useState(false);
  const byName = new Map(insts.map((i) => [i.name, i]));
  const played = insts.filter((i) => i.finding && !i.finding.startsWith("(no model")).length;

  return (
    <div className="rounded-lg border border-line bg-panel-2 p-2.5">
      <button onClick={() => setOpen((v) => !v)} className="flex w-full items-center gap-2 text-left">
        <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${STATUS_DOT[status]}`} />
        <span className="text-sm">{player.emoji}</span>
        <span className="truncate text-[13px] font-semibold text-slate-200">{player.name}</span>
        <span className="ml-auto shrink-0 font-mono text-[9px] text-slate-500">
          {played}/{player.instruments.length} ▸
        </span>
      </button>
      {/* the instruments — always visible as a chip strip, expand for findings */}
      <div className="mt-2 flex flex-wrap gap-1">
        {player.instruments.map((name) => {
          const done = byName.get(name);
          const lit = done && done.finding && !done.finding.startsWith("(no model");
          const amber = done && done.finding.startsWith("(no model");
          return (
            <span key={name} title={done?.finding || name}
              className={`rounded px-1.5 py-0.5 font-mono text-[9px] transition ${
                lit ? "border text-slate-200" : amber ? "border border-warn/40 bg-warn/5 text-warn"
                : "border border-line text-slate-600"}`}
              style={lit ? { borderColor: color, color, background: `${color}14` } : undefined}>
              {name}
            </span>
          );
        })}
      </div>
      {open && (
        <div className="mt-2 space-y-1 border-t border-line pt-2">
          {player.instruments.map((name) => {
            const f = byName.get(name);
            return (
              <div key={name} className="text-[11px] leading-snug">
                <span className="font-mono text-[10px]" style={{ color }}>{name}</span>
                <span className="text-slate-400"> — {f?.finding || <span className="text-slate-600">pending…</span>}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
