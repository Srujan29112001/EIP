"use client";

/** MISSION HUD — the pipeline tab's control room.
 *
 * A live dashboard over the run: an animated completion ring, the L0→L5
 * conveyor with per-layer progress, live counters (active agent, gold links,
 * compute, clock) and a terminal ticker showing the board's last words.
 * Purely derived from the run store — renders nothing new into it.
 */

import { useEffect, useRef, useState } from "react";
import { AGENTS, LAYER_LABELS, agentById } from "@/lib/agents";
import { useRun } from "@/lib/store";

const LAYERS = ["L0", "L1", "L2", "L3", "L4", "L5"] as const;
const LAYER_COLORS: Record<string, string> = {
  L0: "#94a3b8", L1: "#22d3ee", L2: "#8b5cf6", L3: "#fb7185", L4: "#eab308", L5: "#34d399",
};

export function MissionHud() {
  const phase = useRun((s) => s.phase);
  const agentStatus = useRun((s) => s.agentStatus);
  const logs = useRun((s) => s.logs);
  const collabs = useRun((s) => s.collabs);
  const tokens = useRun((s) => s.tokens);

  // mission clock — starts when the HUD mounts (run start), freezes on done
  const t0 = useRef<number | null>(null);
  const [now, setNow] = useState(0);
  useEffect(() => {
    if (t0.current === null) t0.current = Date.now();
    if (phase === "done") return;
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, [phase]);
  const secs = t0.current ? Math.max(0, Math.floor(((phase === "done" ? now : Date.now()) - t0.current) / 1000)) : 0;
  const clock = `${String(Math.floor(secs / 60)).padStart(2, "0")}:${String(secs % 60).padStart(2, "0")}`;

  const tracked = Object.entries(agentStatus);
  const finished = tracked.filter(([, st]) => st === "done" || st === "degraded" || st === "skipped");
  const active = tracked.filter(([, st]) => st === "active");
  const degraded = tracked.filter(([, st]) => st === "degraded");
  const pct = tracked.length ? Math.round((finished.length / tracked.length) * 100) : 0;
  const goldLinks = Object.values(collabs).reduce((n, peers) => n + peers.length, 0);
  const lastLog = logs[logs.length - 1];
  const activeAgent = active.length ? agentById(active[active.length - 1][0]) : null;

  const perLayer = LAYERS.map((layer) => {
    const ids = tracked.filter(([id]) => AGENTS.find((a) => a.id === id)?.layer === layer);
    const doneN = ids.filter(([, st]) => st === "done" || st === "degraded" || st === "skipped").length;
    const activeN = ids.filter(([, st]) => st === "active").length;
    return { layer, total: ids.length, done: doneN, live: activeN > 0 };
  });

  return (
    <div className="g-border g-border-slow relative overflow-hidden rounded-2xl p-4">
      <div className="grid items-center gap-4 lg:grid-cols-[auto_1fr_auto]">
        {/* completion ring */}
        <div className="flex items-center gap-4">
          <div className="gauge-ring grid h-24 w-24 shrink-0 place-items-center rounded-full"
            style={{ "--pct": pct } as React.CSSProperties}>
            <div className="text-center">
              <div className="font-hero text-2xl font-bold leading-none text-slate-100">{pct}%</div>
              <div className="mt-0.5 font-mono text-[8px] uppercase tracking-wider text-slate-500">
                {finished.length}/{tracked.length || "—"}
              </div>
            </div>
          </div>
          <div>
            <div className="font-mono text-[9px] uppercase tracking-[0.3em] text-cyan">Mission</div>
            <div className="font-hero text-lg font-bold leading-tight text-slate-100">
              {phase === "done" ? "Board adjourned" : "Board in session"}
            </div>
            <div className="mt-1 flex items-center gap-2 font-mono text-[10px] text-slate-500">
              <span className={`h-1.5 w-1.5 rounded-full ${phase === "done" ? "bg-ok" : "pulse-ring bg-cyan"}`}
                style={{ "--ring": "#22d3ee" } as React.CSSProperties} />
              T+{clock}
            </div>
          </div>
        </div>

        {/* layer conveyor */}
        <div className="flex min-w-0 items-center gap-1.5 overflow-x-auto py-1">
          {perLayer.map(({ layer, total, done, live }, i) => (
            <div key={layer} className="flex shrink-0 items-center gap-1.5">
              <div className={`rounded-xl border px-2.5 py-1.5 text-center transition ${
                live ? "border-cyan/50 bg-cyan/5 shadow-[0_0_18px_-6px_rgba(34,211,238,0.6)]"
                  : done > 0 && done === total ? "border-line bg-panel-2/60" : "border-line/60 bg-transparent"}`}>
                <div className="font-mono text-[9px] font-bold" style={{ color: LAYER_COLORS[layer] }}>{layer}</div>
                <div className="font-mono text-[8px] text-slate-500">{LAYER_LABELS[layer]}</div>
                <div className="mt-1 h-0.5 w-14 overflow-hidden rounded-full bg-slate-800">
                  <div className="h-full transition-all duration-700"
                    style={{ width: total ? `${(done / total) * 100}%` : "0%", background: LAYER_COLORS[layer] }} />
                </div>
                <div className="mt-0.5 font-mono text-[8px] text-slate-600">{done}/{total || "·"}</div>
              </div>
              {i < LAYERS.length - 1 && (
                <div className="beam w-4 shrink-0" style={{ animationDelay: `${i * 0.3}s` }} />
              )}
            </div>
          ))}
        </div>

        {/* live counters */}
        <div className="grid grid-cols-3 gap-2 lg:grid-cols-1 lg:gap-1.5">
          <div className="rounded-lg border border-line bg-panel-2/60 px-2.5 py-1.5">
            <div className="font-mono text-[8px] uppercase tracking-wider text-slate-500">now speaking</div>
            <div className="truncate text-xs font-semibold"
              style={{ color: activeAgent?.accent ?? "#475569" }}>
              {activeAgent ? `${activeAgent.icon} ${activeAgent.name}` : phase === "done" ? "—" : "…"}
            </div>
          </div>
          <div className="rounded-lg border border-line bg-panel-2/60 px-2.5 py-1.5">
            <div className="font-mono text-[8px] uppercase tracking-wider text-slate-500">gold links · compute</div>
            <div className="text-xs font-semibold text-slate-200">
              <span className="text-[#fbbf24]">{goldLinks}</span>
              <span className="mx-1 text-slate-600">·</span>
              {tokens > 999 ? `${(tokens / 1000).toFixed(1)}k` : tokens} tok
            </div>
          </div>
          <div className="rounded-lg border border-line bg-panel-2/60 px-2.5 py-1.5">
            <div className="font-mono text-[8px] uppercase tracking-wider text-slate-500">reduced depth</div>
            <div className={`text-xs font-semibold ${degraded.length ? "text-warn" : "text-ok"}`}>
              {degraded.length ? `${degraded.length} agents` : "none"}
            </div>
          </div>
        </div>
      </div>

      {/* activity ticker — the board's last words */}
      {lastLog && (
        <div key={logs.length}
          className="msg-in mt-3 flex items-center gap-2 overflow-hidden rounded-lg bg-ink/70 px-3 py-1.5 font-mono text-[10px]">
          <span className="shrink-0" style={{ color: agentById(lastLog.agent).accent }}>
            {agentById(lastLog.agent).icon} {agentById(lastLog.agent).name} ›
          </span>
          <span className="truncate text-slate-400">{lastLog.text}</span>
        </div>
      )}
    </div>
  );
}
