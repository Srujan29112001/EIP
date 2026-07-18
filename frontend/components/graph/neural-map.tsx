"use client";

/** THE DECISION GRAPH — EIP's neural map.
 *
 * Ported from SRUJAN.K's KnowledgeGraph3D (the portfolio's "Neural Map"):
 * same hand-rolled 3D force simulation in Float32Arrays (zero re-renders per
 * frame), same InstancedMesh cloud, same light-it-up query, same side panel.
 * Only the data changed: instead of projects orbiting a person, claims,
 * risks and agents orbit a decision.
 */

import { useMemo, useRef, useState } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Html, OrbitControls } from "@react-three/drei";
import * as THREE from "three";
import { matchNodes, type GEdge, type GNode } from "@/lib/graph-data";

// ── force-simulated node cloud (runs inside the R3F canvas) ─────────────────
function GraphScene({ nodes, edges, highlights, onSelect }: {
  nodes: GNode[];
  edges: GEdge[];
  highlights: Map<string, number>;
  onSelect: (node: GNode | null) => void;
}) {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const linesRef = useRef<THREE.LineSegments>(null);
  const [hovered, setHovered] = useState<number | null>(null);
  const frameCount = useRef(0);
  const { invalidate } = useThree();

  // physics state lives in refs — no react re-renders per frame
  const sim = useMemo(() => {
    const pos = new Float32Array(nodes.length * 3);
    const vel = new Float32Array(nodes.length * 3);
    const indexById = new Map(nodes.map((n, i) => [n.id, i]));
    // seed: decision at the core, layer hubs inner shell, agents mid, claims outer
    nodes.forEach((n, i) => {
      const r = n.type === "center" ? 0.1 : n.type === "category" ? 6 : n.type === "agent" ? 10 : 16;
      const theta = (i * 2.399963) % (Math.PI * 2); // golden angle
      const phi = Math.acos(1 - 2 * ((i + 0.5) / nodes.length));
      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);
    });
    const edgeIdx = edges
      .map((e) => [indexById.get(e.source), indexById.get(e.target)])
      .filter((p): p is [number, number] => p[0] !== undefined && p[1] !== undefined);
    return { pos, vel, edgeIdx };
  }, [nodes, edges]);

  const dummy = useMemo(() => new THREE.Object3D(), []);
  const baseColors = useMemo(() => nodes.map((n) => new THREE.Color(n.color)), [nodes]);
  const dimColor = useMemo(() => new THREE.Color("#1e293b"), []);
  const litColor = useMemo(() => new THREE.Color("#34D399"), []);

  useFrame(() => {
    const { pos, vel, edgeIdx } = sim;
    const n = nodes.length;
    frameCount.current++;
    const alpha = Math.max(0, 1 - frameCount.current / 420); // settle ~7s

    if (alpha > 0) {
      // pairwise repulsion
      for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
          let dx = pos[i * 3] - pos[j * 3];
          let dy = pos[i * 3 + 1] - pos[j * 3 + 1];
          let dz = pos[i * 3 + 2] - pos[j * 3 + 2];
          let d2 = dx * dx + dy * dy + dz * dz;
          if (d2 < 0.01) { dx = Math.random() - 0.5; dy = Math.random() - 0.5; dz = Math.random() - 0.5; d2 = 0.5; }
          const f = (6 / d2) * alpha * 0.016;
          const d = Math.sqrt(d2);
          vel[i * 3] += (dx / d) * f; vel[i * 3 + 1] += (dy / d) * f; vel[i * 3 + 2] += (dz / d) * f;
          vel[j * 3] -= (dx / d) * f; vel[j * 3 + 1] -= (dy / d) * f; vel[j * 3 + 2] -= (dz / d) * f;
        }
      }
      // springs along edges
      for (const [a, b] of edgeIdx) {
        const dx = pos[b * 3] - pos[a * 3];
        const dy = pos[b * 3 + 1] - pos[a * 3 + 1];
        const dz = pos[b * 3 + 2] - pos[a * 3 + 2];
        const d = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1;
        const rest = nodes[b].type === "category" ? 7 : 4.5;
        const f = (d - rest) * 0.02 * alpha;
        vel[a * 3] += (dx / d) * f; vel[a * 3 + 1] += (dy / d) * f; vel[a * 3 + 2] += (dz / d) * f;
        vel[b * 3] -= (dx / d) * f; vel[b * 3 + 1] -= (dy / d) * f; vel[b * 3 + 2] -= (dz / d) * f;
      }
      // gravity + integrate
      for (let i = 0; i < n; i++) {
        vel[i * 3] -= pos[i * 3] * 0.002 * alpha;
        vel[i * 3 + 1] -= pos[i * 3 + 1] * 0.002 * alpha;
        vel[i * 3 + 2] -= pos[i * 3 + 2] * 0.002 * alpha;
        vel[i * 3] *= 0.88; vel[i * 3 + 1] *= 0.88; vel[i * 3 + 2] *= 0.88;
        pos[i * 3] += vel[i * 3]; pos[i * 3 + 1] += vel[i * 3 + 1]; pos[i * 3 + 2] += vel[i * 3 + 2];
      }
    }

    // write instances
    const mesh = meshRef.current;
    if (mesh) {
      const hasHighlights = highlights.size > 0;
      for (let i = 0; i < n; i++) {
        const node = nodes[i];
        const lit = highlights.has(node.id);
        const dimmable = node.type === "claim" || node.type === "risk";
        const scale = (node.size / 9) * (hovered === i ? 1.5 : 1) * (lit ? 1.35 : 1);
        dummy.position.set(pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2]);
        dummy.scale.setScalar(scale);
        dummy.updateMatrix();
        mesh.setMatrixAt(i, dummy.matrix);
        const color = lit ? litColor : hasHighlights && dimmable ? dimColor : baseColors[i];
        mesh.setColorAt(i, color);
      }
      mesh.instanceMatrix.needsUpdate = true;
      if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    }

    // write edge lines
    const lines = linesRef.current;
    if (lines) {
      const geo = lines.geometry;
      const arr = geo.attributes.position.array as Float32Array;
      sim.edgeIdx.forEach(([a, b], k) => {
        arr[k * 6] = pos[a * 3]; arr[k * 6 + 1] = pos[a * 3 + 1]; arr[k * 6 + 2] = pos[a * 3 + 2];
        arr[k * 6 + 3] = pos[b * 3]; arr[k * 6 + 4] = pos[b * 3 + 1]; arr[k * 6 + 5] = pos[b * 3 + 2];
      });
      geo.attributes.position.needsUpdate = true;
    }
    invalidate();
  });

  const linePositions = useMemo(() => new Float32Array(sim.edgeIdx.length * 6), [sim.edgeIdx.length]);
  const hoveredNode = hovered !== null ? nodes[hovered] : null;

  return (
    <>
      <ambientLight intensity={0.6} />
      <pointLight position={[20, 20, 20]} intensity={900} color="#67e8f9" />
      <pointLight position={[-20, -10, -20]} intensity={500} color="#a78bfa" />

      <lineSegments ref={linesRef}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[linePositions, 3]} />
        </bufferGeometry>
        <lineBasicMaterial color="#22d3ee" transparent opacity={0.12} />
      </lineSegments>

      <instancedMesh
        ref={meshRef}
        args={[undefined, undefined, nodes.length]}
        onPointerMove={(e) => { e.stopPropagation(); setHovered(e.instanceId ?? null); }}
        onPointerOut={() => setHovered(null)}
        onClick={(e) => {
          e.stopPropagation();
          const node = e.instanceId !== undefined ? nodes[e.instanceId] : null;
          onSelect(node && node.detail ? node : null);
        }}
      >
        <sphereGeometry args={[0.55, 20, 20]} />
        <meshStandardMaterial roughness={0.35} metalness={0.25} emissiveIntensity={0.35} />
      </instancedMesh>

      {/* layer-hub labels — always visible */}
      {nodes.map((node, i) =>
        node.type === "category" ? (
          <Html key={node.id}
            position={[sim.pos[i * 3], sim.pos[i * 3 + 1] + 1.6, sim.pos[i * 3 + 2]]}
            center style={{ pointerEvents: "none" }}>
            <span className="whitespace-nowrap font-mono text-[11px] font-bold tracking-widest"
              style={{ color: node.color }}>
              {node.label.toUpperCase()}
            </span>
          </Html>
        ) : null,
      )}

      {/* hover tooltip */}
      {hoveredNode && hovered !== null && (
        <Html position={[sim.pos[hovered * 3], sim.pos[hovered * 3 + 1] + 1.3, sim.pos[hovered * 3 + 2]]}
          center style={{ pointerEvents: "none" }}>
          <span className="whitespace-nowrap rounded border border-cyan-500/30 bg-black/85 px-2 py-1 font-mono text-[10px] text-cyan-300">
            {hoveredNode.label}{highlights.has(hoveredNode.id) ? ` · ${highlights.get(hoveredNode.id)}%` : ""}
          </span>
        </Html>
      )}
    </>
  );
}

