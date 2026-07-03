"use client";

import { useState } from "react";
import { SlidersHorizontal } from "lucide-react";
import { useRun } from "@/lib/store";

const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));

/** What-If simulator — re-runs the finance modeler's deterministic core live on
 * the client. Same math as the backend (runway → Economics → weighted overall),
 * clearly labelled directional: it moves one dimension, not the whole board. */
export function WhatIf() {
  const core = useRun((s) => s.financeCore);
  const verdict = useRun((s) => s.verdict);
  const [capital, setCapital] = useState<number | null>(null);
  const [burn, setBurn] = useState<number | null>(null);

  if (!core || !verdict?.dimensions) return null;
  const dims = verdict.dimensions;

  const cap = capital ?? core.capital_lakhs;
  const b = burn ?? core.burn_lakhs_pm;
  const runway = b > 0 ? cap / b : 99;

  // mirror of backend math: raw econ score, preserving the red-team penalty delta
  const baseRaw = clamp(core.runway_months / 3.0, 1.0, 9.0);
  const penalty = baseRaw - (dims.Economics ?? baseRaw);
  const newEcon = clamp(clamp(runway / 3.0, 1.0, 9.0) - penalty, 0.5, 10);
  // weights mirror backend weighing_engine (6-dim when Regulatory present, else 5-dim)
  const weights: Record<string, number> = "Regulatory" in dims
    ? { Market: 0.25, Economics: 0.25, Regulatory: 0.125, Evidence: 0.10, Execution: 0.125, Timing: 0.15 }
    : { Market: 0.3, Economics: 0.3, Evidence: 0.15, Execution: 0.125, Timing: 0.125 };
  const overall = Object.entries(weights).reduce(
    (sum, [k, w]) => sum + (k === "Economics" ? newEcon : dims[k] ?? 5) * w, 0);
  const delta = overall - (verdict.score ?? overall);

  const Slider = ({ label, value, min, max, step, onChange, unit }: {
    label: string; value: number; min: number; max: number; step: number;
    onChange: (v: number) => void; unit: string;
  }) => (
    <label className="block">
      <span className="flex justify-between font-mono text-[10px] uppercase tracking-wider text-slate-500">
        {label} <span className="text-cyan">₹{value}{unit}</span>
      </span>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-[--color-cyan]" />
    </label>
  );

  return (
    <section className="rounded-xl border border-line bg-panel p-4">
      <h3 className="mb-3 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        <SlidersHorizontal size={13} /> What-if — survival math, live
      </h3>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-3">
          <Slider label="Capital" value={cap} min={2} max={Math.max(2000, core.capital_lakhs * 3)}
            step={1} onChange={setCapital} unit="L" />
          <Slider label="Monthly burn" value={b} min={0.5} max={Math.max(50, core.burn_lakhs_pm * 4)}
            step={0.1} onChange={setBurn} unit="L/mo" />
          <button onClick={() => { setCapital(null); setBurn(null); }}
            className="font-mono text-[10px] text-slate-500 hover:text-cyan">↺ reset to analysed values</button>
        </div>
        <div className="rounded-lg border border-line bg-panel-2 p-3 font-mono text-xs">
          <div className="flex justify-between text-slate-400">
            <span>runway</span><span className="text-slate-200">{runway.toFixed(1)} months</span>
          </div>
          <div className="mt-1 flex justify-between text-slate-400">
            <span>economics dimension</span><span className="text-slate-200">{newEcon.toFixed(1)}/10</span>
          </div>
          <div className="mt-1 flex justify-between text-slate-400">
            <span>projected overall</span>
            <span className={delta > 0.05 ? "text-ok" : delta < -0.05 ? "text-err" : "text-slate-200"}>
              {overall.toFixed(1)}/10 ({delta >= 0 ? "+" : ""}{delta.toFixed(1)})
            </span>
          </div>
          <p className="mt-3 text-[10px] leading-relaxed text-slate-500">
            Deterministic core re-run only — market, evidence and timing hold still.
            A full re-analysis needs a new run.
          </p>
        </div>
      </div>
    </section>
  );
}
