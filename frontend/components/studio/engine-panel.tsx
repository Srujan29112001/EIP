"use client";

/** Engine panel v2 — the Helix "AI engine" step, EIP-scale.
 * 8 cloud providers with per-provider key + model, temperature and max-token
 * sliders, and an optional per-agent override table. Persists to localStorage
 * (keys stay in the browser; sent per-run, never stored server-side).
 */

import { useEffect, useRef, useState } from "react";
import { Cpu, Eye, EyeOff, Layers, Rocket, Sparkles, Zap } from "lucide-react";
import type { EngineStatus } from "@/lib/api";
import { AGENTS } from "@/lib/agents";
import { CLASS_META, SPECIALIZATION, SPECIALIST_MODELS, specialistModel, type SpecClass } from "@/lib/specialists";
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
  const [mode, setMode] = useState<"specialized" | "single" | "perAgent">("specialized");
  const [hydrated, setHydrated] = useState(false);
  const providerGridRef = useRef<HTMLDivElement>(null);

  // hydrate persisted config once (keys never leave the browser except per-run)
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORE_KEY);
      if (raw) {
        const saved = JSON.parse(raw) as Partial<EngineSelection> & { mode?: "specialized" | "single" | "perAgent" };
        const m = saved.mode ?? "specialized";
        onChange({ ...engine, ...saved, compute: engine.compute, specialized: m !== "single" });
        setMode(m);
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
        agent_routes: engine.agent_routes, class_routes: engine.class_routes,
        specialized: engine.specialized, temperature: engine.temperature,
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
  // pin a whole specialty to a provider (+ model). Empty provider = back to auto.
  const setClassRoute = (cls: string, provider: string, model?: string) => {
    const next = { ...engine.class_routes };
    if (!provider) {
      delete next[cls];
    } else {
      const m = (model ?? SPECIALIST_MODELS[provider]?.[cls as SpecClass] ?? "").trim()
        || PROVIDERS.find((x) => x.id === provider)?.models[0] || "";
      next[cls] = m ? `${provider}:${m}` : "";
    }
    set("class_routes", next);
  };
  // jump the user to a provider's key entry (keys are per-provider, added once)
  const openProviderKeys = (id: string) => {
    setOpenProvider(id);
    requestAnimationFrame(() =>
      providerGridRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }));
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
  const cloudOK = !["local", "demo"].includes(engine.compute);
  // a cloud provider the user picked but can't actually reach yet (no key, not on server)
  const needsKey = (p: string) =>
    cloudOK && !!p && p !== "ollama" && !hasAnyKey(p) && !serverProviders.includes(p);
  const autoProvider = engine.provider || keyedProviders[0]?.id || serverProviders[0] || "groq";

  return (
    <div className="space-y-4">
      {/* compute mode cards */}
      <div className="grid grid-cols-2 gap-2 md:grid-cols-5">
        {([
          ["auto", "Auto", Sparkles, "best available"],
          ["hybrid", "Hybrid", Layers, "local + cloud · tiered"],
          ["local", "Local GPU", Cpu, "private · free · Ollama"],
          ["cloud", "My API keys", Zap, "your keys only · no fallback"],
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

      {/* hybrid: explain the tiered split + local-model status */}
      {engine.compute === "hybrid" && (
        <div className="rounded-lg border border-cyan/30 bg-cyan/[0.04] p-3 font-mono text-[10px] leading-relaxed text-slate-300">
          <b className="text-cyan">Hybrid — tiered routing.</b> Your <b className="text-slate-100">local GPU</b> (Ollama)
          runs the high-volume, lower-stakes work — extraction, grounding and domain analysis (t1/t2), so private
          data stays on your machine — and the <b className="text-slate-100">cloud frontier</b> runs the hard
          reasoning &amp; synthesis — crucible, weighing, verdict, reporter (t3). Add your cloud key(s) below for
          the reasoning tier. Strict: no cross-tier fallback.
          <span className="mt-1.5 block">
            {status?.local
              ? <span className="text-ok">✓ local model detected: {status.local_model} — local tiers will run on it.</span>
              : <span className="text-warn">⚠ local model not detected — start Ollama, or the local tiers (extraction/analysis)
                  will show reduced-depth. (Use Auto if you want cloud to cover them instead.)</span>}
          </span>
        </div>
      )}

      {/* provider grid — 8 providers, each with its own key + model */}
      {!["local", "demo"].includes(engine.compute) && (
      <div ref={providerGridRef} className="scroll-mt-4">
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
                <span className={`font-mono text-[10px] ${filled >= 1 ? "text-ok" : "text-slate-400"}`}>
                  {filled}/16 keys{filled >= 1 ? " ✓" : ""}
                </span>
              </div>
              {/* how many keys? — the rule, right where you paste them */}
              <div className="mb-2.5 rounded-md border border-line bg-panel px-2.5 py-2 font-mono text-[10px] leading-relaxed text-slate-400">
                <span className="text-slate-200">How many keys?</span> One is enough to start.
                Add more (up to 16) only for a <b className="text-slate-200">free-tier</b> provider you route a
                lot of agents to — the board rotates across them so it never gets rate-limited half-way through a
                War Room. A <b className="text-slate-200">paid</b> key, or a provider you send only a few agents to,
                needs just <b className="text-slate-200">1</b>. Keys are sent per-run and never stored server-side.
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

      {/* routing: specialist per-class (recommended) vs one engine vs manual per-agent */}
      <div>
        <div className="mb-2 flex flex-wrap items-center gap-1">
          <span className="mr-2 font-mono text-[10px] uppercase tracking-wider text-slate-400">routing</span>
          {(["specialized", "single", "perAgent"] as const).map((m) => (
            <button key={m}
              onClick={() => {
                setMode(m);
                if (m === "single") {
                  // pin a concrete single engine immediately so it's never "everything"
                  const p = engine.provider || autoProvider;
                  const mdl = engine.model || PROVIDERS.find((x) => x.id === p)?.models[0] || "";
                  const route = mdl ? `${p}:${mdl}` : "";
                  onChange({ ...engine, specialized: false, class_routes: {}, provider: p, model: mdl,
                    routes: route ? { t1: route, t2: route, t3: route } : {} });
                } else if (m === "specialized") onChange({ ...engine, specialized: true, model: "", routes: {} });
                else onChange({ ...engine, specialized: true });
              }}
              className={`rounded-full px-3 py-1 font-mono text-[10px] transition ${
                mode === m ? "bg-brand/20 text-brand" : "text-slate-400 hover:text-slate-300"}`}>
              {m === "specialized" ? "🎯 specialized (recommended)" : m === "single" ? "one engine" : "per-agent"}
            </button>
          ))}
        </div>

        {mode === "specialized" && (() => {
          const counts = Object.values(SPECIALIZATION).reduce<Record<string, number>>(
            (acc, c) => ((acc[c] = (acc[c] ?? 0) + 1), acc), {});
          return (
            <div className="rounded-lg border border-line bg-panel-2 p-3">
              <p className="mb-2.5 font-mono text-[10px] leading-relaxed text-slate-400">
                Each specialty gets the model its JOB needs. Leave a row on{" "}
                <b className="text-slate-200">auto</b> to use the best fit on your keyed providers, or pin a
                specific provider + model per specialty. Keys are added once per provider (in the grid above,
                shared by every agent on that provider) — the ⚠ button jumps you there. Routing is strict:
                a failing model reports its reason instead of silently switching.
              </p>
              <div className="space-y-1.5">
                {(Object.keys(CLASS_META) as SpecClass[]).map((cls) => {
                  const cr = engine.class_routes[cls] ?? "";
                  const [cp, cm] = cr.includes(":")
                    ? [cr.split(":")[0], cr.split(":").slice(1).join(":")] : ["", ""];
                  const resolved = cp ? cm : (SPECIALIST_MODELS[autoProvider]?.[cls] ?? "tier default");
                  return (
                    <div key={cls} className="flex flex-wrap items-center gap-2 rounded-lg border border-line bg-panel px-2.5 py-2">
                      <span className="text-sm">{CLASS_META[cls].icon}</span>
                      <span className="w-24 shrink-0 text-xs font-semibold text-slate-200">{CLASS_META[cls].label}</span>
                      <span className="shrink-0 font-mono text-[10px] text-slate-400">{counts[cls] ?? 0} agents</span>
                      <select value={cp}
                        onChange={(e) => setClassRoute(cls, e.target.value)}
                        className="shrink-0 rounded border border-line bg-ink/70 px-1.5 py-1 font-mono text-[10px] outline-none focus:border-cyan/60">
                        <option value="">auto (best keyed)</option>
                        <option value="ollama">ollama (local)</option>
                        {PROVIDERS.map((x) => <option key={x.id} value={x.id}>{x.id}</option>)}
                      </select>
                      <input value={cp ? cm : resolved} readOnly={!cp}
                        list={cp ? `cls-models-${cls}` : undefined}
                        onChange={(e) => setClassRoute(cls, cp, e.target.value)}
                        title={cp ? "model id — type any" : "auto: best model for this specialty on your provider"}
                        className={`min-w-[7rem] flex-1 rounded border border-line px-1.5 py-1 font-mono text-[10px] ${
                          cp ? "bg-ink/70 text-cyan outline-none focus:border-cyan/60" : "bg-panel-2 text-slate-400"}`} />
                      {cp && (
                        <datalist id={`cls-models-${cls}`}>
                          {(PROVIDERS.find((x) => x.id === cp)?.models ?? []).map((m) => <option key={m} value={m} />)}
                        </datalist>
                      )}
                      {needsKey(cp) && (
                        <button type="button" onClick={() => openProviderKeys(cp)}
                          className="shrink-0 rounded-full border border-warn/50 bg-warn/10 px-2 py-0.5 font-mono text-[10px] text-warn transition hover:bg-warn/20">
                          ⚠ add {cp} key
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
              <p className="mt-2 font-mono text-[10px] text-slate-400">
                Popular picks: reasoning → Claude / Gemini 2.5 Pro / o4-mini · quant → o4-mini / DeepSeek-Reasoner ·
                extraction → Groq 8B (fast & cheap). A per-agent override still beats its specialty here.
                Note: only Groq &amp; Gemini have truly free API tiers — Claude/OpenAI/xAI keys need billing enabled.
              </p>
            </div>
          );
        })()}

        {mode === "single" && (() => {
          const setSingle = (provider: string, model?: string) => {
            if (!provider) { onChange({ ...engine, provider: "", model: "", routes: {} }); return; }
            const m = model !== undefined ? model.trim()
              : (provider === engine.provider ? engine.model : "")
                || PROVIDERS.find((x) => x.id === provider)?.models[0] || "";
            const route = m ? `${provider}:${m}` : "";
            onChange({ ...engine, provider, model: m, specialized: false, class_routes: {},
              routes: route ? { t1: route, t2: route, t3: route } : {} });
          };
          return (
            <div className="rounded-lg border border-line bg-panel-2 p-3">
              <p className="mb-2.5 font-mono text-[10px] leading-relaxed text-slate-400">
                One model runs <b className="text-slate-200">every</b> agent. Pick the provider + model for the whole
                board below. Its keys rotate across all you added — and there is <b className="text-slate-200">no
                fallback</b>: if this engine fails, agents show the reason instead of switching providers.
              </p>
              <div className="flex flex-wrap items-center gap-2">
                <span className="shrink-0 font-mono text-[10px] uppercase tracking-wider text-slate-400">the engine</span>
                <select value={engine.provider}
                  onChange={(e) => setSingle(e.target.value)}
                  className="shrink-0 rounded border border-line bg-ink/70 px-2 py-1.5 font-mono text-[11px] outline-none focus:border-cyan/60">
                  <option value="">— pick one provider —</option>
                  <option value="ollama">ollama (local)</option>
                  {PROVIDERS.map((x) => (
                    <option key={x.id} value={x.id}>{x.id}{needsKey(x.id) ? " (needs key)" : ""}</option>
                  ))}
                </select>
                {engine.provider && engine.provider !== "ollama" && (
                  <input value={engine.model} list="single-models"
                    onChange={(e) => setSingle(engine.provider, e.target.value)}
                    placeholder={PROVIDERS.find((x) => x.id === engine.provider)?.models[0] ?? "model id"}
                    className="min-w-[9rem] flex-1 rounded border border-line bg-ink/70 px-2 py-1.5 font-mono text-[11px] text-cyan outline-none focus:border-cyan/60" />
                )}
                <datalist id="single-models">
                  {(PROVIDERS.find((x) => x.id === engine.provider)?.models ?? []).map((m) => <option key={m} value={m} />)}
                </datalist>
                {needsKey(engine.provider) && (
                  <button type="button" onClick={() => openProviderKeys(engine.provider)}
                    className="shrink-0 rounded-full border border-warn/50 bg-warn/10 px-2 py-0.5 font-mono text-[10px] text-warn transition hover:bg-warn/20">
                    ⚠ add {engine.provider} key
                  </button>
                )}
              </div>
              {engine.provider ? (
                <p className="mt-2 font-mono text-[10px] text-slate-400">
                  <b className="text-cyan">{engine.provider}:{engine.model || "(provider default)"}</b> runs all{" "}
                  {AGENTS.length} agents · strict — failures show their reason, nothing switches silently.
                </p>
              ) : (
                <p className="mt-2 font-mono text-[10px] text-warn">
                  No provider picked → the board spreads across every keyed provider by priority. Pick one above to
                  force a single engine.
                </p>
              )}
            </div>
          );
        })()}

        {mode === "perAgent" && (
          <div className="scroll-thin max-h-64 space-y-1 overflow-y-auto rounded-lg border border-line bg-panel-2 p-2">
            {AGENTS.filter((a) => !["weighing_engine"].includes(a.id)).map((a) => {
              const route = engine.agent_routes[a.id] ?? "";
              const [rp, rm] = route.includes(":") ? [route.split(":")[0], route.split(":").slice(1).join(":")] : ["", ""];
              const cls = SPECIALIZATION[a.id];
              const spec = specialistModel(a.id, rp || autoProvider);
              return (
                <div key={a.id} className="flex items-center gap-2 rounded-md px-2 py-1 text-xs hover:bg-white/[0.03]">
                  <span className="shrink-0 text-sm leading-none">{a.icon}</span>
                  <span className="w-32 truncate" style={{ color: a.accent }}>{a.name}</span>
                  {cls && (
                    <span title={`${CLASS_META[cls].label} — its specialist default`}
                      className="shrink-0 rounded-full bg-panel px-1.5 py-0.5 font-mono text-[10px] text-slate-400">
                      {CLASS_META[cls].icon}
                    </span>
                  )}
                  <select value={rp}
                    onChange={(e) => setRoute(a.id, e.target.value ? `${e.target.value}:${rm || specialistModel(a.id, e.target.value) || PROVIDERS.find((x) => x.id === e.target.value)?.models[0] || ""}` : "")}
                    className="shrink-0 rounded border border-line bg-ink/70 px-1.5 py-1 font-mono text-[10px] outline-none focus:border-cyan/60">
                    <option value="">{spec ? `auto · ${spec.split("/").pop()}` : "default"}</option>
                    <option value="ollama">ollama (local)</option>
                    {PROVIDERS.map((x) => (
                      <option key={x.id} value={x.id}>{x.id}{needsKey(x.id) ? " (needs key)" : ""}</option>
                    ))}
                  </select>
                  {rp && rp !== "ollama" && (
                    <input value={rm} onChange={(e) => setRoute(a.id, `${rp}:${e.target.value}`)}
                      placeholder="model id" list={`agent-models-${a.id}`}
                      className="min-w-[6rem] flex-1 rounded border border-line bg-ink/70 px-1.5 py-1 font-mono text-[10px] outline-none focus:border-cyan/60" />
                  )}
                  {rp && (
                    <datalist id={`agent-models-${a.id}`}>
                      {(PROVIDERS.find((x) => x.id === rp)?.models ?? []).map((m) => <option key={m} value={m} />)}
                    </datalist>
                  )}
                  {needsKey(rp) && (
                    <button type="button" onClick={() => openProviderKeys(rp)}
                      className="shrink-0 rounded-full border border-warn/50 bg-warn/10 px-1.5 py-0.5 font-mono text-[10px] text-warn transition hover:bg-warn/20">
                      ⚠ key
                    </button>
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
