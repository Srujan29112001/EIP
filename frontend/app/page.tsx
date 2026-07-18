"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { Eye, Flame, Cpu, Link2, ChevronDown } from "lucide-react";
import { AGENTS, LAYER_LABELS } from "@/lib/agents";
import { Reveal } from "@/components/fx/reveal";
import { TiltCard } from "@/components/fx/tilt-card";
import { CountUp } from "@/components/fx/count-up";
import { ScrambleText } from "@/components/fx/scramble-text";

const Hero3D = dynamic(() => import("@/components/fx/hero-3d"), {
  ssr: false,
  loading: () => <div className="absolute inset-0" aria-hidden />,
});

const MODES = [
  {
    icon: "🚀", name: "Founder", tag: "validate an idea or dilemma", accent: "#3FB6A3",
    lines: ["Market · finance · legal · GTM board", "GO / CONDITIONAL / NO-GO verdict", "30-60-90 plan + honest pitch"],
  },
  {
    icon: "📈", name: "Trader", tag: "analyse any listed stock", accent: "#5591E8",
    lines: ["40+ indicators · backtests · quant", "Risk sizing from your capital", "Setup quality — never buy/sell advice"],
  },
  {
    icon: "💰", name: "Wealth", tag: "salary, savings, FIRE, property", accent: "#f59e0b",
    lines: ["Budget · allocation · FIRE math", "Debt payoff + rent-vs-buy", "Money-health verdict + roadmap"],
  },
  {
    icon: "🎩", name: "Intelligent", tag: "the Advisory Engine", accent: "#D9A94A",
    lines: ["The Boss interviews you — no forms", "The Manager composes the pipeline", "QA gate + human review built in"],
  },
];

const PILLARS = [
  { icon: Link2, title: "No naked numbers", text: "Every figure carries a live source or an explicit estimate flag. No hallucinated market sizes." },
  { icon: Eye, title: "Glass box", text: "Watch every agent fire — its prompt, its logs, its confidence, its sources. Nothing hidden." },
  { icon: Flame, title: "The Crucible", text: "A red team, devil's advocate and bias auditor attack every thesis. Including your framing." },
  { icon: Cpu, title: "Your GPU, your data", text: "Full local privacy mode via Ollama, any cloud key you choose, or zero-key demo. It never blanks." },
];

const LAYER_FLOW = [
  { id: "L0", label: "Gateway", color: "#94a3b8" },
  { id: "L1", label: "Grounding", color: "#22d3ee" },
  { id: "L2", label: "Analysis", color: "#8b5cf6" },
  { id: "R2", label: "Deliberation", color: "#f0cb78" },
  { id: "L3", label: "Crucible", color: "#fb7185" },
  { id: "L4", label: "Synthesis", color: "#eab308" },
] as const;

