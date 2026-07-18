"use client";

import { Flame, Swords } from "lucide-react";
import { agentById } from "@/lib/agents";
import { useRun } from "@/lib/store";

/** The Disagreement Panel — dissent is preserved as output, never averaged away
 * (Constitution #2). Conflicts + bias flags from the boardroom, in the verdict. */
export function Disagreements() {
  const board = useRun((s) => s.board);
  const conflicts = board.filter((b) => b.kind === "conflict");
  const biases = board.filter((b) => b.kind === "bias");
  if (!conflicts.length && !biases.length) return null;

  return (
    <section className="glass card-in rounded-2xl p-4">
      <h3 className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        <Swords size={13} /> Where the board disagreed
      </h3>
      <div className="space-y-1.5">
        {conflicts.map((c, i) => (
          <div key={`c${i}`} className="rounded-lg border border-err/25 bg-err/5 p-2.5 text-xs">
            <span className="font-mono text-[10px] uppercase tracking-wider text-err">
              {agentById(c.agent).name} → {agentById(c.vs ?? "").name}
            </span>
            <p className="mt-0.5 text-slate-300">{c.text}</p>
          </div>
        ))}
        {biases.map((f, i) => (
          <div key={`b${i}`} className="rounded-lg border border-warn/25 bg-warn/5 p-2.5 text-xs">
            <span className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider text-warn">
              <Flame size={11} /> your framing
            </span>
            <p className="mt-0.5 text-slate-300">{f.text}</p>
          </div>
        ))}
      </div>
      <p className="mt-2 font-mono text-[10px] text-slate-600">
        Disagreement is data — it is factored into the weighted score, not hidden.
      </p>
    </section>
  );
}
