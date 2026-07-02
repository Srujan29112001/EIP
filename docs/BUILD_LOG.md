# EIP Build Log

Phase-by-phase progress against `MASTER_PLAN.md`.

## Phase 0 — Foundation (2026-07-02)
- [x] Legacy code + 30 status docs archived to `legacy/` (nothing deleted)
- [x] New README, master plan committed
- [x] Backend skeleton: FastAPI + SSE event contract + scripted demo producer
- [x] Frontend skeleton: Next.js 16 + Tailwind v4 + design tokens + agent registry

## Phase 1 — The Spine (in progress)
- [x] Hybrid LLM gateway (ollama / anthropic / openai / google / deepseek / groq / openrouter / lmstudio / mock) with degradation ladder + structured outputs
- [x] Venture pipeline (LangGraph): 10 real agents end-to-end
  - L0 Intake Parser, Context Profiler, Scope Planner
  - L1 Web Researcher, News Intelligence
  - L2 Market Analyst, Finance Modeler
  - L3 Red Team
  - L4 Weighing Engine (deterministic), Verdict Composer
- [x] Intake wizard (3 steps) → SSE run → live Pipeline Studio (rail + logs + boardroom feed)
- [x] Decision Room v1: verdict card, dimension radar, risks/opportunities, agent accordion
- [ ] User verification gate: real end-to-end run reviewed

## Phase 2 — Grounding & trust (next)
See MASTER_PLAN.md §9.
