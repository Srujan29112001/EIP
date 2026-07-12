/** The agent registry — the client mirror of backend/app/agents/registry.py.
 *
 * Only implemented agents are listed (they drive the pipeline rail and the
 * landing-page "live" counts); new agents are appended as backend phases land.
 * ids, layers and accents must stay in sync with the backend registry.
 */

export type Layer = "L0" | "L1" | "L2" | "L3" | "L4" | "L5";

export interface AgentInfo {
  id: string;
  name: string;
  layer: Layer;
  cluster: string;
  blurb: string;
  accent: string;
  icon?: string;
}

export const LAYER_LABELS: Record<Layer, string> = {
  L0: "Gateway",
  L1: "Grounding",
  L2: "Domain analysis",
  L3: "The Crucible",
  L4: "Synthesis",
  L5: "Memory",
};

/** Accent families per layer (globals.css tokens), shaded per agent for identity. */
export const AGENTS: AgentInfo[] = [
  // L0 — Orchestration (Intelligent Mode: the Advisory Engine pair — brass)
  { id: "boss", name: "Boss", layer: "L0", cluster: "gateway", blurb: "Conversational intake — a real dialogue distilled into the structured Brief", accent: "#d9a94a" },
  { id: "manager", name: "Manager", layer: "L0", cluster: "gateway", blurb: "Dynamic orchestrator — plans the board from the whole pool, within the guaranteed spine", accent: "#f0cb78" },
  // L0 — Gateway (slate family)
  { id: "intake_parser", name: "Intake Parser", layer: "L0", cluster: "gateway", blurb: "Turns your words into a structured brief", accent: "#94a3b8" },
  { id: "context_profiler", name: "Context Profiler", layer: "L0", cluster: "gateway", blurb: "Works out who is asking — stage, capital, risk", accent: "#a8b6c8" },
  { id: "scope_planner", name: "Scope Planner", layer: "L0", cluster: "gateway", blurb: "Decides which specialists to convene", accent: "#8494ab" },
  // L1 — Grounding (cyan family)
  { id: "web_researcher", name: "Web Researcher", layer: "L1", cluster: "grounding", blurb: "Live web evidence — competitors, markets, claims", accent: "#22d3ee" },
  { id: "news_intel", name: "News Intelligence", layer: "L1", cluster: "grounding", blurb: "What is happening right now in this space", accent: "#67e8f9" },
  { id: "market_data", name: "Market Data", layer: "L1", cluster: "grounding", blurb: "Live prices & index pulse (NSE/global)", accent: "#06b6d4" },
  { id: "macro_data", name: "Macro Data", layer: "L1", cluster: "grounding", blurb: "GDP, inflation, rates from official series", accent: "#38bdf8" },
  { id: "doc_analyst", name: "Document Analyst", layer: "L1", cluster: "grounding", blurb: "Your uploads, on the evidence board", accent: "#0ea5e9" },
  { id: "sentiment_analyst", name: "Sentiment Analyst", layer: "L1", cluster: "grounding", blurb: "News/social mood as a live demand signal", accent: "#7dd3fc" },
  { id: "rag_memory", name: "RAG Memory", layer: "L1", cluster: "grounding", blurb: "Indexes the board — every specialist retrieves its most-relevant evidence", accent: "#5eead4" },
  // L2 — Domain analysis (violet family for venture cluster)
  { id: "market_analyst", name: "Market Analyst", layer: "L2", cluster: "venture", blurb: "Market size, growth, competition — sourced", accent: "#8b5cf6" },
  { id: "market_research", name: "Market Research", layer: "L2", cluster: "venture", blurb: "TAM/SAM/SOM, segments, real demand signals", accent: "#9d7bf5" },
  { id: "finance_modeler", name: "Finance Modeler", layer: "L2", cluster: "venture", blurb: "Unit economics, runway, breakeven — real math", accent: "#a78bfa" },
  { id: "competitor_intel", name: "Competitor Intelligence", layer: "L2", cluster: "venture", blurb: "Positioning map, moats, whitespace", accent: "#7c3aed" },
  { id: "gtm_distribution", name: "GTM & Distribution", layer: "L2", cluster: "venture", blurb: "Channels, launch sequence, CAC reality", accent: "#9333ea" },
  { id: "legal", name: "Legal", layer: "L2", cluster: "venture", blurb: "Structure, contracts, IP exposure", accent: "#c084fc" },
  { id: "tax", name: "Tax (India-first)", layer: "L2", cluster: "venture", blurb: "GST, exemptions, legitimate optimization", accent: "#a855f7" },
  { id: "policy_compliance", name: "Policy & Compliance", layer: "L2", cluster: "venture", blurb: "Acts, licences, compliance calendar", accent: "#8b5cf6" },
  { id: "industry_expert", name: "Industry Expert", layer: "L2", cluster: "venture", blurb: "Insider benchmarks and failure modes", accent: "#6d28d9" },
  // L2 — Venture extras + World cluster (Phase 7)
  { id: "business_model", name: "Business Model", layer: "L2", cluster: "venture", blurb: "Canvas analysis + model recommendation", accent: "#8b5cf6" },
  { id: "marketing_strategy", name: "Marketing Strategist", layer: "L2", cluster: "venture", blurb: "Positioning, CAC/LTV, growth loops", accent: "#a855f7" },
  { id: "subsidies_schemes", name: "Subsidies & Schemes", layer: "L2", cluster: "venture", blurb: "Government money you're leaving on the table", accent: "#c084fc" },
  { id: "banking", name: "Banker & Capital", layer: "L2", cluster: "venture", blurb: "Loans, working capital, schemes, the capital stack", accent: "#b794f6" },
  { id: "pricing_strategist", name: "Pricing Strategist", layer: "L2", cluster: "venture", blurb: "WTP bands, price architecture, the first experiment", accent: "#a78bfa" },
  { id: "supply_chain", name: "Supply-Chain Analyst", layer: "L2", cluster: "venture", blurb: "Input fragility, single points of failure, logistics cost", accent: "#8b5cf6" },
  { id: "cap_table", name: "Cap-Table Modeler", layer: "L2", cluster: "venture", blurb: "Round math, ESOP, founder dilution across scenarios", accent: "#9333ea" },
  { id: "patent_ip", name: "Patent / IP Scout", layer: "L2", cluster: "venture", blurb: "Prior-art, freedom-to-operate, what's protectable", accent: "#c084fc" },
  { id: "insurance_risk", name: "Insurance & Risk-Transfer", layer: "L2", cluster: "venture", blurb: "What to insure, what to transfer, what to engineer around", accent: "#7c3aed" },
  { id: "ai_ml_strategist", name: "AI & ML Strategist", layer: "L2", cluster: "venture", blurb: "AI feasibility, build-vs-buy, data moats, governance", accent: "#818cf8" },
  { id: "data_analytics", name: "Data Science & Analytics", layer: "L2", cluster: "venture", blurb: "Metric tree, instrumentation, honest predictability", accent: "#6366f1" },
  { id: "software_architecture", name: "Software Architecture", layer: "L2", cluster: "venture", blurb: "Feasibility, build cost/time, the scaling wall", accent: "#a5b4fc" },
  { id: "product_ux", name: "Product & UX Design", layer: "L2", cluster: "venture", blurb: "The core loop, PMF signals, onboarding friction", accent: "#c4b5fd" },
  { id: "cybersecurity_privacy", name: "Cybersecurity & Privacy", layer: "L2", cluster: "venture", blurb: "Threat model, privacy-by-design, cert readiness", accent: "#8b5cf6" },
  { id: "fundraising_capital", name: "Fundraising & Capital", layer: "L2", cluster: "venture", blurb: "Round strategy, investor match, terms to never sign", accent: "#a78bfa" },
  { id: "sales_revops", name: "Sales & Revenue Ops", layer: "L2", cluster: "venture", blurb: "Sales motion, pipeline math, comp that works", accent: "#9333ea" },
  { id: "partnerships_bd", name: "Partnerships & BD", layer: "L2", cluster: "venture", blurb: "Alliances and deal structures that keep the company", accent: "#7c3aed" },
  { id: "brand_creative", name: "Brand & Creative", layer: "L2", cluster: "venture", blurb: "Identity, naming, the territory to own", accent: "#c084fc" },
  { id: "pr_communications", name: "PR & Communications", layer: "L2", cluster: "venture", blurb: "Press angles, the outlets that matter, crisis comms", accent: "#d8b4fe" },
  { id: "hr_talent", name: "HR & Talent", layer: "L2", cluster: "venture", blurb: "Hiring order, salary bands, team risk", accent: "#9333ea" },
  { id: "optimization_predictor", name: "Loophole Predictor", layer: "L2", cluster: "venture", blurb: "Legit optimizations + their grey-zone risk", accent: "#7c3aed" },
  { id: "regulator", name: "Regulator Watch", layer: "L2", cluster: "venture", blurb: "SEBI/RBI/CCI/FSSAI posture & scrutiny", accent: "#6d28d9" },
  { id: "macroeconomist", name: "Macroeconomist", layer: "L2", cluster: "world", blurb: "The cycle, read from real series", accent: "#3b82f6" },
  { id: "geopolitics", name: "Geopolitics", layer: "L2", cluster: "world", blurb: "Sanctions, supply chains, exposures", accent: "#60a5fa" },
  { id: "intl_markets", name: "International Markets", layer: "L2", cluster: "world", blurb: "First foreign market + entry friction", accent: "#2563eb" },
  { id: "trends", name: "Trends & Weak Signals", layer: "L2", cluster: "world", blurb: "What's emerging before it's obvious", accent: "#93c5fd" },
  { id: "esg_impact", name: "ESG & Impact", layer: "L2", cluster: "world", blurb: "Where impact becomes a moat", accent: "#1d4ed8" },
  { id: "sustainability_accountant", name: "Sustainability Accountant", layer: "L2", cluster: "world", blurb: "Carbon/impact quantified into cost & moat", accent: "#60a5fa" },
  { id: "deep_tech", name: "Emerging / Deep Tech", layer: "L2", cluster: "world", blurb: "Frontier-tech maturity (TRL), enabler or threat", accent: "#93c5fd" },
  // L2 — Wealth cluster (amber family)
  { id: "salary_budget", name: "Salary & Budget", layer: "L2", cluster: "wealth", blurb: "Savings rate, 50/30/20, surplus math", accent: "#f59e0b" },
  { id: "portfolio_allocator", name: "Portfolio Allocator", layer: "L2", cluster: "wealth", blurb: "Glide-path allocation for your age & risk", accent: "#fbbf24" },
  { id: "fire_planner", name: "FIRE Planner", layer: "L2", cluster: "wealth", blurb: "Your number and the years to reach it", accent: "#f97316" },
  { id: "debt_banking", name: "Debt & Banking", layer: "L2", cluster: "wealth", blurb: "What to pay off first and why", accent: "#fb923c" },
  { id: "real_estate", name: "Real Estate", layer: "L2", cluster: "wealth", blurb: "Rent-vs-buy math, REITs, timing", accent: "#fdba74" },
  { id: "location_scout", name: "Location Scout", layer: "L2", cluster: "wealth", blurb: "Schemes & opportunities where you are", accent: "#ea580c" },
  // L2 — Human layer (pink family — does this fit the human, not just the market)
  { id: "human_behaviour", name: "Human Behaviour", layer: "L2", cluster: "human", blurb: "How real people will actually behave toward this", accent: "#ec4899" },
  { id: "human_needs", name: "Human Needs", layer: "L2", cluster: "human", blurb: "Does this serve a real, durable need (Maslow)", accent: "#f472b6" },
  { id: "consumer_analysis", name: "Consumer Analysis", layer: "L2", cluster: "human", blurb: "Segments, willingness to pay, purchase journey", accent: "#f9a8d4" },
  { id: "production_ops", name: "Production & Ops", layer: "L2", cluster: "human", blurb: "Making the thing: inputs, capacity, fragility", accent: "#db2777" },
  { id: "philosophy_ethics", name: "Philosophy & Ethics", layer: "L2", cluster: "human", blurb: "The examined view — stakeholders, 2nd-order effects", accent: "#be185d" },
  { id: "money_happiness", name: "Money & Happiness", layer: "L2", cluster: "human", blurb: "Will this actually buy a better life", accent: "#fb7185" },
  { id: "philanthropy_impact", name: "Philanthropy & Impact", layer: "L2", cluster: "human", blurb: "Where doing good compounds the mission", accent: "#fda4af" },
  { id: "cohort_retention", name: "Cohort / Retention Analyst", layer: "L2", cluster: "human", blurb: "Retention curves, LTV by cohort, churn drivers", accent: "#f472b6" },
  { id: "customer_success", name: "Customer Success & Retention", layer: "L2", cluster: "human", blurb: "Onboarding, activation, expansion, churn saves", accent: "#f9a8d4" },
  { id: "founder_coaching", name: "Founder Coaching & Org", layer: "L2", cluster: "human", blurb: "Founder leverage, decision hygiene, culture for scale", accent: "#fb7185" },
  // L2 — Markets cluster (green family — the Trading Co-Pilot)
  { id: "technical_analyst", name: "Technical Analyst", layer: "L2", cluster: "markets", blurb: "Indicators, levels, multi-signal read — pure math", accent: "#34d399" },
  { id: "stock_analyst", name: "Stock Analyst", layer: "L2", cluster: "markets", blurb: "Fundamentals + what the market is pricing in", accent: "#6ee7b7" },
  { id: "backtest_engineer", name: "Backtest Engineer", layer: "L2", cluster: "markets", blurb: "Every signal proves itself on history first", accent: "#10b981" },
  { id: "quant_signals", name: "Quant Signals", layer: "L2", cluster: "markets", blurb: "Regime + ensemble vote → setup quality", accent: "#2dd4bf" },
  { id: "risk_manager", name: "Risk Manager", layer: "L2", cluster: "markets", blurb: "Position sizing, stops, exposure — always on", accent: "#059669" },
  { id: "fund_analyst", name: "Fund Analyst", layer: "L2", cluster: "markets", blurb: "Mutual funds & hedge strategies — education", accent: "#4ade80" },
  { id: "options_desk", name: "Options Desk", layer: "L2", cluster: "markets", blurb: "Defined-risk structures — education only", accent: "#22c55e" },
  { id: "microstructure", name: "HFT / Microstructure", layer: "L2", cluster: "markets", blurb: "How the plumbing works — education", accent: "#16a34a" },
  // L3 — Crucible (red/orange family)
  { id: "red_team", name: "Red Team", layer: "L3", cluster: "crucible", blurb: "Attacks the thesis with evidence", accent: "#fb7185" },
  { id: "fact_checker", name: "Fact Checker", layer: "L3", cluster: "crucible", blurb: "Every claim must trace to the evidence board", accent: "#f97316" },
  { id: "bias_auditor", name: "Bias Auditor", layer: "L3", cluster: "crucible", blurb: "Names the biases in your framing", accent: "#fbbf24" },
  { id: "devils_advocate", name: "Devil's Advocate", layer: "L3", cluster: "crucible", blurb: "Steel-mans the NO case", accent: "#f43f5e" },
  // L4 — Synthesis (gold family)
  { id: "connecting_dots", name: "Connecting Dots", layer: "L4", cluster: "synthesis", blurb: "Cross-domain patterns and weak signals", accent: "#fde047" },
  { id: "cross_pollinate", name: "Cross-Pollinator", layer: "L4", cluster: "synthesis", blurb: "Every specialist read against every other — synergies & tensions", accent: "#fbbf24" },
  { id: "compliance_scan", name: "Compliance Sentinel", layer: "L4", cluster: "synthesis", blurb: "Deterministic regulatory red-flag scan — nothing missed", accent: "#f87171" },
  { id: "storytelling", name: "Storyteller", layer: "L4", cluster: "synthesis", blurb: "The pitch — hook, narrative, one-liner, three beats", accent: "#fca5a5" },
  { id: "scenario_planner", name: "Scenario Planner", layer: "L4", cluster: "synthesis", blurb: "Monte-Carlo the verdict — P10/P50/P90 + what breaks it", accent: "#fef08a" },
  { id: "negotiation_coach", name: "Negotiation Coach", layer: "L4", cluster: "synthesis", blurb: "BATNA, anchor, concessions for the next conversation", accent: "#fdba74" },
  { id: "outcome_tracker", name: "Outcome Tracker", layer: "L5", cluster: "memory", blurb: "Graded outcomes → GO hit-rate calibration + learned weights", accent: "#a78bfa" },
  { id: "weighing_engine", name: "Weighing Engine", layer: "L4", cluster: "synthesis", blurb: "Deterministic scoring — disagreement preserved", accent: "#eab308" },
  { id: "visualizer", name: "Visualizer", layer: "L4", cluster: "synthesis", blurb: "Best-fit interactive charts for every insight", accent: "#fcd34d" },
  { id: "reporter", name: "Reporter", layer: "L4", cluster: "synthesis", blurb: "The full written decision report", accent: "#fde68a" },
  { id: "verdict_composer", name: "Verdict Composer", layer: "L4", cluster: "synthesis", blurb: "The decision document, with sensitivities", accent: "#facc15" },
];

