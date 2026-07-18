"use client";

/** Intelligent Mode live surfaces — the Advisory Engine's four visible brains:
 *   ManagerPlanPanel — 🎼 the dynamic routing plan (picks / benches / locked spine)
 *   QaGatePanel      — ✅ the blocking accuracy gate, pass/fail + issues + re-dispatch
 *   HitlBanner       — 🧑‍⚖️ the human review gate for regulated content (approve/reject)
 */

import { useState } from "react";
import { reviewDecision } from "@/lib/api";
import { agentById } from "@/lib/agents";
import { useRun } from "@/lib/store";

function chip(id: string) {
  const a = agentById(id);
  return (
    <span key={id} className="inline-flex items-center gap-1 rounded border border-line bg-panel-2 px-1.5 py-0.5 font-mono text-[10px] text-slate-300">
      <span>{a.icon}</span> {a.name}
    </span>
  );
}

/** 🎼 The Manager's routing plan — how the board was chosen for THIS brief. */
export function ManagerPlanPanel() {
  const plan = useRun((s) => s.managerPlan);
  if (!plan) return null;
  return (
    <div className="rounded-xl border border-brand/40 bg-gradient-to-b from-brand/5 to-panel p-4">
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <span className="text-lg">🎼</span>
        <h3 className="font-display text-sm font-bold text-slate-100">Manager&apos;s plan</h3>
        {plan.mode_label && (
          <span className="rounded border border-brand/40 bg-brand/10 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-wider text-brand">
            {plan.mode_label} engagement
          </span>
        )}
        {plan.regulated && (
          <span className="rounded border border-err/40 bg-err/10 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-wider text-err">
            regulated · human review
          </span>
        )}
        <span className="ml-auto font-mono text-[9px] text-slate-600">{plan.route}</span>
      </div>
      {plan.focus && <p className="mb-3 text-xs leading-relaxed text-slate-400">{plan.focus}</p>}
      <div className="grid gap-3 sm:grid-cols-2">
        {plan.picks.length > 0 && (
          <div>
            <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-ok">
              ＋ routed in for this brief
            </div>
            <div className="space-y-1">
              {plan.picks.map((p) => (
                <div key={p.id} className="text-[11px] text-slate-400">
                  {chip(p.id)} <span className="text-slate-500">{p.reason}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        {plan.drops.length > 0 && (
          <div>
            <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-slate-500">
              － benched (not needed here)
            </div>
            <div className="space-y-1">
              {plan.drops.map((d) => (
                <div key={d.id} className="text-[11px] text-slate-500">
                  {chip(d.id)} <span className="text-slate-600">{d.reason}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      {plan.spine_locked.length > 0 && (
        <div className="mt-3 border-t border-line pt-2">
          <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-slate-500">
            🔒 guaranteed spine — the Manager can never drop these
          </div>
          <div className="flex flex-wrap gap-1">{plan.spine_locked.map(chip)}</div>
        </div>
      )}
    </div>
  );
}

/** ✅ The blocking QA gate — its verdict per round, with the issues it caught. */
export function QaGatePanel() {
  const qa = useRun((s) => s.qa);
  if (!qa.length) return null;
  // collapse to the LATEST status per round (started → passed/failed)
  const byRound = new Map<number, (typeof qa)[number]>();
  for (const e of qa) byRound.set(e.round, e);
  const rounds = [...byRound.values()].filter((e) => e.status !== "started");
  if (!rounds.length) {
    return (
      <div className="glass card-in rounded-2xl p-3 font-mono text-xs text-muted">
        ✅ QA gate running — fact traces, red-team severity, framing bias, verdict integrity…
      </div>
    );
  }
  return (
    <div className="glass card-in rounded-2xl p-4">
      <div className="mb-2 flex items-center gap-2">
        <span className="text-lg">✅</span>
        <h3 className="font-display text-sm font-bold text-slate-100">QA gate</h3>
        <span className="font-mono text-[9px] text-slate-600">blocks the report until the board is clean</span>
      </div>
      <div className="space-y-2.5">
        {rounds.map((e) => (
          <div key={e.round}>
            <div className="mb-1 flex items-center gap-2">
              <span className="font-mono text-[10px] uppercase tracking-wider text-slate-500">
                round {e.round}
              </span>
              <span
                className={`rounded px-1.5 py-0.5 font-mono text-[9px] font-semibold uppercase tracking-wider ${
                  e.status === "passed" ? "bg-ok/15 text-ok" : "bg-err/15 text-err"
                }`}
              >
                {e.status === "passed" ? "✓ passed" : "✕ failed — re-dispatched"}
              </span>
              {e.issues.length > 0 && (
                <span className="font-mono text-[10px] text-slate-600">
                  {e.issues.length} issue{e.issues.length > 1 ? "s" : ""}
                </span>
              )}
            </div>
            {e.issues.length > 0 && (
              <div className="space-y-1 pl-2">
                {e.issues.slice(0, 6).map((iss, i) => (
                  <div key={i} className="flex items-start gap-1.5 text-[11px] leading-snug">
                    <span
                      className={`mt-0.5 shrink-0 rounded px-1 font-mono text-[8px] uppercase ${
                        iss.severity >= 0.9
                          ? "bg-err/20 text-err"
                          : iss.severity >= 0.75
                          ? "bg-warn/20 text-warn"
                          : "bg-panel-2 text-slate-500"
                      }`}
                    >
                      {iss.kind}
                    </span>
                    <span className="text-slate-400">
                      {iss.agent && <span className="text-slate-600">[{agentById(iss.agent).name}] </span>}
                      {iss.note}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/** 🌟 Above & Beyond — "you didn't ask, but you should know" (the conversation's
 * mechanism: Trends + Connecting Dots + the Coverage Auditor, in every deliverable). */
export function AboveBeyondPanel() {
  const beyond = useRun((s) => s.beyond);
  if (!beyond.length) return null;
  return (
    <div className="rounded-xl border border-brand/50 bg-gradient-to-b from-brand/10 to-panel p-4">
      <div className="mb-2 flex items-center gap-2">
        <span className="text-lg">🌟</span>
        <h3 className="font-display text-sm font-bold text-slate-100">
          You didn&apos;t ask, but you should know
        </h3>
        <span className="font-mono text-[9px] uppercase tracking-wider text-slate-500">
          above &amp; beyond · trends + connecting dots + coverage auditor
        </span>
      </div>
      <div className="space-y-2">
        {beyond.map((b, i) => (
          <div key={i} className="rounded-lg border border-line bg-panel-2 p-2.5">
            <div className="text-[13px] leading-snug text-slate-200">{b.insight}</div>
            <div className="mt-1 flex flex-wrap items-center gap-2 font-mono text-[10px]">
              <span className="text-slate-500">why it matters: <span className="text-slate-400">{b.why}</span></span>
              {b.source && (
                <span className="ml-auto rounded border border-line px-1.5 py-0.5 text-slate-500">
                  {agentById(b.source).icon} {agentById(b.source).name}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/** ⚡ The Manager's rulings — conflicts weighed, stressed, then decided on the record. */
export function RulingsPanel() {
  const rulings = useRun((s) => s.rulings);
  if (!rulings.length) return null;
  return (
    <div className="glass card-in rounded-2xl p-4">
      <div className="mb-2 flex items-center gap-2">
        <span className="text-lg">⚡</span>
        <h3 className="font-display text-sm font-bold text-slate-100">The Manager&apos;s rulings</h3>
        <span className="font-mono text-[9px] uppercase tracking-wider text-slate-500">
          conflicts → weighed · stressed by the crucible · decided on the record
        </span>
      </div>
      <div className="space-y-2">
        {rulings.map((r, i) => (
          <div key={i} className="rounded-lg border border-line bg-panel-2 p-2.5">
            <div className="font-mono text-[10px] uppercase tracking-wider text-warn">⚔ {r.topic}</div>
            <div className="mt-1 text-[13px] leading-snug text-slate-200">🎼 {r.ruling}</div>
            <div className="mt-0.5 text-[11px] leading-snug text-slate-500">{r.rationale}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

/** 🧑‍⚖️ The human-in-the-loop review gate for regulated content. */
export function HitlBanner() {
  const hitl = useRun((s) => s.hitl);
  const runId = useRun((s) => s.runId);
  const [sent, setSent] = useState<"approve" | "reject" | null>(null);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);

  if (!hitl) return null;

  const decide = async (decision: "approve" | "reject") => {
    if (!runId || busy) return;
    setBusy(true);
    const ok = await reviewDecision(runId, decision, note);
    if (ok) setSent(decision);
    setBusy(false);
  };

  if (hitl.status === "resumed") {
    const d = hitl.decision;
    const tone =
      d === "approve" || d === "auto_approved"
        ? ["border-ok/40 bg-ok/10 text-ok", "✓ approved — deliverable published"]
        : d === "reject"
        ? ["border-err/40 bg-err/10 text-err", "✕ rejected — report withheld"]
        : ["border-warn/40 bg-warn/10 text-warn", "⧗ review window lapsed — published marked UNREVIEWED"];
    return (
      <div className={`rounded-xl border p-3 font-mono text-xs ${tone[0]}`}>
        🧑‍⚖️ Human review {tone[1]}
        {hitl.note && <span className="ml-1 text-slate-400">· “{hitl.note}”</span>}
      </div>
    );
  }

  // status === "pause" — awaiting the reviewer
  return (
    <div className="glow-active rounded-xl border-2 border-err/60 bg-gradient-to-b from-err/10 to-panel p-4">
      <div className="mb-1.5 flex items-center gap-2">
        <span className="text-lg">🧑‍⚖️</span>
        <h3 className="font-display text-sm font-bold text-slate-100">Human review required</h3>
        <span className="rounded border border-err/40 bg-err/10 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-wider text-err">
          paused
        </span>
      </div>
      <p className="mb-2 text-xs leading-relaxed text-slate-300">{hitl.reason}</p>
      {hitl.sections.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-1">
          <span className="font-mono text-[10px] text-slate-500">regulated by:</span>
          {hitl.sections.map(chip)}
        </div>
      )}
      {sent ? (
        <div className="font-mono text-[11px] text-slate-400">
          decision sent: <span className={sent === "approve" ? "text-ok" : "text-err"}>{sent}</span> —
          the pipeline is resuming.
        </div>
      ) : (
        <div className="space-y-2">
          <input
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="reviewer note (optional — recorded in the audit trail)"
            className="w-full rounded-md border border-line bg-panel-2 px-2.5 py-1.5 text-xs outline-none focus:border-err/60"
          />
          <div className="flex gap-2">
            <button
              onClick={() => decide("approve")}
              disabled={busy}
              className="rounded-md bg-ok/90 px-4 py-1.5 font-mono text-xs font-semibold text-ink transition enabled:hover:brightness-110 disabled:opacity-40"
            >
              ✓ approve &amp; publish
            </button>
            <button
              onClick={() => decide("reject")}
              disabled={busy}
              className="rounded-md border border-err/50 bg-err/10 px-4 py-1.5 font-mono text-xs font-semibold text-err transition enabled:hover:bg-err/20 disabled:opacity-40"
            >
              ✕ reject &amp; withhold
            </button>
          </div>
          <p className="font-mono text-[10px] leading-relaxed text-slate-600">
            Decision-support, not licensed advice. If you don&apos;t decide in time, the board publishes
            the deliverable marked UNREVIEWED, with the disclaimer attached.
          </p>
        </div>
      )}
    </div>
  );
}
