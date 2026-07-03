import Link from "next/link";
import { Eye, Flame, Cpu, Link2 } from "lucide-react";
import { AGENTS, LAYER_LABELS } from "@/lib/agents";

const PILLARS = [
  { icon: Link2, title: "No naked numbers", text: "Every figure carries a live source or an explicit estimate flag. No hallucinated market sizes." },
  { icon: Eye, title: "Glass box", text: "Watch every agent fire — its prompt, its logs, its confidence, its sources. Nothing hidden." },
  { icon: Flame, title: "The Crucible", text: "A red team, devil's advocate and bias auditor attack every thesis. Including your framing." },
  { icon: Cpu, title: "Your GPU, your data", text: "Full local privacy mode via Ollama, any cloud key you choose, or zero-key demo. It never blanks." },
];

export default function Landing() {
  return (
    <div className="mx-auto max-w-5xl px-6">
      <nav className="flex items-center justify-between py-6">
        <span className="font-display text-lg font-bold tracking-tight">
          EIP<span className="text-cyan">.</span>
        </span>
        <span className="flex items-center gap-2">
          <Link href="/graph"
            className="rounded-lg px-3 py-2 font-mono text-xs uppercase tracking-wider text-slate-500 transition hover:text-cyan">
            Graph
          </Link>
          <Link href="/history"
            className="rounded-lg px-3 py-2 font-mono text-xs uppercase tracking-wider text-slate-500 transition hover:text-cyan">
            History
          </Link>
          <Link href="/studio"
            className="rounded-lg border border-line px-4 py-2 font-mono text-xs uppercase tracking-wider text-slate-300 transition hover:border-cyan/60 hover:text-cyan">
            Open Studio →
          </Link>
        </span>
      </nav>

      <header className="py-20 text-center">
        <p className="mb-4 font-mono text-[11px] uppercase tracking-[0.3em] text-cyan">
          The Money Intelligence OS
        </p>
        <h1 className="mx-auto max-w-3xl font-display text-5xl font-bold leading-tight">
          A board of{" "}
          <span className="bg-gradient-to-r from-brand to-cyan bg-clip-text text-transparent">
            40 specialists
          </span>{" "}
          that argues about your decision. In front of you.
        </h1>
        <p className="mx-auto mt-5 max-w-2xl text-slate-400">
          Describe an idea, a stock, or a salary. EIP researches it with live data, runs the real math,
          red-teams the thesis, audits your biases — and hands you a weighted, sourced verdict.
        </p>
        <Link href="/studio"
          className="mt-8 inline-block rounded-xl bg-gradient-to-r from-brand to-cyan px-8 py-3.5 font-display font-bold text-ink transition hover:brightness-110">
          ⚡ Convene the Board
        </Link>
        <p className="mt-3 font-mono text-[10px] text-slate-600">
          works with zero API keys · runs on your own GPU · founder / trader / wealth modes
        </p>
      </header>

      <section className="grid gap-4 py-10 md:grid-cols-2">
        {PILLARS.map((p) => (
          <div key={p.title} className="rounded-xl border border-line bg-panel p-5">
            <p.icon size={18} className="mb-2 text-cyan" />
            <h3 className="font-display font-bold">{p.title}</h3>
            <p className="mt-1 text-sm text-slate-400">{p.text}</p>
          </div>
        ))}
      </section>

      <section className="py-10">
        <h2 className="mb-4 text-center font-mono text-[11px] uppercase tracking-[0.3em] text-muted">
          Five layers of intelligence
        </h2>
        <div className="flex flex-wrap justify-center gap-2">
          {(["L0", "L1", "L2", "L3", "L4"] as const).map((l) => (
            <div key={l} className="rounded-lg border border-line bg-panel px-4 py-2 text-center">
              <div className="font-mono text-[10px] text-cyan">{l}</div>
              <div className="text-xs text-slate-300">{LAYER_LABELS[l]}</div>
              <div className="font-mono text-[9px] text-slate-600">
                {AGENTS.filter((a) => a.layer === l).length} live · more landing
              </div>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-line py-8 text-center font-mono text-[10px] text-slate-600">
        EIP provides analytics and education, not investment advice. It is not SEBI-registered.
      </footer>
    </div>
  );
}
