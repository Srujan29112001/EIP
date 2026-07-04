"use client";

import { useState } from "react";
import { API_BASE, type EngineStatus } from "@/lib/api";
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
  target_customer: "",
  competitors: "",
  revenue_model: "",
  symbol: "",
  trading_style: "swing",
  capital: 100000,
  risk_pct: 1.0,
  thesis: "",
  existing_position: 0,
  dependents: 0,
  current_debt: 0,
  monthly_sip: 0,
  monthly_income: 80000,
  monthly_expenses: 50000,
  current_savings: 500000,
  age: 30,
  risk_appetite: "moderate",
  city: "",
  goals: "",
  documents: [],
  agent_context: {},
  engine: {
    compute: "auto", provider: "", api_key: "", model: "",
    api_keys: {}, api_keys_multi: {}, agent_routes: {}, routes: {}, temperature: null, max_tokens_cap: 0,
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
  const [docBusy, setDocBusy] = useState(false);
  const [docError, setDocError] = useState("");
  const set = <K extends keyof IntakeForm>(k: K, v: IntakeForm[K]) => setF((p) => ({ ...p, [k]: v }));

  const addDocument = async (file: File) => {
    setDocBusy(true);
    setDocError("");
    try {
      const body = new FormData();
      body.append("file", file);
      const r = await fetch(`${API_BASE}/api/extract`, { method: "POST", body });
      if (!r.ok) throw new Error((await r.json().catch(() => null))?.detail ?? `extract failed (${r.status})`);
      const doc = await r.json();
      setF((p) => ({ ...p, documents: [...p.documents, { name: doc.name, text: doc.text }].slice(0, 3) }));
    } catch (e) {
      setDocError(e instanceof Error ? e.message : "extraction failed");
    } finally {
      setDocBusy(false);
    }
  };
  const trader = f.mode === "trader";
  const wealth = f.mode === "wealth";
  const founder = f.mode === "founder";
  const ready = trader ? f.symbol.trim().length >= 2
    : wealth ? f.monthly_income > 0
    : f.situation.trim().length >= 20;

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="font-display text-3xl font-bold">
        Convene your <span className="holo-text">board</span>
      </h1>
      <p className="mt-1 text-sm text-slate-400">
        Describe the situation like you would to a smart friend. The board does the rest — live data, real math, open argument.
      </p>

      {/* mode tabs */}
      <div className="mt-6 flex gap-2">
        {([["founder", "🚀 Founder", "validate an idea or dilemma"],
           ["trader", "📈 Trader", "analyse any listed stock"],
           ["wealth", "💰 Wealth", "salary, savings, FIRE, property"]] as const).map(([id, label, sub]) => (
          <button key={id} onClick={() => set("mode", id)}
            className={`flex-1 rounded-xl border p-3 text-left transition ${
              f.mode === id ? "border-cyan/70 bg-cyan/10" : "border-line bg-panel hover:border-slate-500"}`}>
            <div className="text-sm font-semibold">{label}</div>
            <div className="font-mono text-[10px] text-muted">{sub}</div>
          </button>
        ))}
      </div>

      {/* step 1 — trader: the symbol IS the situation */}
      {trader && (
        <section className="mt-4 rounded-xl border border-line bg-panel p-5">
          <h2 className="mb-3 font-mono text-xs uppercase tracking-widest text-l1">01 · What are you looking at?</h2>
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <Field label="Symbol (NSE default)">
              <input value={f.symbol} onChange={(e) => set("symbol", e.target.value.toUpperCase())}
                placeholder="RELIANCE · TCS · AAPL" className={selectCls} />
            </Field>
            <Field label="Style">
              <select value={f.trading_style}
                onChange={(e) => set("trading_style", e.target.value as IntakeForm["trading_style"])}
                className={selectCls}>
                <option value="intraday">intraday</option>
                <option value="swing">swing</option>
                <option value="position">position</option>
                <option value="options_edu">options (education)</option>
              </select>
            </Field>
            <Field label="Capital (₹)">
              <input type="number" min={1000} step={1000} value={f.capital}
                onChange={(e) => set("capital", Number(e.target.value))} className={selectCls} />
            </Field>
            <Field label={`Risk per trade · ${f.risk_pct}%`}>
              <input type="range" min={0.25} max={5} step={0.25} value={f.risk_pct}
                onChange={(e) => set("risk_pct", Number(e.target.value))}
                className="mt-3 w-full accent-[#06b6d4]" />
            </Field>
            <Field label="Your thesis (why this stock?)">
              <input value={f.thesis} onChange={(e) => set("thesis", e.target.value)}
                placeholder="the board will stress-test it" className={selectCls} />
            </Field>
            <Field label="Shares already held">
              <input type="number" min={0} value={f.existing_position}
                onChange={(e) => set("existing_position", Number(e.target.value))} className={selectCls} />
            </Field>
          </div>
          <p className="mt-3 rounded-lg bg-panel-2 p-2.5 font-mono text-[10px] leading-relaxed text-slate-500">
            EIP analyses setups and teaches — it never tells you to buy or sell, never predicts prices,
            never executes. Not SEBI-registered advice. Decisions and outcomes are yours.
          </p>
        </section>
      )}

      {/* step 1 — wealth: the money picture */}
      {wealth && (
        <section className="mt-4 rounded-xl border border-line bg-panel p-5">
          <h2 className="mb-3 font-mono text-xs uppercase tracking-widest text-l1">01 · Your money picture</h2>
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <Field label="Monthly income (₹)">
              <input type="number" min={0} step={5000} value={f.monthly_income}
                onChange={(e) => set("monthly_income", Number(e.target.value))} className={selectCls} />
            </Field>
            <Field label="Monthly expenses (₹)">
              <input type="number" min={0} step={5000} value={f.monthly_expenses}
                onChange={(e) => set("monthly_expenses", Number(e.target.value))} className={selectCls} />
            </Field>
            <Field label="Current savings (₹)">
              <input type="number" min={0} step={50000} value={f.current_savings}
                onChange={(e) => set("current_savings", Number(e.target.value))} className={selectCls} />
            </Field>
            <Field label="Age">
              <input type="number" min={18} max={80} value={f.age}
                onChange={(e) => set("age", Number(e.target.value))} className={selectCls} />
            </Field>
            <Field label="Risk appetite">
              <select value={f.risk_appetite}
                onChange={(e) => set("risk_appetite", e.target.value as IntakeForm["risk_appetite"])}
                className={selectCls}>
                <option value="conservative">conservative</option>
                <option value="moderate">moderate</option>
                <option value="aggressive">aggressive</option>
              </select>
            </Field>
            <Field label="City (for local scout)">
              <input value={f.city} onChange={(e) => set("city", e.target.value)}
                placeholder="Bangalore" className={selectCls} />
            </Field>
            <Field label="Goals">
              <input value={f.goals} onChange={(e) => set("goals", e.target.value)}
                placeholder="house in 5y, FIRE by 45…" className={selectCls} />
            </Field>
            <Field label="Biggest worry">
              <input value={f.uncertainty} onChange={(e) => set("uncertainty", e.target.value)}
                placeholder="am I saving enough?" className={selectCls} />
            </Field>
            <Field label="Dependents">
              <input type="number" min={0} max={10} value={f.dependents}
                onChange={(e) => set("dependents", Number(e.target.value))} className={selectCls} />
            </Field>
            <Field label="Outstanding debt (₹)">
              <input type="number" min={0} step={10000} value={f.current_debt}
                onChange={(e) => set("current_debt", Number(e.target.value))} className={selectCls} />
            </Field>
            <Field label="Existing SIP (₹/month)">
              <input type="number" min={0} step={1000} value={f.monthly_sip}
                onChange={(e) => set("monthly_sip", Number(e.target.value))} className={selectCls} />
            </Field>
          </div>
          <p className="mt-3 rounded-lg bg-panel-2 p-2.5 font-mono text-[10px] leading-relaxed text-slate-500">
            The wealth board teaches money math — it never recommends specific securities and is not
            SEBI-registered advice. Numbers stay on your machine unless you choose a cloud engine.
          </p>
        </section>
      )}

      {/* step 1 — founder: the situation */}
      {founder && (
      <section className="mt-4 rounded-xl border border-line bg-panel p-5">
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
          <Field label="Target customer (optional)">
            <input value={f.target_customer} onChange={(e) => set("target_customer", e.target.value)}
              placeholder="e.g. urban working women 25-40" className={selectCls} />
          </Field>
          <Field label="Known competitors (optional)">
            <input value={f.competitors} onChange={(e) => set("competitors", e.target.value)}
              placeholder="names or links — the board digs in" className={selectCls} />
          </Field>
          <Field label="Revenue model (optional)">
            <input value={f.revenue_model} onChange={(e) => set("revenue_model", e.target.value)}
              placeholder="subscription · one-off · B2B…" className={selectCls} />
          </Field>
        </div>

        {/* ground it — document intelligence (PDF/TXT/MD/CSV; scans/OCR later) */}
        <div className="mt-4 rounded-lg border border-dashed border-line bg-panel-2 p-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-[10px] uppercase tracking-wider text-slate-500">
              ground it (optional) · pitch deck / P&L / contract
            </span>
            <label className="cursor-pointer rounded-md border border-line px-2.5 py-1 font-mono text-[10px] text-slate-300 transition hover:border-cyan/60 hover:text-cyan">
              {docBusy ? "extracting…" : "+ add PDF / TXT"}
              <input type="file" accept=".pdf,.txt,.md,.csv" className="hidden" disabled={docBusy}
                onChange={(e) => e.target.files?.[0] && addDocument(e.target.files[0])} />
            </label>
            {docError && <span className="font-mono text-[10px] text-err">{docError}</span>}
          </div>
          {f.documents.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {f.documents.map((d, i) => (
                <span key={i} className="inline-flex items-center gap-1.5 rounded border border-cyan/30 bg-cyan/5 px-2 py-0.5 font-mono text-[10px] text-cyan">
                  📄 {d.name} · {(d.text.length / 1000).toFixed(1)}k chars
                  <button onClick={() => set("documents", f.documents.filter((_, x) => x !== i))}
                    className="text-slate-500 hover:text-err">✕</button>
                </span>
              ))}
            </div>
          )}
        </div>
      </section>
      )}

      {/* step 2 — depth (every mode: deeper = more specialists convened) */}
      <section className="mt-4 rounded-xl border border-line bg-panel p-5">
        <h2 className="mb-3 font-mono text-xs uppercase tracking-widest text-l1">02 · Choose the depth</h2>
        <div className="grid grid-cols-1 gap-2 md:grid-cols-3">
          {([
            ["pulse", "Pulse", founder ? "13 specialists · ~2 min · the fast read"
              : trader ? "18 specialists · the core trading desk" : "14 specialists · the money desk"],
            ["board", "Board Meeting", founder ? "26 specialists · venture board + human layer"
              : trader ? "26 specialists · + macro, geopolitics, psychology" : "22 specialists · + macro, funds, life-fit"],
            ["war_room", "War Room", founder ? "37 specialists · world cluster + live debates"
              : trader ? "34 specialists · the full house" : "29 specialists · the full house"],
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

      {/* your board — hand-pick and brief the employees (every mode) */}
      <section className="mt-4 rounded-xl border border-line bg-panel p-5">
        <h2 className="mb-3 font-mono text-xs uppercase tracking-widest text-l1">
          03 · Pick your board
        </h2>
        <BoardPicker mode={f.mode} depth={f.depth} enabled={f.agents_enabled}
          onChange={(ids) => set("agents_enabled", ids)}
          agentContext={f.agent_context}
          onContext={(ctx) => set("agent_context", ctx)} />
      </section>

      {/* engine */}
      <section className="mt-4 rounded-xl border border-line bg-panel p-5">
        <h2 className="mb-3 font-mono text-xs uppercase tracking-widest text-l1">
          04 · Choose the engine
        </h2>
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
          {!ready
            ? trader ? "enter a symbol to begin"
              : wealth ? "enter your monthly income to begin"
              : "describe your situation (≥ 20 chars) to begin"
            : `${f.agents_enabled.length > 0 ? f.agents_enabled.length
                : { founder: { pulse: 13, board: 26, war_room: 37 },
                    trader: { pulse: 18, board: 26, war_room: 34 },
                    wealth: { pulse: 14, board: 22, war_room: 29 } }[f.mode][f.depth]
              } specialists ready · ${
                { pulse: "Pulse", board: "Board Meeting", war_room: "War Room" }[f.depth]}${
                trader ? ` · ${f.symbol}` : ""}`}
        </span>
        <button disabled={!ready} onClick={() => onRun(f)}
          className="rounded-lg bg-gradient-to-r from-brand to-cyan px-6 py-2.5 font-display text-sm font-bold text-ink transition enabled:hover:brightness-110 disabled:opacity-40">
          ⚡ Convene the Board
        </button>
      </div>
    </div>
  );
}