/** per-agent icons (emoji render crisply inside SVG nodes too) */
const ICONS: Record<string, string> = {
  boss: "🎩", manager: "🎼",
  intake_parser: "📥", context_profiler: "🪪", scope_planner: "🗺️",
  web_researcher: "🔎", news_intel: "📰", market_data: "📈", macro_data: "🌐", doc_analyst: "📄",
  sentiment_analyst: "💬", pricing_strategist: "💲", supply_chain: "🚛", cap_table: "🪙",
  patent_ip: "📑", insurance_risk: "☂️", sustainability_accountant: "♻️", cohort_retention: "🔁",
  scenario_planner: "🎲", negotiation_coach: "🤝",
  rag_memory: "📚", ai_ml_strategist: "🤖", data_analytics: "📐", software_architecture: "💻",
  product_ux: "🖌️", cybersecurity_privacy: "🔐", deep_tech: "🛰️", fundraising_capital: "💰",
  sales_revops: "📞", customer_success: "💚", partnerships_bd: "🔗", brand_creative: "✨",
  pr_communications: "📢", founder_coaching: "🧗", outcome_tracker: "🗂️",
  market_analyst: "🧭", market_research: "🔬", finance_modeler: "🧮", competitor_intel: "♟️", gtm_distribution: "🚚",
  legal: "⚖️", tax: "🧾", policy_compliance: "📋", industry_expert: "🏭",
  business_model: "🧩", marketing_strategy: "📣", subsidies_schemes: "🎁", banking: "🏦", hr_talent: "🧑‍🤝‍🧑",
  optimization_predictor: "🕳️", regulator: "🏛️",
  macroeconomist: "🏦", geopolitics: "🗺️", intl_markets: "✈️", trends: "📡", esg_impact: "🌱",
  technical_analyst: "📊", stock_analyst: "🏢", backtest_engineer: "🧪", quant_signals: "🎯",
  risk_manager: "🛡️", fund_analyst: "🧺", options_desk: "🎛️", microstructure: "⚡",
  salary_budget: "💵", portfolio_allocator: "🥧", fire_planner: "🔥", debt_banking: "🏧",
  real_estate: "🏠", location_scout: "📍",
  human_behaviour: "🧠", human_needs: "🪷", consumer_analysis: "🛒", production_ops: "🏗️",
  philosophy_ethics: "🦉", money_happiness: "😊", philanthropy_impact: "🤲",
  red_team: "⚔️", devils_advocate: "😈", bias_auditor: "🪞", fact_checker: "✅",
  connecting_dots: "🕸️", cross_pollinate: "🐝", compliance_scan: "🚨", weighing_engine: "⚖️", verdict_composer: "📜",
  storytelling: "🎙️", visualizer: "🎨", reporter: "🖋️",
};
for (const a of AGENTS) a.icon = ICONS[a.id] ?? "🤖";

