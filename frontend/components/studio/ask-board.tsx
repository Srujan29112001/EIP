"use client";

/** Ask the Board — grounded chat over THIS run's evidence. The spokesperson
 * may only cite what the board actually produced; questions outside the
 * evidence get an honest "not in the record" instead of a hallucination.
 */

import { useRef, useState } from "react";
import { CornerDownLeft, MessagesSquare } from "lucide-react";
import { askBoard } from "@/lib/api";
import { useRun } from "@/lib/store";

interface Msg { role: "you" | "board"; text: string; route?: string }

const SUGGESTIONS = [
  "What is the single biggest risk here?",
  "Why is the score not higher?",
  "What would change this verdict?",
];

export function AskBoard() {
  const runId = useRun((s) => s.runId);
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  if (!runId) return null;

  const send = async (text: string) => {
    const question = text.trim();
    if (!question || busy) return;
    setQ("");
    setBusy(true);
    setMsgs((m) => [...m, { role: "you", text: question }]);
    try {
      const res = await askBoard(runId, question);
      setMsgs((m) => [...m, { role: "board", text: res.answer, route: res.route }]);
    } catch {
      setMsgs((m) => [...m, { role: "board", text: "The board is unreachable — is the backend running?" }]);
    } finally {
      setBusy(false);
      setTimeout(() => endRef.current?.scrollIntoView({ block: "nearest" }), 50);
    }
  };

  return (
    <section className="rounded-xl border border-line bg-panel p-4 transition hover:border-cyan/25">
      <h3 className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        <MessagesSquare size={13} /> Ask the board — grounded in this run only
      </h3>

      {msgs.length === 0 && (
        <div className="mb-2 flex flex-wrap gap-1.5">
          {SUGGESTIONS.map((s) => (
            <button key={s} onClick={() => send(s)}
              className="rounded-full border border-line px-2.5 py-1 font-mono text-[10px] text-slate-500 transition hover:border-cyan/50 hover:text-cyan">
              {s}
            </button>
          ))}
        </div>
      )}

      {msgs.length > 0 && (
        <div className="scroll-thin mb-3 max-h-72 space-y-2 overflow-y-auto pr-1">
          {msgs.map((m, i) => (
            <div key={i} className={`rounded-lg p-2.5 text-xs leading-relaxed ${
              m.role === "you" ? "ml-8 border border-brand/30 bg-brand/10 text-slate-200"
                : "mr-8 border border-line bg-panel-2 text-slate-300"}`}>
              <div className="mb-0.5 font-mono text-[9px] uppercase tracking-wider text-slate-500">
                {m.role === "you" ? "you" : `the board${m.route && m.route !== "none" ? ` · via ${m.route}` : ""}`}
              </div>
              <p className="whitespace-pre-wrap">{m.text}</p>
            </div>
          ))}
          {busy && <div className="mr-8 rounded-lg border border-line bg-panel-2 p-2.5 font-mono text-xs text-slate-500">the board is deliberating<span className="cursor-blink">…</span></div>}
          <div ref={endRef} />
        </div>
      )}

      <div className="flex items-center gap-2">
        <input value={q} onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") send(q); }}
          placeholder='e.g. "Why did the fact checker flag the market claim?"'
          className="flex-1 rounded-lg border border-line bg-panel-2 px-3 py-2 text-sm outline-none focus:border-cyan/60" />
        <button onClick={() => send(q)} disabled={busy || q.trim().length < 3}
          className="flex items-center gap-1.5 rounded-lg bg-gradient-to-r from-brand to-cyan px-4 py-2 font-display text-xs font-bold text-ink transition enabled:hover:brightness-110 disabled:opacity-40">
          Ask <CornerDownLeft size={12} />
        </button>
      </div>
      <p className="mt-2 font-mono text-[9px] text-slate-600">
        Answers cite the agents and evidence of this run — questions beyond the record get an honest &quot;not in the record&quot;.
      </p>
    </section>
  );
}
