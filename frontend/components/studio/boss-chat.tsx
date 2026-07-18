"use client";

/** 🎩 The Boss — Intelligent Mode's conversational intake.
 *
 * A real multi-turn dialogue (not a form) that distills into the structured
 * Brief. The Boss NEVER advises — it listens, clarifies and captures. Each turn
 * POSTs the whole transcript to /api/intake; the backend returns either the next
 * question or the finished brief. Stateless by design: keys are per-call,
 * nothing persists server-side.
 */

import { useEffect, useRef, useState } from "react";
import { bossIntake } from "@/lib/api";
import type { BossTurn, EngagementMode, EngineSelection } from "@/lib/types";

type Msg = { role: "user" | "assistant"; content: string };

const OPENING =
  "I'm the Boss — I'll run the intake, then hand your brief to the board. " +
  "Tell me the decision or problem you're actually wrestling with, the way you'd " +
  "tell a trusted advisor. No forms — just talk.";

const MODE_META: Record<Exclude<EngagementMode, "">, { label: string; desk: string }> = {
  founder: { label: "🚀 Founder", desk: "validate / build a venture" },
  trader: { label: "📈 Trader", desk: "evaluate a stock or position" },
  wealth: { label: "💰 Wealth", desk: "grow / protect personal money" },
  operator: { label: "⚙️ Operator", desk: "scale an existing company" },
};

export function BossChat({
  engine,
  onConversation,
  onBrief,
  onComplete,
}: {
  engine: EngineSelection;
  onConversation: (c: Msg[]) => void;
  onBrief: (b: Record<string, string>) => void;
  onComplete: (done: boolean) => void;
}) {
  const [messages, setMessages] = useState<Msg[]>([{ role: "assistant", content: OPENING }]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [turn, setTurn] = useState<BossTurn | null>(null);
  const [error, setError] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, busy]);

  const complete = turn?.complete ?? false;

  const send = async () => {
    const text = draft.trim();
    if (!text || busy || complete) return;
    setError("");
    const next: Msg[] = [...messages, { role: "user", content: text }];
    setMessages(next);
    setDraft("");
    setBusy(true);
    // only the client↔Boss exchanges are sent (drop the static opening line)
    const convo = next.filter((m, i) => !(i === 0 && m.role === "assistant"));
    try {
      const t = await bossIntake(convo, engine);
      setTurn(t);
      onConversation(convo);
      if (t.brief && Object.keys(t.brief).length) onBrief(t.brief);
      onComplete(t.complete);
      const reply = t.complete
        ? `Got it — I have enough. ${briefLine(t)} Handing the board your brief now. ` +
          "You can still adjust the depth and roster below before you convene."
        : t.question || "Tell me a little more.";
      setMessages((m) => [...m, { role: "assistant", content: reply }]);
    } catch {
      setError("The Boss couldn't reach a model — check the engine, or type your situation and convene directly.");
      onComplete(false);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="mt-4 rounded-2xl border border-brand/40 bg-panel p-5 shadow-[0_18px_44px_-22px_rgba(0,0,0,0.7),inset_0_1px_0_rgba(255,255,255,0.05)]">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="font-mono text-xs uppercase tracking-widest text-brand">
          01 · 🎩 Intake conversation
        </h2>
        {turn && (
          <span className="flex items-center gap-1.5 font-mono text-[10px] text-muted">
            {turn.engagement_mode && MODE_META[turn.engagement_mode] && (
              <span className="rounded border border-brand/40 bg-brand/10 px-1.5 py-0.5 text-brand">
                {MODE_META[turn.engagement_mode].label}
              </span>
            )}
            brief {Math.round((turn.completeness || 0) * 100)}% ·{" "}
            {complete ? <span className="text-ok">ready</span> : "in progress"}
            {turn.demo && <span className="ml-1 text-warn">· demo ladder</span>}
          </span>
        )}
      </div>

      {/* completeness meter */}
      <div className="mb-3 h-1 overflow-hidden rounded-full bg-panel-2">
        <div
          className="h-full bg-gradient-to-r from-brand to-cyan transition-all duration-500"
          style={{ width: `${Math.round((turn?.completeness ?? 0.05) * 100)}%` }}
        />
      </div>

      <div ref={scrollRef} className="max-h-72 space-y-2.5 overflow-y-auto pr-1">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`msg-in max-w-[85%] rounded-2xl px-3.5 py-2 text-sm leading-relaxed ${
                m.role === "user"
                  ? "rounded-br-sm bg-cyan/15 text-slate-100 shadow-[0_0_20px_-10px_rgba(34,211,238,0.5)]"
                  : "rounded-bl-sm border border-line bg-panel-2 text-slate-300"
              }`}
            >
              {m.role === "assistant" && <span className="mr-1">🎩</span>}
              {m.content}
            </div>
          </div>
        ))}
        {busy && (
          <div className="flex justify-start">
            <div className="msg-in rounded-2xl rounded-bl-sm border border-line bg-panel-2 px-3.5 py-2 text-sm text-muted">
              🎩 <span className="typing-dots ml-1"><span /><span /><span /></span>
            </div>
          </div>
        )}
      </div>

      {turn && !complete && turn.missing.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          <span className="font-mono text-[10px] text-slate-400">still capturing:</span>
          {turn.missing.slice(0, 5).map((m) => (
            <span key={m} className="rounded border border-line px-1.5 py-0.5 font-mono text-[10px] text-slate-400">
              {m}
            </span>
          ))}
        </div>
      )}

      {!complete && (
        <div className="mt-3 flex gap-2">
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), send())}
            disabled={busy}
            placeholder="type your answer… (Enter to send)"
            className="flex-1 rounded-md border border-line bg-panel-2 px-3 py-2 text-sm outline-none focus:border-brand/60 disabled:opacity-50"
          />
          <button
            onClick={send}
            disabled={busy || !draft.trim()}
            className="rounded-md bg-brand/90 px-4 py-2 font-mono text-xs font-semibold text-ink transition enabled:hover:brightness-110 disabled:opacity-70 disabled:saturate-[0.6]"
          >
            send
          </button>
        </div>
      )}

      {complete && turn && (
        <div className="mt-3 rounded-lg border border-ok/40 bg-ok/5 p-3">
          <div className="mb-1.5 flex flex-wrap items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-ok">
            ✓ brief captured — the 🎼 Manager will score the orchestra
            {turn.engagement_mode && MODE_META[turn.engagement_mode] && (
              <span className="rounded border border-brand/40 bg-brand/10 px-1.5 py-0.5 text-brand">
                detected focus: {MODE_META[turn.engagement_mode].label}
              </span>
            )}
          </div>
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(turn.brief)
              .filter(([, v]) => v)
              .slice(0, 8)
              .map(([k, v]) => (
                <span key={k} className="rounded border border-line bg-panel-2 px-2 py-0.5 font-mono text-[10px] text-slate-400">
                  <span className="text-slate-400">{k}:</span> {String(v).slice(0, 40)}
                </span>
              ))}
          </div>
        </div>
      )}

      {error && <p className="mt-2 font-mono text-[10px] text-err">{error}</p>}
      <p className="mt-3 font-mono text-[10px] leading-relaxed text-slate-400">
        The Boss listens and captures — it gives no advice. Once the brief is complete, the 🎼 Manager
        plans the board dynamically from the whole pool, a blocking QA gate checks every claim, and
        regulated content pauses for your review before the report publishes.
      </p>
    </section>
  );
}

function briefLine(t: BossTurn): string {
  const s = t.brief.situation || t.brief.industry || "";
  return s ? `The real ask: ${String(s).slice(0, 90)}.` : "";
}
