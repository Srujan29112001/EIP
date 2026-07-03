"use client";

import { useState } from "react";
import type { EngineStatus } from "@/lib/api";
import type { IntakeForm } from "@/lib/types";
import { BoardPicker } from "./board-picker";
import { EnginePanel } from "./engine-panel";

const DEFAULTS: IntakeForm = {
  mode: "founder",
  situation: "",
  industry: "",
  geography: "India",
  stage: "ideation",
  budget_band: "under_10L",
  team_size: "solo",
  uncertainty: "",
  depth: "pulse",
  agents_enabled: [],
  engine: {
    compute: "auto", provider: "", api_key: "", model: "",
    api_keys: {}, agent_routes: {}, temperature: null, max_tokens_cap: 0,
  },
};

const Field = ({ label, children }: { label: string; children: React.ReactNode }) => (
  <label className="block">
    <span className="mb-1 block font-mono text-[11px] uppercase tracking-wider text-muted">{label}</span>
    {children}
  </label>
);

const selectCls =
  "w-full rounded-md border border-line bg-panel-2 px-3 py-2 text-sm outline-none focus:border-cyan/60";

export function IntakeWizard({ onRun, engine }: { onRun: (f: IntakeForm) => void; engine?: EngineStatus | null }) {
  const [f, setF] = useState<IntakeForm>(DEFAULTS);
  const set = <K extends keyof IntakeForm>(k: K, v: IntakeForm[K]) => setF((p) => ({ ...p, [k]: v }));
  const ready = f.situation.trim().length >= 20;

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="font-display text-3xl font-bold">
        Convene your <span className="bg-gradient-to-r from-brand to-cyan bg-clip-text text-transparent">board</span>
      </h1>
      <p className="mt-1 text-sm text-slate-400">
        Describe the situation like you would to a smart friend. The board does the rest — live data, real math, open argument.
      </p>

      {/* step 1 — situation */}
      <section className="mt-8 rounded-xl border border-line bg-panel p-5">
        <h2 className="mb-3 font-mono text-xs uppercase tracking-widest text-l1">01 · What&apos;s the situation?</h2>
        <textarea
          value={f.situation}
          onChange={(e) => set("situation", e.target.value)}
          rows={5}
          placeholder="e.g. I want to start a D2C millet-based snacks brand in Bangalore targeting health-conscious professionals. I have savings, no co-founder yet, and I'm unsure the market is big enough…"
          className="w-full resize-none rounded-md border border-line bg-panel-2 p-3 text-sm leading-relaxed outline-none focus:border-cyan/60"
        />
        <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-3">
          <Field label="Industry (optional)">
            <input value={f.industry} onChange={(e) => set("industry", e.target.value)}
              placeholder="auto-detected" className={selectCls} />
          </Field>
          <Field label="Geography">
            <select value={f.geography} onChange={(e) => set("geography", e.target.value)} className={selectCls}>
              <option>India</option><option>Global</option><option>US</option><option>Europe</option><option>SEA</option>
            </select>
          </Field>
          <Field label="Stage">
            <select value={f.stage} onChange={(e) => set("stage", e.target.value)} className={selectCls}>
              {["ideation", "validation", "mvp", "traction", "scaling", "expansion"].map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </Field>
          <Field label="Budget">
            <select value={f.budget_band} onChange={(e) => set("budget_band", e.target.value)} className={selectCls}>
              <option value="under_10L">&lt; ₹10L</option>
              <option value="10L_1Cr">₹10L – ₹1Cr</option>
              <option value="1Cr_10Cr">₹1Cr – ₹10Cr</option>
              <option value="above_10Cr">&gt; ₹10Cr</option>
            </select>
          </Field>
          <Field label="Team">
            <select value={f.team_size} onChange={(e) => set("team_size", e.target.value)} className={selectCls}>
              <option value="solo">solo</option><option value="2_5">2–5</option>
              <option value="5_20">5–20</option><option value="20_plus">20+</option>
            </select>
          </Field>
          <Field label="Biggest uncertainty">
            <input value={f.uncertainty} onChange={(e) => set("uncertainty", e.target.value)}
              placeholder="what keeps you up at night?" className={selectCls} />
          </Field>
        </div>
      </section>

      {/* step 2 — depth */}
      <section className="mt-4 rounded-xl border border-line bg-panel p-5">
        <h2 className="mb-3 font-mono text-xs uppercase tracking-widest text-l1">02 · Choose the depth</h2>
        <div className="grid grid-cols-1 gap-2 md:grid-cols-3">
          {([
            ["pulse", "Pulse", "11 specialists · ~2 min · the fast read"],
            ["board", "Board Meeting", "19 specialists · full venture board + devil's advocate"],
            ["war_room", "War Room", "full board · debate rounds land in Phase 3b"],
          ] as const).map(([id, label, sub]) => (
            <button key={id} onClick={() => set("depth", id)}
              className={`rounded-lg border p-3 text-left transition ${
                f.depth === id ? "border-cyan/70 bg-cyan/10" : "border-line bg-panel-2 hover:border-slate-500"}`}>
              <div className="text-sm font-semibold">{label}</div>
              <div className="font-mono text-[10px] text-muted">{sub}</div>
            </button>
          ))}
        </div>
      </section>

      {/* step 3 — your board (hand-pick the employees) */}
      <section className="mt-4 rounded-xl border border-line bg-panel p-5">
        <h2 className="mb-3 font-mono text-xs uppercase tracking-widest text-l1">03 · Pick your board</h2>
        <BoardPicker depth={f.depth} enabled={f.agents_enabled}
          onChange={(ids) => set("agents_enabled", ids)} />
      </section>

      {/* step 4 — engine */}
      <section className="mt-4 rounded-xl border border-line bg-panel p-5">
        <h2 className="mb-3 font-mono text-xs uppercase tracking-widest text-l1">04 · Choose the engine</h2>
        {engine && (
          <div className="mb-3 flex flex-wrap items-center gap-1.5 font-mono text-[10px]">
            <span className={`rounded border px-1.5 py-0.5 ${
              engine.local ? "border-ok/40 bg-ok/10 text-ok" : "border-line text-slate-600"}`}>
              local gpu ({engine.local_model}) {engine.local ? "✓" : "not detected"}
            </span>
          </div>
        )}
        <EnginePanel engine={f.engine} onChange={(e) => set("engine", e)} status={engine} />
      </section>

      {/* run bar */}
      <div className="sticky bottom-4 mt-6 flex items-center justify-between rounded-xl border border-line bg-panel/90 p-4 backdrop-blur">
        <span className="font-mono text-[11px] text-muted">
          {ready
            ? `${f.agents_enabled.length > 0 ? f.agents_enabled.length : f.depth === "pulse" ? 11 : 19} specialists ready · ${
                { pulse: "Pulse", board: "Board Meeting", war_room: "War Room" }[f.depth]} depth`
            : "describe your situation (≥ 20 chars) to begin"}
        </span>
        <button disabled={!ready} onClick={() => onRun(f)}
          className="rounded-lg bg-gradient-to-r from-brand to-cyan px-6 py-2.5 font-display text-sm font-bold text-ink transition enabled:hover:brightness-110 disabled:opacity-40">
          ⚡ Convene the Board
        </button>
      </div>
    </div>
  );
}
