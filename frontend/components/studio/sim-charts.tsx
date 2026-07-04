"use client";

/** Simulation layer of the Decision Room — every insight gets an interactive
 * past/future chart you can bend with condition sliders. All math is the
 * deterministic mirror of the backend cores; clearly labelled directional.
 */

import { useMemo, useState } from "react";
import { LineChart, SlidersHorizontal, TrendingUp } from "lucide-react";
import { useRun } from "@/lib/store";
import type { AgentOutput } from "@/lib/types";
import { SimSlider, TimeSeries, type SeriesPoint } from "./charts";

const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));

/** Mirror of the backend weighing engines: base weights per mode, renormalized
 * over whichever dimensions this run produced. Keep in sync with venture/
 * markets/wealth weighing. */
export function weightsFor(dims: Record<string, number>): Record<string, number> {
  const founder = { Market: 0.25, Economics: 0.25, Evidence: 0.10, Execution: 0.125,
    Timing: 0.15, Regulatory: 0.125, HumanFit: 0.12 } as Record<string, number>;
  const trader = { Trend: 0.25, Momentum: 0.2, Value: 0.2, History: 0.2,
    RiskFit: 0.15, Psychology: 0.12 } as Record<string, number>;
  const wealth = { Cashflow: 0.3, Allocation: 0.2, GoalFit: 0.25, DebtHealth: 0.15,
    Opportunity: 0.1, LifeFit: 0.15 } as Record<string, number>;
  const base = "Trend" in dims ? trader : "Cashflow" in dims ? wealth : founder;
  const picked = Object.fromEntries(Object.keys(dims).filter((k) => k in base).map((k) => [k, base[k]]));
  const total = Object.values(picked).reduce((s, v) => s + v, 0) || 1;
  return Object.fromEntries(Object.entries(picked).map(([k, v]) => [k, v / total]));
}

/* ── 1 · Cash & runway simulator (Economics insight) ─────────────────────── */

export function RunwaySim() {
  const core = useRun((s) => s.financeCore);
  const verdict = useRun((s) => s.verdict);
  const [capital, setCapital] = useState<number | null>(null);
  const [burn, setBurn] = useState<number | null>(null);
  const [revM, setRevM] = useState(0);        // revenue starting month (0 = none)
  const [revGrow, setRevGrow] = useState(15); // % m/m growth once revenue starts

  if (!core || !verdict?.dimensions) return null;
  const dims = verdict.dimensions;
  const cap = capital ?? core.capital_lakhs;
  const b = burn ?? core.burn_lakhs_pm;

  // simulate 30 months of cash: burn out, optional revenue ramp
  const future: SeriesPoint[] = [];
  let cash = cap, rev = 0, cashOut: number | null = null;
  for (let m = 0; m <= 30; m++) {
    future.push({ x: m, y: Math.round(cash * 10) / 10, label: `month ${m}` });
    if (revM > 0 && m >= revM) rev = rev === 0 ? b * 0.15 : rev * (1 + revGrow / 100);
    cash = cash - b + Math.min(rev, b * 2.5);
    if (cashOut === null && cash <= 0) cashOut = m + 1;
  }
  const runway = b > 0 ? cap / b : 99;

  // mirror of backend weighing (Economics ← runway, red-team penalty preserved)
  const baseRaw = clamp(core.runway_months / 3.0, 1.0, 9.0);
  const penalty = baseRaw - (dims.Economics ?? baseRaw);
  const newEcon = clamp(clamp(runway / 3.0, 1.0, 9.0) - penalty, 0.5, 10);
  const weights = weightsFor(dims);
  const overall = Object.entries(weights).reduce(
    (s, [k, w]) => s + (k === "Economics" ? newEcon : dims[k] ?? 5) * w, 0);
  const delta = overall - (verdict.score ?? overall);

  return (
    <section className="rounded-xl border border-line bg-panel p-4 transition hover:border-cyan/25">
      <h3 className="mb-3 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        <SlidersHorizontal size={13} /> Survival simulator — cash, live
      </h3>
      <div className="grid gap-4 lg:grid-cols-[1fr_260px]">
        <div>
          <TimeSeries past={[{ x: 0, y: cap, label: "today" }]} future={future.slice(1)}
            color="#9ae64a" futureColor="#22d3ee" yLabel="cash ₹L" zeroLine markerX={cashOut} height={200} />
          <p className="mt-1 font-mono text-[10px] text-slate-500">
            {cashOut ? `cash-out at month ${cashOut}` : "solvent through month 30"} ·
            runway {runway.toFixed(1)} mo · deterministic core re-run, directional only
          </p>
        </div>
        <div className="space-y-3">
          <SimSlider label="Capital" value={cap} min={2} max={Math.max(2000, core.capital_lakhs * 3)} step={1}
            onChange={setCapital} fmt={(v) => `₹${v}L`} />
          <SimSlider label="Monthly burn" value={b} min={0.5} max={Math.max(50, core.burn_lakhs_pm * 4)} step={0.1}
            onChange={setBurn} fmt={(v) => `₹${v.toFixed(1)}L`} />
          <SimSlider label="Revenue starts" value={revM} min={0} max={18} step={1}
            onChange={setRevM} fmt={(v) => (v === 0 ? "never" : `month ${v}`)} />
          <SimSlider label="Revenue growth" value={revGrow} min={0} max={40} step={1}
            onChange={setRevGrow} fmt={(v) => `${v}%/mo`} />
          <div className="rounded-lg border border-line bg-panel-2 p-2.5 font-mono text-xs">
            <div className="flex justify-between text-slate-400">
              <span>projected verdict</span>
              <span className={delta > 0.05 ? "text-ok" : delta < -0.05 ? "text-err" : "text-slate-200"}>
                {overall.toFixed(1)}/10 ({delta >= 0 ? "+" : ""}{delta.toFixed(1)})
              </span>
            </div>
          </div>
          <button onClick={() => { setCapital(null); setBurn(null); setRevM(0); setRevGrow(15); }}
            className="font-mono text-[10px] text-slate-500 hover:text-cyan">↺ reset to analysed values</button>
        </div>
      </div>
    </section>
  );
}

