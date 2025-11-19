"""
Macroeconomics Agent
Provides macro-level economic analysis, central bank policy interpretation, and economic cycle insights
"""
import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from services.llm_service import LLMService
from services.rag_service import RAGService

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from base_agent import BaseAgent


class MacroeconomicsAgent(BaseAgent):
    """
    Macroeconomics Agent - Macro-level economic intelligence

    Capabilities:
    - GDP, inflation, interest rate analysis
    - Central bank policy interpretation (Fed, ECB, BoJ, RBI, PBoC)
    - Economic cycle analysis (expansion, peak, contraction, trough)
    - Sector impact assessment from macro trends
    - Currency trend analysis
    - Global economic correlation analysis
    - Leading indicators monitoring
    - Policy rate forecasting
    """

    def __init__(self):
        super().__init__(
            name="Macroeconomics Agent",
            description="Analyzes macroeconomic trends and their business impact"
        )
        self.llm_service = LLMService()
        self.rag_service = RAGService()

        # Global economic data (simplified - in production would come from APIs)
        self.economic_data = {
            "US": {
                "gdp_growth": 2.5,  # %
                "inflation": 3.2,  # %
                "interest_rate": 5.25,  # %
                "unemployment": 3.8,  # %
                "cycle_stage": "Late Expansion",
                "central_bank": "Federal Reserve",
                "policy_stance": "Restrictive (fighting inflation)",
                "next_move_likely": "Hold or cut rates",
                "key_indicators": {
                    "PMI": 49.8,  # <50 = contraction
                    "retail_sales_growth": 2.1,
                    "housing_starts": "Declining",
                    "consumer_confidence": 68.5
                }
            },
            "EU": {
                "gdp_growth": 0.6,
                "inflation": 2.9,
                "interest_rate": 4.0,
                "unemployment": 6.5,
                "cycle_stage": "Stagnation",
                "central_bank": "European Central Bank",
                "policy_stance": "Restrictive",
                "next_move_likely": "Potential cuts if inflation stabilizes",
                "key_indicators": {
                    "PMI": 46.1,
                    "retail_sales_growth": -0.3,
                    "housing_starts": "Stable",
                    "consumer_confidence": 60.2
                }
            },
            "China": {
                "gdp_growth": 5.2,
                "inflation": 0.2,  # Very low, deflation risk
                "interest_rate": 3.45,
                "unemployment": 5.2,
                "cycle_stage": "Early Expansion (post-reopening)",
                "central_bank": "People's Bank of China",
                "policy_stance": "Accommodative (supporting growth)",
                "next_move_likely": "Further stimulus measures",
                "key_indicators": {
                    "PMI": 50.2,
                    "retail_sales_growth": 5.5,
                    "housing_starts": "Declining (property crisis)",
                    "consumer_confidence": 85.6
                }
            },
            "India": {
                "gdp_growth": 7.6,
                "inflation": 5.1,
                "interest_rate": 6.5,
                "unemployment": 7.8,
                "cycle_stage": "Strong Expansion",
                "central_bank": "Reserve Bank of India",
                "policy_stance": "Neutral to accommodative",
                "next_move_likely": "Hold rates, monitor inflation",
                "key_indicators": {
                    "PMI": 56.5,
                    "retail_sales_growth": 6.2,
                    "housing_starts": "Growing",
                    "consumer_confidence": 95.3
                }
            },
            "Japan": {
                "gdp_growth": 1.2,
                "inflation": 2.8,
                "interest_rate": 0.1,  # Near zero
                "unemployment": 2.5,
                "cycle_stage": "Moderate Expansion",
                "central_bank": "Bank of Japan",
                "policy_stance": "Ultra-accommodative (ending negative rates)",
                "next_move_likely": "Gradual normalization",
                "key_indicators": {
                    "PMI": 48.9,
                    "retail_sales_growth": 1.3,
                    "housing_starts": "Stable",
                    "consumer_confidence": 72.1
                }
            },
            "UK": {
                "gdp_growth": 0.3,
                "inflation": 4.0,
                "interest_rate": 5.25,
                "unemployment": 4.2,
                "cycle_stage": "Stagnation",
                "central_bank": "Bank of England",
                "policy_stance": "Restrictive",
                "next_move_likely": "Rate cuts in H2 2025",
                "key_indicators": {
                    "PMI": 47.8,
                    "retail_sales_growth": 0.1,
                    "housing_starts": "Declining",
                    "consumer_confidence": 58.7
                }
            }
        }

        # Economic cycles framework
        self.cycle_characteristics = {
            "Early Expansion": {
                "duration": "6-12 months",
                "gdp": "Accelerating (2-4%)",
                "inflation": "Low and stable",
                "unemployment": "High but declining",
                "interest_rates": "Low, accommodative",
                "best_sectors": ["Technology", "Consumer Discretionary", "Financials"],
                "worst_sectors": ["Utilities", "Consumer Staples"],
                "business_strategy": "Invest aggressively, hire, expand capacity",
                "investment_strategy": "Equities (growth stocks), commodities"
            },
            "Strong Expansion": {
                "duration": "12-24 months",
                "gdp": "Strong growth (>4%)",
                "inflation": "Rising gradually",
                "unemployment": "Low and falling",
                "interest_rates": "Rising (central banks tightening)",
                "best_sectors": ["Industrials", "Materials", "Energy"],
                "worst_sectors": ["Bonds", "Utilities"],
                "business_strategy": "Maximize growth, consider M&A, optimize operations",
                "investment_strategy": "Equities (value stocks), real assets, commodities"
            },
            "Late Expansion": {
                "duration": "6-18 months",
                "gdp": "Slowing growth (1-3%)",
                "inflation": "High (central bank concern)",
                "unemployment": "Very low",
                "interest_rates": "High and rising (restrictive)",
                "best_sectors": ["Energy", "Healthcare", "Consumer Staples"],
                "worst_sectors": ["Technology (growth)", "Real Estate"],
                "business_strategy": "Preserve margins, cautious hiring, build cash reserves",
                "investment_strategy": "Defensive equities, short duration bonds, cash"
            },
            "Peak": {
                "duration": "3-6 months",
                "gdp": "Near zero or slightly negative",
                "inflation": "High but peaking",
                "unemployment": "Starting to rise",
                "interest_rates": "High but stabilizing",
                "best_sectors": ["Healthcare", "Utilities", "Consumer Staples"],
                "worst_sectors": ["Cyclicals", "Small caps"],
                "business_strategy": "Defensive positioning, delay major investments, de-risk",
                "investment_strategy": "Bonds (duration), gold, defensive equities"
            },
            "Contraction": {
                "duration": "6-18 months",
                "gdp": "Negative growth",
                "inflation": "Falling rapidly",
                "unemployment": "Rising sharply",
                "interest_rates": "Falling (central banks easing)",
                "best_sectors": ["Consumer Staples", "Healthcare", "Utilities"],
                "worst_sectors": ["Industrials", "Materials", "Consumer Discretionary"],
                "business_strategy": "Cost cutting, preserve cash, avoid leverage",
                "investment_strategy": "Bonds, defensive equities, cash, wait for opportunities"
            },
            "Trough": {
                "duration": "3-6 months",
                "gdp": "Stabilizing",
                "inflation": "Very low",
                "unemployment": "High but stabilizing",
                "interest_rates": "Very low",
                "best_sectors": ["Technology", "Consumer Discretionary (early)"],
                "worst_sectors": ["Utilities"],
                "business_strategy": "Prepare for recovery, strategic acquisitions, selective hiring",
                "investment_strategy": "Equities (growth), high yield bonds, emerging markets"
            },
            "Stagnation": {
                "duration": "Varies",
                "gdp": "Low growth (<1%)",
                "inflation": "Variable",
                "unemployment": "Elevated",
                "interest_rates": "Variable",
                "best_sectors": ["Quality companies with pricing power"],
                "worst_sectors": ["Cyclicals", "Commodities"],
                "business_strategy": "Focus on profitability over growth, operational excellence",
                "investment_strategy": "Quality equities, diversified portfolio"
            }
        }

        # Leading indicators
        self.leading_indicators = [
            "Yield curve (10Y-2Y spread)",
            "PMI manufacturing index",
            "Consumer confidence index",
            "Housing starts",
            "Stock market performance",
            "Money supply growth (M2)",
            "Initial jobless claims",
            "Corporate credit spreads",
            "Commodity prices",
            "Business confidence surveys"
        ]

    async def process(
        self,
        query: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process macroeconomics query"""

        try:
            # Extract regions of interest
            regions = self._extract_regions(query)

            # Classify analysis type
            analysis_type = self._classify_macro_query(query)

            # Perform analysis
            if "cycle" in query.lower() or "recession" in query.lower():
                result = await self._economic_cycle_analysis(regions)
            elif "inflation" in query.lower():
                result = await self._inflation_analysis(regions)
            elif "interest rate" in query.lower() or "fed" in query.lower() or "central bank" in query.lower():
                result = await self._interest_rate_analysis(regions)
            elif "impact" in query.lower() or "affect" in query.lower():
                result = await self._business_impact_analysis(regions, user_context)
            elif "forecast" in query.lower() or "outlook" in query.lower():
                result = await self._economic_outlook(regions)
            elif "sector" in query.lower():
                result = await self._sector_rotation_analysis(regions)
            else:
                result = await self._comprehensive_macro_analysis(regions)

            return {
                "agent": self.name,
                "query": query,
                "analysis_type": analysis_type,
                "regions_analyzed": regions,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "agent": self.name,
                "error": str(e),
                "fallback_response": "Unable to complete macroeconomic analysis. Please consult an economist."
            }

    def _extract_regions(self, query: str) -> List[str]:
        """Extract regions from query"""
        regions = []
        query_lower = query.lower()

        for region in self.economic_data.keys():
            if region.lower() in query_lower:
                regions.append(region)

        # If no specific regions mentioned, return major economies
        if not regions:
            return ["US", "EU", "China", "India"]

        return regions

    def _classify_macro_query(self, query: str) -> str:
        """Classify macroeconomic query type"""
        query_lower = query.lower()

        if "cycle" in query_lower or "recession" in query_lower:
            return "economic_cycle"
        elif "inflation" in query_lower:
            return "inflation"
        elif "interest rate" in query_lower or "fed" in query_lower:
            return "monetary_policy"
        elif "impact" in query_lower:
            return "business_impact"
        elif "forecast" in query_lower:
            return "outlook"
        elif "sector" in query_lower:
            return "sector_rotation"
        else:
            return "comprehensive"

    async def _economic_cycle_analysis(self, regions: List[str]) -> Dict[str, Any]:
        """Analyze economic cycles"""

        analysis = {
            "current_cycle_stages": {},
            "recession_probability": {},
            "cycle_insights": [],
            "strategic_implications": {},
            "leading_indicators_status": {}
        }

        for region in regions:
            if region not in self.economic_data:
                continue

            data = self.economic_data[region]
            cycle_stage = data["cycle_stage"]

            analysis["current_cycle_stages"][region] = {
                "stage": cycle_stage,
                "characteristics": self.cycle_characteristics.get(cycle_stage, {}),
                "duration_in_stage": "Estimated 8-12 months",  # Would be calculated from historical data
                "next_stage_likely": self._predict_next_cycle_stage(data)
            }

            analysis["recession_probability"][region] = self._calculate_recession_probability(data)

            analysis["strategic_implications"][region] = self._get_cycle_strategic_implications(cycle_stage)

        # Leading indicators check
        analysis["leading_indicators_status"] = self._assess_leading_indicators(regions)

        # LLM-enhanced insights
        llm_insights = await self._get_llm_cycle_insights(regions, analysis)
        analysis["llm_insights"] = llm_insights

        return analysis

    def _predict_next_cycle_stage(self, data: Dict) -> str:
        """Predict next economic cycle stage"""
        current_stage = data["cycle_stage"]

        stage_progression = {
            "Trough": "Early Expansion",
            "Early Expansion": "Strong Expansion",
            "Strong Expansion": "Late Expansion",
            "Late Expansion": "Peak",
            "Peak": "Contraction",
            "Contraction": "Trough",
            "Stagnation": "Early Expansion (if stimulus) or Contraction (if no stimulus)"
        }

        return stage_progression.get(current_stage, "Uncertain")

    def _calculate_recession_probability(self, data: Dict) -> Dict[str, Any]:
        """Calculate recession probability (simplified model)"""

        score = 0
        max_score = 10

        # Factors indicating recession risk
        if data["gdp_growth"] < 1.0:
            score += 3
        elif data["gdp_growth"] < 2.0:
            score += 1

        if data["inflation"] > 5.0:
            score += 2
        elif data["inflation"] > 4.0:
            score += 1

        if data["interest_rate"] > 5.0:
            score += 2

        if data["unemployment"] > 6.0:
            score += 2

        if data["key_indicators"]["PMI"] < 50:
            score += 2

        probability_pct = (score / max_score) * 100

        if probability_pct > 70:
            level = "Very High"
        elif probability_pct > 50:
            level = "High"
        elif probability_pct > 30:
            level = "Moderate"
        elif probability_pct > 15:
            level = "Low"
        else:
            level = "Very Low"

        return {
            "probability_pct": probability_pct,
            "level": level,
            "horizon": "Next 12 months",
            "key_risk_factors": self._identify_recession_risk_factors(data)
        }

    def _identify_recession_risk_factors(self, data: Dict) -> List[str]:
        """Identify specific recession risk factors"""
        risks = []

        if data["gdp_growth"] < 2.0:
            risks.append(f"Weak GDP growth ({data['gdp_growth']}%)")

        if data["inflation"] > 4.0:
            risks.append(f"Elevated inflation ({data['inflation']}%)")

        if data["interest_rate"] > 5.0:
            risks.append(f"High interest rates ({data['interest_rate']}%) constraining activity")

        if data["key_indicators"]["PMI"] < 50:
            risks.append(f"Manufacturing contraction (PMI: {data['key_indicators']['PMI']})")

        if "Declining" in data["key_indicators"]["housing_starts"]:
            risks.append("Housing market weakness")

        if not risks:
            risks.append("No major red flags detected")

        return risks

    def _get_cycle_strategic_implications(self, cycle_stage: str) -> Dict[str, Any]:
        """Get strategic business implications for cycle stage"""

        characteristics = self.cycle_characteristics.get(cycle_stage, {})

        return {
            "cycle_stage": cycle_stage,
            "business_strategy": characteristics.get("business_strategy", ""),
            "investment_strategy": characteristics.get("investment_strategy", ""),
            "best_sectors": characteristics.get("best_sectors", []),
            "worst_sectors": characteristics.get("worst_sectors", []),
            "risk_level": self._map_cycle_to_risk(cycle_stage)
        }

    def _map_cycle_to_risk(self, cycle_stage: str) -> str:
        """Map cycle stage to risk level"""
        risk_mapping = {
            "Early Expansion": "Low",
            "Strong Expansion": "Low-Moderate",
            "Late Expansion": "Moderate-High",
            "Peak": "High",
            "Contraction": "Very High",
            "Trough": "Moderate (but opportunity)",
            "Stagnation": "Moderate"
        }
        return risk_mapping.get(cycle_stage, "Moderate")

    def _assess_leading_indicators(self, regions: List[str]) -> Dict[str, Any]:
        """Assess status of leading economic indicators"""

        indicators_status = {
            "summary": "",
            "indicators": [],
            "overall_signal": ""
        }

        # Simplified assessment
        positive_signals = 0
        negative_signals = 0
        total_signals = 0

        for region in regions:
            if region not in self.economic_data:
                continue

            data = self.economic_data[region]

            # PMI
            pmi = data["key_indicators"]["PMI"]
            if pmi > 50:
                positive_signals += 1
            else:
                negative_signals += 1
            total_signals += 1

            indicators_status["indicators"].append({
                "indicator": f"PMI ({region})",
                "value": pmi,
                "signal": "Expansion" if pmi > 50 else "Contraction",
                "importance": "High"
            })

            # Consumer confidence
            cc = data["key_indicators"]["consumer_confidence"]
            if cc > 80:
                positive_signals += 1
            elif cc < 60:
                negative_signals += 1
            total_signals += 1

            indicators_status["indicators"].append({
                "indicator": f"Consumer Confidence ({region})",
                "value": cc,
                "signal": "Strong" if cc > 80 else ("Weak" if cc < 60 else "Moderate"),
                "importance": "Medium"
            })

        # Overall signal
        if positive_signals > negative_signals * 2:
            indicators_status["overall_signal"] = "Strongly Positive"
        elif positive_signals > negative_signals:
            indicators_status["overall_signal"] = "Moderately Positive"
        elif negative_signals > positive_signals:
            indicators_status["overall_signal"] = "Negative"
        else:
            indicators_status["overall_signal"] = "Mixed"

        indicators_status["summary"] = f"{positive_signals}/{total_signals} indicators showing positive signals"

        return indicators_status

    async def _inflation_analysis(self, regions: List[str]) -> Dict[str, Any]:
        """Analyze inflation trends"""

        analysis = {
            "current_inflation": {},
            "inflation_drivers": {},
            "outlook": {},
            "business_implications": {}
        }

        for region in regions:
            if region not in self.economic_data:
                continue

            data = self.economic_data[region]
            inflation = data["inflation"]

            analysis["current_inflation"][region] = {
                "rate": inflation,
                "trend": self._assess_inflation_trend(inflation, data),
                "target": self._get_inflation_target(region),
                "deviation_from_target": inflation - self._get_inflation_target(region)
            }

            analysis["inflation_drivers"][region] = self._identify_inflation_drivers(data)

            analysis["outlook"][region] = self._forecast_inflation(data)

            analysis["business_implications"][region] = self._get_inflation_business_implications(inflation)

        # LLM-enhanced insights
        llm_insights = await self._get_llm_inflation_insights(regions, analysis)
        analysis["llm_insights"] = llm_insights

        return analysis

    def _assess_inflation_trend(self, inflation: float, data: Dict) -> str:
        """Assess inflation trend"""
        # Simplified - in reality would compare to historical data
        if inflation > 4.0:
            return "High and concerning"
        elif inflation > 3.0:
            return "Elevated"
        elif inflation > 2.0:
            return "Moderate"
        elif inflation > 0.5:
            return "Low but positive"
        else:
            return "Very low / Deflation risk"

    def _get_inflation_target(self, region: str) -> float:
        """Get central bank inflation target"""
        targets = {
            "US": 2.0,
            "EU": 2.0,
            "UK": 2.0,
            "Japan": 2.0,
            "India": 4.0,  # RBI targets 4% +/- 2%
            "China": 3.0
        }
        return targets.get(region, 2.0)

    def _identify_inflation_drivers(self, data: Dict) -> List[str]:
        """Identify drivers of inflation"""
        drivers = []

        if data["gdp_growth"] > 4.0:
            drivers.append("Strong demand-side pressures")

        if data["interest_rate"] < 3.0:
            drivers.append("Accommodative monetary policy")

        if data.get("supply_chain_issues", False):
            drivers.append("Supply chain disruptions")

        if data.get("energy_prices", "") == "High":
            drivers.append("Elevated energy costs")

        if data["unemployment"] < 4.0:
            drivers.append("Tight labor market / wage pressures")

        if not drivers:
            drivers.append("Moderate demand-pull inflation")

        return drivers

    def _forecast_inflation(self, data: Dict) -> Dict[str, Any]:
        """Forecast inflation trajectory"""

        current_inflation = data["inflation"]
        interest_rate = data["interest_rate"]

        # Simplified forecasting logic
        if interest_rate > 5.0 and current_inflation > 3.0:
            forecast = {
                "3_month": current_inflation - 0.3,
                "6_month": current_inflation - 0.6,
                "12_month": current_inflation - 1.2,
                "trend": "Declining due to restrictive monetary policy"
            }
        elif current_inflation < 1.0:
            forecast = {
                "3_month": current_inflation + 0.1,
                "6_month": current_inflation + 0.3,
                "12_month": current_inflation + 0.6,
                "trend": "Gradually rising from low base"
            }
        else:
            forecast = {
                "3_month": current_inflation - 0.1,
                "6_month": current_inflation - 0.2,
                "12_month": current_inflation - 0.3,
                "trend": "Gradually moderating"
            }

        return forecast

    def _get_inflation_business_implications(self, inflation: float) -> List[str]:
        """Get business implications of inflation level"""

        if inflation > 5.0:
            return [
                "⚠️ High input cost pressures",
                "Need aggressive price increase strategy",
                "Supply chain cost management critical",
                "Consider long-term supply contracts",
                "Wage pressure increasing - plan for higher labor costs"
            ]
        elif inflation > 3.0:
            return [
                "Moderate input cost increases",
                "Selective price increases appropriate",
                "Monitor margin compression",
                "Efficiency improvements important"
            ]
        elif inflation > 0.5:
            return [
                "Stable cost environment",
                "Gradual price increases possible",
                "Focus on volume growth"
            ]
        else:
            return [
                "Deflationary pressures",
                "Pricing power limited",
                "Cost cutting imperative",
                "Volume growth over pricing"
            ]

    async def _interest_rate_analysis(self, regions: List[str]) -> Dict[str, Any]:
        """Analyze interest rates and monetary policy"""

        analysis = {
            "current_rates": {},
            "policy_stance": {},
            "rate_forecasts": {},
            "business_impact": {}
        }

        for region in regions:
            if region not in self.economic_data:
                continue

            data = self.economic_data[region]

            analysis["current_rates"][region] = {
                "policy_rate": data["interest_rate"],
                "historical_context": self._get_rate_historical_context(data["interest_rate"]),
                "real_rate": data["interest_rate"] - data["inflation"]  # Real interest rate
            }

            analysis["policy_stance"][region] = {
                "stance": data["policy_stance"],
                "central_bank": data["central_bank"],
                "next_move": data["next_move_likely"],
                "rationale": self._explain_policy_stance(data)
            }

            analysis["rate_forecasts"][region] = self._forecast_interest_rates(data)

            analysis["business_impact"][region] = self._get_rate_business_impact(data["interest_rate"])

        # LLM-enhanced insights
        llm_insights = await self._get_llm_rate_insights(regions, analysis)
        analysis["llm_insights"] = llm_insights

        return analysis

    def _get_rate_historical_context(self, rate: float) -> str:
        """Provide historical context for interest rate"""
        if rate > 5.0:
            return "Elevated - restrictive territory"
        elif rate > 3.0:
            return "Moderate - neutral territory"
        elif rate > 1.0:
            return "Low - accommodative"
        else:
            return "Very low - ultra-accommodative"

    def _explain_policy_stance(self, data: Dict) -> str:
        """Explain central bank policy stance"""
        if data["inflation"] > 4.0 and data["interest_rate"] > 5.0:
            return "Fighting inflation with restrictive policy"
        elif data["inflation"] < 2.0 and data["gdp_growth"] < 2.0:
            return "Supporting growth with accommodative policy"
        elif data["gdp_growth"] < 0:
            return "Combating recession with aggressive easing"
        else:
            return "Balancing growth and inflation objectives"

    def _forecast_interest_rates(self, data: Dict) -> Dict[str, Any]:
        """Forecast interest rate trajectory"""

        current_rate = data["interest_rate"]
        inflation = data["inflation"]
        gdp_growth = data["gdp_growth"]

        # Simplified forecasting
        if inflation > 4.0 and current_rate < 5.0:
            forecast = {
                "3_month": current_rate + 0.25,
                "6_month": current_rate + 0.50,
                "12_month": current_rate + 0.75,
                "direction": "Rising"
            }
        elif inflation < 2.0 and gdp_growth < 1.0:
            forecast = {
                "3_month": current_rate - 0.25,
                "6_month": current_rate - 0.50,
                "12_month": current_rate - 1.00,
                "direction": "Falling"
            }
        elif inflation > 3.0 and current_rate > 5.0:
            forecast = {
                "3_month": current_rate,
                "6_month": current_rate - 0.25,
                "12_month": current_rate - 0.75,
                "direction": "Peaking then declining"
            }
        else:
            forecast = {
                "3_month": current_rate,
                "6_month": current_rate,
                "12_month": current_rate - 0.25,
                "direction": "Stable to slightly lower"
            }

        return forecast

    def _get_rate_business_impact(self, rate: float) -> List[str]:
        """Get business impact of interest rate level"""

        if rate > 5.0:
            return [
                "⚠️ High borrowing costs - defer debt-financed expansion",
                "Focus on cash generation and debt paydown",
                "Capital expenditures should be selective",
                "Variable rate debt exposure is expensive",
                "Consider refinancing to fixed rates if appropriate"
            ]
        elif rate > 3.0:
            return [
                "Moderate borrowing costs",
                "Selective financing for high-ROI projects",
                "Balance growth and financial prudence",
                "Lock in rates for long-term financing"
            ]
        elif rate > 1.0:
            return [
                "Favorable borrowing environment",
                "Good time for debt-financed growth",
                "M&A financing attractive",
                "Refinance expensive debt"
            ]
        else:
            return [
                "✓ Very favorable borrowing costs",
                "Opportune time for major investments",
                "Cheap financing available",
                "Growth investments highly attractive"
            ]

    async def _business_impact_analysis(
        self,
        regions: List[str],
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze business impact of macroeconomic conditions"""

        analysis = {
            "impact_by_region": {},
            "sector_impact": {},
            "strategic_recommendations": [],
            "risk_mitigation": []
        }

        for region in regions:
            if region not in self.economic_data:
                continue

            data = self.economic_data[region]

            analysis["impact_by_region"][region] = {
                "demand_outlook": self._assess_demand_outlook(data),
                "cost_pressures": self._assess_cost_pressures(data),
                "financing_environment": self._assess_financing(data),
                "labor_market": self._assess_labor_market(data),
                "overall_business_environment": self._score_business_environment(data)
            }

        # Sector-specific impact (if user context provides sector)
        if user_context and "sector" in user_context:
            analysis["sector_impact"] = self._analyze_sector_impact(
                user_context["sector"], regions
            )

        # Strategic recommendations
        analysis["strategic_recommendations"] = self._generate_macro_strategies(regions)

        # LLM-enhanced insights
        llm_insights = await self._get_llm_business_impact_insights(regions, user_context)
        analysis["llm_insights"] = llm_insights

        return analysis

    def _assess_demand_outlook(self, data: Dict) -> Dict[str, Any]:
        """Assess demand outlook"""
        gdp = data["gdp_growth"]

        if gdp > 5.0:
            outlook = "Very Strong"
        elif gdp > 3.0:
            outlook = "Strong"
        elif gdp > 1.0:
            outlook = "Moderate"
        elif gdp > 0:
            outlook = "Weak"
        else:
            outlook = "Contracting"

        return {
            "outlook": outlook,
            "gdp_growth": gdp,
            "consumer_confidence": data["key_indicators"]["consumer_confidence"],
            "retail_sales": data["key_indicators"]["retail_sales_growth"]
        }

    def _assess_cost_pressures(self, data: Dict) -> str:
        """Assess cost pressures"""
        inflation = data["inflation"]

        if inflation > 5.0:
            return "Very High cost pressures"
        elif inflation > 3.0:
            return "Elevated cost pressures"
        elif inflation > 1.0:
            return "Moderate cost pressures"
        else:
            return "Low cost pressures"

    def _assess_financing(self, data: Dict) -> str:
        """Assess financing environment"""
        rate = data["interest_rate"]

        if rate > 5.0:
            return "Expensive - restrictive"
        elif rate > 3.0:
            return "Moderate cost"
        elif rate > 1.0:
            return "Affordable"
        else:
            return "Very cheap - highly accommodative"

    def _assess_labor_market(self, data: Dict) -> Dict[str, Any]:
        """Assess labor market conditions"""
        unemployment = data["unemployment"]

        if unemployment < 4.0:
            tightness = "Very Tight"
            hiring_difficulty = "High"
            wage_pressure = "High"
        elif unemployment < 5.0:
            tightness = "Tight"
            hiring_difficulty = "Moderate-High"
            wage_pressure = "Moderate-High"
        elif unemployment < 6.0:
            tightness = "Balanced"
            hiring_difficulty = "Moderate"
            wage_pressure = "Moderate"
        else:
            tightness = "Slack"
            hiring_difficulty = "Low"
            wage_pressure = "Low"

        return {
            "unemployment_rate": unemployment,
            "market_tightness": tightness,
            "hiring_difficulty": hiring_difficulty,
            "wage_pressure": wage_pressure
        }

    def _score_business_environment(self, data: Dict) -> Dict[str, Any]:
        """Score overall business environment (0-10)"""

        score = 5.0  # Start at neutral

        # Positive factors
        if data["gdp_growth"] > 3.0:
            score += 1.5
        elif data["gdp_growth"] > 2.0:
            score += 0.75

        if data["inflation"] < 3.0 and data["inflation"] > 0.5:
            score += 1.0

        if data["interest_rate"] < 4.0:
            score += 1.0

        # Negative factors
        if data["inflation"] > 5.0:
            score -= 1.5

        if data["interest_rate"] > 5.5:
            score -= 1.0

        if data["gdp_growth"] < 1.0:
            score -= 2.0

        score = max(0.0, min(10.0, score))

        if score > 7.5:
            rating = "Excellent"
        elif score > 6.0:
            rating = "Good"
        elif score > 4.5:
            rating = "Neutral"
        elif score > 3.0:
            rating = "Challenging"
        else:
            rating = "Difficult"

        return {
            "score": score,
            "rating": rating,
            "trend": data["cycle_stage"]
        }

    def _analyze_sector_impact(self, sector: str, regions: List[str]) -> Dict[str, Any]:
        """Analyze macroeconomic impact on specific sector"""

        # Sector sensitivities (simplified)
        sector_sensitivities = {
            "Technology": {
                "interest_rate_sensitive": True,
                "gdp_sensitive": True,
                "inflation_sensitive": False,
                "cycle_preference": ["Early Expansion", "Strong Expansion"]
            },
            "Consumer Discretionary": {
                "interest_rate_sensitive": True,
                "gdp_sensitive": True,
                "inflation_sensitive": True,
                "cycle_preference": ["Early Expansion", "Strong Expansion"]
            },
            "Consumer Staples": {
                "interest_rate_sensitive": False,
                "gdp_sensitive": False,
                "inflation_sensitive": True,
                "cycle_preference": ["Late Expansion", "Contraction"]
            },
            "Financials": {
                "interest_rate_sensitive": True,
                "gdp_sensitive": True,
                "inflation_sensitive": False,
                "cycle_preference": ["Early Expansion", "Strong Expansion"]
            },
            "Healthcare": {
                "interest_rate_sensitive": False,
                "gdp_sensitive": False,
                "inflation_sensitive": False,
                "cycle_preference": ["All stages"]
            },
            "Industrials": {
                "interest_rate_sensitive": True,
                "gdp_sensitive": True,
                "inflation_sensitive": True,
                "cycle_preference": ["Strong Expansion"]
            },
            "Materials": {
                "interest_rate_sensitive": True,
                "gdp_sensitive": True,
                "inflation_sensitive": True,
                "cycle_preference": ["Strong Expansion", "Late Expansion"]
            },
            "Energy": {
                "interest_rate_sensitive": False,
                "gdp_sensitive": True,
                "inflation_sensitive": True,
                "cycle_preference": ["Late Expansion"]
            },
            "Utilities": {
                "interest_rate_sensitive": True,
                "gdp_sensitive": False,
                "inflation_sensitive": False,
                "cycle_preference": ["Late Expansion", "Contraction"]
            },
            "Real Estate": {
                "interest_rate_sensitive": True,
                "gdp_sensitive": True,
                "inflation_sensitive": True,
                "cycle_preference": ["Early Expansion", "Strong Expansion"]
            }
        }

        sensitivity = sector_sensitivities.get(sector, {
            "interest_rate_sensitive": True,
            "gdp_sensitive": True,
            "inflation_sensitive": True,
            "cycle_preference": ["Varies"]
        })

        impact_assessment = {
            "sector": sector,
            "sensitivities": sensitivity,
            "current_environment_suitability": {},
            "recommendations": []
        }

        for region in regions:
            if region not in self.economic_data:
                continue

            data = self.economic_data[region]
            cycle_stage = data["cycle_stage"]

            # Assess suitability
            score = 5.0

            if sensitivity["interest_rate_sensitive"] and data["interest_rate"] > 5.0:
                score -= 1.5

            if sensitivity["gdp_sensitive"]:
                if data["gdp_growth"] > 4.0:
                    score += 2.0
                elif data["gdp_growth"] < 1.0:
                    score -= 2.0

            if cycle_stage in sensitivity["cycle_preference"]:
                score += 1.5

            impact_assessment["current_environment_suitability"][region] = {
                "score": score,
                "rating": "Favorable" if score > 6.0 else ("Neutral" if score > 4.0 else "Challenging"),
                "key_factors": self._identify_sector_key_factors(sector, data)
            }

        return impact_assessment

    def _identify_sector_key_factors(self, sector: str, data: Dict) -> List[str]:
        """Identify key macroeconomic factors affecting sector"""

        factors = []

        if sector in ["Technology", "Consumer Discretionary", "Real Estate"]:
            factors.append(f"Interest rates at {data['interest_rate']}% - {'headwind' if data['interest_rate'] > 5.0 else 'tailwind'}")

        if sector in ["Consumer Discretionary", "Consumer Staples", "Retail"]:
            factors.append(f"Consumer confidence at {data['key_indicators']['consumer_confidence']}")

        if sector in ["Materials", "Energy", "Industrials"]:
            factors.append(f"GDP growth at {data['gdp_growth']}% - demand {'strong' if data['gdp_growth'] > 3.0 else 'moderate'}")

        if sector == "Financials":
            factors.append(f"Interest rate environment: {data['policy_stance']}")

        return factors

    def _generate_macro_strategies(self, regions: List[str]) -> List[Dict[str, Any]]:
        """Generate strategic recommendations based on macro conditions"""

        strategies = []

        for region in regions:
            if region not in self.economic_data:
                continue

            data = self.economic_data[region]
            cycle = data["cycle_stage"]

            cycle_characteristics = self.cycle_characteristics.get(cycle, {})
            strategy = cycle_characteristics.get("business_strategy", "")

            if strategy:
                strategies.append({
                    "region": region,
                    "cycle_stage": cycle,
                    "strategy": strategy,
                    "rationale": f"Aligning with {cycle} phase characteristics"
                })

        return strategies

    async def _economic_outlook(self, regions: List[str]) -> Dict[str, Any]:
        """Provide economic outlook"""

        outlook = {
            "regional_forecasts": {},
            "key_trends": [],
            "risks": [],
            "opportunities": []
        }

        for region in regions:
            if region not in self.economic_data:
                continue

            data = self.economic_data[region]

            outlook["regional_forecasts"][region] = {
                "gdp_forecast_12m": self._forecast_gdp(data),
                "inflation_forecast_12m": self._forecast_inflation(data),
                "rate_forecast_12m": self._forecast_interest_rates(data),
                "cycle_forecast": self._predict_next_cycle_stage(data),
                "summary": self._generate_outlook_summary(data)
            }

        # Global trends
        outlook["key_trends"] = [
            "Central banks nearing end of tightening cycle",
            "Inflation gradually moderating but sticky services inflation",
            "Divergent growth trajectories (India/US strong, EU/China weak)",
            "Technology sector adapting to higher interest rate environment",
            "Geopolitical tensions impacting supply chains and trade"
        ]

        # Risks
        outlook["risks"] = [
            "Recession in developed markets",
            "Sticky inflation requiring prolonged tight monetary policy",
            "Banking sector stress from high rates",
            "China property sector contagion",
            "Geopolitical escalation (Ukraine, Middle East, Taiwan)"
        ]

        # Opportunities
        outlook["opportunities"] = [
            "Emerging market growth (India, Southeast Asia)",
            "AI/technology transformation opportunities",
            "Energy transition investments",
            "Nearshoring/reshoring beneficiaries",
            "Distressed asset opportunities if recession materializes"
        ]

        # LLM-enhanced outlook
        llm_insights = await self._get_llm_outlook_insights(regions, outlook)
        outlook["llm_insights"] = llm_insights

        return outlook

    def _forecast_gdp(self, data: Dict) -> Dict[str, float]:
        """Forecast GDP growth"""
        current_gdp = data["gdp_growth"]

        # Simplified mean reversion model
        if current_gdp > 5.0:
            forecast_12m = current_gdp - 1.0
        elif current_gdp < 1.0:
            forecast_12m = current_gdp + 0.5
        else:
            forecast_12m = current_gdp - 0.2

        return {
            "current": current_gdp,
            "forecast_12m": forecast_12m
        }

    def _generate_outlook_summary(self, data: Dict) -> str:
        """Generate outlook summary"""
        cycle = data["cycle_stage"]
        gdp = data["gdp_growth"]
        inflation = data["inflation"]

        if cycle in ["Early Expansion", "Strong Expansion"]:
            return f"Positive outlook with {gdp}% growth. {inflation}% inflation {'manageable' if inflation < 4.0 else 'elevated but peaking'}."
        elif cycle == "Late Expansion":
            return f"Maturing cycle with {gdp}% growth slowing. Inflation at {inflation}% keeping policy restrictive."
        elif cycle == "Contraction":
            return f"Recessionary environment with negative growth. Policy easing underway but lagged effects."
        else:
            return f"Mixed signals with {gdp}% growth and {inflation}% inflation. Outlook uncertain."

    async def _sector_rotation_analysis(self, regions: List[str]) -> Dict[str, Any]:
        """Analyze sector rotation opportunities"""

        analysis = {
            "current_cycle_stages": {},
            "favored_sectors": {},
            "sectors_to_avoid": {},
            "rotation_strategy": []
        }

        for region in regions:
            if region not in self.economic_data:
                continue

            data = self.economic_data[region]
            cycle = data["cycle_stage"]

            cycle_chars = self.cycle_characteristics.get(cycle, {})

            analysis["current_cycle_stages"][region] = cycle
            analysis["favored_sectors"][region] = cycle_chars.get("best_sectors", [])
            analysis["sectors_to_avoid"][region] = cycle_chars.get("worst_sectors", [])

        # Rotation strategy
        analysis["rotation_strategy"] = [
            {
                "action": "Overweight",
                "sectors": list(set(sum([analysis["favored_sectors"].get(r, []) for r in regions], []))),
                "rationale": "Aligned with current economic cycle stage"
            },
            {
                "action": "Underweight",
                "sectors": list(set(sum([analysis["sectors_to_avoid"].get(r, []) for r in regions], []))),
                "rationale": "Unfavorable cycle positioning"
            }
        ]

        # LLM-enhanced insights
        llm_insights = await self._get_llm_sector_rotation_insights(regions, analysis)
        analysis["llm_insights"] = llm_insights

        return analysis

    async def _comprehensive_macro_analysis(self, regions: List[str]) -> Dict[str, Any]:
        """Comprehensive macroeconomic analysis"""

        analysis = {
            "executive_summary": {},
            "cycle_analysis": await self._economic_cycle_analysis(regions),
            "inflation_analysis": await self._inflation_analysis(regions),
            "rate_analysis": await self._interest_rate_analysis(regions),
            "outlook": await self._economic_outlook(regions),
            "strategic_implications": []
        }

        # Executive summary
        analysis["executive_summary"] = {
            "key_takeaways": [
                "Global economy in transition - developed markets slowing, emerging markets growing",
                "Inflation moderating but central banks remain cautious",
                "Interest rates near peak, cuts likely in H2 2025",
                "Sector rotation opportunities emerging"
            ],
            "investment_implications": "Favor quality companies in defensive sectors short-term, position for cyclical recovery medium-term"
        }

        # Strategic implications
        analysis["strategic_implications"] = self._generate_macro_strategies(regions)

        # LLM-enhanced comprehensive insights
        llm_insights = await self._get_llm_comprehensive_macro_insights(regions, analysis)
        analysis["llm_insights"] = llm_insights

        return analysis

    # LLM-enhanced analysis methods

    async def _get_llm_cycle_insights(self, regions: List[str], analysis: Dict) -> str:
        """Get LLM insights on economic cycle"""
        prompt = f"""
        As a macroeconomist, analyze the economic cycle:

        Regions: {', '.join(regions)}
        Analysis: {json.dumps(analysis, indent=2, default=str)}

        Provide:
        1. Most critical insight about current cycle stage
        2. Biggest risk to outlook
        3. One actionable recommendation

        Be concise and specific.
        """

        try:
            response = await self.llm_service.generate_completion(
                prompt=prompt, max_tokens=400, temperature=0.7
            )
            return response
        except:
            return "LLM analysis unavailable."

    async def _get_llm_inflation_insights(self, regions: List[str], analysis: Dict) -> str:
        """Get LLM insights on inflation"""
        prompt = f"""
        As an inflation expert, analyze:

        Regions: {', '.join(regions)}
        Analysis: {json.dumps(analysis, indent=2, default=str)}

        Provide:
        1. Will inflation stay elevated or fall quickly?
        2. Key business implication

        Be direct and practical.
        """

        try:
            response = await self.llm_service.generate_completion(
                prompt=prompt, max_tokens=300, temperature=0.7
            )
            return response
        except:
            return "LLM analysis unavailable."

    async def _get_llm_rate_insights(self, regions: List[str], analysis: Dict) -> str:
        """Get LLM insights on interest rates"""
        prompt = f"""
        As a monetary policy analyst:

        Regions: {', '.join(regions)}
        Analysis: {json.dumps(analysis, indent=2, default=str)}

        Provide:
        1. When will central banks cut rates?
        2. Business financing implication

        Be concise.
        """

        try:
            response = await self.llm_service.generate_completion(
                prompt=prompt, max_tokens=300, temperature=0.7
            )
            return response
        except:
            return "LLM analysis unavailable."

    async def _get_llm_business_impact_insights(self, regions: List[str], user_context: Optional[Dict]) -> str:
        """Get LLM insights on business impact"""
        prompt = f"""
        Advise on business strategy given macro conditions:

        Regions: {', '.join(regions)}
        User Context: {json.dumps(user_context, indent=2) if user_context else 'Not provided'}

        Provide:
        1. Top strategic priority now
        2. One underappreciated risk

        Be actionable.
        """

        try:
            response = await self.llm_service.generate_completion(
                prompt=prompt, max_tokens=300, temperature=0.7
            )
            return response
        except:
            return "LLM analysis unavailable."

    async def _get_llm_outlook_insights(self, regions: List[str], outlook: Dict) -> str:
        """Get LLM economic outlook insights"""
        prompt = f"""
        As a chief economist, provide outlook:

        Regions: {', '.join(regions)}
        Forecast Data: {json.dumps(outlook, indent=2, default=str)}

        Provide:
        1. Base case scenario (60% probability)
        2. Bear case scenario (20% probability)
        3. Bull case scenario (20% probability)

        Be specific with timelines.
        """

        try:
            response = await self.llm_service.generate_completion(
                prompt=prompt, max_tokens=500, temperature=0.7
            )
            return response
        except:
            return "LLM analysis unavailable."

    async def _get_llm_sector_rotation_insights(self, regions: List[str], analysis: Dict) -> str:
        """Get LLM sector rotation insights"""
        prompt = f"""
        As a sector strategist:

        Regions: {', '.join(regions)}
        Analysis: {json.dumps(analysis, indent=2, default=str)}

        Provide:
        1. #1 sector to overweight now
        2. #1 sector to avoid
        3. Contrarian bet

        Be specific.
        """

        try:
            response = await self.llm_service.generate_completion(
                prompt=prompt, max_tokens=300, temperature=0.7
            )
            return response
        except:
            return "LLM analysis unavailable."

    async def _get_llm_comprehensive_macro_insights(self, regions: List[str], analysis: Dict) -> str:
        """Get comprehensive LLM macroeconomic insights"""
        prompt = f"""
        As a global macro strategist, synthesize:

        Regions: {', '.join(regions)}
        Full Analysis: {json.dumps(analysis, indent=2, default=str)}

        Provide:
        1. The single most important macro trend
        2. Biggest opportunity
        3. Biggest threat
        4. One bold prediction for 2025

        Be insightful.
        """

        try:
            response = await self.llm_service.generate_completion(
                prompt=prompt, max_tokens=600, temperature=0.8
            )
            return response
        except:
            return "LLM analysis unavailable."


if __name__ == "__main__":
    """Test the Macroeconomics Agent"""
    import asyncio

    async def test():
        agent = MacroeconomicsAgent()

        query = "What's the outlook for the US economy? Are we headed for a recession?"

        result = await agent.process(query)

        print("=" * 80)
        print("MACROECONOMICS AGENT TEST")
        print("=" * 80)
        print(f"Query: {query}")
        print(f"\nResult: {json.dumps(result, indent=2, default=str)}")

    asyncio.run(test())