/** what goes in / what comes out, per agent (drives stage cards + graph nodes) */
export const STAGE_IO: Record<string, { in: string; out: string }> = {
  boss: { in: "Your intake conversation (multi-turn)", out: "The structured handoff Brief" },
  manager: { in: "Brief + profile + the whole agent pool", out: "The routing plan — picks, benches, locked spine" },
  intake_parser: { in: "Your raw description", out: "Structured brief" },
  context_profiler: { in: "Brief", out: "Who is asking — capital, risk, stage" },
  scope_planner: { in: "Brief + depth + your toggles", out: "The convened board" },
  web_researcher: { in: "Brief keywords", out: "Sourced web evidence" },
  news_intel: { in: "Industry + geography", out: "Live headlines on the board" },
  market_data: { in: "Geography / symbol", out: "Live prices & history (yfinance)" },
  macro_data: { in: "Geography", out: "GDP · inflation · rates (World Bank)" },
  doc_analyst: { in: "Your uploaded documents", out: "Cited chunks + key facts" },
  market_analyst: { in: "Brief + evidence board", out: "Market score + analysis" },
  market_research: { in: "Market analyst + competitor reads", out: "TAM/SAM/SOM + segments + demand signal" },
  finance_modeler: { in: "Budget + team", out: "Runway math + economics score" },
  competitor_intel: { in: "Evidence board", out: "Positioning, moats, whitespace" },
  gtm_distribution: { in: "Brief + team + stage", out: "Channels + execution score" },
  legal: { in: "Brief", out: "Structure + legal exposure" },
  tax: { in: "Brief + geography", out: "GST posture + optimization" },
  policy_compliance: { in: "Evidence board", out: "Acts, licences, compliance" },
  industry_expert: { in: "Brief + evidence", out: "Insider benchmarks" },
  business_model: { in: "Brief + evidence", out: "Canvas + model recommendation" },
  marketing_strategy: { in: "Brief + evidence", out: "Positioning + growth loop" },
  subsidies_schemes: { in: "Brief + geography", out: "Schemes you qualify for" },
  banking: { in: "Finance model + schemes + tax", out: "Credit facility + capital-stack move" },
  pricing_strategist: { in: "Consumer + market research + finance", out: "WTP band + price architecture + first experiment" },
  supply_chain: { in: "Production + industry reads", out: "Critical inputs + single point of failure + resilience move" },
  cohort_retention: { in: "Consumer + marketing reads", out: "M1/M3/M6 retention + churn driver + LTV lever" },
  cap_table: { in: "Finance model + capital plan", out: "Round structure + founder dilution path + ESOP" },
  patent_ip: { in: "Legal + industry reads", out: "Protectable IP + freedom-to-operate risk" },
  insurance_risk: { in: "Legal + ops reads", out: "Needed covers + liability to transfer" },
  sustainability_accountant: { in: "ESG + ops + finance reads", out: "Footprint cost vs green moat" },
  sentiment_analyst: { in: "Live news/web evidence", out: "Net demand mood + strongest signals" },
  scenario_planner: { in: "Dimension scores + confidence", out: "P10/P50/P90 + P(GO) + what breaks it" },
  negotiation_coach: { in: "Verdict + board findings", out: "BATNA + anchor + concessions + walk-away" },
  rag_memory: { in: "Every evidence item + past runs", out: "BM25 index — per-agent relevance retrieval" },
  ai_ml_strategist: { in: "Brief + architecture/data reads", out: "AI leverage + build-vs-buy + governance" },
  data_analytics: { in: "Market + finance reads", out: "Metric tree + instrumentation + first prediction" },
  software_architecture: { in: "Product + finance reads", out: "Architecture + build cost/time + scaling wall" },
  product_ux: { in: "Consumer + behaviour reads", out: "Core loop + PMF signal + onboarding fix" },
  cybersecurity_privacy: { in: "Architecture + policy reads", out: "Threat model + privacy duty + cert path" },
  deep_tech: { in: "Trends + industry reads", out: "TRL read + enabler-or-threat + adoption window" },
  fundraising_capital: { in: "Cap-table + finance + banking reads", out: "Raise-vs-bootstrap + investor match + terms" },
  sales_revops: { in: "GTM + pricing reads", out: "Sales motion + pipeline math + first hire trigger" },
  customer_success: { in: "Cohort + consumer reads", out: "Activation moment + churn kill + expansion lever" },
  partnerships_bd: { in: "GTM + industry reads", out: "The one partner type + deal structure" },
  brand_creative: { in: "Marketing + consumer reads", out: "Positioning territory + naming direction" },
  pr_communications: { in: "Brand + live news reads", out: "Press angle + outlets + crisis pre-draft" },
  founder_coaching: { in: "HR + behaviour reads", out: "Founder risk + decision ritual + culture norm" },
  outcome_tracker: { in: "Your graded outcomes", out: "GO hit-rate + learned weights fed back" },
  hr_talent: { in: "Team + stage", out: "Hiring order + salary bands" },
  optimization_predictor: { in: "Brief + evidence", out: "Legit optimizations + risks" },
  regulator: { in: "Evidence board", out: "Regulator posture + scrutiny map" },
  macroeconomist: { in: "Macro series on the board", out: "Cycle read for this decision" },
  geopolitics: { in: "Evidence board", out: "Exposures + one hedge" },
  intl_markets: { in: "Brief", out: "First foreign market + friction" },
  trends: { in: "News + evidence", out: "Emerging trends + weak signal" },
  esg_impact: { in: "Brief + evidence", out: "ESG posture + impact moat" },
  technical_analyst: { in: "2y OHLCV", out: "Indicator reads + levels" },
  stock_analyst: { in: "Fundamentals + news", out: "Quality + valuation read" },
  backtest_engineer: { in: "2y OHLCV", out: "Strategy proof-of-work table" },
  quant_signals: { in: "Technicals + backtests", out: "Setup quality + votes" },
  risk_manager: { in: "Capital + risk% + ATR", out: "Position size + stop + max loss" },
  fund_analyst: { in: "Symbol + sector", out: "Fund-route education" },
  options_desk: { in: "Technical view + IV", out: "Defined-risk structure education" },
  microstructure: { in: "Symbol + size", out: "Execution reality check" },
  salary_budget: { in: "Income + expenses", out: "Savings rate + 50/30/20" },
  portfolio_allocator: { in: "Age + risk appetite", out: "Glide-path allocation" },
  fire_planner: { in: "Expenses + savings + surplus", out: "FIRE number + years" },
  debt_banking: { in: "Profile", out: "Debt payoff order" },
  real_estate: { in: "City + profile", out: "Rent-vs-buy read" },
  location_scout: { in: "City + profile", out: "Local schemes + opportunities" },
  human_behaviour: { in: "Brief + evidence", out: "Psychological forces for/against" },
  human_needs: { in: "Brief", out: "Needs-hierarchy fit + durability" },
  consumer_analysis: { in: "Brief + evidence", out: "Segments + willingness to pay" },
  production_ops: { in: "Brief + evidence", out: "Inputs, capacity, breaking point" },
  philosophy_ethics: { in: "All context", out: "Stakeholder costs + examined view" },
  money_happiness: { in: "Profile + brief", out: "Life-fit: time vs money vs wellbeing" },
  philanthropy_impact: { in: "Brief + evidence", out: "Impact angle + giving structure" },
  red_team: { in: "All analyst outputs", out: "Evidence-backed attacks" },
  devils_advocate: { in: "All outputs", out: "The steel-manned NO case" },
  bias_auditor: { in: "Your own framing", out: "Named biases with quotes" },
  fact_checker: { in: "Claims vs evidence board", out: "supported / unsupported verdicts" },
  connecting_dots: { in: "Every domain verdict", out: "Cross-domain patterns" },
  cross_pollinate: { in: "Every specialist's headline", out: "Synergies, tensions & emergent insights" },
  compliance_scan: { in: "Regulatory/legal/tax outputs + evidence", out: "Ranked compliance red-flags" },
  weighing_engine: { in: "Scores × penalties × evidence", out: "Deterministic weighted verdict" },
  verdict_composer: { in: "The weighed number", out: "The decision document" },
  storytelling: { in: "Verdict + every board finding", out: "Hook · narrative · one-liner · 3 beats" },
  visualizer: { in: "Every output + evidence figure", out: "Interactive chart gallery" },
  reporter: { in: "Everything the board produced", out: "The full written report" },
};

