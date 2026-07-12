"""The Orchestra score — Intelligent Mode's two-tier ensemble.

This is the data behind the "composition engine" (expert-orchestra-map): every
main expert is a PLAYER (musician); under each sit 4–5 junior specialists —
the INSTRUMENTS — each with one specific skill. The Manager decomposes the
brief into a task graph and puts every player AND every instrument to work.

Intelligent Mode runs THIS roster as one general advisory (any business/life
brief), not the founder/trader/wealth boards. Player ids reuse EIP agent ids
where a player already exists (icons/registry line up); the instruments are new.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Instrument:
    name: str
    skill: str


@dataclass(frozen=True)
class Player:
    id: str
    name: str
    emoji: str
    family: str            # family id "02".."11"
    role: str
    instruments: tuple[Instrument, ...]


@dataclass(frozen=True)
class Family:
    id: str
    name: str
    color: str
    tag: str
    scored: bool           # do its players feed the weighed verdict?


def _P(pid, name, emoji, fam, role, insts):
    return Player(pid, name, emoji, fam, role, tuple(Instrument(n, s) for n, s in insts))


FAMILIES: list[Family] = [
    Family("02", "Framing & Intake", "#3FB6A3", "parse the noise into a score in the right key", False),
    Family("03", "Research & Intelligence", "#5591E8", "reconnaissance — gather the raw sound", False),
    Family("04", "Analysis & Modeling", "#927BE6", "the rhythm section — turn sound into structure", True),
    Family("05", "Domain, Strategy & Structure", "#E8944E", "the melody — the strategic core", True),
    Family("06", "Legal, Regulatory & Fiscal", "#D97595", "the rules of the score — stay in key, stay legal", True),
    Family("07", "Technology & Engineering", "#35C1D6", "the bench — can it be built", True),
    Family("08", "Commercial & Growth", "#B4C24A", "raise, sell, price, keep", True),
    Family("09", "Human, Society & Meaning", "#5FB56A", "the emotional register — why any of this matters", True),
    Family("10", "Adversarial & Quality Assurance", "#E85F55", "the critics — tune it before it ships", False),
    Family("11", "Synthesis & Delivery", "#CE73BE", "the performance — connect, tell, decide, present", False),
]
FAMILY_BY_ID = {f.id: f for f in FAMILIES}

PLAYERS: list[Player] = [
    # ── 02 · Framing & Intake ─────────────────────────────────────────────
    _P("intake_parser", "Intake Parser", "📥", "02",
       "Turns a messy multi-format client dump into a clean, structured brief.", [
        ("Intent & Entity Extractor", "NER, intent classification and key-fact extraction from raw input"),
        ("Taxonomy Tagger", "Classifies by stage (idea/MVP/scaling), sector, geo and ask-type"),
        ("Ambiguity & Gap Flagger", "Detects missing info and contradictions; produces the unknowns list"),
        ("Schema Normaliser", "Maps free text and documents onto the structured brief schema"),
        ("Multimodal Ingestor", "Parses PDFs, decks, spreadsheets, images and voice notes into text and data")]),
    _P("context_profiler", "Context Profiler", "🪪", "02",
       "Builds the who-and-where profile the whole engagement is calibrated against.", [
        ("Founder/Company Profiler", "Track record, team composition, prior traction and reputation"),
        ("Readiness Assessor", "Stage-gating and TRL/MRL-style readiness scoring"),
        ("Resource & Asset Auditor", "Inventory of capital, team, IP, network and unfair advantages"),
        ("Geo-Context Mapper", "Location-specific norms, infrastructure and ecosystem maturity"),
        ("Precedent Retriever", "Finds similar ventures and what happened to them")]),
    _P("scope_planner", "Scope Planner", "🗺️", "02",
       "Decides what the engagement will and will not cover, and how deep.", [
        ("Objective Decomposer", "Converts goals into sub-questions and hypotheses to test"),
        ("Success-Metric Definer", "Defines measurable outcomes, KPIs and decision thresholds"),
        ("Boundary & Exclusion Setter", "Scopes work in/out; maintains the assumptions log"),
        ("Depth Estimator", "Decides how deep each dimension warrants; time-vs-quality trade-offs"),
        ("Deliverable Designer", "Specifies final artifacts and acceptance criteria")]),
    # ── 03 · Research & Intelligence ──────────────────────────────────────
    _P("web_researcher", "Web Researcher", "🔎", "03",
       "Finds and verifies primary information the rest of the floor builds on.", [
        ("Search Strategist", "Query design, boolean/advanced operators, engine and database selection"),
        ("Source-Credibility Grader", "Evaluates authority, recency, bias and primary-vs-secondary status"),
        ("Deep-Dive Extractor", "Pulls structured facts, quotes and data out of long documents"),
        ("Citation & Provenance Tracker", "Logs sources so every claim is traceable, not invented"),
        ("Academic & Patent Search Specialist", "Scholarly databases, patents and grey literature")]),
    _P("news_intel", "News Intelligence", "📰", "03",
       "Tracks what is happening right now and what the story is becoming.", [
        ("Real-Time Monitor", "Breaking-news feeds, alerting and event detection"),
        ("Narrative & Sentiment Tracker", "Media framing, tone shifts and public perception"),
        ("Chronology Builder", "Sequences events into causal timelines"),
        ("Source-Diversity Balancer", "Cross-outlet coverage to avoid single-narrative capture"),
        ("Rumor-vs-Fact Triager", "Separates unconfirmed noise from verified signal")]),
    _P("market_data", "Market Data", "📈", "03",
       "Quantifies the market — size, price, demand and segments.", [
        ("Market Sizer", "TAM/SAM/SOM via top-down and bottom-up methods"),
        ("Pricing & Demand Collector", "Price points, elasticity signals and volume data"),
        ("Segmentation Data Specialist", "Demographic, firmographic and behavioural segment data"),
        ("Data-Source Curator", "Knows where trustworthy market data lives and how to access it"),
        ("Data Cleaner & Validator", "Dedupes, normalises and sanity-checks the numbers")]),
    _P("macro_data", "Macro Data", "🌐", "03",
       "Supplies the macroeconomic backdrop every model needs.", [
        ("Indicator Collector", "GDP, inflation, rates, FX, PMI and employment series"),
        ("Institutional-Source Specialist", "RBI, Fed, IMF and World Bank data pipelines"),
        ("Time-Series Wrangler", "Seasonality, trend extraction and base-effect handling"),
        ("Cross-Country Comparator", "Normalises indicators for like-for-like comparison"),
        ("Leading/Lagging Classifier", "Sorts signals that predict from signals that confirm")]),
    _P("competitor_intel", "Competitor Intelligence", "♟️", "03",
       "Maps the board and predicts the other players' moves.", [
        ("Competitor Mapper", "Direct, indirect and substitute landscape"),
        ("Product & Pricing Teardown Analyst", "Feature matrices and pricing comparison"),
        ("Funding & Financials Tracker", "Raises, burn and valuation signals"),
        ("Positioning & Moat Analyst", "Differentiation, defensibility and switching costs"),
        ("Move Predictor", "Anticipates competitors' next moves via game theory")]),
    _P("regulator", "Regulator Watch", "🏛️", "03",
       "Watches the rule-makers before the rules land.", [
        ("Rule-Change Monitor", "Tracks new regulations, drafts and consultation periods"),
        ("Agency-Behaviour Analyst", "Models how a specific regulator tends to act"),
        ("Enforcement-Trend Tracker", "Fines, actions and precedents over time"),
        ("Jurisdiction Mapper", "Which rules apply in which territory"),
        ("Regulatory-Calendar Keeper", "Deadlines, comment windows and sunset dates")]),
    _P("trends", "Trends & Weak Signals", "📡", "03",
       "Hears the faint sounds before they become the melody.", [
        ("Horizon Scanner", "Scans fringe and emerging sources for early signals"),
        ("Weak-Signal Detector", "Spots faint but meaningful patterns before they are obvious"),
        ("Trend Extrapolator", "S-curves, diffusion of innovation and adoption timing"),
        ("Cross-Domain Analogizer", "Detects patterns transferring between industries"),
        ("Hype-vs-Substance Filter", "Discounts hype-cycle noise to find the real signal")]),
    _P("intl_markets", "International Markets", "✈️", "03",
       "Plans how to cross borders without breaking.", [
        ("Market-Entry Strategist", "Entry modes (export/JV/subsidiary) and sequencing"),
        ("Localisation Analyst", "Language, product and legal adaptation requirements"),
        ("Trade & Tariff Analyst", "Customs, duties and trade-agreement effects"),
        ("Cultural-Fit Assessor", "Hofstede-style dimensions and consumer-behaviour differences"),
        ("Country-Risk Scorer", "Political, economic and currency risk by country")]),
    _P("geopolitics", "Geopolitics", "🗺️", "03",
       "Reads the world map for risk the venture is exposed to.", [
        ("Geopolitical Risk Analyst", "Conflict, instability and regime-change risk"),
        ("Sanctions & Export-Control Specialist", "OFAC-type regimes, dual-use and compliance"),
        ("Supply-Chain Exposure Mapper", "Chokepoints and dependency risk (chips, energy, rare earths)"),
        ("Bloc & Alliance Analyst", "Trade blocs, decoupling and friend-shoring dynamics"),
        ("Scenario Builder", "Constructs plausible geopolitical futures")]),
    # ── 04 · Analysis & Modeling ──────────────────────────────────────────
    _P("market_analyst", "Market Analyst", "🧭", "04",
       "Turns raw research into where the real opening is.", [
        ("Opportunity Synthesizer", "Turns scattered data into a clear opening"),
        ("Demand Modeler", "Forecasts demand and adoption curves"),
        ("Segmentation Strategist", "Prioritises segments by attractiveness and fit"),
        ("Whitespace Finder", "Surfaces unmet needs and underserved niches"),
        ("Go/No-Go Framer", "Structures the decision with explicit thresholds")]),
    _P("finance_modeler", "Finance Modeler", "🧮", "04",
       "Makes the numbers real — economics, projections and valuation.", [
        ("Unit-Economics Analyst", "CAC, LTV, contribution margin and payback period"),
        ("3-Statement Modeler", "Builds P&L, balance-sheet and cash-flow projections"),
        ("Valuation & DCF Specialist", "DCF, comparables and precedent transactions"),
        ("Scenario & Sensitivity Analyst", "Base/bull/bear cases and Monte-Carlo runs"),
        ("Cap-Table & Dilution Modeler", "Rounds, dilution, option pools and exit waterfalls")]),
    _P("macroeconomist", "Macroeconomist", "🏦", "04",
       "Positions the venture inside the wider economic weather.", [
        ("Cycle Positioner", "Locates where we are in the business/credit cycle"),
        ("Policy-Impact Analyst", "Fiscal and monetary policy effects on the venture"),
        ("Rate & Inflation Translator", "What macro means for costs and financing"),
        ("Sector-Sensitivity Mapper", "How macro shocks hit this specific sector"),
        ("Macro-Scenario Modeler", "Recession, stagflation and soft-landing implications")]),
    _P("consumer_analysis", "Consumer Analysis", "🛒", "04",
       "Understands who buys, why, and what they will pay.", [
        ("Persona Builder", "Evidence-based personas with jobs, pains and gains"),
        ("Purchase-Behaviour Analyst", "Buying triggers and decision journeys"),
        ("Journey Mapper", "End-to-end CX mapping and friction points"),
        ("Willingness-to-Pay Researcher", "Van Westendorp and conjoint studies"),
        ("Cohort & Retention Analyst", "Behavioural cohorts and churn drivers")]),
    _P("weighing_engine", "Weighing Engine", "⚖️", "04",
       "Scores the options so the verdict is defensible, not vibes.", [
        ("Multi-Criteria Scorer", "MCDA/AHP weighted scoring models"),
        ("Trade-Off Quantifier", "Pareto analysis and cost-benefit"),
        ("Probability & Risk Weigher", "Expected-value math and decision trees"),
        ("Option Ranker", "Ranks strategies by weighted score"),
        ("Assumption Stress-Tester", "Tests how sensitive the ranking is to assumptions")]),
    # ── 05 · Domain, Strategy & Structure ─────────────────────────────────
    _P("industry_expert", "Industry Expert", "🏭", "05",
       "Deep vertical knowledge — instantiated per sector you serve.", [
        ("Value-Chain Mapper", "The industry value chain and where margin pools sit"),
        ("KPI & Benchmark Keeper", "Sector-specific metrics and benchmarks"),
        ("Vertical-Regulation Specialist", "Industry-specific rules and standards"),
        ("Ecosystem Mapper", "Incumbents, disruptors and enablers"),
        ("Best-Practice Librarian", "Playbooks, standards and known pitfalls")]),
    _P("business_model", "Business Model", "🧩", "05",
       "Designs how the venture creates, delivers and captures value.", [
        ("Canvas Architect", "Business-model and lean canvas, value-proposition design"),
        ("Revenue-Model Designer", "Subscription, transaction, marketplace and licensing models"),
        ("Moat Designer", "Network effects, switching costs and scale economies"),
        ("Platform Dynamics Specialist", "Liquidity, chicken-and-egg and take-rate"),
        ("Pattern Librarian", "50+ business-model patterns (razor-blade, freemium, etc.)")]),
    _P("gtm_distribution", "GTM & Distribution", "🚚", "05",
       "Gets the product to market through the right motion and channels.", [
        ("Channel Strategist", "Direct, indirect and partner channel mix"),
        ("GTM-Motion Designer", "PLG vs sales-led vs community-led"),
        ("Launch Planner", "Sequencing, beachhead selection and rollout"),
        ("Distribution-Economics Analyst", "Channel margins and CAC by channel"),
        ("Channel-Conflict Manager", "Manages overlapping and competing channels")]),
    _P("marketing_strategy", "Marketing Strategy", "📣", "05",
       "Positions the venture and builds the demand engine.", [
        ("Positioning Strategist", "Category design and value narrative"),
        ("Demand-Gen Architect", "Paid/organic mix and funnel design"),
        ("Content & SEO Strategist", "The organic content engine"),
        ("Mix & Budget Allocator", "Channel budget optimisation and attribution"),
        ("Campaign Experimenter", "A/B tests creatives, channels and offers")]),
    _P("production_ops", "Production & Ops", "🏗️", "05",
       "Designs how the thing actually gets made and delivered.", [
        ("Process Designer", "Workflow design using lean and Six Sigma"),
        ("Capacity Planner", "Bottleneck analysis and theory of constraints"),
        ("Quality-Systems Specialist", "QA/QC and ISO-style standards"),
        ("COGS & Efficiency Analyst", "Cost reduction and yield improvement"),
        ("Ops-Metrics & Dashboard Builder", "OEE, cycle time and SLAs")]),
    _P("hr_talent", "HR & Talent", "🧑‍🤝‍🧑", "05",
       "Designs the team, the comp and the culture that scale.", [
        ("Org Designer", "Structure, roles and spans/layers"),
        ("Hiring & Sourcing Strategist", "Role specs, sourcing channels and hiring funnel"),
        ("Comp & Equity Designer", "Comp bands, ESOP and incentives"),
        ("Culture Architect", "Values, rituals and engagement"),
        ("Talent-Market Analyst", "Availability, salary benchmarks and skill scarcity")]),
    _P("banking", "Banking", "🏦", "05",
       "Runs the money plumbing — credit, treasury and payments.", [
        ("Debt & Credit Structurer", "Loans, lines, venture debt and terms"),
        ("Treasury & Cash Manager", "Cash management and working capital"),
        ("Payments-Infrastructure Specialist", "Rails, gateways and PSP selection"),
        ("Trade-Finance Specialist", "Letters of credit, factoring and export finance"),
        ("Bank-Relationship Manager", "Bank selection, covenants and negotiation")]),
    _P("supply_chain", "Supply Chain & Procurement", "📦", "05",
       "Designs and de-risks the flow of goods, suppliers and inventory.", [
        ("Supply-Chain Designer", "Network design and flow optimisation"),
        ("Sourcing & Procurement Specialist", "Vendor selection and negotiation"),
        ("Logistics Planner", "Distribution, freight and last-mile"),
        ("Inventory & Demand Planner", "Stock levels, safety stock and forecasting"),
        ("Supplier-Risk Analyst", "Dependency, concentration and resilience risk")]),
    # ── 06 · Legal, Regulatory & Fiscal ───────────────────────────────────
    _P("legal", "Legal", "⚖️", "06",
       "The venture's counsel — structure, contracts and dispute risk.", [
        ("Entity & Structuring Counsel", "Incorporation and holding structures"),
        ("Contracts Drafter/Reviewer", "MSAs, shareholder agreements, ToS and employment"),
        ("IP Counsel", "Trademark, copyright and patent basics"),
        ("Compliance-Framework Specialist", "Sector compliance and statutory filings"),
        ("Dispute-Risk Analyst", "Exposure assessment and dispute avoidance")]),
    _P("tax", "Tax (India-first)", "🧾", "06",
       "Optimises the tax position legally, at home and across borders.", [
        ("GST & Indirect-Tax Specialist", "GST structuring, input credit and filings"),
        ("Direct-Tax Specialist", "Income tax, MAT and deductions"),
        ("Cross-Border Tax Specialist", "Transfer pricing, DTAA and permanent-establishment risk"),
        ("Tax-Incentive Optimizer", "Startup holidays, R&D and SEZ benefits"),
        ("Compliance-Calendar Keeper", "TDS, advance tax and filing deadlines")]),
    _P("policy_compliance", "Policy & Compliance", "📋", "06",
       "Keeps the venture licensed, compliant and audit-ready.", [
        ("Licensing Specialist", "Required licenses and permits by activity and geo"),
        ("Data-Privacy Specialist", "DPDP Act, GDPR and consent management"),
        ("Sector-Compliance Mapper", "FSSAI, RBI, SEBI and other sector rules"),
        ("Audit-Readiness Specialist", "Documentation, controls and evidence"),
        ("Policy Interpreter", "Translates dense policy text into concrete requirements")]),
    _P("subsidies_schemes", "Subsidies & Schemes", "🎁", "06",
       "Finds and captures the free money — grants, subsidies and incentives.", [
        ("Scheme-Discovery Specialist", "Central/state schemes, grants and incentives"),
        ("Eligibility Mapper", "Matches the venture to scheme criteria"),
        ("Grant-Application Writer", "Proposals, documentation and submission"),
        ("Stacking Optimizer", "Combines multiple benefits legally"),
        ("Deadline & Renewal Tracker", "Application windows and renewals")]),
    _P("optimization_predictor", "Loophole Predictor", "🕳️", "06",
       "Aggressive-but-legal optimisation — reviewed by Legal and Ethics.", [
        ("Arbitrage Spotter", "Legal gray zones and jurisdictional arbitrage, within the law"),
        ("Structuring Optimizer", "Legal structures that reduce cost and friction"),
        ("Rule-Closure Predictor", "Anticipates when a loophole will be shut"),
        ("Loophole Risk-Rater", "How defensible and how risky a given gap is"),
        ("Case-Law Miner", "How similar structures fared in precedent")]),
    _P("patent_ip", "Intellectual Property & Patents", "📑", "06",
       "Turns inventions and brand into protected, monetisable assets.", [
        ("Patent Strategist", "What to patent, when and where"),
        ("Search & FTO Analyst", "Prior-art search and freedom-to-operate"),
        ("Trademark/Copyright Specialist", "Brand and content protection"),
        ("Portfolio Manager", "Maintains and prunes the IP portfolio"),
        ("Licensing & Monetisation Advisor", "Turns IP into revenue via licensing")]),
    _P("insurance_risk", "Risk & Insurance", "🛡️", "06",
       "Names what could go wrong and buys it down.", [
        ("Risk-Register Analyst", "Identifies, scores and tracks enterprise risks"),
        ("Insurance Strategist", "Coverage design and carrier selection"),
        ("Continuity Planner", "Business-continuity and disaster recovery"),
        ("Contingency Planner", "Scenario responses and playbooks"),
        ("Compliance-Risk Analyst", "Regulatory and reputational risk exposure")]),
    # ── 07 · Technology & Engineering ─────────────────────────────────────
    _P("ai_ml_strategist", "AI & ML Strategist", "🤖", "07",
       "Decides where AI genuinely creates value — and how to build or buy it.", [
        ("Use-Case & Feasibility Assessor", "Where AI adds value vs where it is hype"),
        ("Model-Selection Advisor", "Foundation models, fine-tuning vs API, build-vs-buy"),
        ("AI Product Designer", "Human-AI interaction and workflow integration"),
        ("AI-Governance Specialist", "Bias, safety, explainability and compliance"),
        ("Data-Readiness Assessor", "Whether data exists and is good enough for AI")]),
    _P("data_analytics", "Data Science & Analytics", "📊", "07",
       "Builds the data spine — instrumentation, experiments and prediction.", [
        ("Data-Strategy Architect", "What to collect and the data infrastructure"),
        ("Instrumentation Engineer", "Event tracking and metric trees"),
        ("Experimentation Specialist", "A/B testing and causal inference"),
        ("Predictive-Modeling Analyst", "Forecasting and ML models"),
        ("BI & Insight Analyst", "Dashboards and storytelling with data")]),
    _P("software_architecture", "Software Architecture & Engineering", "💻", "07",
       "Answers can-it-be-built, how, how long and how much.", [
        ("Tech-Feasibility Assessor", "Whether and how hard something is to build"),
        ("Architecture & Stack Advisor", "System design and technology choices"),
        ("Cost & Timeline Estimator", "Effort estimation and team sizing"),
        ("Scalability Engineer", "Performance, uptime and scaling"),
        ("Buildability & Tech-Debt Auditor", "MVP scoping and technical-risk review")]),
    _P("product_ux", "Product & UX Design", "🎯", "07",
       "Shapes what to build and how it should feel to use.", [
        ("Product Strategist", "Vision, roadmap and prioritisation"),
        ("User Researcher", "Interviews, usability and discovery"),
        ("UX/UI Designer", "Flows, wireframes and design systems"),
        ("Prototyper", "Rapid prototypes and MVP design"),
        ("PMF & Metrics Specialist", "Sean-Ellis test, activation and retention")]),
    _P("cybersecurity_privacy", "Cybersecurity & Data Privacy", "🔐", "07",
       "Keeps the venture and its users safe and compliant by design.", [
        ("Posture Assessor", "Vulnerabilities and security maturity"),
        ("Threat Modeler", "Attack surface and threat scenarios"),
        ("Privacy-by-Design Specialist", "Data minimisation, consent, DPDP/GDPR"),
        ("Certification Advisor", "SOC 2 and ISO 27001 readiness"),
        ("Incident-Response Planner", "Breach readiness and response plans")]),
    _P("deep_tech", "Emerging / Deep Tech Scout", "🛰️", "07",
       "Separates buildable frontier tech from science fiction.", [
        ("Landscape Mapper", "Scans frontier and deep-tech domains"),
        ("TRL Assessor", "How mature and ready a frontier tech is"),
        ("Deep-Tech IP Analyst", "Patent landscape and freedom-to-operate"),
        ("Frontier-Feasibility Assessor", "Separates buildable from science fiction"),
        ("Talent & Lab Mapper", "Where the expertise and labs are")]),
    # ── 08 · Commercial & Growth ──────────────────────────────────────────
    _P("fundraising_capital", "Fundraising & Capital", "💰", "08",
       "Gets the venture funded on the best terms — dilutive and non-dilutive.", [
        ("Fundraising Strategist", "Round size, timing and sequencing"),
        ("Investor Matcher", "Right investors by stage, thesis and geo"),
        ("Pitch & Deck Specialist", "Narrative and investor deck"),
        ("Term-Sheet & Valuation Advisor", "Terms, negotiation and dilution"),
        ("Data-Room & DD Manager", "Diligence prep and data room")]),
    _P("sales_revops", "Sales & Revenue Ops", "🤝", "08",
       "Builds the machine that turns interest into revenue.", [
        ("Sales-Strategy Designer", "Motion, ideal-customer profile and model"),
        ("Playbook Builder", "Stages, scripts and methodology"),
        ("Pipeline & Forecast Analyst", "Funnel math and forecasting"),
        ("Comp & Quota Designer", "Quota, commission and team structure"),
        ("Enablement & CRM Specialist", "Tooling and enablement content")]),
    _P("pricing_strategist", "Pricing & Monetization", "🏷️", "08",
       "Decides how the venture captures value — the most under-served lever.", [
        ("Pricing Strategist", "Value-based, cost-plus and competitive pricing"),
        ("Packaging Designer", "Good/better/best tiers and bundling"),
        ("Elasticity Analyst", "Price sensitivity and WTP research"),
        ("Monetisation Designer", "How the business actually makes money"),
        ("Promo Optimizer", "Discounts that do not destroy margin")]),
    _P("customer_success", "Customer Success & Retention", "💚", "08",
       "Keeps and grows customers after the sale.", [
        ("Retention Strategist", "Churn reduction and engagement"),
        ("Churn Analyst", "Churn drivers and cohort analysis"),
        ("Onboarding Designer", "Activation and time-to-value"),
        ("CS-Ops Specialist", "Health scores and playbooks"),
        ("Expansion Strategist", "Upsell, cross-sell and net revenue retention")]),
    _P("partnerships_bd", "Partnerships & BD", "🔗", "08",
       "Builds leverage through alliances the venture cannot buy.", [
        ("Partnership Strategist", "Which partnerships create real leverage"),
        ("Ecosystem Mapper", "Potential partners and integrations"),
        ("Deal Structurer", "Partnership terms and revenue share"),
        ("Alliance Manager", "Manages ongoing partnerships"),
        ("Integration-Partner Specialist", "Technical and channel partnerships")]),
    _P("brand_creative", "Brand & Creative", "✨", "08",
       "Builds an identity people recognise and trust.", [
        ("Brand Strategist", "Brand architecture and positioning"),
        ("Naming Specialist", "Names and verbal identity"),
        ("Visual-Identity Director", "Logo, palette and design language"),
        ("Positioning Specialist", "Distinctive, ownable brand position"),
        ("Creative Director", "Campaign concepts and creative direction")]),
    _P("pr_communications", "PR & Communications", "📢", "08",
       "Shapes the public story and defends it under fire.", [
        ("PR Strategist", "Earned-media strategy"),
        ("Media-Relations Specialist", "Journalist and outlet relationships"),
        ("Crisis-Comms Planner", "Issue management and crisis response"),
        ("Thought-Leadership Ghostwriter", "Founder voice and bylines"),
        ("Comms Planner", "Message calendar and coordination")]),
    _P("community_ecosystem", "Community & Ecosystem", "🫂", "08",
       "Turns users into a compounding network and moat.", [
        ("Community Strategist", "Why, where and how to build community"),
        ("Network-Effects Designer", "Designs compounding network value"),
        ("Ecosystem Builder", "Cultivates partners, creators and advocates"),
        ("DevRel/Advocacy Specialist", "Developer relations and advocacy"),
        ("Community-Ops Manager", "Moderation, events and health metrics")]),
    # ── 09 · Human, Society & Meaning ─────────────────────────────────────
    _P("human_behaviour", "Human Behaviour", "🧠", "09",
       "Explains and shapes how people actually decide and act.", [
        ("Cognitive-Bias Specialist", "Biases affecting users, founders and markets"),
        ("Nudge Designer", "Choice architecture and behavioural interventions"),
        ("Motivation Psychologist", "What actually drives behaviour"),
        ("Persuasion Specialist", "Cialdini-style principles, applied ethically"),
        ("Habit-Change Analyst", "Habit loops and adoption psychology")]),
    _P("human_needs", "Human Needs", "🪷", "09",
       "Finds the real, sometimes unspoken, need under the want.", [
        ("Needs-Hierarchy Analyst", "Maslow-and-beyond need prioritisation"),
        ("JTBD Specialist", "Functional, emotional and social jobs"),
        ("Latent-Need Discoverer", "Unspoken and unmet needs"),
        ("Cultural-Variation Analyst", "How needs differ across cultures"),
        ("Emotional-Need Mapper", "The emotional drivers behind purchases")]),
    _P("philosophy_ethics", "Philosophy & Ethics", "🦉", "09",
       "Checks that clever also means right, across time and stakeholders.", [
        ("Framework Analyst", "Applies multiple moral frameworks to the decision"),
        ("Values-Alignment Checker", "Aligns strategy with stated values"),
        ("Dilemma Resolver", "Structured resolution of ethical tension"),
        ("Second-Order Ethicist", "Unintended consequences and externalities"),
        ("Stakeholder-Ethics Mapper", "Who is affected and what is fair")]),
    _P("money_happiness", "Money & Happiness", "😊", "09",
       "Keeps the founder whole while the venture grows.", [
        ("Wellbeing Economist", "Money-happiness research and diminishing returns"),
        ("Founder-Wellbeing Analyst", "Burnout risk and sustainable pace"),
        ("Purpose-Alignment Coach", "Aligns the venture with personal meaning"),
        ("Meaning-vs-Money Advisor", "Lifestyle vs scale trade-offs"),
        ("Sustainable-Ambition Designer", "Frames the long game")]),
    _P("philanthropy_impact", "Philanthropy & Impact", "🤲", "09",
       "Designs how the venture gives back with real leverage.", [
        ("Impact-Model Designer", "Theory of change and impact pathways"),
        ("CSR Strategist", "CSR compliance and program design"),
        ("Impact-Measurement Specialist", "IMP and SROI metrics"),
        ("Giving-Strategy Advisor", "Effective, high-leverage philanthropy"),
        ("Blended-Value Architect", "Combines profit and purpose")]),
    _P("esg_impact", "ESG & Impact", "🌱", "09",
       "Makes sustainability a strategy and a disclosure, not a slogan.", [
        ("ESG-Framework Specialist", "GRI, SASB and TCFD frameworks"),
        ("Carbon Analyst", "Emissions accounting and reduction"),
        ("Sustainability Strategist", "Circular economy and sustainable ops"),
        ("Reporting & Ratings Specialist", "Disclosures and ratings improvement"),
        ("ESG-Regulation Specialist", "BRSR, CSRD and related rules")]),
    _P("founder_coaching", "Founder Coaching & Org Design", "🧗", "09",
       "Grows the person and the team behind the venture.", [
        ("Founder Coach", "One-on-one founder development"),
        ("Leadership-Development Specialist", "Builds leadership capacity as the team grows"),
        ("Org-Scaling Advisor", "Structure and culture that scale"),
        ("Co-Founder Mediator", "Manages co-founder and team dynamics"),
        ("Decision-Support Facilitator", "Frameworks for high-stakes decisions")]),
    # ── 10 · Adversarial & Quality Assurance ──────────────────────────────
    _P("red_team", "Red Team", "⚔️", "10",
       "Attacks the plan so reality does not have to.", [
        ("Assumption Breaker", "Attacks the core assumptions"),
        ("Failure-Mode Analyst", "FMEA — what could kill this"),
        ("Pre-Mortem Facilitator", "Imagines failure and backcasts the causes"),
        ("Threat Modeler", "Strategic and competitive threats"),
        ("Worst-Case Builder", "Tail risks and disaster scenarios")]),
    _P("fact_checker", "Fact Checker", "✅", "10",
       "Ensures nothing that ships is untrue or unsupported.", [
        ("Claim Verifier", "Checks every factual claim against sources"),
        ("Source Validator", "Confirms source authenticity and authority"),
        ("Data-Integrity Auditor", "Re-checks numbers, units and calculations"),
        ("Statistical-Claim Auditor", "Validates statistics and methodology"),
        ("Consistency Checker", "Finds internal contradictions across the work")]),
    _P("bias_auditor", "Bias Auditor", "🪞", "10",
       "Surfaces the blind spots in the analysis itself.", [
        ("Cognitive-Bias Detector", "Confirmation, anchoring and survivorship bias in the work"),
        ("Sampling-Bias Auditor", "Biased data and samples"),
        ("Framing-Bias Checker", "How framing skews the conclusion"),
        ("Perspective-Diversity Auditor", "Missing viewpoints and stakeholders"),
        ("Fairness Reviewer", "Equity and inclusion considerations")]),
    _P("devils_advocate", "Devil's Advocate", "😈", "10",
       "Argues the other side hard, on purpose.", [
        ("Contrarian Arguer", "Builds the strongest case against"),
        ("Steelman Builder", "The strongest version of the opposing view"),
        ("Alt-Hypothesis Generator", "Other explanations and paths"),
        ("Groupthink Breaker", "Injects dissent when consensus forms too fast"),
        ("Inversion Analyst", "Assumes we are wrong and works backward")]),
    # ── 11 · Synthesis & Delivery ─────────────────────────────────────────
    _P("connecting_dots", "Connecting Dots", "🕸️", "11",
       "The heart of the thesis — weaves every domain into one non-linear whole.", [
        ("Systems Synthesizer", "Feedback loops, causal-loop and stock-flow thinking"),
        ("Cross-Domain Integrator", "Weaves every expert output into one whole"),
        ("Analogy Connector", "Connects disparate insights across domains"),
        ("Insight Distiller", "Extracts the so-what and the key takeaways"),
        ("Emergence Spotter", "Insights that appear only when domains combine")]),
    _P("storytelling", "Story Teller", "📖", "11",
       "Turns the analysis into a narrative the client feels.", [
        ("Narrative Architect", "Story structure, arc and hook"),
        ("Pitch Crafter", "Investor and customer pitch narratives"),
        ("Audience Tailor", "Adapts the story to VC, customer or board"),
        ("Emotional-Arc Designer", "Tension, resolution and resonance"),
        ("Metaphor Smith", "Makes complex ideas vivid and memorable")]),
    _P("visualizer", "Visualizer", "🎨", "11",
       "Makes the complex visible at a glance.", [
        ("Data-Viz Specialist", "Charts that reveal, not decorate"),
        ("Infographic Designer", "Visual summaries of complex findings"),
        ("Diagram & Flow Designer", "Process and architecture diagrams"),
        ("Visual-Metaphor Designer", "Conceptual visuals for abstract ideas"),
        ("Dashboard Builder", "Live, interactive dashboards")]),
    _P("reporter", "Reporter", "🖋️", "11",
       "Assembles everything into a clean, readable deliverable.", [
        ("Executive-Summary Writer", "The TL;DR and key findings up top"),
        ("Document Architect", "Sections, flow and readability"),
        ("Clarity Editor", "Tightens prose and removes jargon"),
        ("Multi-Format Producer", "Report, deck, one-pager and memo"),
        ("Style Editor", "Tone, formatting and house voice")]),
    _P("verdict_composer", "Verdict Composer", "📜", "11",
       "Delivers the decision — what to do, how sure, and what next.", [
        ("Recommendation Synthesizer", "The final here-is-what-to-do"),
        ("Confidence & Caveat Expresser", "Certainty levels, risks and unknowns"),
        ("Action-Plan Generator", "Concrete next steps, owners and timelines"),
        ("Roadmap Builder", "Sequencing, quick wins vs big bets"),
        ("Rationale Documenter", "Why this verdict — full traceability")]),
]

PLAYER_BY_ID: dict[str, Player] = {p.id: p for p in PLAYERS}


def players_in(family_id: str) -> list[Player]:
    return [p for p in PLAYERS if p.family == family_id]


# the general MCDA dimensions the Weighing Engine scores the orchestra verdict on —
# each maps to the scored families whose players produce it (movement → dimension)
ORCHESTRA_DIMENSIONS: dict[str, list[str]] = {
    "Opportunity": ["market_analyst", "consumer_analysis", "competitor_intel", "market_data", "trends"],
    "Economics": ["finance_modeler", "pricing_strategist", "banking", "fundraising_capital", "macroeconomist"],
    "Strategy": ["business_model", "gtm_distribution", "marketing_strategy", "production_ops", "sales_revops"],
    "Feasibility": ["software_architecture", "ai_ml_strategist", "data_analytics", "product_ux",
                    "deep_tech", "supply_chain"],
    "LegalRisk": ["legal", "tax", "policy_compliance", "insurance_risk", "regulator", "cybersecurity_privacy"],
    "Human": ["human_behaviour", "human_needs", "philosophy_ethics", "money_happiness",
              "esg_impact", "philanthropy_impact"],
}

# which families the depth convenes (Pulse = the spine; Board/War add breadth).
# the framing + delivery + QA families always run; these are the ANALYTICAL families.
DEPTH_FAMILIES = {
    "pulse": ["03", "04", "05"],
    "board": ["03", "04", "05", "06", "08", "09"],
    "war_room": ["03", "04", "05", "06", "07", "08", "09"],
}


def count_at_depth(depth: str) -> tuple[int, int]:
    """(#players, #instruments) an orchestra run convenes at this depth."""
    fams = set(DEPTH_FAMILIES.get(depth, DEPTH_FAMILIES["board"])) | {"02", "10", "11"}
    ps = [p for p in PLAYERS if p.family in fams]
    return len(ps), sum(len(p.instruments) for p in ps)
