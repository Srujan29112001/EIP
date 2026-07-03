"use client";

import { useEffect, useRef } from "react";
import { agentById } from "@/lib/agents";
import { useRun } from "@/lib/store";
import type { LogKind } from "@/lib/types";

const KIND_CLS: Record<LogKind, string> = {
  info: "text-slate-300",
  code: "text-cyan/90",
  ok: "text-ok",
  err: "text-err",
  warn: "text-warn",
  muted: "text-slate-500",
};

export function Timeline() {
  const logs = useRun((s) => s.logs);
  const phase = useRun((s) => s.phase);
  const boxRef = useRef<HTMLDivElement>(null);

  // follow the log only while the user is already pinned near the bottom —
  // scrolling up to read must never be yanked away by the next SSE burst
  useEffect(() => {
    const box = boxRef.current;
    if (!box) return;
    const pinned = box.scrollHeight - box.scrollTop - box.clientHeight < 120;
    if (pinned) box.scrollTop = box.scrollHeight;
  }, [logs.length]);

  return (
    <div ref={boxRef}
      className="scroll-thin max-h-[70vh] overflow-y-auto rounded-xl border border-line bg-panel p-4 font-mono text-xs leading-relaxed">
      {logs.length === 0 && <div className="text-slate-500">waiting for the board…</div>}
      {logs.map((l, i) => {
        const a = agentById(l.agent);
        const prev = logs[i - 1];
        return (
          <div key={i}>
            {(!prev || prev.agent !== l.agent) && (
              <div className="mt-3 first:mt-0" style={{ color: a.accent }}>
                ── {a.name} {"─".repeat(Math.max(2, 40 - a.name.length))}
              </div>
            )}
            <div className={`pl-3 ${KIND_CLS[l.kind]}`}>{l.text}</div>
          </div>
        );
      })}
      {phase === "running" && <span className="cursor-blink pl-3 text-cyan">▊</span>}
    </div>
  );
}