/** Capability card data for the board picker: what an agent can do, who it
 * talks to on the blackboard, and the sub-agents working under it. */
export interface AgentCaps {
  can: string[];
  talks_to: string[];
  subagents: string[];
  /** tools & data access badges (additive layer on top of skills) */
  tools: string[];
}

const T0_SUB = "🧮 deterministic math core (no LLM — cannot hallucinate)";
const RESEARCH_SUB = "🔎 research sub-agent — runs its own live web query at Board/War-Room depth";
const T0_IDS = new Set(["market_data", "macro_data", "technical_analyst", "backtest_engineer",
  "quant_signals", "risk_manager", "salary_budget", "portfolio_allocator", "fire_planner",
  "weighing_engine"]);
const NO_RESEARCH = new Set(["boss", "manager", "intake_parser", "context_profiler", "scope_planner", "web_researcher",
  "news_intel", "market_data", "macro_data", "doc_analyst", "finance_modeler", "technical_analyst",
  "backtest_engineer", "quant_signals", "risk_manager", "portfolio_allocator", "fire_planner",
  "salary_budget", "red_team", "fact_checker", "bias_auditor", "devils_advocate", "connecting_dots",
  "weighing_engine", "verdict_composer", "storytelling", "visualizer", "reporter", "options_desk", "microstructure"]);

