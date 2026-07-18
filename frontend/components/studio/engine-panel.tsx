"use client";

/** Engine panel v2 — the Helix "AI engine" step, EIP-scale.
 * 8 cloud providers with per-provider key + model, temperature and max-token
 * sliders, and an optional per-agent override table. Persists to localStorage
 * (keys stay in the browser; sent per-run, never stored server-side).
 */

import { useEffect, useState } from "react";
import { Cpu, Eye, EyeOff, Rocket, Sparkles, Zap } from "lucide-react";
import type { EngineStatus } from "@/lib/api";
import { AGENTS } from "@/lib/agents";
import type { EngineSelection } from "@/lib/types";

export const PROVIDERS: { id: string; label: string; models: string[] }[] = [
  { id: "groq", label: "Groq — free, fast", models: ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"] },
  { id: "google", label: "Google Gemini", models: ["gemini-2.5-flash", "gemini-2.5-pro"] },
  { id: "anthropic", label: "Anthropic (Claude)", models: ["claude-sonnet-4-5", "claude-haiku-4-5"] },
  { id: "openai", label: "OpenAI", models: ["gpt-5-mini", "gpt-5"] },
  { id: "deepseek", label: "DeepSeek", models: ["deepseek-chat", "deepseek-reasoner"] },
  { id: "mistral", label: "Mistral", models: ["mistral-large-latest", "mistral-small-latest"] },
  { id: "xai", label: "xAI (Grok)", models: ["grok-4", "grok-3-mini"] },
  { id: "openrouter", label: "OpenRouter — any model", models: ["deepseek/deepseek-chat", "anthropic/claude-sonnet-4-5", "meta-llama/llama-3.3-70b-instruct"] },
];

const STORE_KEY = "eip_llm";

export function EnginePanel({ engine, onChange, status }: {
  engine: EngineSelection;
  onChange: (e: EngineSelection) => void;
  status?: EngineStatus | null;
}) {
  const [openProvider, setOpenProvider] = useState<string | null>(null);
  const [showKey, setShowKey] = useState<Record<string, boolean>>({});
  const [mode, setMode] = useState<"single" | "perAgent">("single");
  const [hydrated, setHydrated] = useState(false);

  // hydrate persisted config once (keys never leave the browser except per-run)
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORE_KEY);
      if (raw) {
        const saved = JSON.parse(raw) as Partial<EngineSelection> & { mode?: "single" | "perAgent" };
        onChange({ ...engine, ...saved, compute: engine.compute });
        if (saved.mode) setMode(saved.mode);
      }
    } catch { /* fresh start */ }
    setHydrated(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify({
        provider: engine.provider, model: engine.model, api_keys: engine.api_keys,
        api_keys_multi: engine.api_keys_multi, routes: engine.routes,
        agent_routes: engine.agent_routes, temperature: engine.temperature,
        max_tokens_cap: engine.max_tokens_cap, mode,
      }));
    } catch { /* storage full/blocked — per-run config still works */ }
  }, [engine, mode, hydrated]);

  const set = <K extends keyof EngineSelection>(k: K, v: EngineSelection[K]) =>
    onChange({ ...engine, [k]: v });
  const setRoute = (agentId: string, route: string) => {
    const next = { ...engine.agent_routes };
    if (route) next[agentId] = route; else delete next[agentId];
    set("agent_routes", next);
  };

  // 16 key slots per provider; the first non-blank also mirrors to api_keys so
  // the badge/available-provider logic keeps working unchanged
  const keysOf = (p: string): string[] => {
    const arr = engine.api_keys_multi?.[p] ?? [];
    return Array.from({ length: 16 }, (_, i) => arr[i] ?? "");
  };
  const setKeyAt = (p: string, i: number, key: string) => {
    const arr = keysOf(p);
    arr[i] = key;
    const trimmed = arr.map((k) => k.trim());
    const primary = trimmed.find((k) => k) ?? "";
    onChange({
      ...engine,
      api_keys_multi: { ...engine.api_keys_multi, [p]: arr },
      api_keys: { ...engine.api_keys, [p]: primary },
    });
  };
  const hasAnyKey = (p: string) => keysOf(p).some((k) => k.trim());

  const keyedProviders = PROVIDERS.filter((p) => hasAnyKey(p.id));
  const serverProviders = status?.cloud ?? [];
  const temp = engine.temperature ?? 0.4;

  return (
    <div className="space-y-4">
      {/* compute mode cards */}
      <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
        {([
          ["auto", "Auto", Sparkles, "best available"],
          ["local", "Local GPU", Cpu, "private · free · Ollama"],
          ["cloud", "My API keys", Zap, "full depth"],
          ["demo", "Demo", Rocket, "zero keys · deterministic"],
        ] as const).map(([id, label, Icon, sub]) => (
          <button key={id} onClick={() => set("compute", id)}
            className={`rounded-lg border p-3 text-left transition ${
              engine.compute === id ? "border-cyan/70 bg-cyan/10" : "border-line bg-panel-2 hover:border-slate-500"}`}>
            <Icon size={15} className="mb-1 text-cyan" />
            <div className="text-sm font-semibold">{label}</div>
            <div className="font-mono text-[10px] text-muted">{sub}</div>
          </button>
        ))}
      </div>

      {/* local/demo compute needs no cloud keys — hide the provider grid entirely */}
      {["local", "demo"].includes(engine.compute) && (
        <p className="rounded-lg border border-line bg-panel-2 p-3 font-mono text-[10px] leading-relaxed text-slate-400">
          {engine.compute === "local"
            ? "Local GPU mode: everything runs on your machine via Ollama — no API keys, nothing leaves your computer."
            : "Demo mode: deterministic cores only — zero keys, zero network calls to AI providers."}
        </p>
      )}

      {/* provider grid — 8 providers, each with its own key + model */}
      {!["local", "demo"].includes(engine.compute) && (
      <div>
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">providers · bring any key</span>
          {serverProviders.length > 0 && (
            <span className="font-mono text-[10px] text-slate-400">
              server already has: {serverProviders.map((p) => `${p} ✓`).join(" · ")}
            </span>
          )}
        </div>
        <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
          {PROVIDERS.map((p) => {
            const nKeys = keysOf(p.id).filter((k) => k.trim()).length;
            const hasKey = nKeys > 0;
            const onServer = serverProviders.includes(p.id);
            const open = openProvider === p.id;
            return (
              <button key={p.id} onClick={() => setOpenProvider(open ? null : p.id)}
                className={`rounded-lg border p-2.5 text-left transition ${
                  open ? "border-cyan/70 bg-cyan/10"
                    : hasKey || onServer ? "border-ok/40 bg-ok/5" : "border-line bg-panel-2 hover:border-slate-500"}`}>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold">{p.label.split(" — ")[0]}</span>
                  {(hasKey || onServer) && <span className="font-mono text-[10px] text-ok">✓</span>}
                </div>
                <div className="mt-0.5 truncate font-mono text-[10px] text-slate-400">
                  {hasKey ? `${nKeys} key${nKeys > 1 ? "s" : ""} · rotating` : onServer ? "server key" : p.models[0]}
                </div>
              </button>
            );
          })}
        </div>

        {openProvider && (() => {
          const p = PROVIDERS.find((x) => x.id === openProvider)!;
          const slots = keysOf(p.id);
          const filled = slots.filter((k) => k.trim()).length;
          return (
            <div className="mt-2 rounded-lg border border-cyan/30 bg-panel-2 p-3">
              <div className="mb-2 flex flex-wrap items-center gap-2">
                <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
                  {p.label} · up to 16 keys — load spreads across all of them (round-robin)
                </span>
                <span className={`font-mono text-[10px] ${filled >= 7 ? "text-ok" : filled >= 1 ? "text-warn" : "text-slate-400"}`}>
                  {filled}/16 keys{filled < 7 ? " · 7+ recommended for a full War Room + two deliberation rounds" : " ✓"}
                </span>
              </div>
              <div className="space-y-1.5">
                {slots.map((val, i) => (
                  <span key={i} className="relative flex items-center gap-1.5">
                    <span className="w-4 shrink-0 text-center font-mono text-[10px] text-slate-400">{i + 1}</span>
                    <input type={showKey[`${p.id}:${i}`] ? "text" : "password"}
                      value={val}
                      onChange={(e) => setKeyAt(p.id, i, e.target.value)}
                      placeholder={i === 0 ? "paste key (primary)" : `key ${i + 1} (rotation backup)`}
                      className="w-full rounded-md border border-line bg-ink/70 px-3 py-1.5 pr-9 text-sm outline-none focus:border-cyan/60" />
                    <button type="button" onClick={() => setShowKey((s) => ({ ...s, [`${p.id}:${i}`]: !s[`${p.id}:${i}`] }))}
                      className="absolute right-2 text-slate-400 hover:text-slate-300">
                      {showKey[`${p.id}:${i}`] ? <EyeOff size={13} /> : <Eye size={13} />}
                    </button>
                  </span>
                ))}
              </div>
              <label className="mt-2 block">
                <span className="mb-1 block font-mono text-[10px] uppercase tracking-wider text-slate-400">
                  default model (type any id)
                </span>
                <input list={`models-${p.id}`}
                  value={engine.provider === p.id ? engine.model : ""}
                  onChange={(e) => {
                    const m = e.target.value.trim();
                    const route = m ? `${p.id}:${m}` : "";
                    // pin the choice to every tier so it can't be silently downgraded
                    onChange({ ...engine, provider: p.id, model: m,
                      routes: route ? { t1: route, t2: route, t3: route } : {} });
                  }}
                  placeholder={p.models[0]}
                  className="w-full rounded-md border border-line bg-ink/70 px-3 py-2 text-sm outline-none focus:border-cyan/60" />
                <p className="mt-1 font-mono text-[10px] text-slate-400">
                  this exact model is used for every agent (with the fast sibling as a rate-limit fallback)
                </p>
                <datalist id={`models-${p.id}`}>
                  {p.models.map((m) => <option key={m} value={m} />)}
                </datalist>
              </label>
              <p className="mt-2 font-mono text-[10px] leading-relaxed text-slate-400">
                Keys are sent per-run and never stored server-side. Add 5-7 free keys of the same provider
                (e.g. several Groq/Gemini free keys) — the board round-robins across them so a full War Room
                stays narrated instead of exhausting one key half-way.
              </p>
            </div>
          );
        })()}
      </div>
      )}

      {/* temperature + max tokens (Helix sliders) */}
      <div className="grid gap-3 md:grid-cols-2">
        <div className="rounded-lg border border-line bg-panel-2 p-3">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">temperature · creativity</span>
            <span className="rounded bg-brand/20 px-2 py-0.5 font-mono text-[10px] text-brand">{temp.toFixed(2)}</span>
          </div>
          <input type="range" min={0} max={1} step={0.05} value={temp}
            onChange={(e) => set("temperature", Number(e.target.value))}
            className="mt-2 w-full accent-[#6d64a3]" />
          <div className="flex justify-between font-mono text-[10px] text-slate-400">
            <span>precise</span><span>creative</span>
          </div>
        </div>
        <div className="rounded-lg border border-line bg-panel-2 p-3">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">max tokens · per agent call</span>
            <span className="rounded bg-brand/20 px-2 py-0.5 font-mono text-[10px] text-brand">
              {engine.max_tokens_cap === 0 ? "auto" : engine.max_tokens_cap}
            </span>
          </div>
          <input type="range" min={0} max={4096} step={128} value={engine.max_tokens_cap}
            onChange={(e) => set("max_tokens_cap", Number(e.target.value))}
            className="mt-2 w-full accent-[#6d64a3]" />
          <div className="flex justify-between font-mono text-[10px] text-slate-400">
            <span>auto (recommended)</span><span>4096 cap</span>
          </div>
        </div>
      </div>

      {/* one engine vs per-agent */}
      <div>
        <div className="mb-2 flex items-center gap-1">
          <span className="mr-2 font-mono text-[10px] uppercase tracking-wider text-slate-400">routing</span>
          {(["single", "perAgent"] as const).map((m) => (
            <button key={m} onClick={() => setMode(m)}
              className={`rounded-full px-3 py-1 font-mono text-[10px] transition ${
                mode === m ? "bg-brand/20 text-brand" : "text-slate-400 hover:text-slate-300"}`}>
              {m === "single" ? "one engine" : "per-agent"}
            </button>
          ))}
        </div>
        {mode === "perAgent" && (
          <div className="scroll-thin max-h-64 space-y-1 overflow-y-auto rounded-lg border border-line bg-panel-2 p-2">
            {AGENTS.filter((a) => !["weighing_engine"].includes(a.id)).map((a) => {
              const route = engine.agent_routes[a.id] ?? "";
              const [rp, rm] = route.includes(":") ? [route.split(":")[0], route.split(":").slice(1).join(":")] : ["", ""];
              return (
                <div key={a.id} className="flex items-center gap-2 rounded-md px-2 py-1 text-xs hover:bg-white/[0.03]">
                  <span className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: a.accent }} />
                  <span className="w-40 truncate" style={{ color: a.accent }}>{a.name}</span>
                  <select value={rp}
                    onChange={(e) => setRoute(a.id, e.target.value ? `${e.target.value}:${rm || PROVIDERS.find((x) => x.id === e.target.value)?.models[0] || ""}` : "")}
                    className="rounded border border-line bg-ink/70 px-1.5 py-1 font-mono text-[10px] outline-none focus:border-cyan/60">
                    <option value="">default</option>
                    <option value="ollama">ollama (local)</option>
                    {(keyedProviders.length ? keyedProviders : PROVIDERS).map((x) => (
                      <option key={x.id} value={x.id}>{x.id}</option>
                    ))}
                  </select>
                  {rp && (
                    <input value={rm} onChange={(e) => setRoute(a.id, `${rp}:${e.target.value}`)}
                      placeholder="model id"
                      className="flex-1 rounded border border-line bg-ink/70 px-1.5 py-1 font-mono text-[10px] outline-none focus:border-cyan/60" />
                  )}
                </div>
              );
            })}
            <p className="px-2 pt-1 font-mono text-[10px] text-slate-400">
              Weighing Engine takes no model — it is pure math, on purpose.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
