"""
Connecting-Dots News Intelligence Agent
Advanced pattern recognition and meta-analysis across disparate news sources
Identifies non-obvious connections, second-order effects, and emerging narratives
"""
import os
import sys
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import re

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from services.llm_service import LLMService
from services.rag_service import RAGService


class ConnectingDotsAgent:
    """
    Connecting-Dots News Intelligence Agent

    Advanced intelligence layer that performs:
    - Cross-domain pattern recognition (political, economic, social, technological)
    - Causal chain analysis (map cause-and-effect relationships)
    - Second-order thinking (predict non-obvious consequences)
    - Narrative detection (identify emerging narratives across media)
    - Weak signal amplification (detect early indicators of major trends)
    - Contrarian insights (identify what mainstream is missing)
    - Multi-timeframe analysis (short-term noise vs long-term signal)
    - Synthesis intelligence (connect dots across disparate events)
    """

    def __init__(self):
        """Initialize Connecting-Dots Agent"""
        self.name = "ConnectingDotsAgent"
        self.description = "Advanced pattern recognition and meta-intelligence across news and events"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

        # Define domain categories for cross-domain analysis
        self.domains = ["Political", "Economic", "Social", "Technological", "Environmental", "Regulatory"]

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process connecting-dots analysis request"""
        try:
            # Get recent news and events (mock - integrate with real news APIs)
            news_data = await self._fetch_recent_news(query, context)

            # Perform multi-layered analysis
            cross_domain_patterns = await self._cross_domain_pattern_recognition(news_data)
            causal_chains = await self._causal_chain_analysis(news_data)
            second_order_effects = await self._second_order_thinking(news_data, causal_chains)
            narratives = await self._narrative_detection(news_data)
            weak_signals = await self._weak_signal_amplification(news_data)
            contrarian_insights = await self._contrarian_analysis(news_data, narratives)
            timeframe_analysis = await self._multi_timeframe_analysis(news_data)

            # Synthesize meta-intelligence
            synthesis = await self._synthesize_intelligence(
                query=query,
                cross_domain=cross_domain_patterns,
                causal=causal_chains,
                second_order=second_order_effects,
                narratives=narratives,
                weak_signals=weak_signals,
                contrarian=contrarian_insights,
                timeframe=timeframe_analysis
            )

            # Generate actionable insights
            actionable_insights = await self._generate_actionable_insights(synthesis, context)

            # Create response
            response = await self._generate_response(
                query,
                synthesis,
                actionable_insights
            )

            return {
                "answer": response,
                "synthesis": synthesis,
                "cross_domain_patterns": cross_domain_patterns,
                "causal_chains": causal_chains,
                "second_order_effects": second_order_effects,
                "narratives": narratives,
                "weak_signals": weak_signals,
                "contrarian_insights": contrarian_insights,
                "actionable_insights": actionable_insights,
                "confidence": 0.75,  # Lower confidence due to complexity
                "agent": self.name
            }

        except Exception as e:
            return self._error_response(str(e))

    async def _fetch_recent_news(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Fetch recent news across domains (mock - integrate with NewsAPI, Google News, etc.)"""
        # In production, integrate with:
        # - NewsAPI
        # - Google News API
        # - Reuters API
        # - Bloomberg Terminal
        # - Twitter API (for real-time signals)
        # - Financial news APIs

        # Mock news data for demonstration
        return [
            {
                "id": "news_1",
                "headline": "RBI announces 25bps repo rate cut to 6.25%",
                "domain": "Economic",
                "sub_domain": "Monetary Policy",
                "date": "2025-11-15",
                "sentiment": "Positive",
                "entities": ["RBI", "Monetary Policy", "Interest Rates"],
                "impact_sectors": ["Banking", "Real Estate", "Auto", "Consumer Durables"]
            },
            {
                "id": "news_2",
                "headline": "Government announces Production Linked Incentive (PLI) for EV batteries",
                "domain": "Political",
                "sub_domain": "Policy",
                "date": "2025-11-14",
                "sentiment": "Positive",
                "entities": ["Government", "PLI", "EV", "Manufacturing"],
                "impact_sectors": ["Automotive", "Battery Manufacturing", "Clean Energy"]
            },
            {
                "id": "news_3",
                "headline": "Tech layoffs continue - 50,000 jobs cut across major US tech firms",
                "domain": "Technological",
                "sub_domain": "Employment",
                "date": "2025-11-13",
                "sentiment": "Negative",
                "entities": ["Big Tech", "Layoffs", "Silicon Valley"],
                "impact_sectors": ["Technology", "Real Estate (SF Bay Area)", "Consulting"]
            },
            {
                "id": "news_4",
                "headline": "Urban to rural migration accelerates - Tier 2/3 cities see population influx",
                "domain": "Social",
                "sub_domain": "Demographics",
                "date": "2025-11-12",
                "sentiment": "Neutral",
                "entities": ["Remote Work", "Migration", "Urbanization"],
                "impact_sectors": ["Real Estate", "Infrastructure", "Retail"]
            },
            {
                "id": "news_5",
                "headline": "SEBI tightens regulations on finfluencers and unregistered advisors",
                "domain": "Regulatory",
                "sub_domain": "Financial Regulation",
                "date": "2025-11-11",
                "sentiment": "Neutral",
                "entities": ["SEBI", "Finfluencers", "Regulation"],
                "impact_sectors": ["Financial Services", "Social Media", "Edtech"]
            },
            {
                "id": "news_6",
                "headline": "India's GDP growth slows to 5.8% in Q2, below expectations",
                "domain": "Economic",
                "sub_domain": "Macroeconomics",
                "date": "2025-11-10",
                "sentiment": "Negative",
                "entities": ["GDP", "Economic Growth", "India"],
                "impact_sectors": ["All sectors"]
            },
            {
                "id": "news_7",
                "headline": "Massive data breach at major fintech - 10M user records compromised",
                "domain": "Technological",
                "sub_domain": "Cybersecurity",
                "date": "2025-11-09",
                "sentiment": "Negative",
                "entities": ["Data Breach", "Fintech", "Cybersecurity"],
                "impact_sectors": ["Fintech", "Cybersecurity", "Insurance"]
            }
        ]

    async def _cross_domain_pattern_recognition(
        self,
        news_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify patterns across different domains (P.E.S.T.E.R analysis)"""
        # Group news by domain
        domain_map = {}
        for news in news_data:
            domain = news["domain"]
            if domain not in domain_map:
                domain_map[domain] = []
            domain_map[domain].append(news)

        patterns = []

        # Pattern 1: RBI rate cut + EV PLI + GDP slowdown
        pattern_1 = {
            "pattern_id": "PATTERN_1",
            "name": "Coordinated Economic Stimulus",
            "connecting_events": [
                news_data[0],  # RBI rate cut
                news_data[1],  # EV PLI
                news_data[5]   # GDP slowdown
            ],
            "domains_involved": ["Economic", "Political"],
            "insight": "Government using both monetary (RBI) and fiscal (PLI) levers to counter GDP slowdown",
            "confidence": "High",
            "business_implication": "Capital-intensive sectors (auto, infra) will benefit from cheaper credit + incentives",
            "timing": "Short-term boost (next 6-12 months)",
            "who_wins": ["Auto manufacturers", "Real estate developers", "Capital goods"],
            "who_loses": ["Fixed-income investors (lower yields)", "Import-dependent sectors (weaker rupee)"]
        }
        patterns.append(pattern_1)

        # Pattern 2: Tech layoffs + Urban-rural migration + Real estate
        pattern_2 = {
            "pattern_id": "PATTERN_2",
            "name": "Geographic Restructuring of Economy",
            "connecting_events": [
                news_data[2],  # Tech layoffs
                news_data[3]   # Urban-rural migration
            ],
            "domains_involved": ["Technological", "Social", "Economic"],
            "insight": "Tech layoffs (forced) + Remote work acceptance (voluntary) → Tier 1 city exodus → Tier 2/3 boom",
            "confidence": "High",
            "business_implication": "Tier 2/3 city infrastructure and services will be in high demand",
            "timing": "Medium-term structural shift (2-5 years)",
            "who_wins": ["Tier 2/3 real estate", "Local retail", "Co-working spaces in smaller cities"],
            "who_loses": ["Tier 1 commercial real estate", "Metro-area services"]
        }
        patterns.append(pattern_2)

        # Pattern 3: SEBI finfluencer crackdown + Data breach
        pattern_3 = {
            "pattern_id": "PATTERN_3",
            "name": "Digital Trust Crisis",
            "connecting_events": [
                news_data[4],  # SEBI finfluencer regulation
                news_data[6]   # Data breach
            ],
            "domains_involved": ["Regulatory", "Technological"],
            "insight": "Regulatory tightening + security failures → Trust deficit in digital financial services",
            "confidence": "Medium",
            "business_implication": "Compliance and cybersecurity become competitive moats, not just costs",
            "timing": "Immediate (ongoing regulatory action)",
            "who_wins": ["Regulated entities", "Cybersecurity firms", "Traditional banks (trust premium)"],
            "who_loses": ["Unregistered advisors", "Fintech with weak security", "Social media platforms"]
        }
        patterns.append(pattern_3)

        return patterns

    async def _causal_chain_analysis(
        self,
        news_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Map cause-and-effect chains across events"""
        chains = []

        # Chain 1: GDP slowdown → RBI action → Sectoral impact
        chain_1 = {
            "chain_id": "CHAIN_1",
            "trigger_event": news_data[5],  # GDP slowdown
            "causal_links": [
                {
                    "cause": "GDP growth slows to 5.8%",
                    "mechanism": "Economic underperformance signals slack in demand",
                    "effect": "RBI cuts repo rate by 25bps",
                    "confidence": "Very High",
                    "lag_time": "1-2 quarters"
                },
                {
                    "cause": "RBI cuts repo rate to 6.25%",
                    "mechanism": "Lower policy rate → Banks reduce lending rates",
                    "effect": "Home loans, auto loans become cheaper",
                    "confidence": "High",
                    "lag_time": "1-3 months"
                },
                {
                    "cause": "Cheaper home loans",
                    "mechanism": "Lower EMIs → More affordability",
                    "effect": "Real estate demand uptick",
                    "confidence": "Medium-High",
                    "lag_time": "3-6 months"
                },
                {
                    "cause": "Real estate demand increases",
                    "mechanism": "Construction activity ramps up",
                    "effect": "GDP growth recovers (real estate is 7% of GDP)",
                    "confidence": "Medium",
                    "lag_time": "6-12 months"
                }
            ],
            "ultimate_outcome": "GDP growth rebounds to ~6.5% by Q4 2026",
            "feedback_loops": "Positive feedback: Growth → Confidence → Investment → More growth"
        }
        chains.append(chain_1)

        # Chain 2: Tech layoffs → Migration → Infrastructure demand
        chain_2 = {
            "chain_id": "CHAIN_2",
            "trigger_event": news_data[2],  # Tech layoffs
            "causal_links": [
                {
                    "cause": "50,000 tech jobs cut in US",
                    "mechanism": "Laid-off workers seek opportunities, remote work normalized",
                    "effect": "Migration from expensive Tier 1 cities",
                    "confidence": "High",
                    "lag_time": "Immediate to 6 months"
                },
                {
                    "cause": "Professionals move to Tier 2/3 cities",
                    "mechanism": "Increased disposable income in smaller cities",
                    "effect": "Demand for quality housing, cafes, gyms, schools",
                    "confidence": "High",
                    "lag_time": "6-18 months"
                },
                {
                    "cause": "Tier 2/3 infrastructure demand surge",
                    "mechanism": "Local governments invest in amenities to attract talent",
                    "effect": "New airports, metro lines, tech parks in Tier 2 cities",
                    "confidence": "Medium",
                    "lag_time": "2-5 years"
                }
            ],
            "ultimate_outcome": "Rebalancing of economic activity - Tier 2/3 cities become mini-hubs",
            "feedback_loops": "Positive: More talent → Better infra → Attracts companies → More jobs → More talent"
        }
        chains.append(chain_2)

        return chains

    async def _second_order_thinking(
        self,
        news_data: List[Dict[str, Any]],
        causal_chains: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Predict second-order and third-order consequences (non-obvious effects)"""
        second_order = []

        # From RBI rate cut
        effect_1 = {
            "event": "RBI rate cut to 6.25%",
            "first_order_obvious": "Cheaper loans, more borrowing",
            "second_order_effects": [
                {
                    "effect": "Currency depreciation",
                    "mechanism": "Lower rates → Capital outflow → Rupee weakens",
                    "impact": "Imports become expensive (inflation risk), Exports become competitive",
                    "probability": "Medium (50-60%)",
                    "implication_for_entrepreneurs": "Import-dependent startups face margin pressure; Export-oriented businesses benefit"
                },
                {
                    "effect": "Asset price inflation",
                    "mechanism": "Cheap money → Speculative investments → Real estate/stock bubbles",
                    "impact": "Wealth effect for asset holders, affordability crisis for non-owners",
                    "probability": "Medium-High (60-70%)",
                    "implication_for_entrepreneurs": "Funding easier (asset-rich investors), but talent acquisition cost rises (employees demand more)"
                },
                {
                    "effect": "Bank profitability pressure",
                    "mechanism": "Lower rates → Compressed NIMs (Net Interest Margins)",
                    "impact": "Banks become risk-averse, tighten lending standards",
                    "probability": "High (70-80%)",
                    "implication_for_entrepreneurs": "Despite rate cut, getting loans might not be easier (banks selective)"
                }
            ],
            "third_order_effects": [
                {
                    "effect": "Inflation spike forces RBI to reverse course",
                    "mechanism": "Asset inflation + Import inflation → CPI rises → RBI hikes rates again",
                    "timeframe": "12-18 months",
                    "impact": "Boom-bust cycle - those who over-leverage get caught",
                    "implication": "Maintain conservative leverage, don't over-expand on cheap credit"
                }
            ]
        }
        second_order.append(effect_1)

        # From EV PLI scheme
        effect_2 = {
            "event": "Government announces EV battery PLI",
            "first_order_obvious": "Battery manufacturers get subsidies, more local production",
            "second_order_effects": [
                {
                    "effect": "Lithium import dependence becomes strategic risk",
                    "mechanism": "PLI succeeds → Battery demand soars → India still imports 100% lithium",
                    "impact": "Geopolitical vulnerability (China controls lithium supply chain)",
                    "probability": "Very High (80%+)",
                    "implication_for_entrepreneurs": "Opportunities in lithium recycling, alternative battery chemistries (sodium-ion)"
                },
                {
                    "effect": "Traditional auto component makers face obsolescence",
                    "mechanism": "EV has 30% fewer parts than ICE vehicles",
                    "impact": "Engine, transmission, exhaust system manufacturers struggle",
                    "probability": "High (70-80%)",
                    "implication_for_entrepreneurs": "Pivot opportunities - help legacy auto component firms transition to EV parts"
                },
                {
                    "effect": "Electricity grid stress",
                    "mechanism": "Mass EV adoption → Charging demand spikes → Grid overload",
                    "impact": "Need for smart grids, charging infrastructure",
                    "probability": "High (in 5+ years, 80%)",
                    "implication_for_entrepreneurs": "EV charging network, battery swapping, grid management software opportunities"
                }
            ],
            "third_order_effects": []
        }
        second_order.append(effect_2)

        return second_order

    async def _narrative_detection(
        self,
        news_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detect emerging narratives and frames across media"""
        return {
            "dominant_narratives": [
                {
                    "narrative": "Economic Slowdown Concerns",
                    "prevalence": "High (60% of economic news)",
                    "sentiment": "Negative",
                    "evidence": [news_data[5], news_data[0]],  # GDP slowdown, RBI cut
                    "counter_narrative": "Soft landing, not recession",
                    "reality_check": "5.8% growth is still healthy by global standards (EU at 1.5%)"
                },
                {
                    "narrative": "Green Transition is Accelerating",
                    "prevalence": "Medium (40% of policy news)",
                    "sentiment": "Positive",
                    "evidence": [news_data[1]],  # EV PLI
                    "counter_narrative": "Greenwashing, fossil fuels still dominant",
                    "reality_check": "EVs are <2% of vehicle sales, but trajectory is steep"
                },
                {
                    "narrative": "Remote Work is Dead / Return to Office",
                    "prevalence": "High in corporate news, but data contradicts",
                    "sentiment": "Mixed",
                    "evidence": [news_data[3]],  # Migration patterns
                    "counter_narrative": "Hybrid is the new normal",
                    "reality_check": "Narrative pushed by commercial real estate interests; Data shows sustained remote work"
                }
            ],
            "narrative_shifts": [
                {
                    "shift": "From 'Fintech is the future' to 'Fintech needs regulation'",
                    "trigger": news_data[4],  # SEBI crackdown
                    "timing": "Last 3 months",
                    "implications": "Regulatory compliance becomes competitive advantage"
                }
            ],
            "coordinated_messaging": {
                "detected": False,
                "note": "No evidence of coordinated narrative push (would see same talking points across multiple sources)"
            }
        }

    async def _weak_signal_amplification(
        self,
        news_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect weak signals - early indicators of major trends before they're obvious"""
        weak_signals = []

        signal_1 = {
            "signal_id": "WEAK_SIGNAL_1",
            "signal": "Tier 2/3 city migration is accelerating (news_4)",
            "current_prominence": "Low (one news item, buried in social section)",
            "why_it_matters": "This is a structural economic shift that will compound over decades",
            "historical_parallel": "US suburbanization in 1950s-70s (interstate highways + cars)",
            "potential_magnitude": "Could reshape Indian economy - 40% of population in Tier 1 → 60% in Tier 2/3 by 2040",
            "who_is_missing_this": "Most investors focused on Tier 1 metros",
            "contrarian_bet": "Invest in Tier 2/3 real estate, logistics, retail NOW (before it's obvious)",
            "leading_indicators_to_watch": [
                "Pin code-level e-commerce data (Are Tier 2/3 orders growing faster?)",
                "Domestic flight bookings to Tier 2 cities",
                "Co-working space openings in non-metros",
                "LinkedIn job postings mentioning 'remote' in Tier 2 locations"
            ],
            "timing": "Early days (2-3 years before mainstream recognition)",
            "risk": "Could reverse if companies force return-to-office"
        }
        weak_signals.append(signal_1)

        signal_2 = {
            "signal_id": "WEAK_SIGNAL_2",
            "signal": "Data breach at fintech (news_7) + SEBI regulation (news_4)",
            "current_prominence": "Medium (discussed in tech circles, but not mainstream concern yet)",
            "why_it_matters": "Precursor to major digital trust crisis",
            "historical_parallel": "Cambridge Analytica (2018) → GDPR → Entire privacy tech ecosystem",
            "potential_magnitude": "Could birth a ₹10,000 Cr+ cybersecurity/privacy industry in India",
            "who_is_missing_this": "Most startups treating cybersecurity as compliance checkbox",
            "contrarian_bet": "Cybersecurity-as-a-service for SMEs, Privacy-preserving tech (federated learning, etc.)",
            "leading_indicators_to_watch": [
                "Number of data breach disclosures (increasing?)",
                "Cyber insurance premium trends (rising = risk is real)",
                "Regulatory consultations on data protection",
                "Enterprise budget allocation to security"
            ],
            "timing": "Very early (1-2 years before inflection point)",
            "risk": "Hype without substance (many cybersecurity companies fail)"
        }
        weak_signals.append(signal_2)

        return weak_signals

    async def _contrarian_analysis(
        self,
        news_data: List[Dict[str, Any]],
        narratives: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify contrarian insights - what is the mainstream missing?"""
        contrarian = []

        insight_1 = {
            "mainstream_view": "GDP slowdown to 5.8% is bad news",
            "contrarian_view": "Slowdown is healthy correction after overheating",
            "evidence": [
                "Inflation was running hot at 7%+ earlier this year",
                "Unsustainable credit growth in retail loans",
                "Asset prices (stocks, real estate) were in bubble territory"
            ],
            "why_mainstream_is_wrong": "Media conflates 'growth' with 'good' - but quality matters more than speed",
            "actionable_insight": "Slowdown shakes out weak players, creates acquisition opportunities for cash-rich firms",
            "confidence": "Medium (60%)",
            "timeframe": "6-12 months to see if correction is healthy or concerning"
        }
        contrarian.append(insight_1)

        insight_2 = {
            "mainstream_view": "EV PLI is great for environment and economy",
            "contrarian_view": "PLI might be late-stage bet on obsolescing technology",
            "evidence": [
                "Battery tech is still evolving (solid-state, lithium-sulfur on horizon)",
                "Hydrogen fuel cells might leapfrog batteries for commercial vehicles",
                "India lacks lithium - PLI for batteries doesn't solve strategic dependence"
            ],
            "why_mainstream_is_wrong": "Government picking winners is risky - market should decide",
            "actionable_insight": "Hedge bets - don't go all-in on lithium-ion batteries, explore alternatives",
            "confidence": "Low-Medium (40%)",
            "timeframe": "5-10 years to see if batteries remain dominant"
        }
        contrarian.append(insight_2)

        insight_3 = {
            "mainstream_view": "Tech layoffs are bad for economy",
            "contrarian_view": "Layoffs are reallocation from unproductive to productive uses",
            "evidence": [
                "Many laid-off engineers were in low-impact roles (eg. Meta's metaverse)",
                "Talent now available for high-impact sectors (climate, healthcare, education)",
                "Startup ecosystem gets experienced talent at lower cost"
            ],
            "why_mainstream_is_wrong": "Broken windows fallacy - assumes laid-off workers will stay unemployed",
            "actionable_insight": "This is prime hiring time for startups - top talent available, reasonable salaries",
            "confidence": "High (75%)",
            "timeframe": "Already happening (6-12 months for full reallocation)"
        }
        contrarian.append(insight_3)

        return contrarian

    async def _multi_timeframe_analysis(
        self,
        news_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Separate short-term noise from long-term signal"""
        return {
            "immediate_noise": {
                "timeframe": "1-7 days",
                "events": [
                    {
                        "event": "Daily stock market movements",
                        "signal_vs_noise": "99% noise",
                        "action": "Ignore unless >5% move"
                    }
                ]
            },
            "short_term": {
                "timeframe": "1-3 months",
                "events": [
                    {
                        "event": news_data[0]["headline"],  # RBI rate cut
                        "signal_vs_noise": "60% signal (policy response to real data)",
                        "action": "Monitor for follow-up actions",
                        "prediction": "Likely 1-2 more cuts if GDP stays weak"
                    }
                ],
                "interpretation": "RBI in easing cycle - good for borrowers, adjust strategy accordingly"
            },
            "medium_term": {
                "timeframe": "6-24 months",
                "events": [
                    {
                        "event": news_data[1]["headline"],  # EV PLI
                        "signal_vs_noise": "80% signal (structural policy shift)",
                        "action": "Position businesses to capitalize on EV transition",
                        "prediction": "₹50,000 Cr+ investment in battery manufacturing by 2027"
                    },
                    {
                        "event": news_data[3]["headline"],  # Migration
                        "signal_vs_noise": "70% signal (demographic shift)",
                        "action": "Explore Tier 2/3 market opportunities",
                        "prediction": "10-15% of urban professionals will relocate to smaller cities"
                    }
                ],
                "interpretation": "Sectoral and geographic shifts creating new opportunities"
            },
            "long_term": {
                "timeframe": "3-10 years",
                "events": [
                    {
                        "event": "Digitization + AI + Remote work convergence",
                        "signal_vs_noise": "90% signal (secular mega-trend)",
                        "action": "Build digital-first, location-agnostic businesses",
                        "prediction": "Physical location becomes less relevant for knowledge work"
                    },
                    {
                        "event": "Climate transition (implicit in EV PLI)",
                        "signal_vs_noise": "95% signal (civilizational shift)",
                        "action": "Align business models with sustainability",
                        "prediction": "Carbon tax, ESG mandates, green financing become ubiquitous"
                    }
                ],
                "interpretation": "Structural forces reshaping economy - align with these or face obsolescence"
            },
            "recommendation": "Ignore short-term noise, respond tactically to medium-term, position strategically for long-term"
        }

    async def _synthesize_intelligence(
        self,
        query: str,
        cross_domain: List[Dict[str, Any]],
        causal: List[Dict[str, Any]],
        second_order: List[Dict[str, Any]],
        narratives: Dict[str, Any],
        weak_signals: List[Dict[str, Any]],
        contrarian: List[Dict[str, Any]],
        timeframe: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize all layers into meta-intelligence"""
        return {
            "synthesis_summary": "Multiple interconnected forces at play - economic headwinds, policy response, structural shifts",
            "key_insights": [
                "Government using coordinated monetary + fiscal stimulus to counter slowdown (Pattern 1)",
                "Geographic rebalancing underway - Tier 2/3 cities rising (Pattern 2, Weak Signal 1)",
                "Digital trust becoming critical competitive moat (Pattern 3, Weak Signal 2)",
                "Don't confuse slowdown with recession - quality correction (Contrarian 1)",
                "Tech talent reallocation is opportunity, not crisis (Contrarian 3)"
            ],
            "non_obvious_connections": [
                "RBI rate cut → Rupee depreciation → Export competitiveness boost (Second-order)",
                "Tech layoffs → Migration → Tier 2 infrastructure boom (Causal Chain 2)",
                "EV PLI → Lithium dependence → Recycling opportunity (Second-order)"
            ],
            "what_others_are_missing": [
                "Tier 2/3 migration is early-stage mega-trend (Weak Signal 1)",
                "Cybersecurity crisis brewing (Weak Signal 2)",
                "Slowdown is healthy, not harmful (Contrarian 1)"
            ],
            "confidence_levels": {
                "high_confidence_predictions": [
                    "RBI will cut rates 1-2 more times",
                    "EV adoption will accelerate significantly",
                    "Tier 2/3 cities will see infrastructure investment"
                ],
                "medium_confidence_predictions": [
                    "GDP will recover to 6.5% by Q4 2026",
                    "Cybersecurity becomes major sector",
                    "Some asset price inflation in next 12 months"
                ],
                "low_confidence_speculations": [
                    "Battery tech might be leapfrogged by alternatives",
                    "Rupee depreciation extent unknown"
                ]
            },
            "overall_market_sentiment": "Cautiously optimistic - headwinds acknowledged, but policy response proactive",
            "recommended_stance": "Balanced - take advantage of rate cuts, but don't over-leverage; explore Tier 2/3; invest in cybersecurity"
        }

    async def _generate_actionable_insights(
        self,
        synthesis: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Generate specific, actionable insights for entrepreneurs"""
        return [
            {
                "insight": "Cheap credit window opening",
                "action": "Refinance existing debt, lock in lower rates for 3-5 years",
                "timeframe": "Next 3-6 months",
                "risk": "Low"
            },
            {
                "insight": "Tier 2/3 markets underserved",
                "action": "Pilot products/services in cities like Indore, Coimbatore, Jaipur",
                "timeframe": "Start in Q1 2026",
                "risk": "Medium (unproven market)"
            },
            {
                "insight": "Regulatory compliance as moat",
                "action": "Get certifications (ISO 27001, SOC 2) NOW before competitors do",
                "timeframe": "Within 6 months",
                "risk": "Low (cost is low, upside high)"
            },
            {
                "insight": "Talent arbitrage opportunity",
                "action": "Hire senior laid-off tech talent at 20-30% discount to 2021 salaries",
                "timeframe": "Next 6 months (window closing)",
                "risk": "Low"
            },
            {
                "insight": "Export opportunity from rupee weakness",
                "action": "If you have exportable product/service, double down on global expansion",
                "timeframe": "Next 12 months",
                "risk": "Medium (FX volatility)"
            },
            {
                "insight": "EV ecosystem gaps",
                "action": "Explore B2B services for EV players (charging infra, battery mgmt software, recycling)",
                "timeframe": "Start R&D now, launch in 12-18 months",
                "risk": "Medium-High (emerging market)"
            }
        ]

    async def _generate_response(
        self,
        query: str,
        synthesis: Dict[str, Any],
        actionable_insights: List[Dict[str, str]]
    ) -> str:
        """Generate comprehensive response using LLM"""
        prompt = f"""
You are an elite strategic intelligence analyst. Provide a compelling, insight-rich analysis based on this meta-intelligence:

Query: {query}

Synthesis: {json.dumps(synthesis, indent=2)}

Actionable Insights: {json.dumps(actionable_insights, indent=2)}

Generate a response (500-600 words) that:
1. Starts with the key synthesis - what's REALLY happening beneath surface events
2. Explains non-obvious connections that others are missing
3. Provides contrarian perspectives where mainstream is wrong
4. Distinguishes noise from signal (short-term vs long-term)
5. Concludes with specific, actionable recommendations

Write in a direct, confident style. Use phrases like:
- "While everyone is focused on X, the real story is Y"
- "Connect the dots: Event A → Event B → Non-obvious consequence C"
- "Here's what the data shows that narratives miss"
- "Actionable: Do X within Y timeframe before competitors realize"

Be insightful, contrarian where warranted, and actionable.
"""
        try:
            return await self.llm_service.generate(prompt=prompt, temperature=0.7, max_tokens=700)
        except:
            return self._fallback_response(synthesis, actionable_insights)

    def _fallback_response(
        self,
        synthesis: Dict[str, Any],
        actionable_insights: List[Dict[str, str]]
    ) -> str:
        """Fallback response if LLM fails"""
        response = "## Intelligence Synthesis: Connecting the Dots\n\n"
        response += f"**Key Insight:** {synthesis['synthesis_summary']}\n\n"
        response += "**What Others Are Missing:**\n"
        for item in synthesis['what_others_are_missing']:
            response += f"- {item}\n"
        response += "\n**Actionable Recommendations:**\n"
        for insight in actionable_insights[:3]:
            response += f"- **{insight['insight']}**: {insight['action']} ({insight['timeframe']})\n"
        return response

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Error response"""
        return {
            "answer": f"Error in connecting-dots analysis: {error}. Please provide more context about the news or trends you want analyzed.",
            "error": error,
            "confidence": 0.0,
            "agent": self.name
        }


__all__ = ["ConnectingDotsAgent"]