/** A2A affinity — mirror of backend venture.PEERS. Each agent builds on the
 * colleagues it reads off the shared evidence board (drives graph A2A edges). */
export const PEERS: Record<string, string[]> = {
  competitor_intel: ["market_analyst", "market_research"],
  industry_expert: ["market_analyst", "macroeconomist"],
  consumer_analysis: ["human_behaviour", "market_research"],
  market_research: ["market_analyst", "competitor_intel"],
  business_model: ["market_analyst", "market_research", "finance_modeler", "competitor_intel", "consumer_analysis"],
  marketing_strategy: ["consumer_analysis", "competitor_intel", "market_research", "human_behaviour"],
  gtm_distribution: ["market_analyst", "consumer_analysis", "competitor_intel", "marketing_strategy"],
  hr_talent: ["finance_modeler", "industry_expert", "business_model"],
  production_ops: ["industry_expert", "finance_modeler", "business_model"],
  subsidies_schemes: ["finance_modeler", "policy_compliance", "banking"],
  banking: ["finance_modeler", "subsidies_schemes", "tax", "business_model"],
  optimization_predictor: ["tax", "legal", "policy_compliance", "banking"],
  regulator: ["policy_compliance", "legal"],
  trends: ["market_research", "macroeconomist", "consumer_analysis"],
  geopolitics: ["macroeconomist", "intl_markets", "production_ops"],
  intl_markets: ["market_analyst", "competitor_intel", "industry_expert"],
  esg_impact: ["production_ops", "philosophy_ethics", "consumer_analysis"],
  human_needs: ["consumer_analysis", "human_behaviour"],
  money_happiness: ["finance_modeler", "human_needs"],
  philosophy_ethics: ["human_behaviour", "consumer_analysis", "esg_impact"],
  philanthropy_impact: ["esg_impact", "philosophy_ethics"],
  stock_analyst: ["technical_analyst", "macroeconomist"],
  fund_analyst: ["stock_analyst", "risk_manager"],
  options_desk: ["technical_analyst", "risk_manager"],
  fire_planner: ["salary_budget", "portfolio_allocator"],
  real_estate: ["salary_budget", "debt_banking", "banking"],
  debt_banking: ["salary_budget", "banking"],
  location_scout: ["subsidies_schemes"],
  pricing_strategist: ["consumer_analysis", "market_research", "finance_modeler"],
  supply_chain: ["production_ops", "industry_expert"],
  cohort_retention: ["consumer_analysis", "marketing_strategy"],
  cap_table: ["finance_modeler", "banking"],
  patent_ip: ["legal", "industry_expert"],
  insurance_risk: ["legal", "production_ops"],
  sustainability_accountant: ["esg_impact", "production_ops", "finance_modeler"],
  sentiment_analyst: ["news_intel", "consumer_analysis"],
  ai_ml_strategist: ["software_architecture", "data_analytics"],
  data_analytics: ["market_research", "finance_modeler"],
  software_architecture: ["product_ux", "finance_modeler"],
  product_ux: ["consumer_analysis", "human_behaviour"],
  cybersecurity_privacy: ["software_architecture", "policy_compliance"],
  deep_tech: ["trends", "industry_expert"],
  fundraising_capital: ["cap_table", "finance_modeler", "banking"],
  sales_revops: ["gtm_distribution", "pricing_strategist"],
  customer_success: ["cohort_retention", "consumer_analysis"],
  partnerships_bd: ["gtm_distribution", "industry_expert"],
  brand_creative: ["marketing_strategy", "consumer_analysis"],
  pr_communications: ["brand_creative", "news_intel"],
  founder_coaching: ["hr_talent", "human_behaviour"],
};

