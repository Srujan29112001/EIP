"use client";

/** Pipeline v2 — Helix-grade stage cards. Every agent gets a card showing:
 * what went in, its live terminal log, the EXACT prompt it sent its model
 * (radical transparency), and what came out. Connector lines fill as data
 * flows down the pipeline.
 */

import { useEffect, useState } from "react";
import { AlertTriangle, Check, Eye, Loader2, X } from "lucide-react";
import { AGENTS, STAGE_IO, agentById } from "@/lib/agents";
import { useRun } from "@/lib/store";
import type { AgentOutput, LogKind, StageStatus } from "@/lib/types";

const KIND_CLS: Record<LogKind, string> = {
  info: "text-slate-300", code: "text-cyan/90", ok: "text-ok",
  err: "text-err", warn: "text-warn", muted: "text-slate-500",
};

function StatusBadge({ status, accent }: { status: StageStatus; accent: string }) {
  if (status === "active")
    return <span className="inline-flex shrink-0 items-center gap-1.5 rounded-full px-2 py-0.5 font-mono text-[9px]"
      style={{ color: accent, background: `${accent}24` }}><Loader2 size={11} className="animate-spin" /> running</span>;
  if (status === "done")
    return <span className="inline-flex shrink-0 items-center gap-1.5 rounded-full bg-ok/15 px-2 py-0.5 font-mono text-[9px] text-ok"><Check size={11} /> done</span>;
  if (status === "degraded")
    return <span title="ran on its deterministic core only — no LLM reached this agent"
      className="inline-flex shrink-0 items-center gap-1.5 rounded-full bg-warn/15 px-2 py-0.5 font-mono text-[9px] text-warn"><AlertTriangle size={11} /> reduced depth</span>;
  if (status === "error")
    return <span className="inline-flex shrink-0 items-center gap-1.5 rounded-full bg-err/15 px-2 py-0.5 font-mono text-[9px] text-err"><X size={11} /> error</span>;
  if (status === "skipped")
    return <span className="inline-flex shrink-0 items-center rounded-full bg-slate-800 px-2 py-0.5 font-mono text-[9px] text-slate-500">benched</span>;
  return <span className="inline-flex shrink-0 items-center rounded-full bg-slate-800/60 px-2 py-0.5 font-mono text-[9px] text-slate-500">queued</span>;
}

