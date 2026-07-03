"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronDown, History } from "lucide-react";
import { getRun, listRuns, type RunSummary } from "@/lib/api";

const BAND_CLS: Record<string, string> = {
  GO: "text-ok border-ok/40",
  CONDITIONAL_GO: "text-warn border-warn/40",
  NO_GO: "text-err border-err/40",
};

type Detail = { verdict?: Record<string, unknown>; dimensions?: Record<string, number> };

export default function HistoryPage() {
  const [runs, setRuns] = useState<RunSummary[] | null>(null);
  const [open, setOpen] = useState<string | null>(null);
  const [details, setDetails] = useState<Record<string, Detail>>({});

  useEffect(() => {
    listRuns().then(setRuns);
  }, []);

  const toggle = async (id: string) => {
    if (open === id) return setOpen(null);
    setOpen(id);
    if (!details[id]) {
      const rec = await getRun(id);
      const state = (rec?.state ?? {}) as { verdict?: Record<string, unknown>; dimensions?: Record<string, number> };
      setDetails((d) => ({ ...d, [id]: { verdict: state.verdict, dimensions: state.dimensions } }));
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-6 py-8">
      <nav className="mb-8 flex items-center justify-between">
        <Link href="/" className="font-display text-lg font-bold">EIP<span className="text-cyan">.</span></Link>
        <Link href="/studio"
          className="rounded-lg border border-line px-4 py-2 font-mono text-xs uppercase tracking-wider text-slate-300 transition hover:border-cyan/60 hover:text-cyan">
          Open Studio →
        </Link>
      </nav>

      <h1 className="flex items-center gap-2 font-display text-2xl font-bold">
        <History size={20} className="text-cyan" /> Past decisions
      </h1>
      <p className="mt-1 text-sm text-slate-400">
        Every run is memory. Outcome tracking and the 3D Decision Graph land in Phase 5.
      </p>

      <div className="mt-6 space-y-2">
        {runs === null && <p className="font-mono text-xs text-slate-500">loading…</p>}
        {runs?.length === 0 && (
          <p className="rounded-xl border border-line bg-panel p-4 text-sm text-slate-500">
            No runs yet — convene your first board in the <Link className="text-cyan hover:underline" href="/studio">Studio</Link>.
          </p>
        )}
        {runs?.map((r) => {
          const d = details[r.id];
          const isOpen = open === r.id;
          return (
            <div key={r.id} className="rounded-xl border border-line bg-panel">
              <button onClick={() => toggle(r.id)} className="flex w-full items-center gap-3 p-4 text-left">
                <span className={`rounded border px-2 py-1 font-mono text-xs ${BAND_CLS[r.band] ?? "text-slate-400 border-line"}`}>
                  {r.score?.toFixed?.(1) ?? r.score}/10
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm text-slate-200">{r.situation}</span>
                  <span className="font-mono text-[10px] text-slate-500">
                    {new Date(r.created_at).toLocaleString()} · {r.mode} · {r.band?.replaceAll("_", " ")}
                  </span>
                </span>
                <ChevronDown size={14} className={`shrink-0 text-slate-600 transition ${isOpen ? "rotate-180" : ""}`} />
              </button>
              {isOpen && (
                <div className="border-t border-line p-4 text-xs leading-relaxed text-slate-300">
                  {!d && <span className="font-mono text-slate-500">loading…</span>}
                  {d?.verdict ? (
                    <>
                      <p>{String(d.verdict.reasoning ?? "")}</p>
                      <div className="mt-2 flex flex-wrap gap-1.5 font-mono text-[10px]">
                        {Object.entries((d.verdict.dimensions ?? {}) as Record<string, number>).map(([k, v]) => (
                          <span key={k} className="rounded border border-line bg-panel-2 px-1.5 py-0.5 text-slate-400">
                            {k} {v}
                          </span>
                        ))}
                      </div>
                    </>
                  ) : d ? (
                    <span className="font-mono text-slate-500">no verdict stored for this run</span>
                  ) : null}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
