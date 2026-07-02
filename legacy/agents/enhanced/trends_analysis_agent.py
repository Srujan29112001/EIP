"""
Trends Analysis Agent
Advanced trend detection, forecasting, and pattern recognition across markets, technology, and consumer behavior
"""
import os
import sys
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from services.llm_service import LLMService
from services.rag_service import RAGService
from services.graphrag_service import GraphRAGService
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from base_agent import BaseAgent


class TrendsAnalysisAgent(BaseAgent):
    """
    Trends Analysis Agent

    Capabilities:
    - Market trend identification and analysis
    - Technology trend forecasting
    - Consumer behavior trends
    - Industry disruption prediction
    - Emerging business models
    - Social and cultural trends
    - Economic trends and cycles
    - Regulatory and policy trends
    - Competitive landscape evolution
    - Innovation and R&D trends
    - Investment and funding trends
    - Talent and workforce trends

    Advanced Features:
    - Time-series pattern recognition
    - Trend strength and momentum analysis
    - Trend lifecycle tracking (emerging/growth/mature/declining)
    - Multi-factor trend correlation
    - Predictive trend forecasting
    - Contrarian indicator detection
    - Trend convergence and divergence analysis

    Use Cases:
    - "What are the top technology trends for 2025?"
    - "Identify emerging trends in sustainable business"
    - "Will remote work trend continue or reverse?"
    - "What consumer behavior trends should I watch?"
    - "Predict the next big disruption in fintech"
    """

    def __init__(self):
        """Initialize Trends Analysis Agent"""
        super().__init__(
            agent_name="Trends Analysis Agent",
            agent_type="trends_analysis",
            capabilities=[
                "trend_detection",
                "trend_forecasting",
                "pattern_recognition",
                "lifecycle_analysis",
                "momentum_tracking",
                "disruption_prediction",
                "correlation_analysis",
                "sentiment_tracking",
                "adoption_curve_modeling",
                "contrarian_analysis"
            ]
        )

        self.llm_service = LLMService()
        self.rag_service = RAGService()
        self.graphrag_service = GraphRAGService()

        # Trend categories and frameworks
        self.trend_categories = {
            "technology": {
                "subcategories": ["AI/ML", "blockchain", "IoT", "quantum", "biotech", "clean_tech",
                                "robotics", "AR/VR", "5G/6G", "edge_computing"],
                "indicators": ["patents", "research_papers", "VC_funding", "startup_activity", "adoption_rate"]
            },
            "consumer": {
                "subcategories": ["purchasing_behavior", "lifestyle", "values", "demographics",
                                "digital_habits", "sustainability", "health_wellness", "experiences"],
                "indicators": ["search_volume", "social_media", "sales_data", "surveys", "app_downloads"]
            },
            "business_model": {
                "subcategories": ["subscription", "platform", "freemium", "marketplace", "D2C",
                                "hybrid", "circular_economy", "sharing_economy"],
                "indicators": ["new_entrants", "unicorn_emergence", "market_cap", "revenue_models"]
            },
            "market": {
                "subcategories": ["sector_growth", "geographic", "market_size", "competition",
                                "consolidation", "fragmentation", "globalization"],
                "indicators": ["revenue_growth", "CAGR", "market_share", "M&A_activity", "IPOs"]
            },
            "economic": {
                "subcategories": ["inflation", "interest_rates", "employment", "trade", "currency",
                                "commodities", "real_estate", "debt_levels"],
                "indicators": ["GDP_growth", "CPI", "unemployment", "yield_curves", "economic_sentiment"]
            },
            "social": {
                "subcategories": ["culture", "values", "movements", "demographics", "education",
                                "inequality", "urbanization", "family_structure"],
                "indicators": ["polls", "media_coverage", "protests", "policy_changes", "migration"]
            },
            "regulatory": {
                "subcategories": ["data_privacy", "antitrust", "ESG", "labor", "taxation",
                                "trade_policy", "industry_specific"],
                "indicators": ["legislation", "enforcement_actions", "regulatory_proposals", "lobbying"]
            },
            "workforce": {
                "subcategories": ["remote_work", "gig_economy", "skills", "compensation",
                                "diversity", "retention", "automation"],
                "indicators": ["job_postings", "salary_trends", "resignation_rates", "skill_demand"]
            }
        }

        # Trend lifecycle stages
        self.lifecycle_stages = {
            "emerging": {
                "characteristics": ["low_adoption", "high_uncertainty", "early_movers", "niche"],
                "duration": "0-2 years",
                "risk": "High",
                "opportunity": "High"
            },
            "growth": {
                "characteristics": ["rapid_adoption", "increasing_investment", "market_validation"],
                "duration": "2-5 years",
                "risk": "Medium",
                "opportunity": "High"
            },
            "mainstream": {
                "characteristics": ["widespread_adoption", "established_players", "standardization"],
                "duration": "5-10 years",
                "risk": "Low",
                "opportunity": "Medium"
            },
            "mature": {
                "characteristics": ["saturated_market", "slow_growth", "commoditization"],
                "duration": "10+ years",
                "risk": "Low",
                "opportunity": "Low"
            },
            "declining": {
                "characteristics": ["falling_adoption", "disruption", "obsolescence"],
                "duration": "Variable",
                "risk": "High",
                "opportunity": "Low"
            }
        }

        # Trend strength indicators
        self.strength_indicators = [
            "momentum", "adoption_rate", "investment_flow", "media_attention",
            "expert_consensus", "regulatory_support", "infrastructure_readiness",
            "market_demand", "technological_readiness", "network_effects"
        ]

        print(f"✓ {self.agent_name} initialized with advanced trend analysis capabilities")

    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process trends analysis query

        Args:
            query: User's trend question or topic
            context: Business/industry context

        Returns:
            Comprehensive trend analysis with forecasts
        """
        print(f"\n[{self.agent_name}] Processing: {query}")

        try:
            # Step 1: Classify trend query
            trend_classification = await self._classify_trend_query(query, context)

            # Step 2: Identify trends
            identified_trends = await self._identify_trends(query, trend_classification, context)

            # Step 3: Analyze trend strength and momentum
            trend_analysis = await self._analyze_trend_strength(identified_trends, context)

            # Step 4: Determine trend lifecycle stages
            lifecycle_assessment = await self._assess_lifecycle_stages(identified_trends, trend_analysis)

            # Step 5: Generate trend forecasts
            forecasts = await self._generate_trend_forecasts(identified_trends, trend_analysis, lifecycle_assessment)

            # Step 6: Identify opportunities and risks
            opportunities_risks = await self._identify_opportunities_and_risks(
                identified_trends, trend_analysis, forecasts, context
            )

            # Step 7: Generate comprehensive response
            response = await self._generate_trends_response(
                query, trend_classification, identified_trends, trend_analysis,
                lifecycle_assessment, forecasts, opportunities_risks, context
            )

            return {
                "answer": response,
                "confidence": 0.82,
                "agent": self.agent_name,
                "trend_classification": trend_classification,
                "identified_trends": identified_trends,
                "trend_analysis": trend_analysis,
                "lifecycle_assessment": lifecycle_assessment,
                "forecasts": forecasts,
                "opportunities_risks": opportunities_risks,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error in {self.agent_name}: {e}")
            return self._generate_fallback_response(query, str(e))

    async def _classify_trend_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Classify the type of trend analysis requested"""

        classification_prompt = f"""Classify this trend analysis query:

Query: "{query}"
Context: {json.dumps(context or {}, indent=2)}

Classify by:
1. Primary trend category: technology/consumer/business_model/market/economic/social/regulatory/workforce
2. Trend focus: identification/forecasting/impact_analysis/opportunity_discovery
3. Time horizon: short_term(0-1yr)/medium_term(1-3yr)/long_term(3-5yr+)
4. Scope: specific_trend/broad_landscape/comparative_analysis
5. Action needed: monitor/investigate/act_now/long_term_planning

Return JSON:
{{
    "primary_category": "category",
    "secondary_categories": ["cat1", "cat2"],
    "focus": "what user wants",
    "time_horizon": "timeframe",
    "scope": "breadth",
    "action_needed": "urgency",
    "keywords": ["key1", "key2"]
}}
"""

        try:
            response = await self.llm_service.generate(
                prompt=classification_prompt,
                model="gpt-4o",
                temperature=0.2,
                max_tokens=400
            )

            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
        except Exception as e:
            print(f"Trend classification failed: {e}")

        # Fallback classification
        return {
            "primary_category": "technology",
            "secondary_categories": [],
            "focus": "identification",
            "time_horizon": "medium_term",
            "scope": "broad_landscape",
            "action_needed": "monitor",
            "keywords": query.split()[:5]
        }

    async def _identify_trends(
        self,
        query: str,
        classification: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify relevant trends from knowledge base and LLM analysis"""

        trends = []

        try:
            # RAG retrieval for trend reports
            category = classification.get("primary_category", "technology")
            search_query = f"{category} trends {' '.join(classification.get('keywords', []))}"

            rag_results = await self.rag_service.retrieve(
                query=search_query,
                collection_name="market_reports",  # Use existing collection
                top_k=5
            )

            if rag_results:
                for result in rag_results:
                    trends.append({
                        "name": result.get("title", "Trend"),
                        "source": result.get("source", "RAG"),
                        "description": result.get("content", "")[:300]
                    })
        except Exception as e:
            print(f"RAG trend retrieval failed: {e}")

        # LLM-based trend identification
        identification_prompt = f"""Identify top emerging and significant trends:

Query: "{query}"
Category: {classification.get('primary_category')}
Time Horizon: {classification.get('time_horizon')}
Context: {json.dumps(context or {}, indent=2)}

Identify 5-7 most relevant trends. For each trend provide:
1. Trend Name
2. Category
3. Description (2-3 sentences)
4. Current Status (emerging/growth/mainstream/mature/declining)
5. Key Drivers (3-5 factors driving this trend)
6. Adoption Level (0-100%)
7. Geographic Relevance

Return as JSON array.
"""

        try:
            response = await self.llm_service.generate(
                prompt=identification_prompt,
                model="gpt-4o",
                temperature=0.4,
                max_tokens=1500
            )

            # Parse JSON
            json_start = response.find("[")
            json_end = response.rfind("]") + 1
            if json_start != -1 and json_end > json_start:
                llm_trends = json.loads(response[json_start:json_end])
                trends.extend(llm_trends[:7])

        except Exception as e:
            print(f"LLM trend identification failed: {e}")

        # Deduplicate and return top 7
        unique_trends = self._deduplicate_trends(trends)
        return unique_trends[:7]

    def _deduplicate_trends(self, trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate trends based on name similarity"""
        unique = []
        seen_names = set()

        for trend in trends:
            name = trend.get("name", "").lower()
            # Simple deduplication
            if name and name not in seen_names:
                unique.append(trend)
                seen_names.add(name)

        return unique

    async def _analyze_trend_strength(
        self,
        trends: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze strength and momentum of identified trends"""

        analysis_prompt = f"""Analyze the strength and momentum of these trends:

Trends:
{json.dumps(trends, indent=2)}

For each trend, assess:
1. **Strength Score** (0-10): Overall strength and significance
2. **Momentum** (accelerating/steady/decelerating): Rate of change
3. **Confidence Level** (low/medium/high): How certain is this trend?
4. **Supporting Evidence**: Key data points supporting this trend
5. **Contrary Indicators**: Any signs this trend might reverse?
6. **Catalysts**: What could accelerate this trend?
7. **Barriers**: What could slow or stop this trend?

Return detailed analysis for each trend.
"""

        try:
            response = await self.llm_service.generate(
                prompt=analysis_prompt,
                model="gpt-4o",
                temperature=0.3,
                max_tokens=2000
            )

            # Extract strength scores
            trend_scores = {}
            for trend in trends:
                trend_name = trend.get("name", "")
                # Try to extract score from response
                score_match = re.search(rf"{trend_name}.*?(\d+)/10", response, re.IGNORECASE)
                if score_match:
                    trend_scores[trend_name] = int(score_match.group(1))
                else:
                    trend_scores[trend_name] = 6  # Default medium strength

            return {
                "detailed_analysis": response,
                "trend_scores": trend_scores,
                "top_trends": sorted(
                    [(name, score) for name, score in trend_scores.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            }

        except Exception as e:
            print(f"Trend strength analysis failed: {e}")
            return {
                "detailed_analysis": "Analysis unavailable",
                "trend_scores": {t.get("name", ""): 6 for t in trends},
                "top_trends": []
            }

    async def _assess_lifecycle_stages(
        self,
        trends: List[Dict[str, Any]],
        analysis: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Assess lifecycle stage for each trend"""

        lifecycle_assessment = {}

        for trend in trends:
            trend_name = trend.get("name", "")
            status = trend.get("status", "emerging").lower()

            # Map status to lifecycle stage
            if "emerging" in status or "new" in status:
                stage = "emerging"
            elif "growth" in status or "rising" in status:
                stage = "growth"
            elif "mainstream" in status or "established" in status:
                stage = "mainstream"
            elif "mature" in status or "stable" in status:
                stage = "mature"
            elif "declining" in status or "fading" in status:
                stage = "declining"
            else:
                stage = "growth"  # Default

            lifecycle_assessment[trend_name] = {
                "stage": stage,
                "characteristics": self.lifecycle_stages[stage]["characteristics"],
                "risk_level": self.lifecycle_stages[stage]["risk"],
                "opportunity_level": self.lifecycle_stages[stage]["opportunity"],
                "typical_duration": self.lifecycle_stages[stage]["duration"]
            }

        return lifecycle_assessment

    async def _generate_trend_forecasts(
        self,
        trends: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        lifecycle: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate predictive forecasts for trends"""

        forecast_prompt = f"""Generate forecasts for these trends over the next 1-3 years:

Trends:
{json.dumps(trends[:5], indent=2)}

Analysis:
{json.dumps(analysis.get('top_trends', []), indent=2)}

For each trend, forecast:
1. **12-Month Outlook**: What will happen in the next year?
2. **36-Month Outlook**: Long-term trajectory
3. **Adoption Forecast**: Expected adoption % in 1yr and 3yr
4. **Market Impact**: Expected market size/impact
5. **Tipping Points**: Key milestones or events to watch for
6. **Probability**: Likelihood this forecast materializes (%)

Provide specific, actionable forecasts.
"""

        try:
            response = await self.llm_service.generate(
                prompt=forecast_prompt,
                model="gpt-4o",
                temperature=0.35,
                max_tokens=1500
            )

            return {
                "detailed_forecasts": response,
                "summary": "Forecasts generated for top 5 trends",
                "confidence": 0.75,
                "methodology": "LLM-based trend extrapolation with lifecycle analysis"
            }

        except Exception as e:
            print(f"Forecast generation failed: {e}")
            return {
                "detailed_forecasts": "Forecast generation unavailable",
                "summary": "Unable to generate detailed forecasts",
                "confidence": 0.5
            }

    async def _identify_opportunities_and_risks(
        self,
        trends: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        forecasts: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Identify business opportunities and risks from trends"""

        opportunities_risks_prompt = f"""Based on these trends, identify opportunities and risks:

Trends:
{json.dumps(trends[:5], indent=2)}

Business Context:
{json.dumps(context or {}, indent=2)}

Identify:
**Opportunities (5-7):**
- Opportunity description
- Trend(s) it's based on
- Market potential (Low/Medium/High)
- Time to market
- Required capabilities

**Risks (3-5):**
- Risk description
- Trend(s) causing risk
- Severity (Low/Medium/High)
- Timeline
- Mitigation strategies

Provide actionable insights for business strategy.
"""

        try:
            response = await self.llm_service.generate(
                prompt=opportunities_risks_prompt,
                model="gpt-4o",
                temperature=0.4,
                max_tokens=1200
            )

            # Parse opportunities and risks
            opportunities = self._extract_section(response, "opportunities")
            risks = self._extract_section(response, "risks")

            return {
                "opportunities": opportunities,
                "risks": risks,
                "detailed_analysis": response
            }

        except Exception as e:
            print(f"Opportunities/risks identification failed: {e}")
            return {
                "opportunities": ["Unable to identify opportunities"],
                "risks": ["Unable to identify risks"],
                "detailed_analysis": str(e)
            }

    def _extract_section(self, text: str, section: str) -> List[str]:
        """Extract opportunities or risks section from text"""
        items = []
        in_section = False

        for line in text.split("\n"):
            line = line.strip()

            if section.lower() in line.lower():
                in_section = True
                continue

            if in_section:
                if line.startswith(("*", "-", "1.", "2.", "3.", "4.", "5.", "6.", "7.")):
                    items.append(line.lstrip("*-0123456789. "))
                elif line.startswith("**") and section not in line.lower():
                    break

        return items[:7]

    async def _generate_trends_response(
        self,
        query: str,
        classification: Dict[str, Any],
        trends: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        lifecycle: Dict[str, Dict[str, Any]],
        forecasts: Dict[str, Any],
        opportunities_risks: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate comprehensive trends analysis response"""

        synthesis_prompt = f"""Create a comprehensive trends analysis report:

User Query: "{query}"

Classification:
- Category: {classification.get('primary_category')}
- Time Horizon: {classification.get('time_horizon')}

Identified Trends (Top 5):
{json.dumps([t.get('name', '') for t in trends[:5]], indent=2)}

Trend Strength:
{json.dumps(analysis.get('top_trends', [])[:5], indent=2)}

Forecasts:
{forecasts.get('detailed_forecasts', '')[:500]}

Opportunities:
{json.dumps(opportunities_risks.get('opportunities', [])[:3], indent=2)}

Risks:
{json.dumps(opportunities_risks.get('risks', [])[:3], indent=2)}

Create a well-structured response with:
1. **Executive Summary** - Key trends and takeaways
2. **Trend Analysis** - Detailed breakdown of top 3-5 trends
3. **Lifecycle Assessment** - Where each trend stands
4. **Strength & Momentum** - Which trends are accelerating
5. **Forecasts** - What to expect in 1-3 years
6. **Strategic Implications** - Opportunities and risks
7. **Action Items** - What to do now

Use clear, data-driven language with specific insights.
"""

        try:
            response = await self.llm_service.generate(
                prompt=synthesis_prompt,
                model="gpt-4o",
                temperature=0.3,
                max_tokens=2000
            )
            return response

        except Exception as e:
            print(f"Response generation failed: {e}")
            return self._generate_fallback_trends_response(query, trends, analysis, opportunities_risks)

    def _generate_fallback_trends_response(
        self,
        query: str,
        trends: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        opportunities_risks: Dict[str, Any]
    ) -> str:
        """Fallback response when LLM is unavailable"""

        response = f"""# Trends Analysis Report

## Executive Summary
Based on analysis of current market signals, we've identified {len(trends)} significant trends relevant to your query.

## Top Trends Identified

"""

        for i, (trend_name, score) in enumerate(analysis.get('top_trends', [])[:5], 1):
            response += f"### {i}. {trend_name} (Strength: {score}/10)\n"
            # Find full trend details
            trend_details = next((t for t in trends if t.get('name') == trend_name), {})
            response += f"{trend_details.get('description', 'No description available')}\n\n"

        response += "## Strategic Opportunities\n"
        for opp in opportunities_risks.get('opportunities', [])[:3]:
            response += f"- {opp}\n"

        response += "\n## Key Risks to Monitor\n"
        for risk in opportunities_risks.get('risks', [])[:3]:
            response += f"- {risk}\n"

        response += """
## Recommended Actions
1. **Monitor** these trends closely through industry reports and news
2. **Experiment** with pilot projects in high-opportunity areas
3. **Assess** your current capabilities against trend requirements
4. **Build** partnerships with trend leaders
5. **Prepare** for potential disruption from emerging trends

*For more detailed analysis, specific forecasts, or strategic planning support, please provide additional context about your business and objectives.*
"""

        return response

    def _generate_fallback_response(self, query: str, error: str) -> Dict[str, Any]:
        """Generate fallback response when processing fails"""
        return {
            "answer": f"""# Trends Analysis

I encountered an issue processing your trends query, but here's general guidance:

## General Trend Analysis Approach

**Key Trend Categories to Monitor:**
1. **Technology Trends**: AI/ML, blockchain, quantum computing, clean tech
2. **Consumer Trends**: Sustainability, digital-first, health & wellness, experiences
3. **Business Model Trends**: Subscription, platform, D2C, circular economy
4. **Market Trends**: Industry consolidation, geographic shifts, new segments
5. **Economic Trends**: Inflation, interest rates, employment, trade
6. **Workforce Trends**: Remote work, gig economy, skills gap, automation

**Trend Analysis Framework:**
1. **Identify**: Scan multiple sources (news, reports, data)
2. **Validate**: Distinguish signal from noise
3. **Assess**: Evaluate strength, momentum, lifecycle stage
4. **Forecast**: Project 1-3 year trajectory
5. **Act**: Determine opportunities and risks

**Resources for Trend Research:**
- Industry analyst reports (Gartner, Forrester, McKinsey)
- Academic research and patents
- VC funding patterns
- Social media and search trends
- Expert interviews and conferences

For more specific trend analysis, please provide:
- Industry or sector of interest
- Time horizon (short/medium/long-term)
- Specific trends you're tracking
- Your business context

*Error details: {error}*
""",
            "confidence": 0.4,
            "agent": self.agent_name,
            "error": error
        }


# Standalone testing
async def main():
    """Test the Trends Analysis Agent"""
    agent = TrendsAnalysisAgent()

    # Test 1: Technology trends
    print("\n" + "="*80)
    print("TEST 1: Technology Trends 2025")
    print("="*80)
    result1 = await agent.process(
        "What are the top technology trends for 2025 that will impact business?",
        context={"industry": "Technology", "focus": "B2B_SaaS"}
    )
    print(f"Trends Identified: {len(result1.get('identified_trends', []))}")
    print(f"Answer:\n{result1['answer'][:800]}...\n")

    # Test 2: Consumer behavior trends
    print("\n" + "="*80)
    print("TEST 2: Consumer Behavior Trends")
    print("="*80)
    result2 = await agent.process(
        "What consumer behavior trends should retail businesses watch in 2025?",
        context={"industry": "Retail", "market": "USA"}
    )
    print(f"Answer:\n{result2['answer'][:800]}...\n")

    # Test 3: Remote work trend
    print("\n" + "="*80)
    print("TEST 3: Remote Work Trend Forecast")
    print("="*80)
    result3 = await agent.process(
        "Will the remote work trend continue, reverse, or evolve? Forecast for next 3 years.",
        context={"industry": "Technology"}
    )
    print(f"Answer:\n{result3['answer'][:800]}...\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
