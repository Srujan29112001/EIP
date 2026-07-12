/** Backend client — health probe + the SSE run consumer (Helix consumeSSE pattern). */

import type { BossTurn, EngineSelection, IntakeForm, RunEvent } from "./types";
import { userHeaders } from "./user";

export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface Me {
  user_id: string | null;
  email?: string;
  tier: string;
  tier_info: { label: string; max_depth: string; daily_runs: number; note: string };
  runs?: number;
}

export async function getMe(): Promise<Me | null> {
  try {
    const r = await fetch(`${API_BASE}/api/me`, {
      headers: userHeaders(), signal: AbortSignal.timeout(5000),
    });
    return r.ok ? await r.json() : null;
  } catch {
    return null;
  }
}

export interface EngineStatus {
  local: boolean;
  local_model: string;
  cloud: string[];
  compute: string;
}

export async function backendHealth(): Promise<{ ok: boolean; engine?: EngineStatus }> {
  try {
    const r = await fetch(`${API_BASE}/api/health`, { signal: AbortSignal.timeout(4000) });
    if (!r.ok) return { ok: false };
    return await r.json();
  } catch {
    return { ok: false };
  }
}

export interface RunOutcome {
  decision: string;   // proceeded | declined | modified | pending
  status: string;     // good | mixed | bad | too_early
  note?: string;
}

export interface RunSummary {
  id: string;
  created_at: string;
  mode: string;
  situation: string;
  score: number;
  band: string;
  outcome?: RunOutcome | null;
}

export async function listRuns(): Promise<RunSummary[]> {
  try {
    const r = await fetch(`${API_BASE}/api/runs`, {
      headers: userHeaders(), signal: AbortSignal.timeout(6000),
    });
    return r.ok ? await r.json() : [];
  } catch {
    return [];
  }
}

export interface TrackRecord {
  graded: number;
  tracked: number;
  by_status: Record<string, number>;
  go_hit_rate: number | null;
  go_count: number;
}

export async function getTrackRecord(): Promise<TrackRecord | null> {
  try {
    const r = await fetch(`${API_BASE}/api/track-record`, { signal: AbortSignal.timeout(6000) });
    return r.ok ? await r.json() : null;
  } catch {
    return null;
  }
}

export async function recordOutcome(runId: string, outcome: RunOutcome): Promise<boolean> {
  try {
    const r = await fetch(`${API_BASE}/api/runs/${runId}/outcome`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(outcome),
      signal: AbortSignal.timeout(6000),
    });
    return r.ok;
  } catch {
    return false;
  }
}

export async function getRun(id: string): Promise<(RunSummary & { state: Record<string, unknown> }) | null> {
  try {
    const r = await fetch(`${API_BASE}/api/runs/${id}`, { signal: AbortSignal.timeout(8000) });
    return r.ok ? await r.json() : null;
  } catch {
    return null;
  }
}

export async function askBoard(runId: string, question: string):
  Promise<{ answer: string; route: string; grounded: boolean }> {
  const r = await fetch(`${API_BASE}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ run_id: runId, question }),
    signal: AbortSignal.timeout(90000),
  });
  if (!r.ok) throw new Error(`ask failed: ${r.status}`);
  return r.json();
}

/** One 🎩 Boss turn (Intelligent Mode): the whole conversation in, the next
 * question or the finished Brief out. Stateless — nothing persists server-side. */
export async function bossIntake(
  messages: { role: "user" | "assistant"; content: string }[],
  engine?: Partial<EngineSelection>,
): Promise<BossTurn> {
  const r = await fetch(`${API_BASE}/api/intake`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, engine: engine ?? {} }),
    signal: AbortSignal.timeout(60000),
  });
  if (!r.ok) throw new Error(`intake failed: ${r.status}`);
  return r.json();
}

/** The human-in-the-loop decision — wakes a run paused at the regulated-content
 * gate. One shot per run; the pipeline proceeds (approve) or withholds (reject). */
export async function reviewDecision(
  runId: string, decision: "approve" | "reject", note = "",
): Promise<boolean> {
  try {
    const r = await fetch(`${API_BASE}/api/review/${runId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision, note }),
      signal: AbortSignal.timeout(8000),
    });
    return r.ok;
  } catch {
    return false;
  }
}

/**
 * POST the intake and stream the run: parses `data: {…}` SSE lines and feeds
 * each event to `onEvent` (the store's apply). Resolves when the stream closes.
 */
export async function consumeRun(
  form: IntakeForm,
  onEvent: (e: RunEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...userHeaders() },
    body: JSON.stringify(form),
    signal,
  });
  if (!res.ok || !res.body) throw new Error(`run failed: ${res.status}`);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // SSE frames are separated by a blank line; keep the trailing partial frame.
    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";
    for (const frame of frames) {
      for (const line of frame.split("\n")) {
        if (!line.startsWith("data:")) continue;
        try {
          onEvent(JSON.parse(line.slice(5).trim()) as RunEvent);
        } catch {
          // tolerate malformed frames rather than killing the stream
        }
      }
    }
  }
}
