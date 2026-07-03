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

## Phase 2 — Grounding & trust (built 2026-07-03)
- [x] **Market Data agent (L1, t0):** yfinance connector — index pulse (NIFTY/S&P/STOXX by geography) + Indian sector-proxy table (Dabur for ayurveda, Nykaa for D2C, …); 1y/3m returns + volatility land as sourced claims
- [x] **Macro Data agent (L1, t0):** World Bank API (key-free) — GDP growth, inflation, lending rate, unemployment per geography, every figure with indicator URL
- [x] **Fact Checker (L3):** analyst claims judged against the evidence board (LLM verdicts supported/partly/unsupported/contradicted, lexical-overlap fallback) + sourced-vs-ESTIMATE numbers audit
- [x] **Bias Auditor (L3):** 8-pattern deterministic screen on the founder's framing (ported/inverted from legacy human_behaviour bias DB) + LLM audit with verbatim quotes; emits `bias` events
- [x] **Weighing engine v2:** Timing dimension now computed from real macro + market pulse (was placeholder 5.0); Evidence dimension penalized by failed fact-checks
- [x] Run persistence: SQLite (`backend/data/eip.db`, fail-soft) + `GET /api/runs`, `GET /api/runs/{id}`
- [x] Gateway: one-shot 429 backoff; verdict-composer prompt compacted (fixed Groq free-tier TPM fallback — verdicts are LLM-written again)
- [x] Frontend: Decision Room v2 — Disagreement panel, agent-by-agent accordion (confidence bars + sourced/ESTIMATE number chips), What-If simulator (client-side deterministic finance core re-run), Markdown/JSON export
- [x] Frontend: wizard shows server-configured engines (groq ✓ / local gpu status); `/history` page over the runs API
- [x] Verified with Groq (llama-3.3-70b): 11 agents, LLM verdict, bias flags with quotes, NIFTY+Dabur+World-Bank evidence, run persisted
- [ ] Deferred within Phase 2 scope: PDF export (Markdown ships; print-to-PDF works meanwhile), what-if server-side re-runs (client deterministic mirror ships)

## Phase 3 — Full board (next)
See MASTER_PLAN.md §9. Portable-asset notes: legacy risk taxonomy → Risk agents; Helix `charts.tsx` (26 SVG components) for richer viz; depth selector (pulse/board/war_room) must drive the Scope Planner when the roster grows.