export default function Landing() {
  return (
    <div className="relative overflow-x-clip">
      {/* ── sticky glass nav ── */}
      <nav className="sticky top-0 z-40">
        <div className="glass mx-auto mt-3 flex max-w-6xl items-center justify-between rounded-2xl px-5 py-3">
          <span className="font-hero text-lg font-bold tracking-tight">
            EIP<span className="text-cyan">.</span>
          </span>
          <span className="flex items-center gap-1.5">
            <Link href="/graph"
              className="rounded-lg px-3 py-2 font-mono text-xs uppercase tracking-wider text-slate-400 transition hover:text-cyan">
              Graph
            </Link>
            <Link href="/history"
              className="rounded-lg px-3 py-2 font-mono text-xs uppercase tracking-wider text-slate-400 transition hover:text-cyan">
              History
            </Link>
            <Link href="/studio"
              className="btn-glow rounded-xl border border-cyan/30 px-4 py-2 font-mono text-xs uppercase tracking-wider text-slate-100 transition hover:text-white">
              Open Studio →
            </Link>
          </span>
        </div>
      </nav>

      {/* ── THE OBSERVATORY — full-viewport 3D hero ── */}
      <header className="relative flex min-h-[92vh] flex-col items-center justify-center px-6 text-center">
        <Hero3D />

        <div className="relative z-10">
          <p className="rise-in mb-5 font-mono text-[11px] uppercase tracking-[0.4em] text-cyan">
            <ScrambleText text="THE MONEY INTELLIGENCE OS" />
          </p>
          <h1 className="rise-in-1 mx-auto max-w-4xl text-balance font-hero text-5xl font-extrabold leading-[1.08] md:text-6xl lg:text-7xl">
            An <span className="shimmer-text">orchestra of AI</span> that argues about your <span className="holo-text">decision.</span>
          </h1>
          <p className="rise-in-2 mx-auto mt-6 max-w-2xl text-base text-slate-400 md:text-lg">
            Describe an idea, a stock, or a salary. {AGENTS.length} specialists research it with live data,
            run the real math, red-team the thesis, audit your biases — in front of you —
            and hand you a weighted, sourced verdict.
          </p>

          <div className="rise-in-3 mt-9 flex flex-wrap items-center justify-center gap-4">
            <Link href="/studio"
              className="btn-glow rounded-2xl bg-gradient-to-r from-brand to-cyan px-8 py-4 font-hero text-base font-bold text-ink transition hover:brightness-110">
              ⚡ Convene the Board
            </Link>
            <Link href="/studio"
              className="glass rounded-2xl px-7 py-4 font-mono text-xs uppercase tracking-wider text-slate-300 transition hover:border-brand/50 hover:text-brand">
              🎩 Talk to the Boss
            </Link>
          </div>
          <p className="rise-in-3 mt-4 font-mono text-[10px] tracking-wide text-slate-400">
            zero API keys needed · runs on your own GPU · founder / trader / wealth / intelligent
          </p>

          {/* live stat band */}
          <div className="rise-in-3 mx-auto mt-12 grid max-w-3xl grid-cols-2 gap-3 md:grid-cols-4">
            {[
              { to: AGENTS.length, suffix: "", label: "AI specialists" },
              { to: 310, suffix: "", label: "junior instruments" },
              { to: 2, suffix: "", label: "deliberation rounds" },
              { to: 15, suffix: "+", label: "interactive charts" },
            ].map((s, i) => (
              <div key={s.label} className={`glass scan-on-hover rounded-2xl px-4 py-4 d-${i + 1}`}>
                <div className="font-hero text-3xl font-bold text-slate-100">
                  <CountUp to={s.to} suffix={s.suffix} />
                </div>
                <div className="mt-1 font-mono text-[10px] uppercase tracking-[0.18em] text-slate-400">{s.label}</div>
              </div>
            ))}
          </div>
        </div>

        <ChevronDown size={20}
          className="absolute bottom-6 z-10 animate-bounce text-slate-400" aria-hidden />
      </header>

      {/* ── FOUR WAYS IN ── */}
      <section className="relative mx-auto max-w-6xl px-6 py-24">
        <Reveal dir="up">
          <p className="text-center font-mono text-[11px] uppercase tracking-[0.35em] text-muted">Choose your door</p>
          <h2 className="mt-3 text-center font-hero text-4xl font-bold md:text-5xl">
            Four ways <span className="shimmer-text">in.</span>
          </h2>
        </Reveal>
        <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {MODES.map((m, i) => (
            <Reveal key={m.name} dir="up" delay={i * 90}>
              <TiltCard className="glass h-full rounded-3xl p-6" max={8}>
                <div className="tilt-pop">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl text-2xl"
                    style={{ background: `${m.accent}1a`, boxShadow: `0 0 24px -6px ${m.accent}88` }}>
                    {m.icon}
                  </div>
                  <h3 className="mt-4 font-hero text-xl font-bold" style={{ color: m.accent }}>{m.name}</h3>
                  <p className="mt-0.5 font-mono text-[10px] uppercase tracking-wider text-slate-400">{m.tag}</p>
                  <ul className="mt-4 space-y-2">
                    {m.lines.map((l) => (
                      <li key={l} className="flex items-start gap-2 text-[13px] leading-snug text-slate-400">
                        <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full" style={{ background: m.accent }} />
                        {l}
                      </li>
                    ))}
                  </ul>
                  <Link href="/studio"
                    className="mt-5 inline-block font-mono text-[11px] uppercase tracking-wider transition hover:translate-x-1"
                    style={{ color: m.accent }}>
                    enter →
                  </Link>
                </div>
              </TiltCard>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ── THE GLASS BOX — living pipeline ── */}
      <section className="relative mx-auto max-w-6xl px-6 py-24">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <Reveal dir="left">
            <p className="font-mono text-[11px] uppercase tracking-[0.35em] text-cyan">Signature nº1</p>
            <h2 className="mt-3 font-hero text-4xl font-bold md:text-5xl">
              The <span className="holo-text">glass box.</span>
            </h2>
            <p className="mt-5 max-w-lg leading-relaxed text-slate-400">
              Most AI gives you an answer. EIP shows you the <b className="text-slate-200">argument</b> —
              every agent lighting up live over SSE, its exact prompt, its sources, its confidence,
              the gold arcs where specialists build on each other, and the crucible tearing into
              the thesis before it ever reaches you.
            </p>
            <ul className="mt-6 space-y-2.5">
              {["Live per-agent status — queued, thinking, done, degraded", "Exact-prompt reveal on every card",
                "Two full deliberation rounds — watch the board change its mind", "A 3D decision graph you can fly through"].map((t, i) => (
                <li key={t} className={`flex items-start gap-2.5 text-sm text-slate-300 d-${i + 1}`}>
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan shadow-[0_0_8px_#22d3ee]" />
                  {t}
                </li>
              ))}
            </ul>
          </Reveal>

          <Reveal dir="right">
            <div className="g-border g-border-slow rounded-3xl p-7">
              <p className="mb-5 text-center font-mono text-[10px] uppercase tracking-[0.3em] text-slate-400">
                one decision · six movements · live
              </p>
              <div className="space-y-2.5">
                {LAYER_FLOW.map((l, i) => (
                  <div key={l.id}>
                    <div className="scan-on-hover flex items-center gap-3 rounded-xl border border-line bg-panel-2/80 px-4 py-2.5">
                      <span className="pulse-ring h-2 w-2 rounded-full"
                        style={{ background: l.color, ["--ring" as string]: l.color, animationDelay: `${i * 0.28}s` }} />
                      <span className="font-mono text-[10px] uppercase tracking-wider" style={{ color: l.color }}>{l.id}</span>
                      <span className="text-sm font-semibold text-slate-200">{l.label}</span>
                      <span className="ml-auto font-mono text-[10px] text-slate-400">
                        {l.id === "R2" ? "all-to-all re-read" :
                          `${AGENTS.filter((a) => a.layer === (l.id as string)).length || "—"} agents`}
                      </span>
                    </div>
                    {i < LAYER_FLOW.length - 1 && <div className="flow-line ml-5 h-3" style={{ animationDelay: `${i * 0.2}s` }} />}
                  </div>
                ))}
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ── THE ORCHESTRA — intelligent mode ── */}
      <section className="relative mx-auto max-w-6xl px-6 py-24">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <Reveal dir="left" className="order-2 lg:order-1">
            <div className="glass relative overflow-hidden rounded-3xl p-8">
              {/* Boss → Manager → sections, breathing */}
              <div className="flex flex-col items-center">
                <div className="glass rounded-2xl px-5 py-2.5 font-mono text-xs" style={{ color: "#F0CB78" }}>
                  🎩 Boss — listens
                </div>
                <div className="flow-line h-6" />
                <div className="g-border relative rounded-2xl px-7 py-3.5">
                  <span className="font-hero text-base font-bold text-slate-100">🎼 The Manager</span>
                  <div className="orbit" style={{ ["--dur" as string]: "10s", ["--dot" as string]: "#F0CB78" }}><span /></div>
                  <div className="orbit" style={{ ["--dur" as string]: "16s", ["--dot" as string]: "#67e8f9" }}><span /></div>
                </div>
                <div className="flow-line h-6" />
                <div className="grid w-full grid-cols-3 gap-2">
                  {[["🔎", "Research", "#5591E8"], ["🧮", "Analysis", "#927BE6"], ["🧩", "Strategy", "#E8944E"],
                    ["⚖️", "Legal", "#D97595"], ["💰", "Commercial", "#B4C24A"], ["🪷", "Human", "#5FB56A"]].map(([e, n, c], i) => (
                    <div key={n} className={`float-y rounded-xl border border-line bg-panel-2/70 p-2.5 text-center`}
                      style={{ animationDelay: `${i * 0.5}s` }}>
                      <div className="text-lg">{e}</div>
                      <div className="font-mono text-[10px] uppercase tracking-wider" style={{ color: c as string }}>{n}</div>
                      <div className="mt-1.5 flex justify-center gap-1">
                        {[0, 1, 2, 3, 4].map((d) => (
                          <span key={d} className="h-1 w-1 rounded-full"
                            style={{ background: c as string, opacity: 0.35 + (d % 3) * 0.3 }} />
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
                <p className="mt-4 font-mono text-[10px] uppercase tracking-[0.25em] text-slate-400">
                  62 players · 310 junior instruments · one score
                </p>
              </div>
            </div>
          </Reveal>

          <Reveal dir="right" className="order-1 lg:order-2">
            <p className="font-mono text-[11px] uppercase tracking-[0.35em]" style={{ color: "#F0CB78" }}>Signature nº2</p>
            <h2 className="mt-3 font-hero text-4xl font-bold md:text-5xl">
              The <span className="shimmer-text">Orchestra.</span>
            </h2>
            <p className="mt-5 max-w-lg leading-relaxed text-slate-400">
              Intelligent Mode has no forms. The 🎩 <b className="text-slate-200">Boss</b> interviews you
              like a trusted advisor; the 🎼 <b className="text-slate-200">Manager</b> composes the entire
              engagement — which experts play, which sit out, the hand-off lines between them, how deep
              each one goes. Every expert conducts its own junior specialists, and you watch both tiers
              light up live.
            </p>
            <div className="mt-6 flex flex-wrap gap-2">
              {["👑 engagement lead", "🧾 coverage audit", "⚡ manager rulings", "🌟 above & beyond", "✅ QA gate", "🧑‍⚖️ human review"].map((c, i) => (
                <span key={c} className={`glass rounded-full px-3 py-1.5 font-mono text-[10px] text-slate-300 d-${(i % 6) + 1}`}>
                  {c}
                </span>
              ))}
            </div>
          </Reveal>
        </div>
      </section>

      {/* ── AGENT MARQUEE ── */}
      <section className="py-14">
        <Reveal dir="up">
          <p className="mb-6 text-center font-mono text-[11px] uppercase tracking-[0.35em] text-muted">
            The full bench — {AGENTS.length} specialists
          </p>
        </Reveal>
        <div className="marquee">
          <div className="marquee-track">
            {[...AGENTS, ...AGENTS].map((a, i) => (
              <span key={`${a.id}-${i}`}
                className="flex shrink-0 items-center gap-2 rounded-full border border-line bg-panel/80 px-4 py-2 text-xs text-slate-400">
                <span className="text-sm">{a.icon}</span> {a.name}
                <span className="font-mono text-[10px] uppercase" style={{ color: a.accent }}>{a.layer}</span>
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ── PILLARS ── */}
      <section className="mx-auto grid max-w-6xl gap-5 px-6 py-20 md:grid-cols-2 lg:grid-cols-4">
        {PILLARS.map((p, i) => (
          <Reveal key={p.title} dir="up" delay={i * 80}>
            <div className="glass scan-on-hover h-full rounded-3xl p-6 transition hover:-translate-y-1">
              <p.icon size={20} className="mb-3 text-cyan" />
              <h3 className="font-hero text-lg font-bold">{p.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-400">{p.text}</p>
            </div>
          </Reveal>
        ))}
      </section>

      {/* ── LAYERS STRIP ── */}
      <section className="mx-auto max-w-6xl px-6 pb-10">
        <Reveal dir="up">
          <div className="beam mb-8" />
          <div className="flex flex-wrap justify-center gap-2.5">
            {(["L0", "L1", "L2", "L3", "L4", "L5"] as const).map((l, i) => (
              <div key={l} className={`glass rounded-2xl px-5 py-3 text-center transition hover:-translate-y-0.5 d-${i + 1}`}>
                <div className="font-mono text-[10px] text-cyan">{l}</div>
                <div className="text-xs text-slate-300">{LAYER_LABELS[l]}</div>
                <div className="font-mono text-[10px] text-slate-400">
                  {AGENTS.filter((a) => a.layer === l).length} live
                </div>
              </div>
            ))}
          </div>
        </Reveal>
      </section>

      {/* ── FINAL CTA ── */}
      <section className="mx-auto max-w-4xl px-6 py-20">
        <Reveal dir="scale">
          <div className="g-border relative overflow-hidden rounded-[2rem] p-10 text-center md:p-14">
            <h2 className="font-hero text-3xl font-bold md:text-5xl">
              Convene the board in <span className="shimmer-text">60 seconds.</span>
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-slate-400">
              No sign-up. No keys required. Pick a door, describe the situation, and watch
              a whole boardroom of specialists earn your verdict.
            </p>
            <Link href="/studio"
              className="btn-glow mt-8 inline-block rounded-2xl bg-gradient-to-r from-brand to-cyan px-10 py-4 font-hero text-base font-bold text-ink transition hover:brightness-110">
              ⚡ Open the Studio
            </Link>
          </div>
        </Reveal>
      </section>

      <footer className="border-t border-line py-8 text-center font-mono text-[10px] text-slate-400">
        EIP provides analytics and education, not investment advice. It is not SEBI-registered.
      </footer>
    </div>
  );
}
