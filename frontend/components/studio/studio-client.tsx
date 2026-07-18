"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { consumeRun, backendHealth, type EngineStatus } from "@/lib/api";
import { useRun } from "@/lib/store";
import type { IntakeForm } from "@/lib/types";
import { Boardroom } from "./boardroom";
import { DecisionRoom } from "./decision-room";
import { FlowMap } from "./flow-map";
import { HitlBanner, ManagerPlanPanel, QaGatePanel, RulingsPanel } from "./intelligent-panels";
import { MissionHud } from "./mission-hud";
import { OrchestraView } from "./orchestra-view";
import { IntakeWizard } from "./intake-wizard";
import { PipelineRail } from "./pipeline-rail";
import { StageCards } from "./stage-cards";

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
        <StudioNav state={backend} />
        <IntakeWizard onRun={start} engine={engine} />
      </>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 pb-6">
      <StudioNav state={backend} />
      <div className="grid gap-4 lg:grid-cols-[300px_1fr]">
        <PipelineRail />
        <main className="min-w-0">
          <div className="glass mb-3 flex items-center gap-1 rounded-xl p-1">
            {(["pipeline", "boardroom", "results"] as const).map((t) => (
              <button key={t} onClick={() => setTab(t)}
                className={`rounded-lg px-3 py-1.5 font-mono text-xs uppercase tracking-wider transition sm:px-4 ${
                  tab === t
                    ? "bg-panel-2 text-cyan shadow-[0_0_18px_-6px_rgba(34,211,238,0.55),inset_0_1px_0_rgba(255,255,255,0.06)]"
                    : "text-slate-400 hover:-translate-y-px hover:text-slate-300"}`}>
                {t}
              </button>
            ))}
            <button onClick={() => { abortRef.current?.abort(); reset(); }}
              className="ml-auto rounded-md px-3 py-1.5 font-mono text-xs text-slate-400 hover:text-err">
              ✕ new run
            </button>
          </div>
          {fatal && (
            <div className="mb-3 rounded-lg border border-err/40 bg-err/10 p-3 text-sm text-err">{fatal}</div>
          )}
          {/* the human-review gate is a blocking action — always visible, any tab */}
          <div className="mb-3 space-y-3 empty:mb-0">
            <HitlBanner />
          </div>
          {tab === "pipeline" && (
            <div className="space-y-3">
              {/* the control room — live completion ring, layer conveyor, mission clock */}
              <MissionHud />
              {/* Intelligent Mode = the Orchestra: the Manager's task graph with every
                  player expanding to its junior instruments lighting up (null otherwise) */}
              <OrchestraView />
              {/* Mode-aware Intelligent runs: the Manager's plan + the blocking QA gate */}
              <ManagerPlanPanel />
              <QaGatePanel />
              <RulingsPanel />
              {/* the living workflow tree — click any agent to jump to its full card */}
              <FlowMap onFocus={(id) =>
                document.getElementById(`stage-${id}`)?.scrollIntoView({ behavior: "smooth", block: "start" })} />
              <StageCards />
            </div>
          )}
          {tab === "boardroom" && <Boardroom />}
          {tab === "results" && <DecisionRoom />}
        </main>
      </div>
    </div>
  );
}

/** The studio's top navigation — home, studio, graph, history + live backend dot.
 *  Present on every studio view (intake AND the run screens). */
function StudioNav({ state }: { state: "checking" | "live" | "offline" }) {
  const cfg = {
    checking: ["bg-slate-600", "checking backend…"],
    live: ["bg-ok", "backend live"],
    offline: ["bg-warn", "backend offline — start uvicorn :8000"],
  }[state];
  return (
    <nav className="sticky top-0 z-40 border-b border-line bg-panel">
      <div className="mx-auto flex max-w-7xl items-center gap-1 px-4 py-2.5">
        <Link href="/" className="mr-2 font-display text-base font-bold tracking-tight text-slate-100 transition hover:text-cyan">
          EIP<span className="text-cyan">.</span>
        </Link>
        <Link href="/" className="rounded-lg px-3 py-1.5 font-mono text-[11px] uppercase tracking-wider text-slate-400 transition hover:bg-panel-2 hover:text-slate-100">
          Home
        </Link>
        <span className="rounded-lg bg-panel-2 px-3 py-1.5 font-mono text-[11px] uppercase tracking-wider text-cyan">
          Studio
        </span>
        <Link href="/graph" className="rounded-lg px-3 py-1.5 font-mono text-[11px] uppercase tracking-wider text-slate-400 transition hover:bg-panel-2 hover:text-slate-100">
          Graph
        </Link>
        <Link href="/history" className="rounded-lg px-3 py-1.5 font-mono text-[11px] uppercase tracking-wider text-slate-400 transition hover:bg-panel-2 hover:text-slate-100">
          History
        </Link>
        <span className="ml-auto flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-slate-400">
          <span className={`h-1.5 w-1.5 rounded-full ${cfg[0]} ${state === "live" ? "pulse-ring" : ""}`}
            style={state === "live" ? ({ "--ring": "#34d399" } as React.CSSProperties) : undefined} /> {cfg[1]}
        </span>
      </div>
    </nav>
  );
}
