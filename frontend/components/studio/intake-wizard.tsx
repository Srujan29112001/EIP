"use client";

import { useState } from "react";
import { ScrambleText } from "@/components/fx/scramble-text";
import { API_BASE, type EngineStatus } from "@/lib/api";
import type { IntakeForm } from "@/lib/types";
import { BoardPicker } from "./board-picker";
import { BossChat } from "./boss-chat";
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
  conversation: [],
  engagement_mode: "",
  hitl_timeout: 300,
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
  const [bossReady, setBossReady] = useState(false);
  const set = <K extends keyof IntakeForm>(k: K, v: IntakeForm[K]) => setF((p) => ({ ...p, [k]: v }));

  const addDocument = async (file: File) => {
    setDocBusy(true);
    setDocError("");
    try {
      if (file.type.startsWith("image/")) {
        // Phase 8.2 — OCR of scanned images, IN THE BROWSER (tesseract.js WASM):
        // zero backend vision deps, so it runs on the free tier. The heavy
        // module is lazy-loaded only when an image is actually uploaded.
        const { default: Tesseract } = await import("tesseract.js");
        const { data } = await Tesseract.recognize(file, "eng", { logger: () => {} });
        const text = (data.text || "").trim();
        if (text.length < 20) throw new Error("OCR found almost no text in this image — try a sharper scan");
        setF((p) => ({ ...p, documents: [...p.documents, { name: `${file.name} (OCR)`, text: text.slice(0, 20000) }].slice(0, 3) }));
      } else {
        const body = new FormData();
        body.append("file", file);
        const r = await fetch(`${API_BASE}/api/extract`, { method: "POST", body });
        if (!r.ok) throw new Error((await r.json().catch(() => null))?.detail ?? `extract failed (${r.status})`);
        const doc = await r.json();
        setF((p) => ({ ...p, documents: [...p.documents, { name: doc.name, text: doc.text }].slice(0, 3) }));
      }
    } catch (e) {
      setDocError(e instanceof Error ? e.message : "extraction failed");
    } finally {
      setDocBusy(false);
    }
  };
  const trader = f.mode === "trader";
  const wealth = f.mode === "wealth";
  const intelligent = f.mode === "intelligent";
  const founder = f.mode === "founder";
  const ready = trader ? f.symbol.trim().length >= 2
    : wealth ? f.monthly_income > 0
    : intelligent ? (bossReady || f.situation.trim().length >= 20)
    : f.situation.trim().length >= 20;

  return (
    <div className="grid-bg mx-auto max-w-3xl px-6 py-10">
      <p className="font-mono text-[10px] uppercase tracking-[0.4em] text-cyan">
        <ScrambleText text="MISSION CONTROL" />
      </p>
      <h1 className="mt-2 font-hero text-4xl font-bold md:text-5xl">
        Convene your <span className="shimmer-text">board.</span>
      </h1>
      <p className="mt-2 text-sm text-slate-400">
        Describe the situation like you would to a smart friend. The board does the rest — live data, real math, open argument.
      </p>
      <div className="beam mt-5" />

      {/* mode doors */}
      <div className="mt-5 grid grid-cols-2 gap-2.5 sm:grid-cols-4">
        {([["founder", "🚀", "Founder", "validate an idea or dilemma", "#22d3ee"],
           ["trader", "📈", "Trader", "analyse any listed stock", "#5591E8"],
           ["wealth", "💰", "Wealth", "salary, savings, FIRE, property", "#f59e0b"],
           ["intelligent", "🎩", "Intelligent", "the Advisory Engine — Boss + Manager", "#D9A94A"]] as const).map(([id, icon, label, sub, accent]) => {
          const on = f.mode === id;
          return (
            <button key={id} onClick={() => {
                set("mode", id);
                // the Advisory Engine is a full board with two-round deliberation by default
                if (id === "intelligent" && f.depth === "pulse") set("depth", "board");
              }}
              className={`relative overflow-hidden rounded-2xl border p-3.5 text-left transition-all duration-300 ${
                on ? "-translate-y-0.5" : "border-line bg-panel hover:-translate-y-0.5 hover:border-slate-500"}`}
              style={on ? {
                borderColor: `${accent}b0`,
                background: `linear-gradient(160deg, ${accent}1f, transparent 65%)`,
                boxShadow: `0 0 32px -10px ${accent}90, inset 0 1px 0 rgba(255,255,255,0.06)`,
              } : undefined}>
              {on && (
                <span className="orbit" style={{ "--dur": "9s", "--dot": accent } as React.CSSProperties}><span /></span>
              )}
              <span className="grid h-9 w-9 place-items-center rounded-xl text-lg"
                style={{ background: `${accent}${on ? "26" : "14"}` }}>
                {icon}
              </span>
              <div className="mt-2 text-sm font-semibold" style={on ? { color: accent } : undefined}>{label}</div>
              <div className="mt-0.5 font-mono text-[10px] leading-snug text-muted">{sub}</div>
            </button>
          );
        })}
      </div>

      {intelligent && (
        <div className="mt-3 rounded-lg border border-brand/30 bg-brand/5 p-3 text-xs leading-relaxed text-slate-400">
          <span className="font-semibold text-slate-200">Intelligent Mode is the Orchestra</span> — no
          forms, no board picking, no depth choosing. The 🎩 <b>Boss</b> is the intelligent chatbot that
          talks to you and retrieves everything the board needs; the 🎼 <b>Manager</b> then composes the
          <b> entire dynamic pipeline</b> — which experts work, which sit out (with reasons), the
          communication lines between them, and how deep each one goes. A blocking ✅ <b>QA gate</b>{" "}
          re-dispatches weak analysis and 🧑‍⚖️ <b>human review</b> guards regulated content.
        </div>
      )}

      {/* step 1 — trader: the symbol IS the situation */}
      {trader && (
        <section className="glass mt-4 rounded-2xl p-5">
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
        <section className="glass mt-4 rounded-2xl p-5">
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

      {/* step 1 — intelligent: the 🎩 Boss conversation */}
      {intelligent && (
        <BossChat
          engine={f.engine}
          onConversation={(c) => set("conversation", c)}
          onBrief={(b) => setF((p) => ({
            ...p,
            engagement_mode: (b.engagement_mode as IntakeForm["engagement_mode"]) || p.engagement_mode,
            situation: b.situation || p.situation,
            industry: b.industry || p.industry,
            geography: b.geography || p.geography,
            stage: b.stage || p.stage,
            budget_band: b.budget_band || p.budget_band,
            team_size: b.team_size || p.team_size,
            uncertainty: b.uncertainty || p.uncertainty,
            target_customer: b.target_customer || p.target_customer,
            competitors: b.competitors || p.competitors,
            revenue_model: b.revenue_model || p.revenue_model,
            // mode-specific fields the trader / wealth desks need
            symbol: b.symbol ? String(b.symbol).toUpperCase() : p.symbol,
            trading_style: (b.trading_style as IntakeForm["trading_style"]) || p.trading_style,
            monthly_income: b.monthly_income ? Number(String(b.monthly_income).replace(/[^\d.]/g, "")) || p.monthly_income : p.monthly_income,
            monthly_expenses: b.monthly_expenses ? Number(String(b.monthly_expenses).replace(/[^\d.]/g, "")) || p.monthly_expenses : p.monthly_expenses,
          }))}
          onComplete={setBossReady}
        />
      )}

      {/* step 1 — founder: the situation */}
      {founder && (
      <section className="glass mt-4 rounded-2xl p-5">
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
              {docBusy ? "extracting…" : "+ add PDF / TXT / scanned image (OCR)"}
              <input type="file" accept=".pdf,.txt,.md,.csv,image/png,image/jpeg,image/webp" className="hidden" disabled={docBusy}
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

      {/* step 2 — depth (form modes; in Intelligent Mode the Manager sets depth) */}
      {!intelligent && (
      <section className="glass mt-4 rounded-2xl p-5">
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
      )}

      {/* your board — hand-pick and brief the employees (form modes; in
          Intelligent Mode casting is the 🎼 Manager's job, not a picker) */}
      {!intelligent && (
      <section className="glass mt-4 rounded-2xl p-5">
        <h2 className="mb-3 font-mono text-xs uppercase tracking-widest text-l1">
          03 · Pick your board
        </h2>
        <BoardPicker mode={f.mode} depth={f.depth} enabled={f.agents_enabled}
          onChange={(ids) => set("agents_enabled", ids)}
          agentContext={f.agent_context}
          onContext={(ctx) => set("agent_context", ctx)} />
      </section>
      )}

      {/* engine */}
      <section className="glass mt-4 rounded-2xl p-5">
        <h2 className="mb-3 font-mono text-xs uppercase tracking-widest text-l1">
          {intelligent ? "02" : "04"} · Choose the engine
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
      <div className="glass sticky bottom-4 mt-6 flex items-center justify-between rounded-2xl p-4 shadow-[0_-8px_40px_-20px_rgba(6,182,212,0.25),0_18px_44px_-22px_rgba(0,0,0,0.7)]">
        <span className="font-mono text-[11px] text-muted">
          {!ready
            ? trader ? "enter a symbol to begin"
              : wealth ? "enter your monthly income to begin"
              : intelligent ? "finish the intake conversation with the 🎩 Boss to begin"
              : "describe your situation (≥ 20 chars) to begin"
            : intelligent
            ? "🎩 brief captured — the 🎼 Manager composes the cast, the lines and the depth"
            : `${f.agents_enabled.length > 0 ? f.agents_enabled.length
                : { founder: { pulse: 13, board: 26, war_room: 37 },
                    trader: { pulse: 18, board: 26, war_room: 34 },
                    wealth: { pulse: 14, board: 22, war_room: 29 } }[
                    f.mode as "founder" | "trader" | "wealth"][f.depth]
              } specialists ready · ${
                { pulse: "Pulse", board: "Board Meeting", war_room: "War Room" }[f.depth]}${
                trader ? ` · ${f.symbol}` : ""}`}
        </span>
        <button disabled={!ready} onClick={() => onRun(f)}
          className={`btn-glow rounded-xl bg-gradient-to-r px-6 py-2.5 font-hero text-sm font-bold text-ink transition enabled:hover:brightness-110 disabled:opacity-40 ${
            intelligent ? "from-brand to-l5" : "from-brand to-cyan"}`}>
          {intelligent ? "🎩 Run the Advisory Engine" : "⚡ Convene the Board"}
        </button>
      </div>
    </div>
  );
}
