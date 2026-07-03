/** Decision Graph data — turns a run (live store state or a saved run record)
 * into the node/edge cloud the 3D neural map renders. Shapes mirror the
 * SRUJAN.K KnowledgeGraph3D port in components/graph/neural-map.tsx.
 */

import { AGENTS, LAYER_LABELS, agentById, type Layer } from "./agents";
import type { AgentOutput, BoardItem, Verdict } from "./types";

export interface GNode {
  id: string;
  label: string;
  type: "center" | "category" | "agent" | "claim" | "risk";
  color: string;
  size: number;
  detail?: {
    title?: string;
    description: string;
    tech?: string[];
    metric?: string;
    links?: { label: string; url: string }[];
    kind?: string;
  };
}

export interface GEdge { source: string; target: string }

export interface GraphInput {
  brief: Record<string, unknown> | null;
  board: BoardItem[];
  agentOutputs: Record<string, AgentOutput>;
  verdict: Verdict | null;
}

const LAYER_COLORS: Record<Layer, string> = {
  L0: "#94a3b8", L1: "#22d3ee", L2: "#8b5cf6", L3: "#fb7185", L4: "#eab308", L5: "#a78bfa",
};

export function buildGraph(input: GraphInput): { nodes: GNode[]; edges: GEdge[] } {
  const nodes: GNode[] = [];
  const edges: GEdge[] = [];
  const summary = String(input.brief?.summary ?? "Your decision");

  nodes.push({
    id: "center",
    label: summary.length > 42 ? summary.slice(0, 42) + "…" : summary,
    type: "center", color: "#6d64a3", size: 15,
    detail: { title: "The decision", description: summary, kind: "idea" },
  });

  // layer hubs — only for layers that actually produced something
  const ranAgents = AGENTS.filter((a) => input.agentOutputs[a.id]);
  const layers = [...new Set(ranAgents.map((a) => a.layer))];
  for (const layer of layers) {
    nodes.push({
      id: `hub_${layer}`, label: LAYER_LABELS[layer], type: "category",
      color: LAYER_COLORS[layer], size: 10,
    });
    edges.push({ source: "center", target: `hub_${layer}` });
  }

  // agents, wired to their layer hub
  for (const a of ranAgents) {
    const out = input.agentOutputs[a.id];
    const score = typeof out.score === "number" ? `${out.score}/10` : undefined;
    nodes.push({
      id: a.id, label: a.name, type: "agent", color: a.accent, size: 7,
      detail: {
        title: a.name, kind: `${a.layer} · ${a.cluster}`,
        description: [out.verdict_line, out.analysis].filter(Boolean).join("\n\n") || a.blurb,
        tech: out.route ? [String(out.route)] : [],
        metric: score,
      },
    });
    edges.push({ source: `hub_${a.layer}`, target: a.id });
  }

  // claims → their author agent (cap for legibility & sim cost)
  input.board.filter((b) => b.kind === "claim").slice(0, 44).forEach((c, i) => {
    const sourced = Boolean(c.source?.url);
    const id = `claim_${i}`;
    nodes.push({
      id, label: c.text.length > 46 ? c.text.slice(0, 46) + "…" : c.text,
      type: "claim", color: sourced ? "#22d3ee" : "#fbbf24",
      size: 3.6 + (c.confidence ?? 0.5) * 2.2,
      detail: {
        title: sourced ? "Sourced claim" : "Agent claim (unsourced)",
        kind: `by ${agentById(c.agent).name}`,
        description: c.text,
        links: c.source?.url ? [{ label: c.source.name || "source", url: c.source.url }] : [],
      },
    });
    edges.push({ source: input.agentOutputs[c.agent] ? c.agent : "center", target: id });
  });

  // risks from the verdict
  (input.verdict?.risks ?? []).slice(0, 8).forEach((r, i) => {
    const id = `risk_${i}`;
    nodes.push({
      id, label: r.text.length > 40 ? r.text.slice(0, 40) + "…" : r.text,
      type: "risk", color: "#fb7185", size: 5.5,
      detail: { title: "Risk", kind: `flagged by ${agentById(r.source_agent).name}`, description: r.text },
    });
    edges.push({ source: input.agentOutputs[r.source_agent] ? r.source_agent : "center", target: id });
  });

  // conflicts become agent↔agent edges (the argument, made visible)
  for (const c of input.board.filter((b) => b.kind === "conflict")) {
    if (input.agentOutputs[c.agent] && c.vs && input.agentOutputs[c.vs]) {
      edges.push({ source: c.agent, target: c.vs });
    }
  }

  return { nodes, edges };
}

/** Client-side "light it up" matcher — token overlap with node text, 0–100. */
export function matchNodes(query: string, nodes: GNode[]): Map<string, number> {
  const terms = query.toLowerCase().split(/[^a-z0-9]+/).filter((t) => t.length >= 3);
  const out = new Map<string, number>();
  if (!terms.length) return out;
  for (const n of nodes) {
    if (n.type === "category" || n.type === "center") continue;
    const hay = `${n.label} ${n.detail?.description ?? ""} ${n.detail?.kind ?? ""}`.toLowerCase();
    const hits = terms.filter((t) => hay.includes(t)).length;
    if (hits > 0) out.set(n.id, Math.round((hits / terms.length) * 100));
  }
  return out;
}