// ── section wrapper: query bar, canvas, detail side panel ───────────────────
export function NeuralMap({ nodes, edges, height = 520 }: {
  nodes: GNode[];
  edges: GEdge[];
  height?: number;
}) {
  const [selected, setSelected] = useState<GNode | null>(null);
  const [query, setQuery] = useState("");
  const [highlights, setHighlights] = useState<Map<string, number>>(new Map());

  const runQuery = () => setHighlights(query.trim().length >= 3 ? matchNodes(query, nodes) : new Map());
  const clearQuery = () => { setQuery(""); setHighlights(new Map()); };
  const matches = [...highlights.entries()]
    .map(([id, rel]) => ({ node: nodes.find((n) => n.id === id), rel }))
    .filter((m): m is { node: GNode; rel: number } => Boolean(m.node))
    .sort((a, b) => b.rel - a.rel);

  if (nodes.length < 3) {
    return (
      <div className="glass card-in rounded-2xl p-6 text-center font-mono text-xs text-slate-500">
        The Decision Graph grows as the board works — run an analysis to map it.
      </div>
    );
  }

  return (
    <div>
      {/* query bar — "light it up" */}
      <div className="mb-3 flex flex-col gap-2 sm:flex-row">
        <div className="flex flex-1 items-center gap-2 rounded-xl border border-cyan-900/40 bg-ink/80 px-4">
          <svg className="h-4 w-4 shrink-0 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M17 11a6 6 0 11-12 0 6 6 0 0112 0z" />
          </svg>
          <input value={query} onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") runQuery(); }}
            placeholder='Try "regulation" or "runway" — see what lights up'
            className="flex-1 bg-transparent py-2.5 text-sm text-white outline-none placeholder:text-slate-600" />
          {highlights.size > 0 && (
            <button onClick={clearQuery} className="p-1 text-slate-500 hover:text-white" aria-label="Clear">✕</button>
          )}
        </div>
        <button onClick={runQuery} disabled={query.trim().length < 3}
          className="rounded-xl bg-gradient-to-r from-brand to-cyan px-5 py-2.5 text-sm font-bold text-ink transition hover:brightness-110 disabled:opacity-40">
          Light it up
        </button>
      </div>

      <div className="grid gap-3 lg:grid-cols-[1fr_280px]">
        {/* 3D canvas */}
        <div className="relative overflow-hidden rounded-2xl border border-cyan-900/30 bg-ink/60"
          style={{ height }}>
          <Canvas frameloop="demand" camera={{ position: [0, 4, 30], fov: 50 }} dpr={[1, 1.75]}>
            <GraphScene nodes={nodes} edges={edges} highlights={highlights} onSelect={setSelected} />
            <OrbitControls enablePan={false} enableZoom={false} autoRotate autoRotateSpeed={0.6} makeDefault />
          </Canvas>
          <div className="pointer-events-none absolute bottom-3 left-3 flex flex-wrap gap-1.5 font-mono text-[10px]">
            <span className="rounded border border-white/10 bg-black/70 px-2 py-1 text-slate-400">
              {nodes.filter((n) => n.type === "agent").length} agents · {nodes.filter((n) => n.type === "claim").length} claims · {nodes.filter((n) => n.type === "risk").length} risks
            </span>
            <span className="rounded border border-white/10 bg-black/70 px-2 py-1">
              <span style={{ color: "#8b5cf6" }}>● analysis</span>{" "}
              <span style={{ color: "#22d3ee" }}>● sourced</span>{" "}
              <span style={{ color: "#fbbf24" }}>● unsourced</span>{" "}
              <span style={{ color: "#fb7185" }}>● risk/crucible</span>{" "}
              <span style={{ color: "#eab308" }}>● synthesis</span>
            </span>
          </div>
        </div>

        {/* side panel */}
        <div className="space-y-3">
          {selected?.detail ? (
            <div className="rounded-2xl border border-cyan-900/30 bg-ink/80 p-4">
              <div className="mb-2 flex items-start justify-between gap-2">
                <h3 className="font-display text-sm font-bold leading-snug text-white">
                  {selected.detail.title || selected.label}
                </h3>
                <button onClick={() => setSelected(null)} className="shrink-0 p-1 text-slate-500 hover:text-white" aria-label="Close">✕</button>
              </div>
              <div className="mb-2 flex flex-wrap gap-1.5">
                {selected.detail.kind && (
                  <span className="rounded border border-white/15 px-2 py-0.5 font-mono text-[10px] text-slate-400">{selected.detail.kind}</span>
                )}
                {selected.detail.metric && (
                  <span className="rounded bg-white/5 px-2 py-0.5 font-mono text-[10px] text-slate-400">{selected.detail.metric}</span>
                )}
              </div>
              <p className="mb-2 max-h-64 overflow-y-auto whitespace-pre-line pr-1 text-[13px] leading-relaxed text-slate-300">
                {selected.detail.description}
              </p>
              <div className="mb-2 flex flex-wrap gap-1">
                {(selected.detail.tech || []).map((t) => (
                  <span key={t} className="rounded border border-white/10 bg-panel-2 px-1.5 py-0.5 font-mono text-[10px] text-slate-500">{t}</span>
                ))}
              </div>
              {(selected.detail.links || []).map((l) => (
                <a key={l.url} href={l.url} target="_blank" rel="noopener noreferrer"
                  className="mr-3 inline-block font-mono text-xs text-cyan-400 underline underline-offset-2 hover:text-cyan-300">
                  {l.label} ↗
                </a>
              ))}
            </div>
          ) : (
            <div className="rounded-2xl border border-cyan-900/30 bg-ink/80 p-4">
              <p className="text-xs leading-relaxed text-slate-400">
                <span className="font-medium text-white">Drag</span> to orbit ·{" "}
                <span className="font-medium text-white">hover</span> for names ·{" "}
                <span className="font-medium text-white">click</span> any node for its evidence and sources.
                Everything here was produced by the board — nothing is decorative.
              </p>
            </div>
          )}

          {highlights.size > 0 && (
            <div className="rounded-2xl border border-emerald-500/25 bg-ink/80 p-4">
              <h3 className="mb-2 font-mono text-[10px] uppercase tracking-wider text-emerald-400">
                {matches.length} matches lit up
              </h3>
              <div className="max-h-52 space-y-1.5 overflow-y-auto pr-1">
                {matches.map(({ node, rel }) => (
                  <button key={node.id} onClick={() => setSelected(node)}
                    className="flex w-full items-center gap-2 text-left text-xs hover:text-white">
                    <span className="w-9 shrink-0 font-mono text-emerald-400">{rel}%</span>
                    <span className="truncate text-slate-400">{node.label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
