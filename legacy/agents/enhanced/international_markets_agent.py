"""
International Markets Agent
Provides cross-border analysis, currency insights, and global market entry strategies
"""
import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from services.llm_service import LLMService
from services.rag_service import RAGService

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from base_agent import BaseAgent


class InternationalMarketsAgent(BaseAgent):
    """
    International Markets Agent - Cross-border business intelligence

    Capabilities:
    - Currency exchange rate analysis and forecasting
    - International trade regulations and compliance
    - Cross-border tax implications
    - Global market entry strategies
    - Country-specific business environment assessment
    - Geopolitical risk analysis
    - International expansion roadmap
    - Export/import regulation guidance
    """

    def __init__(self):
        super().__init__(
            name="International Markets Agent",
            description="Analyzes international markets and cross-border opportunities"
        )
        self.llm_service = LLMService()
        self.rag_service = RAGService()

        # Major markets database
        self.markets = {
            "US": {
                "region": "North America",
                "gdp_trillions": 25.5,
                "ease_of_business": 4,
                "currency": "USD",
                "trade_barriers": "Low",
                "tax_rate": "21% corporate",
                "entry_difficulty": "Medium",
                "market_size": "Huge",
                "consumer_spending": "High",
                "key_sectors": ["Technology", "Finance", "Healthcare", "E-commerce"]
            },
            "EU": {
                "region": "Europe",
                "gdp_trillions": 17.2,
                "ease_of_business": 4,
                "currency": "EUR",
                "trade_barriers": "Low within EU",
                "tax_rate": "19-35% corporate",
                "entry_difficulty": "Medium",
                "market_size": "Large",
                "consumer_spending": "High",
                "key_sectors": ["Manufacturing", "Automotive", "Finance", "Luxury goods"]
            },
            "China": {
                "region": "Asia",
                "gdp_trillions": 17.9,
                "ease_of_business": 3,
                "currency": "CNY",
                "trade_barriers": "Medium-High",
                "tax_rate": "25% corporate",
                "entry_difficulty": "High",
                "market_size": "Huge",
                "consumer_spending": "Growing rapidly",
                "key_sectors": ["Manufacturing", "E-commerce", "Technology", "Automotive"]
            },
            "India": {
                "region": "Asia",
                "gdp_trillions": 3.7,
                "ease_of_business": 3,
                "currency": "INR",
                "trade_barriers": "Medium",
                "tax_rate": "25.17% corporate",
                "entry_difficulty": "Medium",
                "market_size": "Large and growing",
                "consumer_spending": "Rapidly growing",
                "key_sectors": ["Technology", "E-commerce", "Manufacturing", "Services"]
            },
            "UK": {
                "region": "Europe",
                "gdp_trillions": 3.1,
                "ease_of_business": 4,
                "currency": "GBP",
                "trade_barriers": "Low",
                "tax_rate": "19% corporate",
                "entry_difficulty": "Low-Medium",
                "market_size": "Medium",
                "consumer_spending": "High",
                "key_sectors": ["Finance", "Technology", "Creative industries", "Professional services"]
            },
            "Japan": {
                "region": "Asia",
                "gdp_trillions": 4.2,
                "ease_of_business": 3,
                "currency": "JPY",
                "trade_barriers": "Medium",
                "tax_rate": "23.2% corporate",
                "entry_difficulty": "High",
                "market_size": "Large",
                "consumer_spending": "High",
                "key_sectors": ["Technology", "Automotive", "Electronics", "Manufacturing"]
            },
            "Brazil": {
                "region": "South America",
                "gdp_trillions": 1.9,
                "ease_of_business": 2,
                "currency": "BRL",
                "trade_barriers": "High",
                "tax_rate": "34% corporate",
                "entry_difficulty": "High",
                "market_size": "Large",
                "consumer_spending": "Growing",
                "key_sectors": ["Agriculture", "Mining", "Manufacturing", "E-commerce"]
            },
            "UAE": {
                "region": "Middle East",
                "gdp_trillions": 0.5,
                "ease_of_business": 5,
                "currency": "AED",
                "trade_barriers": "Very Low",
                "tax_rate": "0-9% corporate",
                "entry_difficulty": "Low",
                "market_size": "Medium",
                "consumer_spending": "Very High",
                "key_sectors": ["Trade", "Tourism", "Real estate", "Finance"]
            },
            "Singapore": {
                "region": "Asia",
                "gdp_trillions": 0.4,
                "ease_of_business": 5,
                "currency": "SGD",
                "trade_barriers": "Very Low",
                "tax_rate": "17% corporate",
                "entry_difficulty": "Low",
                "market_size": "Small",
                "consumer_spending": "Very High",
                "key_sectors": ["Finance", "Trade", "Technology", "Logistics"]
            },
            "Germany": {
                "region": "Europe",
                "gdp_trillions": 4.3,
                "ease_of_business": 4,
                "currency": "EUR",
                "trade_barriers": "Low",
                "tax_rate": "30% corporate",
                "entry_difficulty": "Medium",
                "market_size": "Large",
                "consumer_spending": "High",
                "key_sectors": ["Manufacturing", "Automotive", "Engineering", "Technology"]
            }
        }

        # Currency pairs and trends
        self.currency_insights = {
            "USD": {"strength": "Strong", "trend": "Stable", "volatility": "Low"},
            "EUR": {"strength": "Moderate", "trend": "Stable", "volatility": "Low"},
            "GBP": {"strength": "Moderate", "trend": "Recovering", "volatility": "Medium"},
            "CNY": {"strength": "Moderate", "trend": "Controlled appreciation", "volatility": "Low"},
            "INR": {"strength": "Weak", "trend": "Depreciating gradually", "volatility": "Medium"},
            "JPY": {"strength": "Weak", "trend": "Depreciating", "volatility": "Medium"},
            "BRL": {"strength": "Weak", "trend": "Volatile", "volatility": "High"},
            "AED": {"strength": "Strong", "trend": "Pegged to USD", "volatility": "Very Low"},
            "SGD": {"strength": "Strong", "trend": "Stable appreciation", "volatility": "Low"}
        }

        # Trade agreements and blocs
        self.trade_blocs = {
            "NAFTA/USMCA": ["US", "Canada", "Mexico"],
            "EU": ["Germany", "France", "Italy", "Spain", "Netherlands", "Poland", "etc."],
            "ASEAN": ["Singapore", "Indonesia", "Thailand", "Malaysia", "Vietnam", "Philippines"],
            "RCEP": ["China", "Japan", "South Korea", "ASEAN members", "Australia", "New Zealand"],
            "MERCOSUR": ["Brazil", "Argentina", "Uruguay", "Paraguay"]
        }

    async def process(
        self,
        query: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process international markets query"""

        try:
            # Extract key parameters
            target_markets = self._extract_target_markets(query)
            analysis_type = self._classify_query(query)

            # Perform analysis based on query type
            if "expand" in query.lower() or "entry" in query.lower():
                result = await self._market_entry_analysis(target_markets, user_context)
            elif "currency" in query.lower() or "forex" in query.lower() or "exchange" in query.lower():
                result = await self._currency_analysis(target_markets)
            elif "regulation" in query.lower() or "compliance" in query.lower():
                result = await self._regulatory_analysis(target_markets)
            elif "risk" in query.lower() or "geopolitical" in query.lower():
                result = await self._geopolitical_risk_analysis(target_markets)
            elif "tax" in query.lower() or "cross-border tax" in query.lower():
                result = await self._cross_border_tax_analysis(target_markets)
            elif "compare" in query.lower():
                result = await self._market_comparison(target_markets)
            else:
                result = await self._comprehensive_market_analysis(target_markets, user_context)

            return {
                "agent": self.name,
                "query": query,
                "analysis_type": analysis_type,
                "target_markets": target_markets,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "agent": self.name,
                "error": str(e),
                "fallback_response": "Unable to complete international markets analysis. Please try again or consult an international trade specialist."
            }

    def _extract_target_markets(self, query: str) -> List[str]:
        """Extract target markets from query"""
        markets_found = []
        query_lower = query.lower()

        for market in self.markets.keys():
            if market.lower() in query_lower:
                markets_found.append(market)

        # If no specific markets mentioned, return top markets
        if not markets_found:
            return ["US", "EU", "China", "India", "UK"]

        return markets_found

    def _classify_query(self, query: str) -> str:
        """Classify the type of international markets query"""
        query_lower = query.lower()

        if "expand" in query_lower or "entry" in query_lower:
            return "market_entry"
        elif "currency" in query_lower or "forex" in query_lower:
            return "currency_analysis"
        elif "regulation" in query_lower or "compliance" in query_lower:
            return "regulatory"
        elif "risk" in query_lower or "geopolitical" in query_lower:
            return "risk_analysis"
        elif "tax" in query_lower:
            return "cross_border_tax"
        elif "compare" in query_lower:
            return "comparison"
        else:
            return "comprehensive"

    async def _market_entry_analysis(
        self,
        target_markets: List[str],
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze market entry strategies"""

        analysis = {
            "recommended_markets": [],
            "entry_strategies": {},
            "timeline": {},
            "estimated_costs": {},
            "key_considerations": {}
        }

        for market in target_markets:
            if market not in self.markets:
                continue

            market_data = self.markets[market]

            # Score market attractiveness
            score = self._calculate_market_attractiveness(market_data)

            analysis["recommended_markets"].append({
                "market": market,
                "score": score,
                "rationale": f"Market size: {market_data['market_size']}, Entry difficulty: {market_data['entry_difficulty']}"
            })

            # Entry strategy
            analysis["entry_strategies"][market] = self._recommend_entry_strategy(market, market_data)

            # Timeline
            analysis["timeline"][market] = self._estimate_entry_timeline(market_data)

            # Costs
            analysis["estimated_costs"][market] = self._estimate_entry_costs(market_data)

            # Key considerations
            analysis["key_considerations"][market] = self._identify_key_considerations(market, market_data)

        # Sort by score
        analysis["recommended_markets"].sort(key=lambda x: x["score"], reverse=True)

        # LLM-enhanced recommendations
        llm_analysis = await self._get_llm_market_entry_insights(target_markets, analysis)
        analysis["llm_insights"] = llm_analysis

        return analysis

    def _calculate_market_attractiveness(self, market_data: Dict) -> float:
        """Calculate market attractiveness score (0-10)"""
        score = 0.0

        # Market size score
        if market_data["market_size"] == "Huge":
            score += 3.0
        elif market_data["market_size"] == "Large":
            score += 2.5
        elif market_data["market_size"] == "Medium":
            score += 1.5
        else:
            score += 0.5

        # Ease of business
        score += market_data["ease_of_business"] * 1.0

        # Entry difficulty (inverse scoring)
        if market_data["entry_difficulty"] == "Low":
            score += 2.0
        elif market_data["entry_difficulty"] == "Low-Medium":
            score += 1.5
        elif market_data["entry_difficulty"] == "Medium":
            score += 1.0
        else:
            score += 0.5

        # Consumer spending
        if "High" in market_data["consumer_spending"] or "Very High" in market_data["consumer_spending"]:
            score += 1.5
        elif "Growing" in market_data["consumer_spending"]:
            score += 1.0

        return min(score, 10.0)

    def _recommend_entry_strategy(self, market: str, market_data: Dict) -> Dict[str, Any]:
        """Recommend market entry strategy"""

        if market_data["entry_difficulty"] == "Low" or market in ["Singapore", "UAE"]:
            return {
                "primary_strategy": "Direct Entry (Subsidiary)",
                "alternative": "Local office with expat management",
                "rationale": "Low barriers to entry, straightforward registration process",
                "steps": [
                    "Register local entity",
                    "Open corporate bank account",
                    "Hire local team",
                    "Obtain business licenses",
                    "Launch operations"
                ]
            }
        elif market_data["entry_difficulty"] == "Medium":
            return {
                "primary_strategy": "Joint Venture or Strategic Partnership",
                "alternative": "Acquisition of local player",
                "rationale": "Benefits from local partner's market knowledge and relationships",
                "steps": [
                    "Identify potential partners",
                    "Due diligence on partners",
                    "Negotiate partnership terms",
                    "Establish joint entity",
                    "Phased market rollout"
                ]
            }
        else:  # High difficulty
            return {
                "primary_strategy": "Phased Entry via Distribution Partnership",
                "alternative": "Licensing model initially",
                "rationale": "Minimize upfront risk in complex regulatory environment",
                "steps": [
                    "Appoint exclusive distributor",
                    "Test market with limited product line",
                    "Build brand presence",
                    "Gather market intelligence",
                    "Transition to direct presence after 12-24 months"
                ]
            }

    def _estimate_entry_timeline(self, market_data: Dict) -> Dict[str, str]:
        """Estimate timeline for market entry"""

        if market_data["entry_difficulty"] == "Low":
            return {
                "planning_phase": "1-2 months",
                "setup_phase": "2-3 months",
                "launch_phase": "1-2 months",
                "total": "4-7 months"
            }
        elif market_data["entry_difficulty"] in ["Medium", "Low-Medium"]:
            return {
                "planning_phase": "2-3 months",
                "setup_phase": "4-6 months",
                "launch_phase": "2-3 months",
                "total": "8-12 months"
            }
        else:
            return {
                "planning_phase": "3-6 months",
                "setup_phase": "6-12 months",
                "launch_phase": "3-6 months",
                "total": "12-24 months"
            }

    def _estimate_entry_costs(self, market_data: Dict) -> Dict[str, str]:
        """Estimate costs for market entry"""

        base_costs = {
            "legal_and_registration": "$10,000 - $50,000",
            "office_setup": "$20,000 - $100,000",
            "initial_team": "$100,000 - $500,000",
            "marketing_launch": "$50,000 - $200,000",
            "working_capital": "$100,000 - $500,000",
            "total_first_year": "$280,000 - $1,350,000"
        }

        # Adjust for market difficulty
        if market_data["entry_difficulty"] == "High":
            return {
                "legal_and_registration": "$50,000 - $200,000",
                "office_setup": "$50,000 - $200,000",
                "initial_team": "$200,000 - $1,000,000",
                "marketing_launch": "$100,000 - $500,000",
                "working_capital": "$200,000 - $1,000,000",
                "consultants_advisors": "$50,000 - $200,000",
                "total_first_year": "$650,000 - $3,100,000"
            }

        return base_costs

    def _identify_key_considerations(self, market: str, market_data: Dict) -> List[str]:
        """Identify key considerations for market entry"""

        considerations = [
            f"Corporate tax rate: {market_data['tax_rate']}",
            f"Currency: {market_data['currency']} - {self.currency_insights.get(market_data['currency'], {}).get('trend', 'Unknown trend')}",
            f"Trade barriers: {market_data['trade_barriers']}",
            f"Key sectors: {', '.join(market_data['key_sectors'][:3])}"
        ]

        # Market-specific considerations
        if market == "China":
            considerations.extend([
                "Mandatory joint venture for certain sectors",
                "Data localization requirements",
                "Internet restrictions (Great Firewall)",
                "Strong local competition"
            ])
        elif market == "India":
            considerations.extend([
                "Complex regulatory environment",
                "FDI restrictions in certain sectors",
                "State-level variations in regulations",
                "Strong price sensitivity"
            ])
        elif market == "Brazil":
            considerations.extend([
                "High tax complexity (multiple layers)",
                "Protectionist trade policies",
                "Bureaucratic challenges",
                "Currency volatility"
            ])
        elif market in ["US"]:
            considerations.extend([
                "Strong IP protection",
                "Sophisticated competition",
                "State-by-state variations",
                "High customer expectations"
            ])
        elif market == "EU":
            considerations.extend([
                "GDPR compliance required",
                "27 member states with variations",
                "Strong consumer protection laws",
                "Language and cultural diversity"
            ])

        return considerations

    async def _currency_analysis(self, target_markets: List[str]) -> Dict[str, Any]:
        """Analyze currency implications"""

        analysis = {
            "currencies": {},
            "hedging_strategies": [],
            "risk_assessment": {},
            "recommendations": []
        }

        for market in target_markets:
            if market not in self.markets:
                continue

            currency = self.markets[market]["currency"]
            currency_info = self.currency_insights.get(currency, {})

            analysis["currencies"][market] = {
                "currency": currency,
                "strength": currency_info.get("strength", "Unknown"),
                "trend": currency_info.get("trend", "Unknown"),
                "volatility": currency_info.get("volatility", "Unknown"),
                "implications": self._get_currency_implications(currency_info)
            }

        # Hedging strategies
        analysis["hedging_strategies"] = [
            {
                "strategy": "Forward Contracts",
                "description": "Lock in exchange rates for future transactions",
                "best_for": "Predictable cash flows, 3-12 month horizon",
                "cost": "Low (no upfront premium)"
            },
            {
                "strategy": "Currency Options",
                "description": "Right but not obligation to exchange at set rate",
                "best_for": "Uncertain cash flows, want flexibility",
                "cost": "Medium (premium required)"
            },
            {
                "strategy": "Natural Hedging",
                "description": "Match revenues and expenses in same currency",
                "best_for": "Operations in multiple countries",
                "cost": "None (operational strategy)"
            },
            {
                "strategy": "Currency ETFs",
                "description": "Invest in currency-focused ETFs for hedge",
                "best_for": "Long-term currency exposure management",
                "cost": "Medium (management fees)"
            }
        ]

        # LLM-enhanced analysis
        llm_insights = await self._get_llm_currency_insights(target_markets, analysis)
        analysis["llm_insights"] = llm_insights

        return analysis

    def _get_currency_implications(self, currency_info: Dict) -> List[str]:
        """Get business implications of currency characteristics"""
        implications = []

        volatility = currency_info.get("volatility", "Unknown")
        trend = currency_info.get("trend", "Unknown")

        if volatility == "High":
            implications.append("⚠️ High FX risk - implement hedging strategy")
            implications.append("Consider pricing in USD or EUR")
            implications.append("Monitor exchange rates daily")
        elif volatility == "Medium":
            implications.append("Moderate FX risk - consider selective hedging")
            implications.append("Quarterly exchange rate reviews recommended")
        else:
            implications.append("✓ Low FX risk - minimal hedging needed")

        if "Depreciat" in trend:
            implications.append("Currency weakening - good for exports, challenging for imports")
            implications.append("Local costs becoming more competitive")
        elif "appreciat" in trend.lower():
            implications.append("Currency strengthening - challenging for exports")
            implications.append("Good time to repatriate profits")

        return implications

    async def _regulatory_analysis(self, target_markets: List[str]) -> Dict[str, Any]:
        """Analyze regulatory requirements"""

        analysis = {
            "compliance_requirements": {},
            "regulatory_complexity": {},
            "timeline_for_compliance": {},
            "estimated_costs": {}
        }

        for market in target_markets:
            if market not in self.markets:
                continue

            analysis["compliance_requirements"][market] = self._get_compliance_requirements(market)
            analysis["regulatory_complexity"][market] = self._assess_regulatory_complexity(market)
            analysis["timeline_for_compliance"][market] = self._estimate_compliance_timeline(market)
            analysis["estimated_costs"][market] = self._estimate_compliance_costs(market)

        # LLM-enhanced analysis
        llm_insights = await self._get_llm_regulatory_insights(target_markets)
        analysis["llm_insights"] = llm_insights

        return analysis

    def _get_compliance_requirements(self, market: str) -> List[str]:
        """Get compliance requirements for market"""

        base_requirements = [
            "Business registration and licensing",
            "Tax registration",
            "Employment regulations compliance",
            "Intellectual property protection",
            "Contract law compliance"
        ]

        market_specific = {
            "EU": [
                "GDPR compliance (data protection)",
                "VAT registration",
                "CE marking for products",
                "Consumer protection directives"
            ],
            "US": [
                "Federal and state tax registration",
                "SEC filings (if raising capital)",
                "Industry-specific regulations (FDA, FCC, etc.)",
                "State-level business licenses"
            ],
            "China": [
                "ICP license for online business",
                "Data localization compliance",
                "WFOE/JV registration",
                "Cybersecurity law compliance"
            ],
            "India": [
                "GST registration",
                "FEMA compliance",
                "RBI regulations (if financial services)",
                "Data localization (certain sectors)"
            ]
        }

        return base_requirements + market_specific.get(market, [])

    def _assess_regulatory_complexity(self, market: str) -> Dict[str, Any]:
        """Assess regulatory complexity"""

        complexity_mapping = {
            "Brazil": {"score": 9, "description": "Very Complex", "challenges": ["Multiple tax layers", "Bureaucratic", "Frequent changes"]},
            "China": {"score": 8, "description": "Very Complex", "challenges": ["Language barrier", "Opaque processes", "Political considerations"]},
            "India": {"score": 7, "description": "Complex", "challenges": ["Federal + state regulations", "Bureaucracy", "Frequent policy changes"]},
            "US": {"score": 6, "description": "Moderately Complex", "challenges": ["Federal + state variations", "Industry-specific regs", "Litigation risk"]},
            "EU": {"score": 6, "description": "Moderately Complex", "challenges": ["27 member states", "GDPR compliance", "Multiple languages"]},
            "Japan": {"score": 7, "description": "Complex", "challenges": ["Language barrier", "Cultural nuances", "Detailed documentation"]},
            "UK": {"score": 4, "description": "Moderate", "challenges": ["Post-Brexit changes", "Professional services rules"]},
            "Singapore": {"score": 2, "description": "Simple", "challenges": ["Few barriers", "Clear processes", "English language"]},
            "UAE": {"score": 3, "description": "Simple", "challenges": ["Free zone vs mainland choice", "Sponsorship requirements"]}
        }

        return complexity_mapping.get(market, {"score": 5, "description": "Moderate", "challenges": ["Standard compliance requirements"]})

    def _estimate_compliance_timeline(self, market: str) -> str:
        """Estimate timeline for compliance"""
        complexity = self._assess_regulatory_complexity(market)

        if complexity["score"] >= 8:
            return "9-18 months"
        elif complexity["score"] >= 6:
            return "6-12 months"
        elif complexity["score"] >= 4:
            return "3-6 months"
        else:
            return "1-3 months"

    def _estimate_compliance_costs(self, market: str) -> str:
        """Estimate compliance costs"""
        complexity = self._assess_regulatory_complexity(market)

        if complexity["score"] >= 8:
            return "$100,000 - $500,000+"
        elif complexity["score"] >= 6:
            return "$50,000 - $200,000"
        elif complexity["score"] >= 4:
            return "$20,000 - $75,000"
        else:
            return "$5,000 - $25,000"

    async def _geopolitical_risk_analysis(self, target_markets: List[str]) -> Dict[str, Any]:
        """Analyze geopolitical risks"""

        analysis = {
            "risk_scores": {},
            "key_risks": {},
            "mitigation_strategies": [],
            "monitoring_recommendations": []
        }

        for market in target_markets:
            analysis["risk_scores"][market] = self._calculate_geopolitical_risk_score(market)
            analysis["key_risks"][market] = self._identify_geopolitical_risks(market)

        # General mitigation strategies
        analysis["mitigation_strategies"] = [
            {
                "strategy": "Geographic Diversification",
                "description": "Spread operations across multiple markets",
                "effectiveness": "High"
            },
            {
                "strategy": "Political Risk Insurance",
                "description": "Insurance against expropriation, political violence, currency inconvertibility",
                "effectiveness": "Medium-High"
            },
            {
                "strategy": "Local Partnerships",
                "description": "Partner with well-connected local entities",
                "effectiveness": "High"
            },
            {
                "strategy": "Flexible Supply Chains",
                "description": "Multi-source critical inputs and maintain backup suppliers",
                "effectiveness": "Medium"
            },
            {
                "strategy": "Scenario Planning",
                "description": "Develop contingency plans for various political scenarios",
                "effectiveness": "Medium"
            }
        ]

        analysis["monitoring_recommendations"] = [
            "Subscribe to political risk monitoring services (e.g., Control Risks, Eurasia Group)",
            "Establish relationships with local embassy/consulate",
            "Monitor local news and social media sentiment",
            "Engage local government relations consultant",
            "Regular scenario planning workshops (quarterly)"
        ]

        # LLM-enhanced analysis
        llm_insights = await self._get_llm_geopolitical_insights(target_markets)
        analysis["llm_insights"] = llm_insights

        return analysis

    def _calculate_geopolitical_risk_score(self, market: str) -> Dict[str, Any]:
        """Calculate geopolitical risk score (0-10, higher = more risk)"""

        risk_scores = {
            "Singapore": {"score": 2.0, "level": "Very Low", "rationale": "Political stability, rule of law, business-friendly"},
            "UAE": {"score": 3.0, "level": "Low", "rationale": "Stable monarchy, pro-business, regional hub"},
            "US": {"score": 3.5, "level": "Low", "rationale": "Democratic stability, but partisan polarization"},
            "Germany": {"score": 2.5, "level": "Very Low", "rationale": "EU member, political stability"},
            "UK": {"score": 3.0, "level": "Low", "rationale": "Post-Brexit adjustments, political stability"},
            "Japan": {"score": 2.5, "level": "Very Low", "rationale": "Political stability, but aging demographics"},
            "China": {"score": 6.5, "level": "Medium-High", "rationale": "Authoritarian governance, US-China tensions, Taiwan risk"},
            "India": {"score": 4.5, "level": "Medium", "rationale": "Democratic but complex politics, regional tensions"},
            "Brazil": {"score": 5.5, "level": "Medium", "rationale": "Political volatility, corruption concerns"},
            "EU": {"score": 3.5, "level": "Low", "rationale": "Generally stable, but Ukraine conflict impact"}
        }

        return risk_scores.get(market, {"score": 5.0, "level": "Medium", "rationale": "Moderate political risk"})

    def _identify_geopolitical_risks(self, market: str) -> List[str]:
        """Identify specific geopolitical risks"""

        risks = {
            "China": [
                "US-China trade tensions and decoupling",
                "Taiwan conflict risk",
                "Technology transfer requirements",
                "Data security and surveillance concerns",
                "Regulatory unpredictability"
            ],
            "India": [
                "India-Pakistan tensions",
                "Bureaucratic challenges",
                "Infrastructure bottlenecks",
                "Regional political variations",
                "Trade policy changes"
            ],
            "Brazil": [
                "Political instability and policy reversals",
                "Corruption risks",
                "Currency volatility",
                "Crime and security concerns",
                "Environmental regulations uncertainty"
            ],
            "US": [
                "Trade policy uncertainty",
                "Regulatory changes with administration shifts",
                "Tech sector antitrust scrutiny",
                "Immigration policy volatility"
            ],
            "EU": [
                "Ukraine-Russia conflict spillover",
                "Energy security concerns",
                "Brexit impact on UK-EU trade",
                "Migration policy debates"
            ],
            "UK": [
                "Post-Brexit trade relationship uncertainties",
                "Scotland independence debate",
                "Regulatory divergence from EU"
            ]
        }

        return risks.get(market, ["Moderate political risk", "Regulatory uncertainty", "Economic volatility"])

    async def _cross_border_tax_analysis(self, target_markets: List[str]) -> Dict[str, Any]:
        """Analyze cross-border tax implications"""

        analysis = {
            "tax_rates": {},
            "double_taxation_treaties": {},
            "tax_optimization_strategies": [],
            "transfer_pricing_considerations": [],
            "withholding_tax_rates": {}
        }

        for market in target_markets:
            if market not in self.markets:
                continue

            market_data = self.markets[market]
            analysis["tax_rates"][market] = {
                "corporate_tax": market_data["tax_rate"],
                "vat_gst": self._get_vat_rate(market),
                "dividend_withholding": self._get_withholding_rate(market, "dividend"),
                "royalty_withholding": self._get_withholding_rate(market, "royalty")
            }

            analysis["double_taxation_treaties"][market] = self._check_tax_treaties(market)

        analysis["tax_optimization_strategies"] = [
            {
                "strategy": "Intellectual Property Holding Company",
                "description": "Hold IP in low-tax jurisdiction, license to operating entities",
                "suitable_jurisdictions": ["Singapore", "UAE", "Ireland", "Netherlands"],
                "tax_savings_potential": "High",
                "complexity": "High",
                "compliance_requirements": ["Transfer pricing documentation", "Substance requirements", "Tax residency certification"]
            },
            {
                "strategy": "Regional Headquarters Structure",
                "description": "Centralize regional management and shared services",
                "suitable_jurisdictions": ["Singapore", "UAE", "Hong Kong"],
                "tax_savings_potential": "Medium",
                "complexity": "Medium",
                "compliance_requirements": ["Economic substance", "Management and control evidence"]
            },
            {
                "strategy": "Tax Treaty Optimization",
                "description": "Structure investments through treaty jurisdictions",
                "suitable_jurisdictions": ["Netherlands", "Luxembourg", "Mauritius (for India)"],
                "tax_savings_potential": "Medium-High",
                "complexity": "Medium",
                "compliance_requirements": ["Treaty eligibility documentation", "Beneficial ownership proof"]
            },
            {
                "strategy": "Advance Pricing Agreements (APAs)",
                "description": "Pre-agree transfer pricing methodology with tax authorities",
                "suitable_jurisdictions": ["US", "India", "China", "Japan"],
                "tax_savings_potential": "Low (but reduces risk)",
                "complexity": "Very High",
                "compliance_requirements": ["Detailed economic analysis", "Multi-year commitment"]
            }
        ]

        analysis["transfer_pricing_considerations"] = [
            "Document intercompany transactions with arm's length pricing",
            "Maintain comparables database",
            "Prepare master file and local file documentation",
            "Consider Country-by-Country Reporting (CbCR) if revenue > $850M",
            "Conduct annual transfer pricing review"
        ]

        # LLM-enhanced insights
        llm_insights = await self._get_llm_tax_insights(target_markets)
        analysis["llm_insights"] = llm_insights

        return analysis

    def _get_vat_rate(self, market: str) -> str:
        """Get VAT/GST rate for market"""
        vat_rates = {
            "EU": "17-27% (varies by member state)",
            "UK": "20%",
            "India": "5-28% GST (based on goods/services)",
            "China": "13% (general goods), 6% (services)",
            "Brazil": "17-25% (varies by state)",
            "Singapore": "8% GST",
            "UAE": "5% VAT",
            "Japan": "10%",
            "US": "0-10% (state sales tax, no federal VAT)"
        }
        return vat_rates.get(market, "Varies")

    def _get_withholding_rate(self, market: str, type: str) -> str:
        """Get withholding tax rates"""
        # Simplified rates - actual rates depend on treaties
        if type == "dividend":
            rates = {
                "US": "30% (treaty rates lower)", "EU": "15-35%", "China": "10%",
                "India": "20%", "Singapore": "0% (exempt)", "UAE": "0%"
            }
        else:  # royalty
            rates = {
                "US": "30% (treaty rates lower)", "EU": "0-20%", "China": "10%",
                "India": "10%", "Singapore": "10%", "UAE": "0%"
            }
        return rates.get(market, "Varies")

    def _check_tax_treaties(self, market: str) -> Dict[str, Any]:
        """Check tax treaty availability"""
        return {
            "has_treaty_network": True if market in ["US", "UK", "Germany", "Singapore", "India"] else False,
            "treaties_count": "80+" if market in ["US", "UK", "Germany"] else "50+",
            "key_treaty_benefits": [
                "Reduced withholding tax rates",
                "Relief from double taxation",
                "Mutual agreement procedure (MAP) for disputes",
                "Exchange of information"
            ]
        }

    async def _market_comparison(self, target_markets: List[str]) -> Dict[str, Any]:
        """Compare multiple markets"""

        comparison = {
            "markets": [],
            "comparison_matrix": {},
            "best_for_categories": {},
            "decision_framework": []
        }

        categories = [
            "market_size", "ease_of_business", "entry_difficulty",
            "tax_rate", "consumer_spending", "gdp"
        ]

        for category in categories:
            comparison["comparison_matrix"][category] = {}
            for market in target_markets:
                if market in self.markets:
                    comparison["comparison_matrix"][category][market] = self.markets[market].get(category, "N/A")

        # Best for categories
        comparison["best_for_categories"] = {
            "Easiest Entry": ["Singapore", "UAE", "UK"],
            "Largest Market": ["US", "China", "EU"],
            "Fastest Growing": ["India", "Vietnam", "Indonesia"],
            "Lowest Tax": ["UAE", "Singapore", "Ireland"],
            "Best for Tech": ["US", "Singapore", "UK", "India"],
            "Best for Manufacturing": ["China", "Vietnam", "India"],
            "Best for Finance": ["Singapore", "UK", "US"]
        }

        # Decision framework
        comparison["decision_framework"] = [
            {
                "question": "What's your primary goal?",
                "options": {
                    "Fast market penetration": "Consider Singapore, UAE (easy entry)",
                    "Access large market": "Consider US, China, EU",
                    "Cost optimization": "Consider India, Vietnam",
                    "Global brand building": "Consider US, UK, EU"
                }
            },
            {
                "question": "What's your risk tolerance?",
                "options": {
                    "Low risk": "Singapore, UAE, UK",
                    "Moderate risk": "US, EU, India",
                    "Higher risk acceptable": "China, Brazil, emerging markets"
                }
            },
            {
                "question": "What resources do you have?",
                "options": {
                    "Limited budget (<$500K)": "Start with Singapore, UAE, or digital-first approach",
                    "Medium budget ($500K-$2M)": "US, UK, or India",
                    "Large budget (>$2M)": "Multiple markets or China/EU"
                }
            }
        ]

        # LLM-enhanced comparison
        llm_comparison = await self._get_llm_market_comparison(target_markets, comparison)
        comparison["llm_insights"] = llm_comparison

        return comparison

    async def _comprehensive_market_analysis(
        self,
        target_markets: List[str],
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Comprehensive market analysis combining multiple dimensions"""

        analysis = {
            "executive_summary": {},
            "market_profiles": {},
            "strategic_recommendations": [],
            "next_steps": []
        }

        # Create market profiles
        for market in target_markets:
            if market not in self.markets:
                continue

            market_data = self.markets[market]

            analysis["market_profiles"][market] = {
                "overview": market_data,
                "attractiveness_score": self._calculate_market_attractiveness(market_data),
                "entry_strategy": self._recommend_entry_strategy(market, market_data),
                "key_risks": self._identify_geopolitical_risks(market),
                "compliance_complexity": self._assess_regulatory_complexity(market),
                "currency_implications": self.currency_insights.get(market_data["currency"], {})
            }

        # Strategic recommendations
        analysis["strategic_recommendations"] = await self._generate_strategic_recommendations(
            target_markets, analysis["market_profiles"], user_context
        )

        # Next steps
        analysis["next_steps"] = [
            "Conduct detailed market research in top 2-3 markets",
            "Engage local advisors (legal, tax, market entry)",
            "Develop detailed financial models for each market",
            "Visit target markets and meet potential partners",
            "Create phased expansion roadmap",
            "Secure necessary funding for international expansion",
            "Build international team and capabilities"
        ]

        # LLM-enhanced comprehensive analysis
        llm_insights = await self._get_llm_comprehensive_insights(target_markets, analysis)
        analysis["llm_insights"] = llm_insights

        return analysis

    async def _generate_strategic_recommendations(
        self,
        markets: List[str],
        profiles: Dict,
        user_context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate strategic recommendations"""

        recommendations = []

        # Sort markets by attractiveness
        sorted_markets = sorted(
            [m for m in markets if m in profiles],
            key=lambda m: profiles[m]["attractiveness_score"],
            reverse=True
        )

        if len(sorted_markets) >= 1:
            top_market = sorted_markets[0]
            recommendations.append({
                "priority": "High",
                "market": top_market,
                "recommendation": f"Prioritize {top_market} for initial international expansion",
                "rationale": f"Highest attractiveness score ({profiles[top_market]['attractiveness_score']:.1f}/10)",
                "timeline": "Start immediately - target entry within 6-12 months"
            })

        if len(sorted_markets) >= 3:
            recommendations.append({
                "priority": "Medium",
                "market": "Multiple",
                "recommendation": "Consider phased multi-market approach",
                "rationale": "Diversify risk and maximize opportunities",
                "timeline": "Stagger entries: Market 1 (Year 1), Market 2 (Year 2), Market 3 (Year 3)"
            })

        return recommendations

    # LLM-enhanced analysis methods

    async def _get_llm_market_entry_insights(
        self,
        markets: List[str],
        analysis: Dict[str, Any]
    ) -> str:
        """Get LLM insights on market entry strategy"""

        prompt = f"""
        As an international expansion advisor, provide strategic insights for market entry:

        Target Markets: {', '.join(markets)}
        Analysis: {json.dumps(analysis, indent=2)}

        Provide:
        1. Top 3 critical success factors for entering these markets
        2. Common pitfalls to avoid
        3. One counterintuitive insight that many companies miss
        4. Recommended sequencing if entering multiple markets

        Be specific and actionable.
        """

        try:
            response = await self.llm_service.generate_completion(
                prompt=prompt,
                max_tokens=800,
                temperature=0.7
            )
            return response
        except Exception as e:
            return "LLM analysis unavailable. Proceed with data-driven analysis above."

    async def _get_llm_currency_insights(
        self,
        markets: List[str],
        analysis: Dict[str, Any]
    ) -> str:
        """Get LLM insights on currency strategy"""

        prompt = f"""
        As a currency risk management expert, analyze the FX implications:

        Target Markets: {', '.join(markets)}
        Currency Analysis: {json.dumps(analysis['currencies'], indent=2)}

        Provide:
        1. Biggest currency risk in this expansion
        2. Most cost-effective hedging approach
        3. Opportunities from currency movements

        Be concise and practical.
        """

        try:
            response = await self.llm_service.generate_completion(
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )
            return response
        except Exception as e:
            return "LLM analysis unavailable."

    async def _get_llm_regulatory_insights(self, markets: List[str]) -> str:
        """Get LLM insights on regulatory landscape"""

        prompt = f"""
        As a regulatory compliance expert, highlight the key compliance considerations:

        Target Markets: {', '.join(markets)}

        For each market, identify:
        1. The most commonly overlooked regulatory requirement
        2. The costliest compliance mistake companies make
        3. One pro tip for navigating the bureaucracy

        Be specific and practical.
        """

        try:
            response = await self.llm_service.generate_completion(
                prompt=prompt,
                max_tokens=700,
                temperature=0.7
            )
            return response
        except Exception as e:
            return "LLM analysis unavailable."

    async def _get_llm_geopolitical_insights(self, markets: List[str]) -> str:
        """Get LLM insights on geopolitical risks"""

        prompt = f"""
        As a geopolitical risk analyst, assess the political landscape:

        Target Markets: {', '.join(markets)}

        Provide:
        1. The most significant near-term political risk (next 12 months)
        2. Long-term geopolitical trends that could impact business (3-5 years)
        3. Early warning signals to monitor

        Be forward-looking and specific.
        """

        try:
            response = await self.llm_service.generate_completion(
                prompt=prompt,
                max_tokens=600,
                temperature=0.7
            )
            return response
        except Exception as e:
            return "LLM analysis unavailable."

    async def _get_llm_tax_insights(self, markets: List[str]) -> str:
        """Get LLM insights on tax strategy"""

        prompt = f"""
        As an international tax strategist, advise on tax optimization:

        Target Markets: {', '.join(markets)}

        Provide:
        1. Most effective legal tax structure for operating in these markets
        2. Key tax treaty benefits to leverage
        3. One innovative but compliant tax planning idea

        Focus on practical, implementable strategies.
        """

        try:
            response = await self.llm_service.generate_completion(
                prompt=prompt,
                max_tokens=600,
                temperature=0.7
            )
            return response
        except Exception as e:
            return "LLM analysis unavailable."

    async def _get_llm_market_comparison(
        self,
        markets: List[str],
        comparison: Dict[str, Any]
    ) -> str:
        """Get LLM market comparison insights"""

        prompt = f"""
        As a market selection consultant, help choose the best market:

        Markets Under Consideration: {', '.join(markets)}
        Comparison Data: {json.dumps(comparison['comparison_matrix'], indent=2)}

        Provide:
        1. Your top recommendation and why
        2. Which market offers the best risk-reward trade-off
        3. One surprising factor that should influence the decision

        Be decisive and data-driven.
        """

        try:
            response = await self.llm_service.generate_completion(
                prompt=prompt,
                max_tokens=600,
                temperature=0.7
            )
            return response
        except Exception as e:
            return "LLM analysis unavailable."

    async def _get_llm_comprehensive_insights(
        self,
        markets: List[str],
        analysis: Dict[str, Any]
    ) -> str:
        """Get comprehensive LLM insights"""

        prompt = f"""
        As a seasoned international business strategist, synthesize the complete analysis:

        Target Markets: {', '.join(markets)}
        Comprehensive Analysis: {json.dumps(analysis, indent=2, default=str)}

        Provide:
        1. Your #1 strategic recommendation
        2. The biggest opportunity being overlooked
        3. The most critical risk to mitigate
        4. A bold prediction about these markets in 3 years

        Be insightful, specific, and actionable.
        """

        try:
            response = await self.llm_service.generate_completion(
                prompt=prompt,
                max_tokens=800,
                temperature=0.8
            )
            return response
        except Exception as e:
            return "LLM analysis unavailable."


if __name__ == "__main__":
    """Test the International Markets Agent"""
    import asyncio

    async def test():
        agent = InternationalMarketsAgent()

        # Test query
        query = "I want to expand my SaaS business to Asia. Which markets should I target?"

        result = await agent.process(query)

        print("=" * 80)
        print("INTERNATIONAL MARKETS AGENT TEST")
        print("=" * 80)
        print(f"Query: {query}")
        print(f"\nResult: {json.dumps(result, indent=2, default=str)}")

    asyncio.run(test())
