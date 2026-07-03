"use client";

import { useEffect, useRef, useState } from "react";
import { consumeRun, backendHealth, type EngineStatus } from "@/lib/api";
import { useRun } from "@/lib/store";
import type { IntakeForm } from "@/lib/types";
import { Boardroom } from "./boardroom";
import { DecisionRoom } from "./decision-room";
import { IntakeWizard } from "./intake-wizard";
import { PipelineRail } from "./pipeline-rail";
import { Timeline } from "./timeline";

type Tab = "pipeline" | "boardroom" | "results";

export function StudioClient() {
  const { phase, begin, apply, reset, fatal, verdict } = useRun();
  const [tab, setTab] = useState<Tab>("pipeline");
  const [backend, setBackend] = useState<"checking" | "live" | "offline">("checking");
  const [engine, setEngine] = useState<EngineStatus | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    backendHealth()
      .then((h) => {
        setBackend(h.ok ? "live" : "offline");
        setEngine(h.engine ?? null);
      })
      .catch(() => setBackend("offline"));
    return () => abortRef.current?.abort();
  }, []);

  // auto-switch to results when the verdict lands
  useEffect(() => {
    if (verdict && phase === "done") setTab("results");
  }, [verdict, phase]);

  const start = async (form: IntakeForm) => {
    begin();
    setTab("pipeline");
    abortRef.current = new AbortController();
    try {
      await consumeRun(form, apply, abortRef.current.signal);
    } catch {
      useRun.getState().apply({ type: "fatal", message: "Backend unreachable — is uvicorn running on :8000?" });
    }
  };

  if (phase === "intake") {
    return (
      <>
        <BackendBadge state={backend} />
        <IntakeWizard onRun={start} engine={engine} />
      </>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-6">
      <BackendBadge state={backend} />
      <div className="grid gap-4 lg:grid-cols-[300px_1fr]">
        <PipelineRail />
        <main>
          <div className="mb-3 flex items-center gap-1 rounded-lg border border-line bg-panel p-1">
            {(["pipeline", "boardroom", "results"] as const).map((t) => (
              <button key={t} onClick={() => setTab(t)}
                className={`rounded-md px-4 py-1.5 font-mono text-xs uppercase tracking-wider transition ${
                  tab === t ? "bg-panel-2 text-cyan" : "text-slate-500 hover:text-slate-300"}`}>
                {t}
              </button>
            ))}
            <button onClick={() => { abortRef.current?.abort(); reset(); }}
              className="ml-auto rounded-md px-3 py-1.5 font-mono text-xs text-slate-500 hover:text-err">
              ✕ new run
            </button>
          </div>
          {fatal && (
            <div className="mb-3 rounded-lg border border-err/40 bg-err/10 p-3 text-sm text-err">{fatal}</div>
          )}
          {tab === "pipeline" && <Timeline />}
          {tab === "boardroom" && <Boardroom />}
          {tab === "results" && <DecisionRoom />}
        </main>
      </div>
    </div>
  );
}

function BackendBadge({ state }: { state: "checking" | "live" | "offline" }) {
  const cfg = {
    checking: ["bg-slate-600", "checking backend…"],
    live: ["bg-ok", "backend live"],
    offline: ["bg-warn", "backend offline — start uvicorn :8000"],
  }[state];
  return (
    <div className="mx-auto flex max-w-7xl items-center gap-2 px-6 pt-4 font-mono text-[10px] uppercase tracking-wider text-slate-500">
      <span className={`h-1.5 w-1.5 rounded-full ${cfg[0]}`} /> {cfg[1]}
    </div>
  );
}
