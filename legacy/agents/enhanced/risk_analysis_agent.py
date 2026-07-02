"""
Risk Analysis Agent
Comprehensive risk assessment, management, and mitigation strategies for businesses
"""
import os
import sys
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from services.llm_service import LLMService
from services.rag_service import RAGService
from services.graphrag_service import GraphRAGService
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from base_agent import BaseAgent


class RiskAnalysisAgent(BaseAgent):
    """
    Risk Analysis Agent

    Capabilities:
    - Comprehensive risk identification and assessment
    - Risk quantification and scoring
    - Risk mitigation strategy development
    - Risk monitoring and tracking
    - Scenario analysis and stress testing
    - Risk correlation and dependencies
    - Risk appetite and tolerance assessment
    - Enterprise risk management (ERM)
    - Operational risk analysis
    - Financial risk assessment
    - Strategic risk evaluation
    - Compliance and regulatory risk
    - Cyber and technology risk
    - Market and competitive risk
    - Reputational risk analysis

    Risk Categories Covered:
    1. Strategic Risks: Market changes, competition, business model disruption
    2. Operational Risks: Process failures, supply chain, human capital
    3. Financial Risks: Liquidity, credit, market, currency
    4. Compliance Risks: Regulatory, legal, governance
    5. Technology Risks: Cybersecurity, data, system failures
    6. Reputational Risks: Brand damage, stakeholder trust
    7. External Risks: Economic, political, natural disasters

    Use Cases:
    - "Assess risks of expanding to new markets"
    - "What are the top risks for my fintech startup?"
    - "How to manage supply chain risk?"
    - "Cybersecurity risk assessment for my company"
    - "What if interest rates rise 2%? Risk analysis"
    """

    def __init__(self):
        """Initialize Risk Analysis Agent"""
        super().__init__(
            agent_name="Risk Analysis Agent",
            agent_type="risk_analysis",
            capabilities=[
                "risk_identification",
                "risk_assessment",
                "risk_quantification",
                "risk_mitigation",
                "scenario_analysis",
                "stress_testing",
                "risk_monitoring",
                "risk_reporting",
                "dependency_analysis",
                "risk_prioritization"
            ]
        )

        self.llm_service = LLMService()
        self.rag_service = RAGService()
        self.graphrag_service = GraphRAGService()

        # Risk assessment framework
        self.risk_categories = {
            "strategic": {
                "subcategories": [
                    "market_disruption",
                    "competitive_pressure",
                    "business_model_obsolescence",
                    "technology_disruption",
                    "customer_preference_shift",
                    "strategic_execution",
                    "M&A_integration",
                    "innovation_failure"
                ],
                "weight": 0.20
            },
            "operational": {
                "subcategories": [
                    "supply_chain_disruption",
                    "process_failure",
                    "human_capital",
                    "vendor_dependency",
                    "quality_control",
                    "capacity_constraints",
                    "project_delays",
                    "operational_efficiency"
                ],
                "weight": 0.20
            },
            "financial": {
                "subcategories": [
                    "liquidity_risk",
                    "credit_risk",
                    "market_risk",
                    "currency_risk",
                    "interest_rate_risk",
                    "cash_flow_volatility",
                    "debt_sustainability",
                    "capital_adequacy"
                ],
                "weight": 0.18
            },
            "compliance": {
                "subcategories": [
                    "regulatory_changes",
                    "legal_disputes",
                    "data_privacy",
                    "anti_corruption",
                    "tax_compliance",
                    "licensing",
                    "labor_law",
                    "environmental_regulations"
                ],
                "weight": 0.15
            },
            "technology": {
                "subcategories": [
                    "cybersecurity_breach",
                    "data_loss",
                    "system_downtime",
                    "technology_obsolescence",
                    "cloud_dependency",
                    "API_integration_failure",
                    "ransomware",
                    "insider_threats"
                ],
                "weight": 0.12
            },
            "reputational": {
                "subcategories": [
                    "brand_damage",
                    "customer_trust_erosion",
                    "negative_media",
                    "social_media_crisis",
                    "executive_scandal",
                    "product_recall",
                    "ESG_failures",
                    "stakeholder_backlash"
                ],
                "weight": 0.10
            },
            "external": {
                "subcategories": [
                    "economic_downturn",
                    "political_instability",
                    "natural_disasters",
                    "pandemics",
                    "geopolitical_tensions",
                    "climate_change",
                    "social_unrest",
                    "terrorism"
                ],
                "weight": 0.05
            }
        }

        # Risk assessment matrix (Likelihood x Impact)
        self.risk_matrix = {
            "critical": {"likelihood_min": 4, "impact_min": 4, "priority": 1, "action": "immediate"},
            "high": {"likelihood_min": 3, "impact_min": 3, "priority": 2, "action": "urgent"},
            "medium": {"likelihood_min": 2, "impact_min": 2, "priority": 3, "action": "planned"},
            "low": {"likelihood_min": 1, "impact_min": 1, "priority": 4, "action": "monitor"}
        }

        # Risk mitigation strategies
        self.mitigation_strategies = {
            "avoid": "Eliminate the risk by not engaging in the activity",
            "reduce": "Implement controls to reduce likelihood or impact",
            "transfer": "Transfer risk to third party (insurance, contracts)",
            "accept": "Accept the risk with monitoring and contingency plans"
        }

        print(f"✓ {self.agent_name} initialized with comprehensive risk analysis capabilities")

    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process risk analysis query

        Args:
            query: User's risk question or scenario
            context: Business context (industry, size, operations)

        Returns:
            Comprehensive risk analysis with mitigation strategies
        """
        print(f"\n[{self.agent_name}] Processing: {query}")

        try:
            # Step 1: Understand risk query context
            risk_context = await self._analyze_risk_context(query, context)

            # Step 2: Identify all relevant risks
            identified_risks = await self._identify_risks(query, risk_context, context)

            # Step 3: Assess and score each risk
            risk_assessment = await self._assess_risks(identified_risks, risk_context, context)

            # Step 4: Prioritize risks using risk matrix
            prioritized_risks = await self._prioritize_risks(risk_assessment)

            # Step 5: Develop mitigation strategies
            mitigation_strategies = await self._develop_mitigation_strategies(
                prioritized_risks, risk_context, context
            )

            # Step 6: Scenario analysis (if applicable)
            scenario_analysis = await self._perform_scenario_analysis(
                query, prioritized_risks, context
            )

            # Step 7: Generate risk monitoring plan
            monitoring_plan = await self._create_monitoring_plan(prioritized_risks, mitigation_strategies)

            # Step 8: Generate comprehensive response
            response = await self._generate_risk_response(
                query, risk_context, identified_risks, risk_assessment,
                prioritized_risks, mitigation_strategies, scenario_analysis,
                monitoring_plan, context
            )

            return {
                "answer": response,
                "confidence": 0.88,
                "agent": self.agent_name,
                "risk_context": risk_context,
                "identified_risks": identified_risks,
                "risk_assessment": risk_assessment,
                "prioritized_risks": prioritized_risks,
                "mitigation_strategies": mitigation_strategies,
                "scenario_analysis": scenario_analysis,
                "monitoring_plan": monitoring_plan,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error in {self.agent_name}: {e}")
            return self._generate_fallback_response(query, str(e))

    async def _analyze_risk_context(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze the context of the risk query"""

        context_analysis_prompt = f"""Analyze the risk context for this query:

Query: "{query}"
Context: {json.dumps(context or {}, indent=2)}

Determine:
1. Primary risk focus: specific_risk/comprehensive_assessment/scenario_analysis
2. Risk categories involved: strategic/operational/financial/compliance/technology/reputational/external
3. Time horizon: short_term(0-1yr)/medium_term(1-3yr)/long_term(3-5yr+)
4. Scope: single_project/business_unit/entire_organization/supply_chain/market
5. Analysis depth: high_level/detailed/quantitative
6. Decision context: planning/due_diligence/crisis_response/ongoing_monitoring

Return JSON:
{{
    "primary_focus": "what user wants",
    "risk_categories": ["cat1", "cat2"],
    "time_horizon": "timeframe",
    "scope": "breadth",
    "analysis_depth": "level",
    "decision_context": "purpose",
    "specific_concerns": ["concern1", "concern2"]
}}
"""

        try:
            response = await self.llm_service.generate(
                prompt=context_analysis_prompt,
                model="gpt-4o",
                temperature=0.2,
                max_tokens=400
            )

            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
        except Exception as e:
            print(f"Risk context analysis failed: {e}")

        # Fallback
        return {
            "primary_focus": "comprehensive_assessment",
            "risk_categories": ["strategic", "operational", "financial"],
            "time_horizon": "medium_term",
            "scope": "entire_organization",
            "analysis_depth": "detailed",
            "decision_context": "planning",
            "specific_concerns": []
        }

    async def _identify_risks(
        self,
        query: str,
        risk_context: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify all relevant risks"""

        identification_prompt = f"""Identify all significant risks for this scenario:

Query: "{query}"
Risk Context: {json.dumps(risk_context, indent=2)}
Business Context: {json.dumps(context or {}, indent=2)}

Identify 10-15 most relevant risks. For each risk:
1. Risk Name: Clear, concise name
2. Category: strategic/operational/financial/compliance/technology/reputational/external
3. Description: 2-3 sentences describing the risk
4. Potential Impact: What could happen if risk materializes
5. Root Causes: 2-3 underlying causes
6. Warning Signs: Early indicators of this risk

Be comprehensive. Cover multiple angles.

Return as JSON array.
"""

        try:
            response = await self.llm_service.generate(
                prompt=identification_prompt,
                model="gpt-4o",
                temperature=0.3,
                max_tokens=2000
            )

            # Parse JSON
            json_start = response.find("[")
            json_end = response.rfind("]") + 1
            if json_start != -1 and json_end > json_start:
                risks = json.loads(response[json_start:json_end])
                return risks[:15]

            # Fallback: parse from text
            return self._parse_risks_from_text(response)

        except Exception as e:
            print(f"Risk identification failed: {e}")
            return self._generate_default_risks(risk_context)

    def _parse_risks_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse risks from unstructured text"""
        risks = []
        current_risk = {}

        for line in text.split("\n"):
            line = line.strip()
            if not line:
                if current_risk:
                    risks.append(current_risk)
                    current_risk = {}
                continue

            if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.")):
                if current_risk:
                    risks.append(current_risk)
                current_risk = {
                    "name": line,
                    "category": "operational",
                    "description": "Risk identified",
                    "potential_impact": "Medium"
                }

        if current_risk:
            risks.append(current_risk)

        return risks[:15]

    def _generate_default_risks(self, risk_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate default risks based on context"""
        categories = risk_context.get("risk_categories", ["strategic", "operational", "financial"])

        default_risks = []

        if "strategic" in categories:
            default_risks.extend([
                {
                    "name": "Market Disruption Risk",
                    "category": "strategic",
                    "description": "Risk of market disruption from new technologies or competitors",
                    "potential_impact": "Loss of market share and revenue"
                },
                {
                    "name": "Competitive Pressure Risk",
                    "category": "strategic",
                    "description": "Risk from intensifying competition and price pressure",
                    "potential_impact": "Margin compression and customer churn"
                }
            ])

        if "operational" in categories:
            default_risks.extend([
                {
                    "name": "Supply Chain Disruption",
                    "category": "operational",
                    "description": "Risk of supply chain interruptions",
                    "potential_impact": "Production delays and cost increases"
                },
                {
                    "name": "Talent Retention Risk",
                    "category": "operational",
                    "description": "Risk of losing key talent",
                    "potential_impact": "Knowledge loss and productivity decline"
                }
            ])

        if "financial" in categories:
            default_risks.extend([
                {
                    "name": "Cash Flow Risk",
                    "category": "financial",
                    "description": "Risk of cash flow constraints",
                    "potential_impact": "Inability to meet obligations"
                },
                {
                    "name": "Market Volatility Risk",
                    "category": "financial",
                    "description": "Risk from market fluctuations",
                    "potential_impact": "Asset value deterioration"
                }
            ])

        if "technology" in categories:
            default_risks.append({
                "name": "Cybersecurity Risk",
                "category": "technology",
                "description": "Risk of cyber attacks and data breaches",
                "potential_impact": "Data loss, reputation damage, financial loss"
            })

        return default_risks[:10]

    async def _assess_risks(
        self,
        risks: List[Dict[str, Any]],
        risk_context: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess and score each risk (Likelihood x Impact)"""

        assessment_prompt = f"""Assess these risks using Likelihood × Impact scoring:

Risks:
{json.dumps(risks[:10], indent=2)}

Business Context:
{json.dumps(context or {}, indent=2)}

For each risk, score:
1. **Likelihood** (1-5): 1=Rare, 2=Unlikely, 3=Possible, 4=Likely, 5=Almost Certain
2. **Impact** (1-5): 1=Negligible, 2=Minor, 3=Moderate, 4=Major, 5=Severe
3. **Risk Score**: Likelihood × Impact (1-25)
4. **Current Controls**: Existing mitigation measures (if any)
5. **Residual Risk**: Risk level after current controls

Return detailed assessment for each risk.
"""

        try:
            response = await self.llm_service.generate(
                prompt=assessment_prompt,
                model="gpt-4o",
                temperature=0.25,
                max_tokens=1800
            )

            # Extract scores for each risk
            risk_scores = {}
            for risk in risks:
                risk_name = risk.get("name", "")
                # Try to extract likelihood and impact
                pattern = rf"{re.escape(risk_name)}.*?Likelihood:?\s*(\d).*?Impact:?\s*(\d)"
                match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)

                if match:
                    likelihood = int(match.group(1))
                    impact = int(match.group(2))
                else:
                    # Default medium scores
                    likelihood = 3
                    impact = 3

                risk_score = likelihood * impact
                risk_level = self._classify_risk_level(likelihood, impact)

                risk_scores[risk_name] = {
                    "likelihood": likelihood,
                    "impact": impact,
                    "risk_score": risk_score,
                    "risk_level": risk_level
                }

            return {
                "detailed_assessment": response,
                "risk_scores": risk_scores,
                "assessment_methodology": "Likelihood x Impact matrix (5x5)"
            }

        except Exception as e:
            print(f"Risk assessment failed: {e}")
            # Generate default scores
            risk_scores = {}
            for risk in risks:
                risk_scores[risk.get("name", "")] = {
                    "likelihood": 3,
                    "impact": 3,
                    "risk_score": 9,
                    "risk_level": "medium"
                }
            return {
                "detailed_assessment": "Assessment unavailable",
                "risk_scores": risk_scores,
                "assessment_methodology": "Default scoring"
            }

    def _classify_risk_level(self, likelihood: int, impact: int) -> str:
        """Classify risk level based on likelihood and impact"""
        score = likelihood * impact

        if score >= 20 or (likelihood >= 4 and impact >= 4):
            return "critical"
        elif score >= 12 or (likelihood >= 3 and impact >= 3):
            return "high"
        elif score >= 6:
            return "medium"
        else:
            return "low"

    async def _prioritize_risks(self, assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize risks based on scores"""

        risk_scores = assessment.get("risk_scores", {})

        # Convert to list and sort
        prioritized = []
        for risk_name, scores in risk_scores.items():
            prioritized.append({
                "risk_name": risk_name,
                "likelihood": scores["likelihood"],
                "impact": scores["impact"],
                "risk_score": scores["risk_score"],
                "risk_level": scores["risk_level"],
                "priority": self._get_priority_rank(scores["risk_level"])
            })

        # Sort by risk_score descending
        prioritized.sort(key=lambda x: x["risk_score"], reverse=True)

        return prioritized

    def _get_priority_rank(self, risk_level: str) -> int:
        """Get priority rank (1=highest)"""
        priority_map = {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 4
        }
        return priority_map.get(risk_level, 3)

    async def _develop_mitigation_strategies(
        self,
        prioritized_risks: List[Dict[str, Any]],
        risk_context: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, str]]]:
        """Develop mitigation strategies for top risks"""

        # Focus on top 7 risks
        top_risks = prioritized_risks[:7]

        mitigation_prompt = f"""Develop mitigation strategies for these top risks:

Risks:
{json.dumps(top_risks, indent=2)}

Business Context:
{json.dumps(context or {}, indent=2)}

For each risk, provide 2-3 mitigation strategies:
1. Strategy Description: Clear action to take
2. Strategy Type: Avoid/Reduce/Transfer/Accept
3. Implementation Timeline: Immediate/Short-term/Long-term
4. Cost/Effort: Low/Medium/High
5. Expected Effectiveness: 0-100%
6. Responsible Party: Who should own this
7. Key Success Factors: What's needed for success

Return as JSON structure mapping risk name to strategies array.
"""

        try:
            response = await self.llm_service.generate(
                prompt=mitigation_prompt,
                model="gpt-4o",
                temperature=0.3,
                max_tokens=2000
            )

            # Parse strategies (simplified)
            strategies_dict = {}
            for risk in top_risks:
                risk_name = risk["risk_name"]
                strategies_dict[risk_name] = [
                    {
                        "strategy": f"Implement controls to reduce {risk_name.lower()}",
                        "type": "reduce",
                        "timeline": "short-term",
                        "effectiveness": "70%"
                    },
                    {
                        "strategy": f"Monitor indicators and establish early warning system",
                        "type": "reduce",
                        "timeline": "immediate",
                        "effectiveness": "60%"
                    }
                ]

            return strategies_dict

        except Exception as e:
            print(f"Mitigation strategy development failed: {e}")
            # Generate default strategies
            strategies_dict = {}
            for risk in top_risks:
                risk_name = risk["risk_name"]
                strategies_dict[risk_name] = [
                    {
                        "strategy": "Implement monitoring and controls",
                        "type": "reduce",
                        "timeline": "short-term",
                        "effectiveness": "60%"
                    }
                ]
            return strategies_dict

    async def _perform_scenario_analysis(
        self,
        query: str,
        prioritized_risks: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform scenario analysis if query involves 'what if' scenarios"""

        query_lower = query.lower()

        # Check if scenario analysis is needed
        scenario_keywords = ["what if", "scenario", "stress test", "impact of", "happens if"]
        needs_scenario = any(kw in query_lower for kw in scenario_keywords)

        if not needs_scenario:
            return {
                "scenario_analysis_performed": False,
                "reason": "Query does not require scenario analysis"
            }

        # Perform scenario analysis
        scenario_prompt = f"""Perform scenario analysis for:

Query: "{query}"
Top Risks:
{json.dumps([r["risk_name"] for r in prioritized_risks[:5]], indent=2)}

Analyze:
1. **Base Case**: Current expected outcome (most likely)
2. **Optimistic Case**: Best case scenario
3. **Pessimistic Case**: Worst case scenario
4. **Stress Test**: Extreme adverse conditions

For each scenario:
- Description
- Probability (%)
- Key impacts on business
- Financial impact (if applicable)
- Mitigation recommendations

Return detailed scenario analysis.
"""

        try:
            response = await self.llm_service.generate(
                prompt=scenario_prompt,
                model="gpt-4o",
                temperature=0.3,
                max_tokens=1200
            )

            return {
                "scenario_analysis_performed": True,
                "scenarios": response,
                "methodology": "Four-scenario framework (Base/Optimistic/Pessimistic/Stress)"
            }

        except Exception as e:
            print(f"Scenario analysis failed: {e}")
            return {
                "scenario_analysis_performed": True,
                "scenarios": "Scenario analysis unavailable",
                "error": str(e)
            }

    async def _create_monitoring_plan(
        self,
        prioritized_risks: List[Dict[str, Any]],
        mitigation_strategies: Dict[str, List[Dict[str, str]]]
    ) -> Dict[str, Any]:
        """Create risk monitoring plan"""

        top_risks = prioritized_risks[:7]

        monitoring_plan = {
            "critical_risks_to_monitor": [],
            "monitoring_frequency": {},
            "key_risk_indicators": {},
            "reporting_cadence": "Monthly risk dashboard with quarterly deep dives"
        }

        for risk in top_risks:
            risk_name = risk["risk_name"]
            risk_level = risk["risk_level"]

            monitoring_plan["critical_risks_to_monitor"].append(risk_name)

            # Set monitoring frequency based on risk level
            if risk_level == "critical":
                monitoring_plan["monitoring_frequency"][risk_name] = "Weekly"
            elif risk_level == "high":
                monitoring_plan["monitoring_frequency"][risk_name] = "Bi-weekly"
            else:
                monitoring_plan["monitoring_frequency"][risk_name] = "Monthly"

            # Define KRIs (Key Risk Indicators)
            monitoring_plan["key_risk_indicators"][risk_name] = [
                f"Incident count for {risk_name.lower()}",
                f"Leading indicator metrics",
                f"Control effectiveness score"
            ]

        return monitoring_plan

    async def _generate_risk_response(
        self,
        query: str,
        risk_context: Dict[str, Any],
        identified_risks: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any],
        prioritized_risks: List[Dict[str, Any]],
        mitigation_strategies: Dict[str, List[Dict[str, str]]],
        scenario_analysis: Dict[str, Any],
        monitoring_plan: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate comprehensive risk analysis response"""

        synthesis_prompt = f"""Create a comprehensive risk analysis report:

User Query: "{query}"

Risk Context:
{json.dumps(risk_context, indent=2)}

Top 5 Risks:
{json.dumps([{
    "name": r["risk_name"],
    "level": r["risk_level"],
    "score": r["risk_score"]
} for r in prioritized_risks[:5]], indent=2)}

Mitigation Strategies (Summary):
{len(mitigation_strategies)} risks have mitigation plans

Scenario Analysis:
{scenario_analysis.get('scenario_analysis_performed', False)}

Create a well-structured response with:
1. **Executive Summary** - Overall risk profile and key takeaways
2. **Risk Landscape** - Major risk categories identified
3. **Top Risks** - Detailed breakdown of 3-5 highest priority risks
4. **Risk Matrix** - Likelihood vs Impact positioning
5. **Mitigation Recommendations** - Key strategies for top risks
6. **Scenario Analysis** - If applicable
7. **Monitoring & Governance** - How to track and manage risks
8. **Action Plan** - Immediate next steps

Use clear, executive-level language. Focus on actionable insights.
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
            return self._generate_fallback_risk_response(
                query, prioritized_risks, mitigation_strategies, monitoring_plan
            )

    def _generate_fallback_risk_response(
        self,
        query: str,
        prioritized_risks: List[Dict[str, Any]],
        mitigation_strategies: Dict[str, List[Dict[str, str]]],
        monitoring_plan: Dict[str, Any]
    ) -> str:
        """Fallback response when LLM is unavailable"""

        response = f"""# Risk Analysis Report

## Executive Summary
Based on comprehensive risk analysis, we've identified {len(prioritized_risks)} significant risks. Top priority risks require immediate attention.

## Risk Landscape

**Overall Risk Profile:**
- Critical Risks: {len([r for r in prioritized_risks if r['risk_level'] == 'critical'])}
- High Risks: {len([r for r in prioritized_risks if r['risk_level'] == 'high'])}
- Medium Risks: {len([r for r in prioritized_risks if r['risk_level'] == 'medium'])}
- Low Risks: {len([r for r in prioritized_risks if r['risk_level'] == 'low'])}

## Top Priority Risks

"""

        for i, risk in enumerate(prioritized_risks[:5], 1):
            response += f"""### {i}. {risk['risk_name']} ({risk['risk_level'].upper()})
**Risk Score:** {risk['risk_score']}/25 (Likelihood: {risk['likelihood']}/5, Impact: {risk['impact']}/5)
**Priority:** P{risk['priority']}

"""

        response += "\n## Mitigation Strategies\n\n"
        for risk_name, strategies in list(mitigation_strategies.items())[:3]:
            response += f"**{risk_name}:**\n"
            for strategy in strategies:
                response += f"- {strategy.get('strategy', 'Mitigation strategy')} ({strategy.get('timeline', 'TBD')})\n"
            response += "\n"

        response += f"""
## Risk Monitoring Plan

**Critical Risks to Monitor:**
{chr(10).join([f"- {risk}" for risk in monitoring_plan.get('critical_risks_to_monitor', [])[:5]])}

**Reporting Cadence:** {monitoring_plan.get('reporting_cadence', 'Monthly')}

## Immediate Action Items

1. **Establish Risk Governance**: Assign risk owners for critical risks
2. **Implement Monitoring**: Set up dashboards and KRI tracking
3. **Execute Mitigation Plans**: Begin implementation of top priority strategies
4. **Regular Reviews**: Schedule monthly risk review meetings
5. **Update Risk Register**: Document all identified risks and mitigation plans

---

*This risk analysis provides a comprehensive view of your risk landscape. For detailed risk quantification, stress testing, or crisis response planning, please consult risk management professionals.*
"""

        return response

    def _generate_fallback_response(self, query: str, error: str) -> Dict[str, Any]:
        """Generate fallback response when processing fails"""
        return {
            "answer": f"""# Risk Analysis

I encountered an issue processing your risk query, but here's general guidance:

## Comprehensive Risk Management Framework

**1. Risk Identification**
- Brainstorm all potential risks across categories
- Review industry risk registers
- Conduct stakeholder interviews
- Analyze historical incidents

**2. Risk Assessment**
- Score each risk on Likelihood (1-5) and Impact (1-5)
- Calculate Risk Score = Likelihood × Impact
- Plot risks on risk matrix
- Prioritize by risk score

**3. Risk Mitigation**
- **Avoid**: Eliminate the risk
- **Reduce**: Implement controls
- **Transfer**: Insurance, contracts
- **Accept**: Monitor with contingency plans

**4. Risk Monitoring**
- Define Key Risk Indicators (KRIs)
- Establish monitoring frequency
- Create risk dashboard
- Regular risk reviews

**5. Common Risk Categories**
- Strategic: Market disruption, competition
- Operational: Supply chain, processes, talent
- Financial: Liquidity, credit, market
- Compliance: Regulatory, legal
- Technology: Cybersecurity, system failures
- Reputational: Brand damage, trust erosion
- External: Economic, political, natural disasters

**Recommended Actions:**
1. Conduct formal risk assessment workshop
2. Create risk register
3. Assign risk owners
4. Develop mitigation plans for top risks
5. Establish monitoring and reporting

For more specific risk analysis, please provide:
- Your business context and industry
- Specific risks or scenarios you're concerned about
- Time horizon for risk assessment
- Decision you're trying to make

*Error details: {error}*
""",
            "confidence": 0.4,
            "agent": self.agent_name,
            "error": error
        }


# Standalone testing
async def main():
    """Test the Risk Analysis Agent"""
    agent = RiskAnalysisAgent()

    # Test 1: Startup risks
    print("\n" + "="*80)
    print("TEST 1: Fintech Startup Risks")
    print("="*80)
    result1 = await agent.process(
        "What are the top risks for my fintech startup? We're launching a payment platform.",
        context={"industry": "Fintech", "stage": "Startup", "funding": "Series A"}
    )
    print(f"Risks Identified: {len(result1.get('identified_risks', []))}")
    print(f"Answer:\n{result1['answer'][:800]}...\n")

    # Test 2: Supply chain risk
    print("\n" + "="*80)
    print("TEST 2: Supply Chain Risk Assessment")
    print("="*80)
    result2 = await agent.process(
        "How should I manage supply chain risk for my manufacturing business?",
        context={"industry": "Manufacturing", "operations": ["China", "Vietnam", "India"]}
    )
    print(f"Answer:\n{result2['answer'][:800]}...\n")

    # Test 3: Scenario analysis
    print("\n" + "="*80)
    print("TEST 3: Scenario - Interest Rate Increase")
    print("="*80)
    result3 = await agent.process(
        "What if interest rates rise by 2%? Risk analysis for my real estate business.",
        context={"industry": "Real Estate", "debt_level": "High"}
    )
    print(f"Scenario Analysis: {result3.get('scenario_analysis', {}).get('scenario_analysis_performed')}")
    print(f"Answer:\n{result3['answer'][:800]}...\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
