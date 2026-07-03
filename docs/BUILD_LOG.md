# EIP Build Log

Phase-by-phase progress against `MASTER_PLAN.md`.

## Phase 0 — Foundation (2026-07-02)
- [x] Legacy code + 30 status docs archived to `legacy/` (nothing deleted)
- [x] New README, master plan committed
- [x] Backend skeleton: FastAPI + SSE event contract + scripted demo producer
- [x] Frontend skeleton: Next.js 16 + Tailwind v4 + design tokens + agent registry

## Phase 1 — The Spine (verified 2026-07-03)
- [x] Hybrid LLM gateway (ollama / anthropic / openai / google / deepseek / groq / openrouter / lmstudio) with degradation ladder + structured outputs
  - honesty note: pipeline is a structured **asyncio DAG** (LangGraph-compatible state shape); LangGraph checkpointing lands in Phase 3. No separate "mock" provider — `compute=demo` short-circuits to deterministic cores, which serves the same purpose.
- [x] Venture pipeline: 10 real agents end-to-end
  - L0 Intake Parser, Context Profiler, Scope Planner
  - L1 Web Researcher, News Intelligence
  - L2 Market Analyst, Finance Modeler
  - L3 Red Team
  - L4 Weighing Engine (deterministic), Verdict Composer
- [x] Intake wizard (3 steps) → SSE run → live Pipeline Studio (rail + logs + boardroom feed)
- [x] Decision Room v1: verdict card, dimension radar, risks/opportunities, agent accordion
- [x] **Verification gate closed (2026-07-03):** full browser E2E on a real idea — 10/10 agents done, 18 externally-sourced claims with live links, 2 Red Team conflicts, verdict 4.6/10 CONDITIONAL_GO, zero keys, zero local model. TypeScript compiles clean.

### Phase 1.1 — Verification repairs (2026-07-03)
- [x] **Restored `frontend/lib/`** (types/agents/store/api) — the root Python-template `.gitignore` had `lib/`, which silently excluded the entire frontend wiring layer from the Phase-1 commit; `.gitignore` scoped so it can't recur
- [x] Backend: engine-payload version skew no longer hangs the SSE stream forever (EngineConfig built inside try + unknown keys filtered) — regression-tested
- [x] Backend: run tasks held by strong reference; pipeline **cancelled when the client disconnects** (no orphaned token burn)
- [x] Backend: untrusted LLM output hardened — partial JSON inherits fallback keys, non-numeric scores/severities coerced, non-dict red-team attacks dropped (one agent degrades; the run never dies)
- [x] Backend: per-provider model override no longer leaks the user's model name into other providers' fallback calls
- [x] Backend: `.env` loading anchored to `backend/.env` regardless of launch CWD
- [x] Frontend: malformed source URLs can't crash the Boardroom; health-probe failure can't strand the badge; log auto-scroll only follows when pinned to bottom; broken `next lint` script removed

## Phase 2 — Grounding & trust (next)
See MASTER_PLAN.md §9. Scan of portable assets complete: legacy bias DB (human_behaviour_agent) → Bias Auditor; legacy risk taxonomy → Risk Register; Helix `web_search.py` (Tavily+DDG) + `export.py` (markdown) + `charts.tsx` (26 SVG components); market-data connector must be written fresh (no real fetcher exists in any prior repo — Finance-and-Trading's was a random-walk simulator).
