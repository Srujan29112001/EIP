"""
Geopolitics Analysis Agent
Advanced geopolitical risk analysis, international relations, and strategic intelligence
"""
import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from services.llm_service import LLMService
from services.rag_service import RAGService
from services.graphrag_service import GraphRAGService
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from base_agent import BaseAgent


class GeopoliticsAgent(BaseAgent):
    """
    Geopolitics Analysis Agent

    Capabilities:
    - Geopolitical risk assessment for businesses
    - International relations analysis
    - Trade war and sanctions impact
    - Regional conflict analysis
    - Global power dynamics and alliances
    - Supply chain geopolitical risks
    - Sovereignty and territorial disputes
    - Energy and resource geopolitics
    - Technology and cyber geopolitics
    - Military and security considerations
    - Diplomatic relations tracking
    - Strategic forecasting

    Use Cases:
    - "How will US-China tensions affect my supply chain?"
    - "Geopolitical risks of expanding to Eastern Europe?"
    - "Impact of Middle East conflicts on oil prices?"
    - "How to navigate India-Pakistan tensions for business?"
    - "Brexit impact on my European operations?"
    """

    def __init__(self):
        """Initialize Geopolitics Analysis Agent"""
        super().__init__(
            agent_name="Geopolitics Analysis Agent",
            agent_type="geopolitics",
            capabilities=[
                "geopolitical_risk_assessment",
                "international_relations_analysis",
                "trade_policy_analysis",
                "sanctions_impact",
                "regional_conflict_analysis",
                "power_dynamics",
                "supply_chain_risk",
                "energy_geopolitics",
                "technology_geopolitics",
                "strategic_forecasting"
            ]
        )

        self.llm_service = LLMService()
        self.rag_service = RAGService()
        self.graphrag_service = GraphRAGService()

        # Geopolitical risk framework
        self.risk_categories = {
            "political_instability": {
                "factors": ["regime_change", "civil_unrest", "coup_risk", "protests", "elections"],
                "impact_areas": ["operations", "assets", "personnel"]
            },
            "trade_restrictions": {
                "factors": ["tariffs", "quotas", "embargoes", "sanctions", "trade_wars"],
                "impact_areas": ["supply_chain", "market_access", "costs"]
            },
            "military_conflict": {
                "factors": ["armed_conflict", "terrorism", "border_disputes", "proxy_wars"],
                "impact_areas": ["safety", "operations", "assets"]
            },
            "regulatory_changes": {
                "factors": ["nationalization", "local_content_requirements", "data_localization"],
                "impact_areas": ["compliance", "ownership", "operations"]
            },
            "diplomatic_relations": {
                "factors": ["bilateral_tensions", "alliance_shifts", "diplomatic_incidents"],
                "impact_areas": ["reputation", "partnerships", "market_access"]
            },
            "economic_sanctions": {
                "factors": ["financial_sanctions", "export_controls", "investment_restrictions"],
                "impact_areas": ["banking", "transactions", "partnerships"]
            },
            "resource_geopolitics": {
                "factors": ["energy_dependency", "critical_minerals", "water_scarcity"],
                "impact_areas": ["supply_chain", "costs", "sustainability"]
            },
            "technology_rivalry": {
                "factors": ["tech_decoupling", "cyber_attacks", "ip_theft", "tech_bans"],
                "impact_areas": ["technology_access", "cybersecurity", "innovation"]
            }
        }

        # Major geopolitical actors and their strategic priorities
        self.geopolitical_actors = {
            "USA": ["democracy_promotion", "free_trade", "tech_leadership", "military_dominance"],
            "China": ["belt_and_road", "tech_sovereignty", "regional_hegemony", "economic_growth"],
            "Russia": ["sphere_of_influence", "energy_leverage", "multipolarity", "security"],
            "EU": ["regulatory_power", "climate_leadership", "strategic_autonomy", "values"],
            "India": ["strategic_autonomy", "economic_growth", "regional_stability", "technology"],
            "Middle_East": ["energy_dominance", "regional_stability", "modernization"],
            "Africa": ["development", "resource_management", "regional_integration"],
            "ASEAN": ["economic_integration", "neutrality", "connectivity"],
            "Latin_America": ["sovereignty", "development", "regional_cooperation"]
        }

        # Key global flashpoints
        self.flashpoints = [
            "Taiwan_Strait", "Ukraine", "South_China_Sea", "Kashmir", "Middle_East",
            "Korean_Peninsula", "Arctic", "Cyber_Space", "Space", "Trade_Routes"
        ]

        print(f"✓ {self.agent_name} initialized with geopolitical intelligence capabilities")

    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process geopolitical analysis query

        Args:
            query: User's geopolitical question or scenario
            context: Business context (industry, regions, operations)

        Returns:
            Comprehensive geopolitical analysis with risk assessment
        """
        print(f"\n[{self.agent_name}] Processing: {query}")

        try:
            # Step 1: Extract entities and context
            entities = await self._extract_geopolitical_entities(query, context)

            # Step 2: Retrieve relevant geopolitical intelligence
            intelligence = await self._gather_geopolitical_intelligence(query, entities)

            # Step 3: Analyze geopolitical risks
            risk_analysis = await self._analyze_geopolitical_risks(query, entities, intelligence, context)

            # Step 4: Generate strategic recommendations
            recommendations = await self._generate_strategic_recommendations(query, risk_analysis, context)

            # Step 5: Create scenario forecasts
            scenarios = await self._create_scenario_forecasts(entities, risk_analysis)

            # Step 6: Generate comprehensive response
            response = await self._generate_geopolitical_response(
                query, entities, intelligence, risk_analysis, recommendations, scenarios, context
            )

            return {
                "answer": response,
                "confidence": 0.85,
                "agent": self.agent_name,
                "entities": entities,
                "risk_analysis": risk_analysis,
                "recommendations": recommendations,
                "scenarios": scenarios,
                "intelligence_sources": intelligence.get("sources", []),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error in {self.agent_name}: {e}")
            return self._generate_fallback_response(query, str(e))

    async def _extract_geopolitical_entities(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract countries, regions, actors, and geopolitical themes"""

        extraction_prompt = f"""Extract geopolitical entities from this query:

Query: "{query}"
Context: {json.dumps(context or {}, indent=2)}

Identify:
1. Countries/regions mentioned
2. Geopolitical actors (governments, alliances, organizations)
3. Geopolitical themes (trade, conflict, sanctions, etc.)
4. Business implications
5. Time horizon (short-term, medium-term, long-term)

Return JSON:
{{
    "countries": ["country1", "country2"],
    "regions": ["region1"],
    "actors": ["actor1", "actor2"],
    "themes": ["theme1", "theme2"],
    "business_context": "what business aspects are affected",
    "time_horizon": "short/medium/long-term",
    "urgency": "low/medium/high"
}}
"""

        try:
            response = await self.llm_service.generate(
                prompt=extraction_prompt,
                model="gpt-4o",
                temperature=0.2,
                max_tokens=500
            )

            # Parse JSON
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
        except Exception as e:
            print(f"Entity extraction failed: {e}")

        # Fallback extraction
        return {
            "countries": [],
            "regions": [],
            "actors": [],
            "themes": ["general_geopolitics"],
            "business_context": "not specified",
            "time_horizon": "medium-term",
            "urgency": "medium"
        }

    async def _gather_geopolitical_intelligence(
        self,
        query: str,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather intelligence from knowledge bases and news sources"""

        intelligence = {"sources": [], "insights": []}

        try:
            # RAG retrieval for geopolitical reports
            search_query = f"geopolitical analysis {' '.join(entities.get('countries', []))} {' '.join(entities.get('themes', []))}"
            rag_results = await self.rag_service.retrieve(
                query=search_query,
                collection_name="geopolitical_intelligence",
                top_k=5
            )

            if rag_results:
                intelligence["sources"].extend([r.get("source", "Unknown") for r in rag_results])
                intelligence["insights"].extend([r.get("content", "") for r in rag_results])
        except Exception as e:
            print(f"RAG retrieval failed: {e}")

        try:
            # GraphRAG for connected geopolitical events
            if entities.get("countries"):
                graph_query = f"""
                MATCH (c:Country)-[r:HAS_RELATION|TRADE_WITH|CONFLICT_WITH]-(other:Country)
                WHERE c.name IN {entities['countries']}
                RETURN c, r, other
                LIMIT 10
                """
                graph_results = await self.graphrag_service.execute_query(graph_query)
                if graph_results:
                    intelligence["graph_connections"] = graph_results
        except Exception as e:
            print(f"GraphRAG query failed: {e}")

        return intelligence

    async def _analyze_geopolitical_risks(
        self,
        query: str,
        entities: Dict[str, Any],
        intelligence: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Comprehensive geopolitical risk analysis"""

        risk_analysis_prompt = f"""Conduct comprehensive geopolitical risk analysis:

Query: "{query}"
Entities: {json.dumps(entities, indent=2)}
Intelligence: {json.dumps(intelligence.get('insights', [])[:3], indent=2)}
Business Context: {json.dumps(context or {}, indent=2)}

Analyze risks across these categories:
1. Political Instability Risk
2. Trade & Economic Restrictions
3. Military & Security Risks
4. Regulatory & Policy Changes
5. Diplomatic Relations Impact
6. Sanctions & Compliance Risks
7. Resource & Energy Geopolitics
8. Technology & Cyber Risks

For each risk category, provide:
- Risk Level (Low/Medium/High/Critical)
- Likelihood (1-10)
- Impact (1-10)
- Time Horizon
- Key Risk Factors
- Mitigation Strategies

Return detailed JSON structure.
"""

        try:
            response = await self.llm_service.generate(
                prompt=risk_analysis_prompt,
                model="gpt-4o",
                temperature=0.3,
                max_tokens=1500
            )

            # Extract risk scores
            risk_levels = {
                "political_instability": self._extract_risk_score(response, "political"),
                "trade_restrictions": self._extract_risk_score(response, "trade"),
                "military_conflict": self._extract_risk_score(response, "military"),
                "regulatory_changes": self._extract_risk_score(response, "regulatory"),
                "diplomatic_relations": self._extract_risk_score(response, "diplomatic"),
                "economic_sanctions": self._extract_risk_score(response, "sanctions"),
                "resource_geopolitics": self._extract_risk_score(response, "resource"),
                "technology_rivalry": self._extract_risk_score(response, "technology")
            }

            # Calculate overall risk score
            overall_risk = sum(risk_levels.values()) / len(risk_levels)

            return {
                "overall_risk_score": round(overall_risk, 2),
                "risk_level": self._classify_risk_level(overall_risk),
                "category_risks": risk_levels,
                "detailed_analysis": response,
                "priority_risks": sorted(
                    [(k, v) for k, v in risk_levels.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
            }

        except Exception as e:
            print(f"Risk analysis failed: {e}")
            return {
                "overall_risk_score": 5.0,
                "risk_level": "Medium",
                "category_risks": {},
                "detailed_analysis": "Risk analysis unavailable",
                "priority_risks": []
            }

    def _extract_risk_score(self, text: str, keyword: str) -> float:
        """Extract risk score from text (1-10 scale)"""
        text_lower = text.lower()

        # Check for explicit scores
        import re
        score_pattern = rf"{keyword}.*?(\d+)/10"
        match = re.search(score_pattern, text_lower)
        if match:
            return float(match.group(1))

        # Check for risk level keywords
        if "critical" in text_lower and keyword in text_lower:
            return 9.0
        elif "high" in text_lower and keyword in text_lower:
            return 7.5
        elif "medium" in text_lower and keyword in text_lower:
            return 5.0
        elif "low" in text_lower and keyword in text_lower:
            return 2.5

        return 5.0  # Default medium risk

    def _classify_risk_level(self, score: float) -> str:
        """Classify overall risk level"""
        if score >= 8.0:
            return "Critical"
        elif score >= 6.5:
            return "High"
        elif score >= 4.0:
            return "Medium"
        else:
            return "Low"

    async def _generate_strategic_recommendations(
        self,
        query: str,
        risk_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Generate strategic recommendations for risk mitigation"""

        recommendations_prompt = f"""Based on this geopolitical risk analysis, provide strategic recommendations:

Query: "{query}"
Risk Level: {risk_analysis.get('risk_level')}
Overall Score: {risk_analysis.get('overall_risk_score')}
Priority Risks: {json.dumps(risk_analysis.get('priority_risks', []), indent=2)}
Business Context: {json.dumps(context or {}, indent=2)}

Provide 5-7 actionable recommendations covering:
1. Risk Mitigation Strategies
2. Operational Adjustments
3. Supply Chain Diversification
4. Market Entry/Exit Strategies
5. Compliance & Legal Actions
6. Monitoring & Intelligence
7. Contingency Planning

For each recommendation:
- Action: Clear action item
- Priority: High/Medium/Low
- Timeline: Immediate/Short-term/Long-term
- Impact: Expected impact
- Resources: What's needed

Return as JSON array.
"""

        try:
            response = await self.llm_service.generate(
                prompt=recommendations_prompt,
                model="gpt-4o",
                temperature=0.4,
                max_tokens=1000
            )

            # Try to parse JSON
            json_start = response.find("[")
            json_end = response.rfind("]") + 1
            if json_start != -1 and json_end > json_start:
                recommendations = json.loads(response[json_start:json_end])
                return recommendations[:7]

            # Fallback: create structured recommendations from text
            return self._parse_recommendations_from_text(response)

        except Exception as e:
            print(f"Recommendations generation failed: {e}")
            return self._default_recommendations(risk_analysis)

    def _parse_recommendations_from_text(self, text: str) -> List[Dict[str, str]]:
        """Parse recommendations from unstructured text"""
        recommendations = []
        lines = text.split("\n")

        current_rec = {}
        for line in lines:
            line = line.strip()
            if not line:
                if current_rec:
                    recommendations.append(current_rec)
                    current_rec = {}
                continue

            if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "-")):
                if current_rec:
                    recommendations.append(current_rec)
                current_rec = {"action": line, "priority": "Medium", "timeline": "Short-term"}

        if current_rec:
            recommendations.append(current_rec)

        return recommendations[:7]

    def _default_recommendations(self, risk_analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Default recommendations based on risk level"""
        risk_level = risk_analysis.get("risk_level", "Medium")

        base_recommendations = [
            {
                "action": "Establish continuous geopolitical monitoring system",
                "priority": "High",
                "timeline": "Immediate",
                "impact": "Critical for early warning"
            },
            {
                "action": "Diversify supply chain to reduce single-country dependency",
                "priority": "High" if risk_level in ["High", "Critical"] else "Medium",
                "timeline": "Short-term",
                "impact": "Reduces operational risk"
            },
            {
                "action": "Develop contingency plans for worst-case scenarios",
                "priority": "High" if risk_level == "Critical" else "Medium",
                "timeline": "Immediate",
                "impact": "Business continuity"
            },
            {
                "action": "Engage government relations and local partners",
                "priority": "Medium",
                "timeline": "Short-term",
                "impact": "Improves local intelligence"
            },
            {
                "action": "Review and update compliance procedures for sanctions",
                "priority": "High",
                "timeline": "Immediate",
                "impact": "Legal protection"
            }
        ]

        return base_recommendations

    async def _create_scenario_forecasts(
        self,
        entities: Dict[str, Any],
        risk_analysis: Dict[str, Any]
    ) -> Dict[str, Dict[str, str]]:
        """Create best/worst/likely case scenarios"""

        scenarios = {
            "best_case": {
                "title": "Diplomatic De-escalation",
                "description": "Tensions ease, trade normalizes, stability returns",
                "probability": "30%",
                "business_impact": "Positive - operations normalize"
            },
            "likely_case": {
                "title": "Managed Tensions",
                "description": "Status quo continues with periodic flare-ups",
                "probability": "50%",
                "business_impact": "Neutral - requires active management"
            },
            "worst_case": {
                "title": "Escalation & Disruption",
                "description": "Significant escalation, major disruptions",
                "probability": "20%",
                "business_impact": "Negative - major operational challenges"
            }
        }

        return scenarios

    async def _generate_geopolitical_response(
        self,
        query: str,
        entities: Dict[str, Any],
        intelligence: Dict[str, Any],
        risk_analysis: Dict[str, Any],
        recommendations: List[Dict[str, str]],
        scenarios: Dict[str, Dict[str, str]],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate comprehensive geopolitical analysis response"""

        synthesis_prompt = f"""Create a comprehensive geopolitical analysis response:

User Query: "{query}"

Key Entities:
{json.dumps(entities, indent=2)}

Risk Analysis:
- Overall Risk: {risk_analysis.get('risk_level')} ({risk_analysis.get('overall_risk_score')}/10)
- Top Risks: {json.dumps([r[0] for r in risk_analysis.get('priority_risks', [])[:3]], indent=2)}

Intelligence:
{json.dumps(intelligence.get('insights', [])[:2], indent=2)}

Strategic Recommendations:
{json.dumps([r.get('action', '') for r in recommendations[:3]], indent=2)}

Scenarios:
- Best Case: {scenarios['best_case']['description']}
- Likely Case: {scenarios['likely_case']['description']}
- Worst Case: {scenarios['worst_case']['description']}

Create a well-structured response with:
1. **Executive Summary** - Key takeaway in 2-3 sentences
2. **Geopolitical Context** - Current situation and dynamics
3. **Risk Assessment** - Detailed risk breakdown
4. **Business Impact** - Specific impacts on operations/strategy
5. **Strategic Recommendations** - Top 3-5 actionable items
6. **Scenario Planning** - What to prepare for
7. **Monitoring Priorities** - What to watch

Use clear, professional language. Focus on actionable intelligence.
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
            return self._generate_fallback_geopolitical_response(query, risk_analysis, recommendations)

    def _generate_fallback_geopolitical_response(
        self,
        query: str,
        risk_analysis: Dict[str, Any],
        recommendations: List[Dict[str, str]]
    ) -> str:
        """Fallback response when LLM is unavailable"""

        response = f"""# Geopolitical Analysis

## Executive Summary
Based on current geopolitical analysis, the overall risk level is **{risk_analysis.get('risk_level', 'Medium')}** (Score: {risk_analysis.get('overall_risk_score', 5.0)}/10).

## Risk Assessment
Priority risks identified:
"""

        for risk_name, risk_score in risk_analysis.get('priority_risks', [])[:3]:
            response += f"- **{risk_name.replace('_', ' ').title()}**: {risk_score}/10\n"

        response += "\n## Strategic Recommendations\n"
        for i, rec in enumerate(recommendations[:5], 1):
            response += f"{i}. **{rec.get('action', 'No action')}** (Priority: {rec.get('priority', 'Medium')})\n"

        response += f"""
## Monitoring Priorities
- Track diplomatic developments and policy announcements
- Monitor trade and economic indicators
- Watch for security incidents and regional tensions
- Review supply chain vulnerabilities regularly

**Note:** This is a preliminary analysis. For detailed strategic planning, consider engaging geopolitical risk consultants.
"""

        return response

    def _generate_fallback_response(self, query: str, error: str) -> Dict[str, Any]:
        """Generate fallback response when processing fails"""
        return {
            "answer": f"""# Geopolitical Analysis

I encountered an issue processing your geopolitical query, but here's general guidance:

## General Geopolitical Considerations

**For Business Operations:**
1. **Risk Assessment**: Conduct regular geopolitical risk assessments
2. **Diversification**: Avoid over-dependence on single countries/regions
3. **Intelligence**: Establish monitoring of political and economic developments
4. **Compliance**: Ensure sanctions and export control compliance
5. **Contingency Planning**: Develop plans for various scenarios

**Key Risk Areas to Monitor:**
- Political stability in operating countries
- Trade policies and tariffs
- Sanctions regimes and compliance
- Regional conflicts and tensions
- Supply chain dependencies
- Currency and economic risks

**Recommended Actions:**
- Engage geopolitical risk consultants
- Monitor reputable intelligence sources
- Build relationships with local partners
- Review insurance and risk mitigation strategies

For more specific analysis, please provide details about:
- Specific countries/regions of interest
- Your business operations and industry
- Particular geopolitical concerns

*Error details: {error}*
""",
            "confidence": 0.4,
            "agent": self.agent_name,
            "error": error
        }


# Standalone testing
async def main():
    """Test the Geopolitics Analysis Agent"""
    agent = GeopoliticsAgent()

    # Test 1: US-China tensions
    print("\n" + "="*80)
    print("TEST 1: US-China Trade War Impact")
    print("="*80)
    result1 = await agent.process(
        "How will US-China trade tensions affect my manufacturing supply chain?",
        context={"industry": "Electronics", "operations": ["China", "Taiwan", "Vietnam"]}
    )
    print(f"Risk Level: {result1.get('risk_analysis', {}).get('risk_level')}")
    print(f"Answer:\n{result1['answer'][:800]}...\n")

    # Test 2: Middle East conflict
    print("\n" + "="*80)
    print("TEST 2: Middle East Stability")
    print("="*80)
    result2 = await agent.process(
        "What are the geopolitical risks of expanding operations to the Middle East?",
        context={"industry": "Energy", "expansion_target": "UAE"}
    )
    print(f"Answer:\n{result2['answer'][:800]}...\n")

    # Test 3: Russia-Ukraine impact
    print("\n" + "="*80)
    print("TEST 3: Russia-Ukraine Conflict")
    print("="*80)
    result3 = await agent.process(
        "How should I navigate the Russia-Ukraine situation for my European business?",
        context={"industry": "Technology", "operations": ["Germany", "Poland"]}
    )
    print(f"Answer:\n{result3['answer'][:800]}...\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