export function StageCards() {
  const { agentStatus, logs, prompts, agentOutputs, scope, brief } = useRun();
  const [openPrompt, setOpenPrompt] = useState<string | null>(null);

  const order = scope.length
    ? scope.filter((id) => id !== "scope_planner")
    : AGENTS.map((a) => a.id);
  const cards = ["intake_parser", "context_profiler", "scope_planner",
    ...order.filter((id) => !["intake_parser", "context_profiler", "scope_planner"].includes(id))]
    .filter((id, i, arr) => arr.indexOf(id) === i)
    .filter((id) => agentStatus[id] || logs.some((l) => l.agent === id));

  const logsByAgent = logs.reduce<Record<string, typeof logs>>((acc, l) => {
    (acc[l.agent] ||= [] as typeof logs).push(l);
    return acc;
  }, {});

  if (!cards.length) {
    return <div className="glass card-in rounded-2xl p-5 font-mono text-xs text-slate-500">waiting for the board…</div>;
  }

  return (
    <div className="space-y-3 pb-4">
      {/* input chips — what the whole run started from */}
      {brief && (
        <div className="rounded-xl border border-brand/30 bg-brand/5 p-3">
          <div className="mb-1.5 font-mono text-[10px] uppercase tracking-widest text-slate-500">input</div>
          <div className="flex flex-wrap gap-1.5 text-xs">
            {Object.entries(brief).filter(([k, v]) => v && k !== "keywords").map(([k, v]) => (
              <span key={k} className="rounded-lg border border-line bg-panel-2 px-2 py-0.5">
                <span className="font-mono text-[9px] uppercase text-slate-500">{k}: </span>
                <span className="text-slate-300">{String(v).slice(0, 60)}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {cards.map((id, idx) => {
        const a = agentById(id);
        const st = agentStatus[id] ?? "queued";
        const alogs = logsByAgent[id] ?? [];
        const out = agentOutputs[id] as AgentOutput | undefined;
        const io = STAGE_IO[id];
        const prompt = prompts[id];
        const done = st === "done";
        return (
          <div key={id} id={`stage-${id}`} className="relative scroll-mt-4 pl-12">
            {/* connector line that fills as the stage completes */}
            {idx < cards.length - 1 && (
              <div className="absolute bottom-[-12px] left-[19px] top-12 w-px bg-white/10">
                <div className="w-full transition-[height] duration-700 ease-out"
                  style={{ height: done ? "100%" : "0%", background: `linear-gradient(${a.accent}, ${a.accent}22)` }} />
              </div>
            )}
            {/* icon dot */}
            <span className="absolute left-1.5 top-1.5 grid h-9 w-9 place-items-center rounded-xl border"
              style={{ borderColor: `${a.accent}${st === "queued" ? "26" : "80"}`,
                background: `${a.accent}${st === "queued" ? "0a" : "24"}`,
                boxShadow: st === "active" ? `0 0 20px -2px ${a.accent}e0` : "none" }}>
              <span className="h-2 w-2 rounded-full" style={{ background: a.accent }} />
            </span>

            <div className={`card-in rounded-xl border bg-panel/80 p-3 backdrop-blur-sm transition ${
              st === "active" ? "border-cyan/40 shadow-[0_0_28px_-10px_rgba(34,211,238,0.5)]" : "border-line"}`}>
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-[9px] text-slate-600">{String(idx + 1).padStart(2, "0")}</span>
                <span className="text-sm font-semibold" style={{ color: st === "queued" ? "#64748b" : a.accent }}>{a.name}</span>
                <span className="font-mono text-[9px] uppercase tracking-wider text-slate-600">{a.layer} · {a.cluster}</span>
                <span className="ml-auto"><StatusBadge status={st} accent={a.accent} /></span>
              </div>

              {io && (
                <div className="mt-1.5 flex flex-wrap gap-1.5 font-mono text-[10px]">
                  <span className="rounded border border-line bg-panel-2 px-1.5 py-0.5 text-slate-500">in → {io.in}</span>
                  <span className="rounded border border-line bg-panel-2 px-1.5 py-0.5 text-slate-500">out → {io.out}</span>
                </div>
              )}

              {alogs.length > 0 && (
                <div className="mt-2 max-h-40 overflow-y-auto rounded-lg bg-ink/70 p-2.5 font-mono text-[11px] leading-relaxed [overflow-wrap:anywhere]">
                  {alogs.map((l, i) => (
                    <div key={i} className={KIND_CLS[l.kind]}>{l.text}</div>
                  ))}
                </div>
              )}

              {prompt && (
                <div className="mt-2">
                  <button onClick={() => setOpenPrompt(id)}
                    className="flex items-center gap-1.5 rounded-lg border border-transparent px-1.5 py-0.5 font-mono text-[10px] text-slate-500 transition hover:border-cyan/30 hover:text-cyan">
                    <Eye size={11} /> view exact prompt
                  </button>
                </div>
              )}

              {out?.verdict_line && (
                <div className="mt-2 rounded-lg border px-2.5 py-1.5 text-xs"
                  style={{ borderColor: `${a.accent}40`, background: `${a.accent}0d` }}>
                  <span className="font-mono text-[9px] uppercase tracking-wider text-slate-500">output › </span>
                  <span className="text-slate-200">{out.verdict_line}</span>
                  {typeof out.score === "number" && (
                    <span className="ml-2 font-mono text-[10px]" style={{ color: a.accent }}>{out.score}/10</span>
                  )}
                </div>
              )}
            </div>
          </div>
        );
      })}

      {/* ── the transparency dialog — the EXACT prompt, in a glass modal ── */}
      {openPrompt && prompts[openPrompt] && (
        <PromptDialog
          agentName={agentById(openPrompt).name}
          accent={agentById(openPrompt).accent}
          prompt={prompts[openPrompt]}
          onClose={() => setOpenPrompt(null)}
        />
      )}
    </div>
  );
}

function PromptDialog({ agentName, accent, prompt, onClose }: {
  agentName: string; accent: string;
  prompt: { system: string; user: string };
  onClose: () => void;
}) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [onClose]);
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog" aria-modal="true" aria-label={`Exact prompt — ${agentName}`}>
      <div className="absolute inset-0 bg-ink/70 backdrop-blur-sm" onClick={onClose} />
      <div className="g-border card-in relative flex max-h-[82vh] w-full max-w-3xl flex-col rounded-2xl">
        <div className="flex items-center gap-2.5 border-b border-line px-5 py-3.5">
          <span className="h-2 w-2 rounded-full" style={{ background: accent, boxShadow: `0 0 10px ${accent}` }} />
          <span className="font-hero text-sm font-bold text-slate-100">{agentName}</span>
          <span className="font-mono text-[10px] uppercase tracking-widest text-slate-500">the exact prompt it sent</span>
          <button onClick={onClose}
            className="ml-auto rounded-lg px-2 py-1 font-mono text-xs text-slate-500 transition hover:text-err">
            ✕ esc
          </button>
        </div>
        <div className="scroll-thin space-y-3 overflow-y-auto p-5 font-mono text-[11px] leading-relaxed">
          <div className="rounded-xl border border-brand/25 bg-brand/5 p-3">
            <div className="mb-1 font-mono text-[9px] uppercase tracking-widest text-brand">system ›</div>
            <p className="whitespace-pre-wrap text-slate-300">{prompt.system}</p>
          </div>
          <div className="rounded-xl border border-cyan/25 bg-cyan/5 p-3">
            <div className="mb-1 font-mono text-[9px] uppercase tracking-widest text-cyan">user ›</div>
            <p className="whitespace-pre-wrap text-slate-300">{prompt.user}</p>
          </div>
        </div>
        <p className="border-t border-line px-5 py-2.5 font-mono text-[9px] text-slate-600">
          radical transparency — this is verbatim what the model received, nothing hidden.
        </p>
      </div>
    </div>
  );
}