/** who reads whose output — the A2A communication map, humanized */
const TALKS: Record<string, string[]> = {
  boss: ["you — the only agent that converses with the client", "manager (the handoff brief)"],
  manager: ["every agent it routes in or benches", "QA gate (re-dispatches failures)", "human reviewer (regulated content)"],
  web_researcher: ["every L2 specialist (via the evidence board)"],
  news_intel: ["every L2 specialist (via the evidence board)"],
  market_data: ["technical analyst", "quant signals", "weighing engine (Timing)"],
  macro_data: ["macroeconomist", "weighing engine (Timing)"],
  doc_analyst: ["every specialist (your documents become shared evidence)"],
  technical_analyst: ["backtest engineer", "quant signals", "options desk", "risk manager"],
  backtest_engineer: ["quant signals (no un-backtested signal may speak)"],
  quant_signals: ["risk manager", "verdict composer"],
  risk_manager: ["verdict composer (position plan)"],
  red_team: ["every analyst it attacks — they rebut in War Room debates"],
  fact_checker: ["weighing engine (failed checks lower Evidence)"],
  bias_auditor: ["you — it audits YOUR framing"],
  devils_advocate: ["verdict composer (the NO case is preserved)"],
  connecting_dots: ["verdict composer (cross-domain patterns)"],
  weighing_engine: ["verdict composer (it may not change the number)"],
  verdict_composer: ["storyteller", "visualizer", "reporter"],
  market_research: ["market analyst", "competitor intel", "business model", "marketing strategist", "trends"],
  banking: ["finance modeler", "subsidies & schemes", "tax", "business model", "optimization predictor"],
  storytelling: ["you — the pitch narrative", "reporter (frames the written report)"],
  visualizer: ["you — every insight becomes an interactive chart"],
  reporter: ["you — the full written decision report"],
};

