# EIP — MASTER PLAN
## From 38 disconnected agents to a working money-intelligence product

> **Status:** APPROVED — GO given 2026-07-02. Building in phases (0 → 6). This document is the source of truth; per-phase progress is tracked in `docs/BUILD_LOG.md`.
> **Author's inputs:** full audit of this repo + your 3 reference apps + your Finance-and-Trading repo (all cloned and read, not guessed), live web research (July 2026), and your actual hardware (RTX 3060 Laptop 6GB VRAM, 16GB RAM, i7-11800H).

---

# PART 1 — WHAT WE ARE ACTUALLY BUILDING

## 1.1 The one-liner

**EIP is a personal money-intelligence operating system.** You tell it your situation — an idea, a dilemma, a stock, a salary — and a transparent board of ~40 specialist AI agents researches it with *real live data*, argues about it, audits your biases, and hands you a weighted, sourced, exportable decision — while you watch every step happen.

Not a chatbot. Not a report generator. A **glass-box decision engine** for the three money questions everyone has:

| Mode | The user's question | What runs |
|---|---|---|
| 🚀 **Founder Mode** | "Should I build this? How?" | Venture pipeline (market, finance, legal, tax, GTM, competition, policy, bias audit → verdict) |
| 📈 **Trader Mode** | "Should I buy/sell/hold this? When?" | Trading Co-Pilot (live data, technicals, timeseries ML, regime detection, backtests, paper trading) |
| 💰 **Wealth Mode** | "What do I do with the money I have?" | Wealth pipeline (salary/budget, portfolio allocation, debt, schemes, FIRE planning, location opportunities) |

One intake. One pipeline view. One decision room. Three modes sharing the same 40-agent brain, the same live-data layer, and the same memory graph.

## 1.2 Why this wins (from live competitor research, July 2026)

Every existing "AI idea validator" has the **same three fatal criticisms** (verified from 2026 comparison reviews):

1. **Hallucinated numbers** — "ValidatorAI confidently stated market size figures that couldn't be verified from any public source"; "VenturusAI frameworks operate on AI-generated competitor lists and market sizing, not live data — a perfectly executed SWOT on imaginary inputs is still imaginary."
2. **Says yes to everything** — no adversarial layer, no calibrated skepticism.
3. **Black box, one-shot** — you get a PDF, you can't see how it thought, you can't interrogate it. DimeADozen charges $59–129 *per report* for this.

EIP's four defensible differentiators (none of which any competitor has together):

1. **No Naked Numbers** — every figure in every output must carry a source chip (live API, web citation, or "LLM estimate — low confidence" flag). This directly kills criticism #1.
2. **Radical transparency** (from your Helix) — the user watches every agent fire, sees its exact prompt, its raw output, its confidence, and the live log. Kills criticism #3.
3. **The Crucible** — a built-in adversarial layer: a red-team agent attacks the thesis, a devil's advocate argues the "no" case, a bias auditor scores the *user's own framing*. Disagreement between agents is **preserved and shown**, not averaged away. Kills criticism #2.
4. **Local privacy mode** — the entire pipeline can run on the user's own GPU (your RTX 3060 → Qwen3-class 4B/8B). Your business idea never leaves your machine. No competitor offers this.

Plus one moat that compounds: **the Decision Graph** — every analysis becomes nodes in a persistent 3D knowledge graph (your SRUJAN.K pattern). The 10th analysis is smarter than the 1st because the system remembers your context, your past decisions, and what happened.

## 1.3 What we are solving (the answer to your question)

The entrepreneur's real problem isn't lack of information — it's **clutter**: 50 browser tabs, gut feelings, unverifiable claims, cognitive bias, and no structured way to weigh conflicting signals. The trader's real problem is the same clutter at higher speed. The salaried saver's problem is the same clutter with lower stakes-awareness.

EIP automates the *weighing*: it turns "I think / I hope / I feel" into "here is the evidence, here is the disagreement, here is the weighted verdict, here is what would change it."

---

# PART 2 — THE HONEST AUDIT (what exists today, verified by reading the code)

This is where this plan differs from the Z.ai output: I read the code. Here is the truth.

## 2.1 EIP repo — reality check

