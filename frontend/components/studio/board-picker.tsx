"use client";

/** The Board Picker — hand-pick your employees for this project.
 * Layer-grouped agent tree with on/off switches; the scope planner benches
 * whoever you switch off (the synthesis layer can't be benched — someone
 * has to sign the verdict).
 */

import { AGENTS, LAYER_LABELS, type Layer } from "@/lib/agents";

const MANDATORY = new Set(["intake_parser", "context_profiler", "scope_planner", "weighing_engine", "verdict_composer"]);
const PULSE_ONLY = new Set(["web_researcher", "news_intel", "market_data", "macro_data",
  "market_analyst", "finance_modeler", "red_team", "fact_checker", "bias_auditor",
  "weighing_engine", "verdict_composer"]);

export function BoardPicker({ depth, enabled, onChange }: {
  depth: "pulse" | "board" | "war_room";
  enabled: string[];              // empty = everyone in depth scope
  onChange: (ids: string[]) => void;
}) {
  const inDepth = (id: string) => depth !== "pulse" || PULSE_ONLY.has(id) || MANDATORY.has(id);
  const roster = AGENTS.filter((a) => inDepth(a.id));
  const isOn = (id: string) => enabled.length === 0 || enabled.includes(id) || MANDATORY.has(id);

  const toggle = (id: string) => {
    if (MANDATORY.has(id)) return;
    const current = enabled.length === 0 ? roster.map((a) => a.id) : [...enabled];
    const next = current.includes(id) ? current.filter((x) => x !== id) : [...current, id];
    // if everything is back on, collapse to "all" (empty list)
    onChange(next.length >= roster.length ? [] : next);
  };

  const layers = [...new Set(roster.map((a) => a.layer))] as Layer[];
  const onCount = roster.filter((a) => isOn(a.id)).length;

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase tracking-wider text-slate-500">
          your board · {onCount}/{roster.length} convened
        </span>
        {enabled.length > 0 && (
          <button onClick={() => onChange([])}
            className="font-mono text-[10px] text-slate-500 hover:text-cyan">↺ everyone back on</button>
        )}
      </div>
      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
        {layers.map((layer) => (
          <div key={layer} className="rounded-lg border border-line bg-panel-2 p-2.5">
            <div className="mb-1.5 font-mono text-[9px] uppercase tracking-widest text-slate-500">
              {layer} · {LAYER_LABELS[layer]}
            </div>
            <div className="space-y-1">
              {roster.filter((a) => a.layer === layer).map((a) => {
                const on = isOn(a.id);
                const locked = MANDATORY.has(a.id);
                return (
                  <button key={a.id} onClick={() => toggle(a.id)} disabled={locked}
                    title={locked ? "Core stage — always runs" : a.blurb}
                    className={`flex w-full items-center gap-2 rounded-md px-1.5 py-1 text-left text-xs transition ${
                      locked ? "cursor-default opacity-80" : "hover:bg-white/[0.04]"}`}>
                    <span className={`relative h-3.5 w-6 shrink-0 rounded-full transition ${on ? "" : "bg-slate-700"}`}
                      style={on ? { background: `${a.accent}66` } : undefined}>
                      <span className={`absolute top-0.5 h-2.5 w-2.5 rounded-full transition-all ${on ? "left-3" : "left-0.5 bg-slate-500"}`}
                        style={on ? { background: a.accent } : undefined} />
                    </span>
                    <span className={on ? "" : "text-slate-600 line-through decoration-slate-700"}
                      style={on ? { color: a.accent } : undefined}>
                      {a.name}
                    </span>
                    {locked && <span className="ml-auto font-mono text-[8px] uppercase text-slate-600">core</span>}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
