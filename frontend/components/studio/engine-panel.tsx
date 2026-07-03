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
        agent_routes: engine.agent_routes, temperature: engine.temperature,
        max_tokens_cap: engine.max_tokens_cap, mode,
      }));
    } catch { /* storage full/blocked — per-run config still works */ }
  }, [engine, mode, hydrated]);

  const set = <K extends keyof EngineSelection>(k: K, v: EngineSelection[K]) =>
    onChange({ ...engine, [k]: v });
  const setKey = (p: string, key: string) =>
    set("api_keys", { ...engine.api_keys, [p]: key });
  const setRoute = (agentId: string, route: string) => {
    const next = { ...engine.agent_routes };
    if (route) next[agentId] = route; else delete next[agentId];
    set("agent_routes", next);
  };

  const keyedProviders = PROVIDERS.filter((p) => engine.api_keys[p.id]?.trim());
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

      {/* provider grid — 8 providers, each with its own key + model */}
      <div>
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <span className="font-mono text-[10px] uppercase tracking-wider text-slate-500">providers · bring any key</span>
          {serverProviders.length > 0 && (
            <span className="font-mono text-[10px] text-slate-600">
              server already has: {serverProviders.map((p) => `${p} ✓`).join(" · ")}
            </span>
          )}
        </div>
        <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
          {PROVIDERS.map((p) => {
            const hasKey = Boolean(engine.api_keys[p.id]?.trim());
            const onServer = serverProviders.includes(p.id);
            const open = openProvider === p.id;
            return (
              <button key={p.id} onClick={() => setOpenProvider(open ? null : p.id)}
                className={`rounded-lg border p-2.5 text-left transition ${
                  open ? "border-cyan/70 bg-cyan/10"
                    : hasKey || onServer ? "border-ok/40 bg-ok/5" : "border-line bg-panel-2 hover:border-slate-500"}`}>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold">{p.label.split(" — ")[0]}</span>
                  {(hasKey || onServer) && <span className="font-mono text-[9px] text-ok">✓</span>}
                </div>
                <div className="mt-0.5 truncate font-mono text-[9px] text-slate-600">
                  {engine.api_keys[p.id]?.trim() ? "your key" : onServer ? "server key" : p.models[0]}
                </div>
              </button>
            );
          })}
        </div>

        {openProvider && (() => {
          const p = PROVIDERS.find((x) => x.id === openProvider)!;
          return (
            <div className="mt-2 grid gap-3 rounded-lg border border-cyan/30 bg-panel-2 p-3 md:grid-cols-2">
              <label className="block">
                <span className="mb-1 block font-mono text-[10px] uppercase tracking-wider text-slate-500">
                  {p.label} · API key (never stored server-side)
                </span>
                <span className="relative block">
                  <input type={showKey[p.id] ? "text" : "password"}
                    value={engine.api_keys[p.id] ?? ""}
                    onChange={(e) => setKey(p.id, e.target.value)}
                    placeholder="paste key"
                    className="w-full rounded-md border border-line bg-ink/70 px-3 py-2 pr-9 text-sm outline-none focus:border-cyan/60" />
                  <button type="button" onClick={() => setShowKey((s) => ({ ...s, [p.id]: !s[p.id] }))}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">
                    {showKey[p.id] ? <EyeOff size={14} /> : <Eye size={14} />}
                  </button>
                </span>
              </label>
              <label className="block">
                <span className="mb-1 block font-mono text-[10px] uppercase tracking-wider text-slate-500">
                  default model (type any id)
                </span>
                <input list={`models-${p.id}`}
                  value={engine.provider === p.id ? engine.model : ""}
                  onChange={(e) => onChange({ ...engine, provider: p.id, model: e.target.value })}
                  placeholder={p.models[0]}
                  className="w-full rounded-md border border-line bg-ink/70 px-3 py-2 text-sm outline-none focus:border-cyan/60" />
                <datalist id={`models-${p.id}`}>
                  {p.models.map((m) => <option key={m} value={m} />)}
                </datalist>
              </label>
            </div>
          );
        })()}
      </div>

      {/* temperature + max tokens (Helix sliders) */}
      <div className="grid gap-3 md:grid-cols-2">
        <div className="rounded-lg border border-line bg-panel-2 p-3">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] uppercase tracking-wider text-slate-500">temperature · creativity</span>
            <span className="rounded bg-brand/20 px-2 py-0.5 font-mono text-[10px] text-brand">{temp.toFixed(2)}</span>
          </div>
          <input type="range" min={0} max={1} step={0.05} value={temp}
            onChange={(e) => set("temperature", Number(e.target.value))}
            className="mt-2 w-full accent-[#6d64a3]" />
          <div className="flex justify-between font-mono text-[9px] text-slate-600">
            <span>precise</span><span>creative</span>
          </div>
        </div>
        <div className="rounded-lg border border-line bg-panel-2 p-3">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] uppercase tracking-wider text-slate-500">max tokens · per agent call</span>
            <span className="rounded bg-brand/20 px-2 py-0.5 font-mono text-[10px] text-brand">
              {engine.max_tokens_cap === 0 ? "auto" : engine.max_tokens_cap}
            </span>
          </div>
          <input type="range" min={0} max={4096} step={128} value={engine.max_tokens_cap}
            onChange={(e) => set("max_tokens_cap", Number(e.target.value))}
            className="mt-2 w-full accent-[#6d64a3]" />
          <div className="flex justify-between font-mono text-[9px] text-slate-600">
            <span>auto (recommended)</span><span>4096 cap</span>
          </div>
        </div>
      </div>

      {/* one engine vs per-agent */}
      <div>
        <div className="mb-2 flex items-center gap-1">
          <span className="mr-2 font-mono text-[10px] uppercase tracking-wider text-slate-500">routing</span>
          {(["single", "perAgent"] as const).map((m) => (
            <button key={m} onClick={() => setMode(m)}
              className={`rounded-full px-3 py-1 font-mono text-[10px] transition ${
                mode === m ? "bg-brand/20 text-brand" : "text-slate-500 hover:text-slate-300"}`}>
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
            <p className="px-2 pt-1 font-mono text-[9px] text-slate-600">
              Weighing Engine takes no model — it is pure math, on purpose.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
