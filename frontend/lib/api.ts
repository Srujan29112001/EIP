/** Backend client — health probe + the SSE run consumer (Helix consumeSSE pattern). */

import type { IntakeForm, RunEvent } from "./types";

export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function backendHealth(): Promise<{ ok: boolean; engine?: Record<string, unknown> }> {
  try {
    const r = await fetch(`${API_BASE}/api/health`, { signal: AbortSignal.timeout(4000) });
    if (!r.ok) return { ok: false };
    return await r.json();
  } catch {
    return { ok: false };
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
    headers: { "Content-Type": "application/json" },
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
