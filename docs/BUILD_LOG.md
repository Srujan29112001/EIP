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

## Phase 3a — Venture board wave (built 2026-07-03)
- [x] 6 new L2 venture agents (`agents/board.py`): Competitor Intelligence, GTM & Distribution, Legal, Tax (India-first), Policy & Compliance, Industry Expert — each deterministic-core + LLM narrative, prompts ported from the legacy generation
- [x] Devil's Advocate (L3): steel-mans the NO case + "what would flip me"
- [x] Connecting Dots (L4): cross-domain patterns + weak signals (honest skip without a model)
- [x] **Depth selector live:** Pulse (11 agents) / Board Meeting (19) / War Room (19, debate rounds in 3b) — wizard step 02, scope planner honors it
- [x] Weighing engine v3: per-dimension agent contribution map; **Regulatory dimension** appears on the radar at board depth; weights renormalized (mirrored in client What-If)
- [x] Gateway: process-wide cloud-concurrency gate (semaphore 3) + escalating 429 backoff — a full 19-agent board now survives a free-tier Groq key (12 LLM-routed calls verified, real devil's-advocate + connecting-dots output)
- Verified: board-depth run → done, 6-dim radar with Regulatory 5.8, verdict 6.3 CONDITIONAL_GO, run persisted

## Frontend Overhaul — "world-class studio" (built 2026-07-03, user feedback round)
Deep extraction pass over all 4 inspiration apps (Helix per-agent AI config + pipeline cards + what-if; SRUJAN.K neural map verbatim; Clinical uncertainty UI; Finance-and-Trading desk patterns), then:
- [x] **4-step wizard:** situation → depth → **Pick your board** (layer-grouped agent toggles; core synthesis locked; scope planner benches the rest with `skipped` stages — verified) → **Engine panel v2**
- [x] **8 providers** (groq / gemini / anthropic / openai / deepseek / mistral / xai / openrouter), each with its own key input (eye-toggle, localStorage-persisted, never stored server-side) + typeable model with suggestions; server-key badges
- [x] **Temperature + max-token sliders** (Helix pattern) honored by the gateway
- [x] **Per-agent routing** ("one engine / per-agent" pill): agent → provider:model overrides, wired through `EngineConfig.agent_routes` into every LLM call
- [x] **Pipeline v2 stage cards:** input chips, per-agent terminal logs, in→out labels, output chips, **"show exact prompt"** reveal (new `prompt` SSE event from `_scored_analysis`) with connector lines that fill as stages complete
- [x] **Flow tab:** the whole workflow as an animated SVG tree — 5 layer columns, pulsing edges into active agents, click-to-inspect (22 nodes / 88 edges on a board run)
- [x] **3D Decision Graph:** SRUJAN.K KnowledgeGraph3D ported (hand-rolled force sim in Float32Arrays, InstancedMesh, hover/click/light-it-up query) — data = agents, sourced/unsourced claims, risks, conflict edges. In the Decision Room + standalone `/graph` page with run selector (three + R3F + drei)
- [x] **Simulation charts on every insight** (new zero-dep `TimeSeries` chart: hover crosshair, projection cones, event markers): Survival simulator (cash curve ±30mo, capital/burn/revenue sliders, cash-out marker), Market pulse (real 1y yfinance series → 6-month scenario cone with drift/volatility sliders), Verdict sensitivity (every dimension bendable)
- [x] market.py ships weekly price series; verified live NIFTY chart + cone in browser; tsc clean

## Phase 3b (part 1) — War Room debates (built 2026-07-03)
- [x] `debate` SSE event + `debate_rounds`: top-3 landed attacks go to open debate — the attacked analyst rebuts or concedes (concession lowers its confidence); Boardroom renders attack/rebuttal/concession turns
- Verified with Groq: finance_modeler + market_analyst produced real rebuttals citing their own evidence

## Design polish — SRUJAN.K aesthetic layer (2026-07-03, feedback round 2)
- [x] Aurora background drift + animated film grain + scanlines (dialed for legibility); panel hover lift/glow; holographic hero text; staged rise-in entrances; ambient agent constellation on the landing hero (pure SVG/CSS)
- [x] Interactive radar: hover an axis → highlights + chips showing exactly which agents scored that dimension (mirror of the weighing map)

## Phase 4 — Trading Co-Pilot (built 2026-07-03)
- [x] **Engines (t0, pure pandas):** `engine/indicators.py` (SMA/EMA/RSI/MACD/Bollinger/ATR, swing S/R, per-reading bullish/bearish verdicts, deterministic trend+momentum scores) · `engine/backtest.py` (BacktestEngine port: SMA-cross + RSI-reversion, hit rate, returns vs buy&hold, max drawdown, sample-size honesty)
- [x] **Markets cluster (`agents/markets.py`):** Market History (2y OHLCV + fundamentals → sourced claims + chart series), Technical Analyst (t0), Backtest Engineer (t0 — every strategy proves itself on the symbol's own history before Quant Signals may speak), Quant Signals (ensemble vote → setup quality + agreement), Risk Manager (t0 — position sizing, 2×ATR stop, max-loss banner), Stock Analyst (t2 valuation narrative)
- [x] **Trading pipeline (`graphs/trading.py`):** trader intake → history+news+macro → deterministic chain → crucible (red team/fact checker/bias auditor reused) → trader weighing (Trend/Momentum/Value/History/RiskFit) → educational setup verdict (FAVOURABLE/MIXED/UNFAVOURABLE — never buy/sell, never price predictions, SEBI framing throughout)
- [x] **Frontend:** Founder/Trader mode tabs; trader intake (symbol, style, capital, risk% slider, compliance note); Trade Desk results card (setup + votes + S/R levels, position plan, backtest proof-of-work table, honesty card); MarketSim/ScoreSim/graph/pipeline all work in trader mode unchanged
- Verified live on RELIANCE.NS via Groq: real SMA/RSI reads, 2y backtests with thin-sample flags, ₹3,000-max-loss position plan, 5.7/10 MIXED_SETUP, persisted to history

## Phase 5 (part 1) — Ask the Board (built 2026-07-03)
- [x] POST /api/ask: grounded Q&A over a persisted run — the spokesperson answers ONLY from the run's verdict/outputs/evidence/attacks, cites agents, admits "not in the record" otherwise
- [x] Decision Room chat panel (suggestions, threaded messages, route chip); runId captured from the done event
- Verified on the RELIANCE run via Groq: answer cited the run's actual 0.8-severity risk

## Next
Phase 3b part 2 (gap-detector replay, Wealth/World clusters), Phase 5 part 2 (outcome tracking, cross-run memory into the Context Profiler), Phase 6 (deploy — Vercel + HF Space, has manual user steps). Options/futures education mode and broker deep-links remain post-launch per MASTER_PLAN §5.4.