| Layer | Claim (per the 30+ status .md files) | Reality (file evidence) | Verdict |
|---|---|---|---|
| 38 agents | "Complete, 100%" | Real class structure, real LLM *call sites* — but **mock data everywhere**: `connecting_dots_agent.py:117` returns hardcoded fake news items; `market_agent.py:152` returns a canned "Global Market Intelligence Report" with invented market size; confidence scores are hardcoded constants (`0.85`, `0.75`) | **Scaffolding with good bones.** The domain decomposition (which sub-analyses each agent runs) is genuinely good and worth porting. The data is fiction. |
| Orchestrator | "A2A protocol, intelligent routing" | `enhanced_agent_orchestrator.py` is a **chatbot router**: keyword match + one LLM classification → pick 1–3 agents → concatenate answers → one synthesis call. No pipeline, no phases, no streaming, no memory. All 38 agents eagerly instantiated at import. | Replace. Keep the routing keyword table and the `agent_context_sharing` map (lines 224–256) as design input. |
| LLM service | "Multi-provider" | `llm_service.py`: OpenAI/Anthropic/DeepSeek via raw httpx. Works, but: no local GPU path, no fallback chain, no structured outputs, no per-agent routing, hard-crashes without a key, `claude-sonnet-4-5` (stale model IDs) | Replace with the hybrid gateway (§6). |
| Backend API | "Complete" | JWT auth, chat, and OCR/VLM document endpoints exist (`api/v1/analyze.py` — PaddleOCR/Textract/GPT-4V). Chat → orchestrator is the only intelligence path. No SSE. | Keep auth shape + document-upload concept; rebuild the run API. |
| Frontend | — | Streamlit: login, chat, static dashboards. | Discard entirely (as you already decided). |
| Kafka / Spark / Airflow / K8s / Terraform / mobile | "Production ready" | Aspirational scaffolding wired to nothing. Requirements pin `pyspark`, `paddlepaddle`, `kafka-python`, `celery` — a multi-GB install that mostly serves nothing. | **Cut from v1.** Archive, don't delete. This is the single biggest "docs vs reality" gap. |
| The 30+ `*_100_PERCENT_*.md` files | — | Self-congratulatory AI-generated status docs contradicting each other | Archive into `docs/archive/`. The repo must look like a product, not a homework trail. |

**Keep from EIP:** the 38 agent *domain designs* (system prompts, sub-analysis decompositions, the A2A affinity map, routing keywords), the auth pattern, the OCR/document-intake concept, Chroma RAG concept.
**Discard:** orchestrator internals, Streamlit, big-data stack, mock data pathways, stale requirements.

## 2.2 Finance-and-Trading repo — the hidden gems

This "rough minor project" contains three things directly better than anything in EIP:

1. **`hybrid_orchestrator.py`** — a real availability-detection + mode system (`FULL_ONLINE / LLM_ONLY / VLM_ONLY / OFFLINE`) with llama.cpp GGUF offline fallback. This is the embryo of EIP's hybrid inference gateway.
2. **`services/backtesting.py`** — a real `BacktestEngine`: positions, trades, portfolio value, PnL, results calculation. Directly portable into the Trading Co-Pilot.
3. **`rl_agent.py`** — a gym-style `TradingEnvironment` + RL signal agent (with honest mock fallback). Portable as an experimental signal source.

Also: trading signal API shapes (`api/trading.py`), alerts, portfolio models, and a full CI/CD + cost-monitoring GitHub Actions setup worth copying.

## 2.3 The three reference apps — patterns being ported

| App | Pattern | Where it goes in EIP |
|---|---|---|
| **Helix** | LangGraph pipeline emitting `{stage, status, log}` SSE events; the **event contract locked before agents are real** (`backend/app/events.py` mock producer = same shape as real pipeline) | The entire run engine. This "contract-first, mock-first" strategy is how we build EIP without burning tokens: frontend works day 1 against scripted events. |
| **Helix** | `lib/agents.ts` — one registry: id, name, role, tech, blurb, accent color → drives landing page AND live studio | `lib/agents.ts` with ~40 EIP agents, per-layer accent families |
| **Helix** | Studio: sticky stage sidebar + Pipeline/Activity/Results tabs, terminal logs (`info/code/ok/err/warn/muted`), verdict card, custom SVG charts (no chart lib), what-if simulator, live/simulated badge | Pipeline Studio + Decision Room (§4.3, §4.4) |
| **Clinical AI Copilot** | Hybrid per-agent LLM config (`CLINICAL_<ROLE>_*` env pattern), 4-level degradation (cloud → local → deterministic → in-browser simulation), 11-agent SSE pipeline, deterministic scoring beneath LLM narrative, uncertainty shown in UI, $0 deploy (Vercel + HF Space) | The reliability spine: every EIP agent = deterministic core + LLM narrative, so the app **works with zero keys** and gets *better* with keys — never breaks. Same deploy topology. |
| **SRUJAN.K** | `KnowledgeGraph3D.tsx`: R3F InstancedMesh + hand-rolled force sim in Float32Arrays (no re-renders), "light it up" query matching, click-to-focus detail panel | The Decision Graph (§4.6). Physics code ports almost verbatim; only the node/edge source changes. |
| **SRUJAN.K** | Design system: purple/cyan identity, grain + scanlines, custom cursor, GSAP preloader, holographic chat | EIP's visual identity (§7) |

---

# PART 3 — THE INTELLIGENCE ARCHITECTURE (multi-layer, 40 agents)

## 3.1 The five layers

Z.ai gave you a 5-phase *sequence*. That's not enough — a sequence is still a pipeline of yes-men. EIP's layers are **functionally different kinds of intelligence**, and the adversarial layer is what makes the output trustworthy:

```
┌─ L0  GATEWAY ─────────────────────────────────────────────────────┐
│  Intake parser · user-context profile · mode router · scope planner│
│  "Who is asking, what are they really asking, which agents fire"   │
└───────────────────────────┬───────────────────────────────────────┘
┌─ L1  GROUNDING ───────────▼───────────────────────────────────────┐
│  Tool agents that fetch REAL data before any opinion is formed:    │
│  web search · news feeds · market data (yfinance/NSE) · macro APIs │
│  · uploaded docs (OCR) · the user's own Decision Graph memory      │
│  Output: a shared, cited EVIDENCE BOARD (the blackboard)           │
└───────────────────────────┬───────────────────────────────────────┘
┌─ L2  DOMAIN ANALYSIS ─────▼───────────────────────────────────────┐
│  ~28 specialist agents, fired in parallel waves per the scope plan │
│  Each: deterministic core (checklists, math, real data) + LLM      │
│  narrative + self-reported confidence + explicit assumptions       │
└───────────────────────────┬───────────────────────────────────────┘
┌─ L3  THE CRUCIBLE (adversarial) ──▼───────────────────────────────┐
│  Red Team attacks the thesis · Devil's Advocate argues NO ·        │
│  Bias Auditor scores the user's framing · Fact Checker spot-checks │
│  L2 claims against L1 evidence · Debate rounds on conflicts        │
└───────────────────────────┬───────────────────────────────────────┘
┌─ L4  SYNTHESIS & VERDICT ─▼───────────────────────────────────────┐
│  Connecting-Dots (cross-domain patterns) · Weighing Engine         │
│  (deterministic weighted scoring, disagreement preserved) ·        │
│  Verdict Composer (score, go/no-go, risks, opportunities, next     │
│  steps, "what would change this verdict") · gap detector w/ replay │
│  loop (re-fires weak L2 agents with sharper prompts, max 2 loops)  │
└───────────────────────────┬───────────────────────────────────────┘
┌─ L5  MEMORY ──────────────▼───────────────────────────────────────┐
│  Decision Graph (nodes: decisions, entities, risks, outcomes) ·    │
│  user profile evolution · outcome tracking ("what happened after") │
└───────────────────────────────────────────────────────────────────┘
```

## 3.2 The agent roster (~40 agents, reorganized from your 38)

Every agent keeps its EIP domain design (prompts + sub-analyses are ported, not discarded) but gets: (a) a deterministic core, (b) L1 grounding inputs, (c) structured output schema, (d) a model-tier assignment (local/cloud), (e) an accent color + card in the UI.

**L0 Gateway (3):** Intake Parser · Context Profiler ("who am I talking to" — persona, stage, risk tolerance, location, capital) · Scope Planner (which agents, what depth, cost estimate)