/** Tools & data access per agent (ADDITIVE — the tech each specialist wields,
 * shown as badges in its capability card, on top of its skills). */
const TOOLS: Record<string, string[]> = {
  boss: ["LLM · t3", "Multi-turn dialogue", "Board · state write", "Deterministic question ladder (zero-key)"],
  manager: ["LLM · t3", "Orchestration (dynamic routing)", "QA gate invoke", "HITL gate invoke", "Board · state R/W"],
  intake_parser: ["Regex core", "LLM · t1", "Board · state write"],
  context_profiler: ["LLM · t1", "Board · state R/W"],
  scope_planner: ["Deterministic core", "Config", "Board · state write"],
  web_researcher: ["Web search (live)", "LLM · t2", "Board · state write"],
  news_intel: ["News RSS (live)", "LLM · t2", "Board"],
  market_data: ["yfinance connector", "Deterministic core", "Board"],
  macro_data: ["World Bank connector", "Deterministic core", "Board"],
  doc_analyst: ["Docs (pypdf)", "Browser OCR (tesseract.js)", "LLM · t2", "Board"],
  sentiment_analyst: ["News/social evidence", "LLM · t2", "RAG retrieval"],
  rag_memory: ["RAG · BM25 index", "Past-run recall", "Board"],
  finance_modeler: ["Deterministic core", "LLM · t2", "Peers mesh"],
  technical_analyst: ["Deterministic core (40+ indicators)", "yfinance"],
  backtest_engineer: ["Deterministic core (backtests)", "yfinance"],
  quant_signals: ["Deterministic core (regime + ensemble)"],
  risk_manager: ["Deterministic core (sizing/ATR)"],
  stock_analyst: ["LLM · t2", "yfinance", "Peers mesh"],
  options_desk: ["Deterministic core", "LLM · t2"],
  salary_budget: ["Deterministic core", "LLM · t2"],
  portfolio_allocator: ["Deterministic core (glide path)"],
  fire_planner: ["Deterministic core (compounding)"],
  debt_banking: ["Deterministic core", "LLM · t2"],
  real_estate: ["Deterministic core", "LLM · t2"],
  location_scout: ["LLM · t2", "Web search"],
  subsidies_schemes: ["LLM · t2", "Web search", "RAG retrieval"],
  regulator: ["Web search", "LLM · t2", "Board"],
  geopolitics: ["LLM · t2", "Web search", "Peers mesh"],
  pricing_strategist: ["Van-Westendorp frame", "LLM · t2", "RAG retrieval"],
  cap_table: ["Deterministic dilution math", "LLM · t2"],
  insurance_risk: ["Risk register frame", "LLM · t2"],
  patent_ip: ["Prior-art heuristics", "LLM · t2", "RAG retrieval"],
  scenario_planner: ["Deterministic Monte-Carlo (1000 draws)", "Seeded RNG"],
  ai_ml_strategist: ["LLM · t3-class ask", "RAG retrieval"],
  data_analytics: ["Metric-tree frame", "LLM · t2", "RAG retrieval"],
  software_architecture: ["Build-estimate frame", "LLM · t3-class ask", "RAG retrieval"],
  cybersecurity_privacy: ["Threat-model frame", "LLM · t2", "RAG retrieval"],
  deep_tech: ["TRL framework", "Web evidence", "LLM · t2"],
  fundraising_capital: ["Dilution math (peer)", "LLM · t2", "RAG retrieval"],
  customer_success: ["Cohort frame (peer)", "LLM · t2"],
  pr_communications: ["Live news evidence", "LLM · t2"],
  red_team: ["LLM · t3", "Board · full read"],
  devils_advocate: ["LLM · t3", "Board · full read"],
  bias_auditor: ["LLM · t3", "Your framing (verbatim)"],
  fact_checker: ["Claim-vs-board overlap", "LLM · t2"],
  cross_pollinate: ["LLM · t3", "Board · full read", "Conflict emit"],
  compliance_scan: ["Regex compliance sweep", "Board · full read"],
  connecting_dots: ["LLM · t3", "Board · full read"],
  weighing_engine: ["Deterministic scoring", "Learned weights (outcomes)", "Board · read"],
  verdict_composer: ["LLM · t3", "Board · read"],
  storytelling: ["LLM · t3"],
  negotiation_coach: ["BATNA framework", "LLM · t3"],
  visualizer: ["Chart-kit (15 animated types)", "Deterministic specs", "LLM · t2 extras"],
  reporter: ["LLM · t3", "Input-shrinking retry ladder", "Split-and-stitch"],
  decision_graph: ["SQLite persistence", "3D graph builder", "Board · read"],
  outcome_tracker: ["SQLite track record", "Deterministic calibration"],
};
const LENS_TOOLS = ["LLM · t2", "RAG retrieval (relevant evidence)", "Peers mesh (round 1)",
  "Full-board deliberation (round 2)"];

