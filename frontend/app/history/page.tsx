"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ChevronDown, History, Target } from "lucide-react";
import {
  getMe, getRun, getTrackRecord, listRuns, recordOutcome,
  type Me, type RunOutcome, type RunSummary, type TrackRecord,
} from "@/lib/api";

const BAND_CLS: Record<string, string> = {
  GO: "text-ok border-ok/40",
  CONDITIONAL_GO: "text-warn border-warn/40",
  NO_GO: "text-err border-err/40",
};

const STATUS_CLS: Record<string, string> = {
  good: "text-ok border-ok/40 bg-ok/10",
  mixed: "text-warn border-warn/40 bg-warn/10",
  bad: "text-err border-err/40 bg-err/10",
  too_early: "text-slate-400 border-line bg-panel-2",
};

const DECISIONS = ["proceeded", "declined", "modified", "pending"];
const STATUSES = ["good", "mixed", "bad", "too_early"];

type Detail = { verdict?: Record<string, unknown>; dimensions?: Record<string, number> };

export default function HistoryPage() {
  const [runs, setRuns] = useState<RunSummary[] | null>(null);
  const [open, setOpen] = useState<string | null>(null);
  const [details, setDetails] = useState<Record<string, Detail>>({});
  const [track, setTrack] = useState<TrackRecord | null>(null);
  const [me, setMe] = useState<Me | null>(null);

  const refresh = () => { listRuns().then(setRuns); getTrackRecord().then(setTrack); getMe().then(setMe); };
  useEffect(() => { refresh(); }, []);

  const toggle = async (id: string) => {
    if (open === id) return setOpen(null);
    setOpen(id);
    if (!details[id]) {
      const rec = await getRun(id);
      const state = (rec?.state ?? {}) as { verdict?: Record<string, unknown>; dimensions?: Record<string, number> };
      setDetails((d) => ({ ...d, [id]: { verdict: state.verdict, dimensions: state.dimensions } }));
    }
  };

  const saveOutcome = async (id: string, o: RunOutcome) => {
    await recordOutcome(id, o);
    refresh();
  };

  return (
    <div className="mx-auto max-w-3xl px-6 py-8">
      <nav className="mb-8 flex items-center justify-between">
        <Link href="/" className="font-display text-lg font-bold">EIP<span className="text-cyan">.</span></Link>
        <div className="flex items-center gap-2">
          {me && (
            <span className="rounded-lg border border-line px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-wider text-slate-400">
              {me.tier_info?.label ?? me.tier} · {me.runs ?? 0} runs
            </span>
          )}
          <Link href="/studio"
            className="rounded-lg border border-line px-4 py-2 font-mono text-xs uppercase tracking-wider text-slate-300 transition hover:border-cyan/60 hover:text-cyan">
            Open Studio →
          </Link>
        </div>
      </nav>

      <h1 className="flex items-center gap-2 font-display text-2xl font-bold">
        <History size={20} className="text-cyan" /> Past decisions
      </h1>
      <p className="mt-1 text-sm text-slate-400">
        Every run is memory. Record what you actually did and how it turned out — the board grades its own calibration.
      </p>

      {/* track record — the platform's own calibration scorecard */}
      {track && track.tracked > 0 && (
        <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="rounded-xl border border-line bg-panel p-3">
            <div className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-widest text-muted">
              <Target size={11} /> GO hit-rate
            </div>
            <div className="mt-1 font-display text-2xl font-bold text-ok">
              {track.go_hit_rate === null ? "—" : `${Math.round(track.go_hit_rate * 100)}%`}
            </div>
            <div className="font-mono text-[9px] text-slate-500">of {track.go_count} GO verdicts</div>
          </div>
          {["good", "mixed", "bad"].map((s) => (
            <div key={s} className="rounded-xl border border-line bg-panel p-3">
              <div className="font-mono text-[10px] uppercase tracking-widest text-muted">{s}</div>
              <div className="mt-1 font-display text-2xl font-bold text-slate-200">{track.by_status?.[s] ?? 0}</div>
              <div className="font-mono text-[9px] text-slate-500">outcomes</div>
            </div>
          ))}
        </div>
      )}

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
                {r.outcome && (
                  <span className={`shrink-0 rounded border px-1.5 py-0.5 font-mono text-[9px] uppercase ${STATUS_CLS[r.outcome.status] ?? ""}`}>
                    {r.outcome.status?.replace("_", " ")}
                  </span>
                )}
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

                  {/* outcome recorder */}
                  <OutcomeRecorder id={r.id} current={r.outcome} onSave={saveOutcome} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function OutcomeRecorder({ id, current, onSave }: {
  id: string;
  current?: RunOutcome | null;
  onSave: (id: string, o: RunOutcome) => void;
}) {
  const [decision, setDecision] = useState(current?.decision ?? "pending");
  const [status, setStatus] = useState(current?.status ?? "too_early");
  const [note, setNote] = useState(current?.note ?? "");
  const [saved, setSaved] = useState(false);

  return (
    <div className="mt-4 rounded-lg border border-line bg-panel-2 p-3">
      <div className="mb-2 flex items-center gap-2 font-mono text-[10px] uppercase tracking-widest text-muted">
        <Target size={11} /> record the outcome
      </div>
      <div className="flex flex-wrap gap-3">
        <label className="flex flex-col gap-1">
          <span className="font-mono text-[9px] uppercase text-slate-500">what you did</span>
          <select value={decision} onChange={(e) => setDecision(e.target.value)}
            className="rounded border border-line bg-panel px-2 py-1 text-xs text-slate-200">
            {DECISIONS.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
        </label>
        <label className="flex flex-col gap-1">
          <span className="font-mono text-[9px] uppercase text-slate-500">how it went</span>
          <select value={status} onChange={(e) => setStatus(e.target.value)}
            className="rounded border border-line bg-panel px-2 py-1 text-xs text-slate-200">
            {STATUSES.map((s) => <option key={s} value={s}>{s.replace("_", " ")}</option>)}
          </select>
        </label>
        <label className="flex flex-1 flex-col gap-1">
          <span className="font-mono text-[9px] uppercase text-slate-500">note (optional)</span>
          <input value={note} onChange={(e) => setNote(e.target.value)}
            placeholder="what actually happened…"
            className="rounded border border-line bg-panel px-2 py-1 text-xs text-slate-200 placeholder:text-slate-600" />
        </label>
      </div>
      <button
        onClick={() => { onSave(id, { decision, status, note }); setSaved(true); setTimeout(() => setSaved(false), 2000); }}
        className="mt-3 rounded-lg bg-gradient-to-r from-brand to-cyan px-4 py-1.5 font-mono text-[11px] font-bold text-ink transition hover:brightness-110">
        {saved ? "saved ✓" : "save outcome"}
      </button>
    </div>
  );
}