**L1 Grounding (5):** Web Researcher · News Intelligence (RSS/GDELT/NewsAPI, replaces mock `_fetch_recent_news`) · Market Data (yfinance/NSE/BSE) · Macro Data (World Bank/RBI/FRED) · Document Analyst (OCR on pitch decks/contracts — keeps EIP's OCR concept)

**L2 Venture cluster (14):** Market Analyst · Competitor Intelligence · Finance Modeler (unit economics, runway — deterministic math core) · Business Model + Recommender (merged) · GTM & Distribution · Marketing Strategist · Legal · Tax (India-first: GST/IT) · Policy & Compliance · Regulator Analysis (SEBI/RBI/CCI) · Subsidies & Schemes (merged Schemes-Monitoring) · Industry Expert · HR & Talent · Loophole/Optimization Predictor

**L2 Markets cluster (8):** Stock Analyst · Technical Analyst (indicators — deterministic) · Quant Signals (timeseries ML ensemble) · Risk Manager (position sizing, VaR — deterministic) · Options & Derivatives · Hedge/Mutual Fund Analyst (merged) · HFT/Microstructure (educational) · Backtest Engineer (ports your `BacktestEngine`)

**L2 Wealth cluster (6):** Salary & Budget Optimizer · Portfolio Allocator · Debt & Banking · FIRE/Goal Planner (absorbs Money-Happiness math) · Real Estate · Location Opportunity Scout (geo-aware: local schemes, markets, costs — your location feature)

**L2 World cluster (5):** Macroeconomist · Geopolitics · International Markets · Trends & Weak Signals · ESG & Impact (absorbs NGO/Philanthropy as a sub-mode)

**L3 Crucible (4):** Red Team (attacks with evidence) · Devil's Advocate (steel-mans the NO) · Bias Auditor (scores user framing + L2 outputs against 20 named biases — ports Human-Behaviour agent) · Fact Checker (samples claims → verifies against L1 board)

**L4 Synthesis (3):** Connecting Dots (cross-domain, ports the good parts) · Weighing Engine (pure deterministic code — no LLM — combines scores × confidence × evidence-quality; preserves dissent) · Verdict Composer (the final narrative + Human-Needs/Philosophy lens folded in as "alignment check": *does this fit the human, not just the market*)

That's 48 named units → ~40 after merges noted above. Phase 1 ships 10 of them end-to-end; the rest arrive in waves (§9).

## 3.3 Agent-to-agent protocol (real this time)

Current EIP "A2A" = concatenate strings. The new protocol is a **typed blackboard**:

- Every agent reads from and writes to a shared run-state: `EvidenceBoard` (cited facts), `ClaimSet` (each claim: text, source, confidence, author-agent), `ConflictLog` (agent X contradicts agent Y on Z).
- Agents don't call each other ad-hoc; the graph defines data edges (your `agent_context_sharing` map becomes the actual LangGraph edge list).
- L3 debate: when `ConflictLog` is non-empty, the two conflicting agents each get one rebuttal round, then the Weighing Engine records the disagreement *as output* ("Finance says X, Market says Y — resolved toward X because evidence weight 0.8 vs 0.5, dissent shown").
- Every inter-agent message is an SSE event → the user literally watches agents talk (your "agent to agent follow" requirement, and the single most demo-able feature).

## 3.4 The EIP Constitution (AI principles — user- and app-perspective)

Baked into every system prompt + enforced in code where possible:

1. **No naked numbers** — every figure carries a source or an explicit "estimate" flag (code-enforced: outputs are schema-validated; unsourced numbers get flagged in UI).
2. **Disagreement is data** — never average away conflict; surface it.
3. **Calibrated humility** — confidence is computed (evidence coverage × model tier × agreement), never hardcoded.
4. **Know the human** — every output is shaped by the Context Profile (a student with ₹50k gets different framing than a funded founder).
5. **Educate, don't just answer** — every verdict includes "how to think about this yourself" (your "teaching the user" requirement).
6. **Hard lines** — no guaranteed-returns language, no "this stock will go up", no unregistered investment advice (§5.4), no execution of trades. The app states plainly what it is: decision support, not an advisor.
7. **Privacy tiers** — Local mode: nothing leaves the machine. BYOK mode: data goes only to the user's chosen provider. Stated on-screen at all times.

---

# PART 4 — THE PRODUCT (pages, inputs, journeys)

## 4.1 Page map

```
/            Landing (the pitch, live pipeline preview, 3 modes)
/studio      THE app: intake wizard → live pipeline → decision room  (Founder + Wealth modes)
/trading     Trading Co-Pilot desk (its own layout; same engine)
/graph       Decision Graph — persistent 3D memory across all runs
/history     Past runs, outcome tracking ("what happened after you decided")
/settings    Providers & keys, local GPU status, privacy tier, profile
```

## 4.2 The Intake (the "steering wheel" — answering your core question)

One conversational wizard, 3 steps, ~2 minutes. **Step 1 is a single smart textarea** — the Intake Parser (L0) extracts structure live as they type (industry, geography, stage chips appear and are user-correctable). No 12-field form up front.

**Step 1 — "What's the situation?"**
- Mode auto-detected from text (or picked): Founder / Trader / Wealth
- One rich prompt: *"Describe your idea, dilemma, or goal — like you'd tell a smart friend."*
- Live-extracted, editable chips: industry · geography (default India 🇮🇳, toggle global) · stage · budget band · team size
- The key extra field: **"What's your biggest uncertainty?"** (this weights the Scope Planner)
- Trader mode instead shows: symbol search (NSE/BSE/US) · style (intraday/swing/position/options) · capital band · risk %
- Wealth mode instead shows: income band · savings · goals · city (for location scout, with consent)

**Step 2 — "Ground it" (optional, skippable)**
- Drop zone: pitch deck / plan / financials / contracts (→ Document Analyst, OCR)
- Competitor or product URLs (→ Web Researcher)
- Portfolio CSV / watchlist (Trader/Wealth)

**Step 3 — "Choose the engine"**
- Depth: **Pulse** (~8 agents, 2 min) / **Board Meeting** (~20 agents, 5–8 min) / **War Room** (all + debate rounds, 10–15 min)
- Compute: **Local GPU** (private, free, RTX 3060 badge with live VRAM check) / **My API key** (provider picker) / **Hybrid** (recommended: local for grunt work, cloud for synthesis) / **Demo** (no keys — simulated, clearly badged)
- Agent roster preview (auto-scoped, individually toggleable) + estimated cost/time
- One sticky **⚡ Convene the Board** button.

## 4.3 The Pipeline Studio (the live run — Helix's studio, scaled to 40 agents)

Two-column command center:

- **Left rail (sticky):** the five layers as collapsible groups; each agent a row with accent dot, status (queued→active→done/error), mini confidence bar when done. Active layer glows. This *is* the "multi-layer intelligence" made visible.
- **Right panel, 3 tabs:**
  - **Pipeline** — vertical timeline of agent cards: input chips (what it received), streaming terminal log (Helix's 6 log kinds), expandable **"Show exact prompt"** (radical transparency), structured output preview, computed confidence + evidence-coverage bars.
  - **Boardroom** (the differentiator tab) — the live agent-to-agent feed: claims landing on the Evidence Board, conflicts opening (`⚔ Finance vs Market on CAC assumption`), debate rebuttals streaming, Red Team attacks, bias flags on *your own framing*. Reads like a group chat between 40 experts.
  - **Results** — fills in live as L4 completes sections; morphs into the Decision Room.

## 4.4 The Decision Room (results)

Top to bottom:
1. **Verdict Card** — score /10 with a **confidence interval band** (not a fake-precise single number), go/conditional-go/no-go, three-sentence reasoning, and **"What would change this verdict"** (the 3 assumptions the verdict is most sensitive to — no competitor has this).
2. **Dimension Radar** — custom SVG (Helix-style, no chart lib): Market · Economics · Regulatory · Execution · Timing · Human-fit, each axis clickable → contributing agents.
3. **The Disagreement Panel** — where agents dissented and why (unique to EIP).
4. **Risk Register** — ranked, each with source agent chip, severity × likelihood, mitigation, and evidence links. Opportunities mirror it.
5. **Agent accordion** — every agent's card: one-line verdict, full analysis, sources, confidence; "weak analysis" flags if the gap detector re-ran it.
6. **What-If Simulator** — sliders (price ±%, CAC, launch city, capital) → re-fires only affected agents (cheap targeted re-runs, not full pipeline).
7. **Ask the Board** — grounded chat, answers *only* from this run's evidence + memory graph, every answer cites which agent/source; suggests "re-run X with…" when asked something outside the evidence.
8. **Export** — PDF decision document / Markdown / JSON / (later) pitch-deck PPTX.

## 4.5 The Trading Co-Pilot desk (`/trading`) — see Part 5.

## 4.6 The Decision Graph (`/graph`)

SRUJAN.K's 3D graph, repurposed: center = you; hubs = your decisions/runs; nodes = entities (markets, companies, regulations, risks), typed & colored by cluster; edges = "informed by / conflicts with / led to". Search "lights up" matches (verbatim port of the matcher). Click node → which agent produced it, in which run, source links. Grows across sessions → the compounding moat, and the input the Context Profiler reads at L0.

---

# PART 5 — THE TRADING CO-PILOT (new flagship agent cluster)

## 5.1 What it is (and honestly, what it is not)

A **real-time decision-support and learning desk** for Indian + global equities: live data, honest quant analytics, backtested-before-shown signals, paper trading, and the full 40-agent context (news, macro, geopolitics feed the trade thesis). It is **not** an execution engine, not an advisory service, and it never promises returns — see §5.4 for why that's not just ethics, it's law.

## 5.2 Data plane (all free-tier viable)

| Source | Data | Notes |
|---|---|---|
| yfinance | NSE/BSE/US OHLCV, fundamentals, options chains | Primary; zero-key; your fintrading repo already assumed this shape |
| NSE public endpoints | Live quotes, indices, FII/DII flows | Free, rate-limited, needs polite client |
| Upstox / Kite Connect / Breeze (optional, user's own account) | Real-time ticks, depth | BYO-broker-key, later phase; Breeze free with ICICI account |
| RSS + GDELT + NewsAPI | Market news, sentiment | Feeds News Intelligence (L1) |
| FRED / World Bank / RBI bulletins | Macro series | Feeds Macroeconomist |

Cached in SQLite/Parquet locally; WebSocket to frontend for live watchlist ticks.

## 5.3 Analytics engine (deterministic core — the Clinical-Copilot pattern applied to markets)

- **Technical layer (pure code, pandas/pandas-ta):** 40+ indicators, support/resistance, volume profile, multi-timeframe alignment (1m→1D per trading style).
- **Timeseries ML (local, runs fine on your GPU/CPU):** regime detection (HMM/clustering: trending/ranging/volatile), volatility forecasting (GARCH), probabilistic price cones (quantile gradient boosting / NeuralProphet — **cones, never point predictions**), anomaly detection on volume/price.
- **Signal ensemble:** technical + ML + sentiment + (experimental) your ported RL agent vote → composite signal with **agreement score**; every signal auto-backtested on trailing data via the ported `BacktestEngine` and shown *with* its historical hit rate, max drawdown, and sample size. A signal that hasn't survived a backtest is never shown.
- **Risk Manager (deterministic, always-on):** position sizing from user's capital & risk %, stop suggestions, exposure/correlation warnings, "this trade risks X% of your capital" banner.
- **Style modes:** Scalping & HFT content is **educational/simulation-only** (retail scalping on 6GB laptop latency is fantasy — the app says so honestly). Intraday/Swing/Position/Options get real workflows: watchlist → thesis card (agents' inputs: news + macro + technicals + Red Team's counter-case) → paper trade → journal.
- **Paper trading first:** every user starts on a simulated book; the Trade Journal agent reviews closed paper trades and teaches ("you cut winners 2× faster than losers — that's loss-aversion", linking Bias Auditor). This is the "makes you smarter" loop.

## 5.4 SEBI compliance (researched July 2026 — this shapes the product)

Findings: unregistered investment advisory is illegal in India; **"for educational purposes only" disclaimers do NOT excuse unregistered advisory activity**; from April 1 2026 retail algo execution requires SEBI-compliant broker APIs, strategy IDs, static IPs; AI does not reduce liability — it increases it.

Therefore, by design:
- EIP presents **analytics, scenarios, and education** — "here is the evidence and the backtest", never "you should buy X".
- **No order execution** in the product. Phase 6+ *may* add order-ticket deep-links into the user's own broker app (user executes, in their broker, under their login) — never auto-trading.
- Personal-use framing: the user analyzes their own decisions with their own keys on their own machine.
- Persistent on-screen: "EIP is not SEBI-registered investment advice. Decisions and outcomes are yours."
- This is a **feature**: "the only trading tool that shows you its homework and refuses to pretend it can predict."

---

# PART 6 — HYBRID INFERENCE (local GPU + BYOK, your core requirement)

## 6.1 Your hardware, honestly

RTX 3060 Laptop = **6GB VRAM** (not 12 like desktop 3060), 16GB RAM. Verified viable (2026 guides):

| Role | Model (Ollama) | VRAM | Used for |
|---|---|---|---|
| Local workhorse | **Qwen3.5:4B** (Q4_K_M) — native tool calling, 256K ctx | ~3.2GB | L0 parsing, L1 extraction/summarization, L2 grunt analysis, log narration |
| Local heavy (optional) | Qwen3:8B (Q4_K_M) | ~5.3GB (tight; short ctx) | Better L2 narrative when nothing else on GPU |
| Embeddings | nomic-embed-text / bge-m3 | CPU-fine | RAG + Decision Graph search |
| Fallbacks | gemma3:4b, llama3.2:3b, phi-4-mini | ~3GB | alternates |

Local server: **Ollama** (native Windows, OpenAI-compatible `/v1`, auto VRAM mgmt — the pragmatic 2026 choice over vLLM-in-WSL2 for 6GB). LM Studio supported as alternate endpoint (same API).

## 6.2 The gateway (one code path, evolved from your fintrading `hybrid_orchestrator` + clinical `llm.py`)

`backend/app/core/llm_gateway.py`: provider registry (anthropic / openai / google / deepseek / groq / mistral / openrouter / **ollama / lmstudio** / mock) → unified `complete()` + `stream()` + `structured()` (JSON-schema enforced, retry-on-invalid). Per-agent routing policy:

| Tier | Agents | Default route | Fallback chain |
|---|---|---|---|
| T1 mechanical | L0 parser, L1 extraction, formatting | **Local Qwen3.5-4B** | → cloud-cheap → deterministic |
| T2 analysis | most L2 domain agents | Local-8B or cloud-cheap (Haiku 4.5 / Gemini Flash / DeepSeek) | → local-4B → deterministic core only |
| T3 reasoning | Crucible, Connecting Dots, Verdict, debate | **Cloud flagship (user's key: Claude Sonnet/Opus class, GPT-5 class, Gemini Pro class)** | → cloud-cheap → local-8B (flagged "reduced depth") |
| T0 deterministic | Weighing Engine, Risk Manager, Backtester, indicators | **No LLM at all** | — |

Degradation ladder (clinical pattern): cloud → local → deterministic-only → scripted demo. **The app never shows a blank screen.** Settings page = provider cards, key vault (local encrypted), live Ollama probe (`/api/tags`), per-tier overrides, live cost meter per run.

## 6.3 Cost reality for the user

Pulse run ≈ free (all-local viable). Board Meeting on hybrid ≈ ₹15–60 of API tokens with a cheap cloud tier; War Room with flagship synthesis ≈ ₹80–300. Shown *before* the run (Scope Planner estimates) and metered live. Local-only mode: ₹0 forever — the accessibility story for "as many people as possible."

---

# PART 7 — TECH STACK (July 2026, verified current)

| Layer | Choice | Why |
|---|---|---|
| Frontend | **Next.js 16.2** (Turbopack default, React Compiler stable) + **React 19.2** + TypeScript | Current stable; View Transitions for wizard→studio morph |
| Styling | Tailwind v4 + custom design tokens | Your three apps' idiom |
| Motion | Motion (framer-motion successor) + GSAP (preloader only) | SRUJAN.K parity |
| 3D | React Three Fiber v9 + ported hand-rolled force sim | SRUJAN.K's exact pattern; no drei dependency risk (clinical memory: drei/R19 peer-dep issues → keep raw three where possible) |
| Charts | **Custom SVG components** (port Helix `charts.tsx`) | Radical-transparency aesthetic; zero chart-lib bloat |
| State | Zustand (run state) + TanStack Query (REST) | Simple, streaming-friendly |
| Backend | **FastAPI** (Python 3.12) | Keeps your ecosystem; best-in-class SSE |
| Orchestration | **LangGraph 1.x** (1.0 GA Oct 2025; durable execution, checkpointing, streaming) + custom SSE emitter | Proven in your own Helix; checkpoint/resume = pause-able 15-min War Rooms |
| Structured outputs | Pydantic v2 schemas on every agent | Kills string-concatenation A2A |
| DB | **SQLite** (users, runs, journal, graph tables) via SQLModel; Postgres swap-in when hosted | Zero-infra local product |
| Vectors | Chroma (persistent, local) | Already in EIP; fine at this scale |
| Cache/queue | None in v1 (asyncio + SQLite) — Redis only if hosted multi-user later | Cut Kafka/Spark/Airflow/K8s (audit §2.1) |
| Streaming | **SSE** frontend↔backend direct (EventSource → FastAPI `StreamingResponse`); WebSocket only for market ticks | Helix/clinical proven; SSE survives proxies, trivially resumable |
| Deploy | Frontend → Vercel; Backend → HF Space (free, no-cold-start, SSE-friendly — clinical-verified) **+ first-class "local backend" mode** (user runs `eip up`, frontend at eip.vercel.app connects to `localhost:8000` — the privacy story) | $0 baseline, identical to your clinical topology |
| Observability | Langfuse (self-hostable) or OTel GenAI + run-ledger table | Per-agent tokens/cost/latency → feeds the live cost meter |

Target monorepo:

```
EIP/
├─ frontend/            # Next.js 16 app (landing, studio, trading, graph, settings)
│  ├─ app/  components/{studio,trading,graph,ui}/  lib/{agents.ts,api.ts,run-store.ts,simulate.ts}
├─ backend/
│  └─ app/
│     ├─ core/          # llm_gateway, config, security, events (SSE contract)
│     ├─ graphs/        # LangGraph defs: venture.py, trading.py, wealth.py
│     ├─ agents/        # one module per agent: schema + deterministic core + prompts
│     ├─ grounding/     # web_search, news, market_data, macro, ocr
│     ├─ engine/        # weighing, backtester, risk, indicators, timeseries
│     ├─ memory/        # decision graph store + retrieval
│     └─ api/           # runs (SSE), chat, trading, graph, settings, auth
├─ legacy/              # ARCHIVED: old agents/, streamlit, kafka/spark/airflow, status docs
└─ docs/                # this plan, ADRs, agent specs
```

## 7.1 The SSE contract (locked in Phase 1, Helix-style, before agents are real)

```jsonc
{ "type": "stage",    "agent": "market_analyst", "status": "queued|active|done|error", "layer": "L2" }
{ "type": "log",      "agent": "market_analyst", "kind": "info|code|ok|err|warn|muted", "text": "…" }
{ "type": "claim",    "agent": "market_analyst", "claim": {"text": "...", "source": {...}, "confidence": 0.72} }
{ "type": "conflict", "a": "finance_modeler", "b": "market_analyst", "topic": "CAC assumption" }
{ "type": "debate",   "agent": "finance_modeler", "round": 1, "text": "…" }
{ "type": "bias",     "target": "user_framing", "bias": "optimism", "note": "…" }
{ "type": "partial",  "section": "verdict|radar|risks|…", "data": {…} }
{ "type": "usage",    "agent": "…", "tokens": 1234, "cost_inr": 2.1, "route": "local|cloud" }
{ "type": "done",     "run_id": "…" }
```

Mock producer emits exactly this shape day 1 → frontend + demo mode complete before a single real agent runs (that's how Helix was built, and it's the token-cheapest path).

---

# PART 8 — DESIGN SYSTEM

- **Palette:** ink `#04060f` / panel `#0a1020` surfaces (Helix) + brand purple `#6D64A3` → cyan `#06B6D4` gradient (SRUJAN.K). Layer accent families: L0 slate · L1 cyan · L2-Venture violet · L2-Markets green · L2-Wealth amber · L2-World blue · L3 red/orange · L4 gold · L5 purple. Semantic: ok `#9ae64a` · warn `#fbbf24` · err `#fb7185` (Helix terminal idiom).
- **Type:** Space Grotesk (display) · Inter (body) · JetBrains Mono (logs, metrics, prompts, money).
- **Texture & feel:** grain + scanlines overlay, custom cursor, GSAP counter preloader (SRUJAN.K) — but dialed to ~30% intensity: this is a *decision instrument*, legibility beats spectacle. Live/Local/Demo badge always visible in navbar (graceful-degradation honesty, all three apps).
- **Signature moment:** "Convene the Board" → View Transition into the studio as 40 agent nodes light up layer by layer.

---

# PART 9 — BUILD PHASES (token-conscious; each ends at a reviewable gate)

Principle: **contract-first, mock-first, then depth** (the Helix method) — the most expensive thing (40 real agents) comes *after* the product shell is proven. Sizes: S ≈ one focused session, M ≈ 1–2 sessions, L ≈ 2–3 sessions.

| Phase | Scope | Exit gate (you verify) |
|---|---|---|
| **0. Foundation** (S) | Archive legacy into `legacy/` + `docs/archive/`; monorepo skeleton; new README; scaffold Next 16 + FastAPI; SSE contract + **mock event producer**; design tokens | Repo looks like a product; `npm run dev` + `uvicorn` serve a landing page and a scripted demo run streams into a bare studio |
| **1. The Spine** (L) | llm_gateway (ollama + anthropic/openai/google/deepseek/groq + mock, structured outputs, degradation ladder); LangGraph venture pipeline with **10 real agents** (Intake Parser, Context Profiler, Scope Planner, Web Researcher, News Intel, Market Analyst, Finance Modeler, Red Team, Weighing Engine, Verdict Composer); full intake wizard; live Pipeline Studio; basic Decision Room (verdict + radar + risks) | **A real end-to-end run** on your GPU alone, and better with a key. Demo mode intact. This is already better than every competitor. |
| **2. Grounding & trust** (M) | yfinance/NSE + macro connectors; No-Naked-Numbers enforcement + source chips; Fact Checker; Bias Auditor; disagreement panel; what-if (targeted re-runs); export MD/PDF; run history | Numbers are sourced; run a real idea past it and check the citations yourself |
| **3. Full board** (L) | Port remaining ~25 L2 agents in 4 waves (Venture → Wealth → World → Markets-analysis), each: schema + deterministic core + ported EIP prompts; Boardroom tab (claims/conflicts/debates live); Crucible debate rounds; gap-detector replay loop | War Room run with 35+ agents, visible agent-to-agent debate |
| **4. Trading Co-Pilot** (L) | Data plane + indicator/timeseries/regime engine; BacktestEngine port; signal ensemble w/ auto-backtest; Risk Manager; paper trading + journal; `/trading` desk UI; SEBI guardrails | Paper-trade NIFTY stocks end-to-end; every signal shows its backtest; nothing executes |
| **5. Memory & chat** (M) | Decision Graph store + 3D `/graph` (port SRUJAN.K sim); Ask-the-Board grounded chat; Context Profiler reads memory; outcome tracking | Second run on a related idea visibly uses memory of the first |
| **6. Ship** (M) | Auth polish; onboarding; Vercel + HF Space deploy; local-backend connect flow; landing page; cost meters; README/docs | **Live public URL** + `eip up` local mode; friends can use it with zero keys (demo) or their key |

Later (post-launch): broker BYO-key ticks, PPTX export, mobile PWA, hosted multi-user tier, community agent packs.

---

# PART 10 — RISKS & OPEN QUESTIONS FOR YOU

**Risks (managed in-design):** hallucinated analysis → grounding + Fact Checker + no-naked-numbers; 6GB VRAM ceiling → 4B default + strict tiering + cloud escape hatch; SEBI → analytics-not-advice by construction; scope explosion → phase gates, Trading and Wealth ship *after* the venture spine proves the engine; long-run streams on free hosting → HF Space (no timeout) or local backend, LangGraph checkpoints allow resume.

**Decisions I've made that you can override:** LangGraph over hand-rolled asyncio; SQLite over Postgres for v1; Ollama over LM Studio as default; cutting Kafka/Spark/Airflow/K8s/mobile from v1; merging ~8 near-duplicate agents; paper-trading-only (no execution).

**Resolved decisions (from the GO instruction):**
1. Providers: the app supports **all major providers + local GPU** with a selector (BYOK) — development uses mock/demo + local Ollama, so no key is required to build or demo; any key the user adds upgrades quality automatically via the gateway.
2. GitHub: build is committed to `main` in phases, pushed to make it live.
3. Name: **EIP** stays.

---

*Plan complete. Nothing has been modified in the repo other than adding this file. Say "go ahead" (optionally "go ahead with Phase 0–1") and building starts exactly as phased above.*


---

# PART 11 — BLUEPRINT RECONCILIATION (added 2026-07-04, original EIP blueprint recovered)

The founder recovered the original EIP blueprint document. Audit of this build against it:

## 11.1 Achieved
Multi-agent A2A over a shared typed blackboard (every agent reads/writes the same evidence board + outputs; debates + conflicts are the visible A2A protocol) · real-time intelligence layer (news/web/market/macro before any opinion) · conversational advisor (Ask the Board, grounded) · Founder + Trader modes end-to-end · transparency studio (exact prompts, flow tree, boardroom) · memory (run persistence + 3D Decision Graph) · hybrid multi-LLM (8 cloud + local) · what-if simulation · tax/legal/policy/market/distribution/investment/news coverage.

## 11.2 Deliberately replaced (same outcome, honest engineering)
Kafka/Spark/Airflow/K8s/Neo4j/Mongo/MLflow → asyncio + SQLite + SSE at this scale (the old repo's big-data stack was wired to nothing). GraphRAG → Decision Graph store + retrieval. These return at hosted scale (Phase 10), not before real load exists.

## 11.3 Gaps → new phases (append-only; nothing already built changes)

| Phase | Scope | Exit gate |
|---|---|---|
| **7. Full board** | Wealth mode (salary/budget, portfolio allocator, debt & banking, FIRE planner, real estate, location scout — deterministic money math + LLM narrative) · remaining venture wave (business model, marketing strategy, subsidies & schemes, HR & talent, loophole/optimization predictor, regulator analysis) · world cluster (macroeconomist, geopolitics, international markets, trends & weak signals, ESG) · markets extras (fund analyst, options desk — educational, HFT/microstructure — educational) | A Wealth run and a War-Room founder run fire 40+ agents with real outputs |
| **8. Document intelligence** | Upload P&L/pitch/contract (PDF/TXT) → extraction → Document Analyst (L1) puts cited chunks on the evidence board for ALL agents; full OCR (images/scans) later in the phase | A run grounded in an uploaded document, chunks cited in claims |
| **9. Advisor & memory v2** | Global advisor chat across ALL runs + profile · outcome tracking ("what happened after") · gap-detector replay loop · compliance calendar & alerts · PDF report export | Second run visibly uses memory of the first; alerts land |
| **10. Hosted scale** | Auth + user tiers (blueprint T1/T2/T3) · Postgres/Redis swap-in · queue/workers · observability · mobile PWA · (only now) streaming infra if load demands | Public multi-user deployment |

Constitution, SEBI guardrails, and glass-box rules apply to every new agent unchanged.