export function capsFor(id: string): AgentCaps {
  const a = agentById(id);
  const io = STAGE_IO[id];
  const can: string[] = [a.blurb];
  if (io) can.push(`reads: ${io.in}`, `produces: ${io.out}`);
  const subagents: string[] = [];
  if (T0_IDS.has(id)) subagents.push(T0_SUB);
  if (!NO_RESEARCH.has(id)) subagents.push(RESEARCH_SUB);
  if (id === "doc_analyst") subagents.push("📄 extraction sub-agent — PDF/TXT → cited chunks + key facts");
  if (id === "visualizer") subagents.push("📊 chart-picker sub-agent — chooses the best chart type per insight");
  const talks_to = TALKS[id]
    ?? ["red team (it will attack this analysis)", "fact checker (claims get verified)",
        "weighing engine (score feeds a dimension)", "connecting dots (patterns across domains)"];
  const tools = TOOLS[id] ?? LENS_TOOLS;
  return { can, talks_to, subagents, tools };
}

const BY_ID = new Map(AGENTS.map((a) => [a.id, a]));

const UNKNOWN: AgentInfo = {
  id: "unknown", name: "Board", layer: "L4", cluster: "synthesis",
  blurb: "", accent: "#64748b",
};

/** Never throws — unknown ids (e.g. future agents, "user_framing") get a neutral identity. */
export function agentById(id: string): AgentInfo {
  return BY_ID.get(id) ?? { ...UNKNOWN, id: id || "unknown", name: id ? prettify(id) : "Board" };
}

function prettify(id: string): string {
  return id.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
