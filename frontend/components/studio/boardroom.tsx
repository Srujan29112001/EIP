"use client";

import { ExternalLink, Flame, Swords } from "lucide-react";
import { agentById } from "@/lib/agents";
import { useRun } from "@/lib/store";

/** The agent-to-agent feed: claims landing, conflicts opening, biases flagged. */
export function Boardroom() {
  const board = useRun((s) => s.board);

  return (
    <div className="scroll-thin max-h-[70vh] space-y-2 overflow-y-auto">
      {board.length === 0 && (
        <div className="rounded-xl border border-line bg-panel p-4 text-xs text-slate-500">
          Claims, conflicts and bias flags appear here as agents talk to each other.
        </div>
      )}
      {board.map((b, i) => {
        const a = agentById(b.agent);
        if (b.kind === "conflict") {
          return (
            <div key={i} className="rounded-lg border border-err/30 bg-err/5 p-3 text-xs">
              <div className="mb-1 flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-err">
                <Swords size={12} /> {a.name} challenges {agentById(b.vs ?? "").name}
              </div>
              <p className="text-slate-300">{b.text}</p>
            </div>
          );
        }
        if (b.kind === "bias") {
          return (
            <div key={i} className="rounded-lg border border-warn/30 bg-warn/5 p-3 text-xs">
              <div className="mb-1 flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-warn">
                <Flame size={12} /> bias flag · {b.agent}
              </div>
              <p className="text-slate-300">{b.text}</p>
            </div>
          );
        }
        return (
          <div key={i} className="rounded-lg border border-line bg-panel p-3 text-xs">
            <div className="mb-1 flex items-center justify-between">
              <span className="font-mono text-[10px] uppercase tracking-wider" style={{ color: a.accent }}>
                {a.name}
              </span>
              {typeof b.confidence === "number" && (
                <span className="font-mono text-[10px] text-slate-500">conf {Math.round(b.confidence * 100)}%</span>
              )}
            </div>
            <p className="text-slate-300">{b.text}</p>
            {b.source?.url && (
              <a href={b.source.url} target="_blank" rel="noreferrer"
                className="mt-1 inline-flex items-center gap-1 font-mono text-[10px] text-cyan hover:underline">
                <ExternalLink size={10} /> {b.source.name || new URL(b.source.url).hostname}
              </a>
            )}
            {!b.source?.url && b.kind === "claim" && (
              <span className="mt-1 inline-block rounded bg-slate-800 px-1.5 py-0.5 font-mono text-[9px] text-warn">
                agent claim — not externally sourced
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}