/* ── 2 · Market pulse simulator — real 1y series + conditions cone ────────── */

export function MarketSim() {
  const outputs = useRun((s) => s.agentOutputs);
  const md = outputs["market_data"] as AgentOutput | undefined;
  const pulses = (md?.pulses ?? []) as {
    label: string; series?: [string, number][]; volatility_pct?: number; ret_1y_pct?: number;
  }[];
  const [sel, setSel] = useState(0);
  const [drift, setDrift] = useState<number | null>(null);
  const [volX, setVolX] = useState(1);

  const pulse = pulses[sel];
  const series = pulse?.series ?? [];
  const past: SeriesPoint[] = useMemo(
    () => series.map(([d, v], i) => ({ x: i, y: v, label: d })), [series]);

  if (!pulse || past.length < 8) return null;

  const last = past[past.length - 1];
  const annDrift = drift ?? pulse.ret_1y_pct ?? 0;                  // default: continue last year's trend
  const vol = ((pulse.volatility_pct ?? 15) / 100) * volX;
  const stepsPerYear = 52;
  const horizon = 26;                                               // ~6 months forward
  const future: SeriesPoint[] = [];
  const cone: { x: number; lo: number; hi: number }[] = [];
  for (let i = 1; i <= horizon; i++) {
    const t = i / stepsPerYear;
    const mean = last.y * Math.pow(1 + annDrift / 100, t);
    const spread = mean * vol * Math.sqrt(t);
    future.push({ x: last.x + i, y: Math.round(mean * 100) / 100, label: `+${i}w` });
    cone.push({ x: last.x + i, lo: mean - spread, hi: mean + spread });
  }

  return (
    <section className="rounded-xl border border-line bg-panel p-4 transition hover:border-cyan/25">
      <h3 className="mb-1 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        <TrendingUp size={13} /> Market pulse — 1y history → 6mo scenario cone
      </h3>
      <div className="mb-2 flex flex-wrap items-center gap-2">
        {pulses.map((p, i) => (
          <button key={i} onClick={() => setSel(i)}
            className={`rounded-full border px-2.5 py-0.5 font-mono text-[10px] transition ${
              i === sel ? "border-cyan/60 bg-cyan/10 text-cyan" : "border-line text-slate-500 hover:text-slate-300"}`}>
            {p.label}
          </button>
        ))}
        <span className="ml-auto font-mono text-[10px] text-slate-600">source: Yahoo Finance · projection: yours</span>
      </div>
      <div className="grid gap-4 lg:grid-cols-[1fr_260px]">
        <TimeSeries past={past} future={future} cone={{ points: cone }} height={210} yLabel="price" />
        <div className="space-y-3">
          <SimSlider label="Assumed annual drift" value={annDrift} min={-40} max={60} step={1}
            onChange={setDrift} fmt={(v) => `${v >= 0 ? "+" : ""}${v.toFixed(0)}%/yr`} />
          <SimSlider label="Volatility regime" value={volX} min={0.5} max={2.5} step={0.1}
            onChange={setVolX} fmt={(v) => `${v.toFixed(1)}×`} />
          <p className="rounded-lg bg-panel-2 p-2.5 text-[10px] leading-relaxed text-slate-500">
            The cone is a probability band, never a prediction (Constitution #6): wider volatility or
            longer horizon = wider cone. History is real data; the future is your assumption made visible.
          </p>
          <button onClick={() => { setDrift(null); setVolX(1); }}
            className="font-mono text-[10px] text-slate-500 hover:text-cyan">↺ reset assumptions</button>
        </div>
      </div>
    </section>
  );
}

/* ── 3 · Verdict sensitivity simulator — bend any dimension ───────────────── */

export function ScoreSim() {
  const verdict = useRun((s) => s.verdict);
  const [overrides, setOverrides] = useState<Record<string, number>>({});

  if (!verdict?.dimensions) return null;
  const dims = verdict.dimensions;
  const weights = weightsFor(dims);
  const val = (k: string) => overrides[k] ?? dims[k] ?? 5;
  const overall = Object.entries(weights).reduce((s, [k, w]) => s + val(k) * w, 0);
  const delta = overall - (verdict.score ?? overall);
  const band = overall >= 7 ? "GO" : overall >= 4.5 ? "CONDITIONAL GO" : "NO-GO";

  return (
    <section className="rounded-xl border border-line bg-panel p-4 transition hover:border-cyan/25">
      <h3 className="mb-3 flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-muted">
        <LineChart size={13} /> Verdict sensitivity — bend any dimension
      </h3>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2.5">
          {Object.keys(weights).map((k) => (
            <SimSlider key={k} label={`${k} (w ${Math.round(weights[k] * 100)}%)`} value={val(k)}
              min={0} max={10} step={0.1}
              onChange={(v) => setOverrides((o) => ({ ...o, [k]: v }))} fmt={(v) => `${v.toFixed(1)}`} />
          ))}
        </div>
        <div className="flex flex-col justify-center rounded-lg border border-line bg-panel-2 p-4 text-center">
          <div className="font-mono text-[10px] uppercase tracking-widest text-slate-500">simulated verdict</div>
          <div className="font-display text-4xl font-bold text-slate-100">
            {overall.toFixed(1)}<span className="text-lg text-slate-500">/10</span>
          </div>
          <div className={`font-mono text-xs ${delta > 0.05 ? "text-ok" : delta < -0.05 ? "text-err" : "text-slate-400"}`}>
            {delta >= 0 ? "▲ +" : "▼ "}{delta.toFixed(1)} vs the board · {band}
          </div>
          <button onClick={() => setOverrides({})}
            className="mt-3 font-mono text-[10px] text-slate-500 hover:text-cyan">↺ back to the board&apos;s numbers</button>
          <p className="mt-2 text-[10px] leading-relaxed text-slate-600">
            This shows which dimension your verdict is most sensitive to — it does not re-run the agents.
          </p>
        </div>
      </div>
    </section>
  );
}
