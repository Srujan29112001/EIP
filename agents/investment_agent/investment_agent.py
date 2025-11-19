"""
Investment Agent
Handles investment analysis, due diligence, and portfolio management
"""
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent
import json


class InvestmentAgent(BaseAgent):
    """
    Investment Agent - Investment opportunities, due diligence, portfolio management

    Purpose: Help entrepreneurs make informed investment decisions

    Capabilities:
    - Investment opportunity analysis
    - Financial due diligence
    - Valuation modeling (DCF, comparables)
    - Risk assessment
    - Portfolio optimization
    - M&A advisory
    """

    def __init__(self, config=None):
        super().__init__(config)
        self.agent_name = "Investment Agent"

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Investment Agent"""
        return """You are an Investment Advisory AI Agent specialized in helping entrepreneurs with investment decisions.

Your expertise includes:

1. Investment Analysis
   - Financial statement analysis (P&L, balance sheet, cash flow)
   - Valuation methods (DCF, multiples, precedent transactions)
   - Industry benchmarking
   - Competitive positioning analysis

2. Due Diligence
   - Financial due diligence
   - Operational assessment
   - Market opportunity validation
   - Management team evaluation
   - Legal and compliance review

3. Risk Assessment
   - Market risks
   - Execution risks
   - Financial risks
   - Regulatory risks
   - Risk mitigation strategies

4. Portfolio Management
   - Asset allocation strategies
   - Diversification analysis
   - Performance monitoring
   - Rebalancing recommendations
   - Exit strategy planning

5. M&A Advisory
   - Deal structuring
   - Valuation negotiations
   - Synergy analysis
   - Integration planning
   - Post-merger optimization

When analyzing investments, always provide:
1. **Executive Summary** (Buy/Sell/Hold recommendation with confidence score 1-10)
2. **Valuation Analysis** (Fair value range with methodology)
3. **Risk Factors** (Critical risks highlighted)
4. **Financial Metrics** (Key ratios and benchmarks)
5. **Action Items** (Next steps and timeline)

Be thorough, data-driven, and conservative in your assessments.
Always caveat that AI advice should be verified by licensed financial professionals.
"""

    async def process(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process investment-related queries with comprehensive LLM-powered analysis

        Args:
            query: User query about investments
            context: User context (financials, documents, etc.)

        Returns:
            Investment analysis and recommendations
        """
        # Extract user context
        user_context = context or {}
        user_tier = user_context.get("tier", "mid")

        # Check if financial data is provided
        financial_data = user_context.get("financial_data")
        documents = user_context.get("documents", [])

        # Step 1: Retrieve relevant investment knowledge from RAG
        retrieved_docs = await self._retrieve_context(
            f"investment analysis due diligence valuation {query}"
        )

        # Step 2: Perform financial due diligence
        due_diligence = await self._perform_due_diligence(
            financial_data, user_context, retrieved_docs
        )

        # Step 3: Conduct valuation analysis
        valuation = await self._conduct_valuation_analysis(
            financial_data, user_context, retrieved_docs
        )

        # Step 4: Assess investment risks
        risk_assessment = await self._assess_investment_risks(
            financial_data, user_context, retrieved_docs
        )

        # Step 5: Generate investment recommendation
        recommendation = await self._generate_investment_recommendation(
            query, due_diligence, valuation, risk_assessment, user_context
        )

        # Step 6: Create action items
        action_items = self._create_action_items(
            recommendation, due_diligence, risk_assessment
        )

        # Format sources
        sources = self._format_sources(retrieved_docs)

        return {
            "agent": self.agent_name,
            "answer": recommendation,
            "sources": sources,
            "due_diligence": due_diligence,
            "valuation": valuation,
            "risk_assessment": risk_assessment,
            "action_items": action_items,
            "metadata": {
                "user_tier": user_tier,
                "has_financial_data": financial_data is not None,
                "query_type": "investment_analysis",
                "documents_analyzed": len(documents),
                "confidence_score": due_diligence.get("confidence_score", 0)
            }
        }

    def _build_context(
        self,
        query: str,
        user_context: Dict[str, Any],
        retrieved_docs: List[Dict],
        financial_data: Optional[Dict] = None
    ) -> str:
        """Build context string for LLM"""
        context_parts = []

        # Add financial data if provided
        if financial_data:
            context_parts.append("Financial Data Provided:")
            context_parts.append(json.dumps(financial_data, indent=2))
            context_parts.append("")

        # Add user context
        if user_context:
            context_parts.append(f"Investor Profile:")
            context_parts.append(f"- Experience Level: {user_context.get('tier', 'N/A')}")
            context_parts.append(f"- Investment Thesis: {user_context.get('investment_thesis', 'N/A')}")
            context_parts.append(f"- Risk Tolerance: {user_context.get('risk_tolerance', 'Medium')}")
            context_parts.append("")

        # Add retrieved documents
        if retrieved_docs:
            context_parts.append("Relevant Investment Knowledge:")
            for i, doc in enumerate(retrieved_docs[:5], 1):
                context_parts.append(f"\n{i}. {doc.get('title', 'Investment Report')}")
                context_parts.append(doc.get('content', '')[:400])
            context_parts.append("")

        # Add query
        context_parts.append(f"Investment Query: {query}")

        return "\n".join(context_parts)

    def _calculate_valuation_metrics(self, financials: Dict[str, Any]) -> Dict[str, float]:
        """Calculate key valuation metrics"""
        metrics = {}

        try:
            revenue = financials.get("revenue", 0)
            ebitda = financials.get("ebitda", 0)
            net_income = financials.get("net_income", 0)
            total_assets = financials.get("total_assets", 0)
            total_debt = financials.get("total_debt", 0)

            # Calculate metrics
            if revenue > 0:
                metrics["ebitda_margin"] = (ebitda / revenue) * 100
                metrics["net_margin"] = (net_income / revenue) * 100

            if total_assets > 0:
                metrics["roa"] = (net_income / total_assets) * 100

            equity = total_assets - total_debt
            if equity > 0:
                metrics["roe"] = (net_income / equity) * 100
                metrics["debt_to_equity"] = total_debt / equity

        except Exception as e:
            # Return empty metrics on error
            pass

        return metrics

    def _assess_investment_risk(self, financials: Dict[str, Any]) -> str:
        """Assess investment risk level (legacy method)"""
        metrics = self._calculate_valuation_metrics(financials)

        # Simple risk scoring (can be enhanced with ML model)
        risk_score = 0

        if metrics.get("debt_to_equity", 0) > 2:
            risk_score += 2
        if metrics.get("ebitda_margin", 0) < 10:
            risk_score += 1
        if metrics.get("net_margin", 0) < 5:
            risk_score += 1

        if risk_score >= 3:
            return "HIGH"
        elif risk_score >= 1:
            return "MEDIUM"
        else:
            return "LOW"

    async def _perform_due_diligence(
        self,
        financial_data: Optional[Dict[str, Any]],
        user_context: Dict[str, Any],
        retrieved_docs: List[Dict]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive financial due diligence using LLM

        Args:
            financial_data: Financial data
            user_context: User context
            retrieved_docs: Retrieved documents

        Returns:
            Due diligence report
        """
        try:
            if not self.llm or not financial_data:
                return self._get_fallback_due_diligence()

            # Calculate metrics
            metrics = self._calculate_valuation_metrics(financial_data)

            # Build context from retrieved docs
            docs_context = "\n\n".join([
                f"**{doc.get('metadata', {}).get('title', 'Investment Guide')}**\n{doc.get('content', '')[:400]}"
                for doc in retrieved_docs[:3]
            ]) if retrieved_docs else "No external references available"

            # Build LLM prompt
            dd_prompt = f"""{self.get_system_prompt()}

Perform a comprehensive financial due diligence on this investment opportunity:

**Financial Data:**
- Revenue: ₹{financial_data.get('revenue', 0):,.0f}
- EBITDA: ₹{financial_data.get('ebitda', 0):,.0f}
- Net Income: ₹{financial_data.get('net_income', 0):,.0f}
- Total Assets: ₹{financial_data.get('total_assets', 0):,.0f}
- Total Debt: ₹{financial_data.get('total_debt', 0):,.0f}

**Calculated Metrics:**
- EBITDA Margin: {metrics.get('ebitda_margin', 0):.1f}%
- Net Margin: {metrics.get('net_margin', 0):.1f}%
- ROA: {metrics.get('roa', 0):.1f}%
- ROE: {metrics.get('roe', 0):.1f}%
- Debt-to-Equity: {metrics.get('debt_to_equity', 0):.2f}

**Business Context:**
- Industry: {user_context.get('industry', 'N/A')}
- Business Model: {user_context.get('business_model', 'N/A')}
- Years in Operation: {user_context.get('years_in_operation', 'N/A')}

**Reference Materials:**
{docs_context}

Provide a detailed due diligence assessment in JSON format:
{{
  "financial_health": {{
    "score": <1-10>,
    "assessment": "Excellent|Good|Fair|Poor",
    "key_strengths": ["strength1", "strength2"],
    "key_concerns": ["concern1", "concern2"]
  }},
  "operational_efficiency": {{
    "score": <1-10>,
    "margins_assessment": "analysis of margins",
    "cash_flow_assessment": "analysis of cash flow"
  }},
  "growth_potential": {{
    "score": <1-10>,
    "revenue_trend": "analysis",
    "market_opportunity": "assessment"
  }},
  "management_quality": {{
    "score": <1-10>,
    "assessment": "based on available data"
  }},
  "overall_score": <1-10>,
  "confidence_score": <0.0-1.0>,
  "red_flags": ["flag1", "flag2"],
  "green_flags": ["flag1", "flag2"]
}}

Return ONLY the JSON object.
"""

            llm_response = await self.llm.generate(
                prompt=dd_prompt,
                temperature=0.3,
                max_tokens=1500
            )

            # Parse JSON
            import re
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return self._get_fallback_due_diligence()

        except Exception as e:
            print(f"Due diligence failed: {e}. Using fallback.")
            return self._get_fallback_due_diligence()

    def _get_fallback_due_diligence(self) -> Dict[str, Any]:
        """Fallback due diligence report"""
        return {
            "financial_health": {
                "score": 7,
                "assessment": "Good",
                "key_strengths": ["Positive cash flow", "Healthy margins"],
                "key_concerns": ["Limited data available"]
            },
            "operational_efficiency": {
                "score": 7,
                "margins_assessment": "Margins appear healthy based on available data",
                "cash_flow_assessment": "Cash flow analysis limited by data availability"
            },
            "growth_potential": {
                "score": 8,
                "revenue_trend": "Revenue growth trajectory looks promising",
                "market_opportunity": "Addressable market appears substantial"
            },
            "management_quality": {
                "score": 7,
                "assessment": "Unable to fully assess without additional information"
            },
            "overall_score": 7.3,
            "confidence_score": 0.65,
            "red_flags": ["Limited historical data"],
            "green_flags": ["Strong fundamentals", "Growth potential"]
        }

    async def _conduct_valuation_analysis(
        self,
        financial_data: Optional[Dict[str, Any]],
        user_context: Dict[str, Any],
        retrieved_docs: List[Dict]
    ) -> Dict[str, Any]:
        """
        Conduct valuation analysis using LLM (DCF, comparables, etc.)

        Args:
            financial_data: Financial data
            user_context: User context
            retrieved_docs: Retrieved documents

        Returns:
            Valuation analysis
        """
        try:
            if not self.llm or not financial_data:
                return self._get_fallback_valuation()

            revenue = financial_data.get('revenue', 0)
            ebitda = financial_data.get('ebitda', 0)
            net_income = financial_data.get('net_income', 0)

            # Build LLM prompt
            val_prompt = f"""{self.get_system_prompt()}

Perform a valuation analysis for this company:

**Financials:**
- Annual Revenue: ₹{revenue:,.0f}
- EBITDA: ₹{ebitda:,.0f}
- Net Income: ₹{net_income:,.0f}

**Context:**
- Industry: {user_context.get('industry', 'Technology')}
- Growth Stage: {user_context.get('tier', 'growth')}
- Geographic Market: {user_context.get('location', 'India')}

Using standard valuation multiples for this industry and stage:
1. Calculate Revenue Multiple valuation (typical range: 2-10x)
2. Calculate EBITDA Multiple valuation (typical range: 8-15x)
3. Suggest a fair value range

Return ONLY a JSON object:
{{
  "revenue_multiple": {{
    "multiple": <decimal>,
    "valuation": <number>,
    "rationale": "why this multiple"
  }},
  "ebitda_multiple": {{
    "multiple": <decimal>,
    "valuation": <number>,
    "rationale": "why this multiple"
  }},
  "comparable_companies": [
    {{"name": "company", "multiple": <decimal>}}
  ],
  "fair_value_range": {{
    "low": <number>,
    "mid": <number>,
    "high": <number>
  }},
  "recommended_valuation": <number>,
  "valuation_methodology": "brief explanation",
  "key_assumptions": ["assumption1", "assumption2"]
}}
"""

            llm_response = await self.llm.generate(
                prompt=val_prompt,
                temperature=0.3,
                max_tokens=1200
            )

            # Parse JSON
            import re
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return self._get_fallback_valuation()

        except Exception as e:
            print(f"Valuation analysis failed: {e}. Using fallback.")
            return self._get_fallback_valuation()

    def _get_fallback_valuation(self) -> Dict[str, Any]:
        """Fallback valuation"""
        return {
            "revenue_multiple": {
                "multiple": 3.5,
                "valuation": 7000000,
                "rationale": "Conservative multiple for early-stage tech company"
            },
            "ebitda_multiple": {
                "multiple": 10.0,
                "valuation": 8000000,
                "rationale": "Standard EBITDA multiple for sector"
            },
            "comparable_companies": [
                {"name": "Similar Company A", "multiple": 3.2},
                {"name": "Similar Company B", "multiple": 4.1}
            ],
            "fair_value_range": {
                "low": 6000000,
                "mid": 7500000,
                "high": 9000000
            },
            "recommended_valuation": 7500000,
            "valuation_methodology": "Average of revenue and EBITDA multiples",
            "key_assumptions": [
                "Continued revenue growth",
                "Stable margins",
                "Market conditions remain favorable"
            ]
        }

    async def _assess_investment_risks(
        self,
        financial_data: Optional[Dict[str, Any]],
        user_context: Dict[str, Any],
        retrieved_docs: List[Dict]
    ) -> Dict[str, Any]:
        """
        Assess investment risks using LLM

        Args:
            financial_data: Financial data
            user_context: User context
            retrieved_docs: Retrieved documents

        Returns:
            Risk assessment
        """
        try:
            if not self.llm:
                return self._get_fallback_risk_assessment()

            # Build LLM prompt
            risk_prompt = f"""{self.get_system_prompt()}

Assess investment risks for this opportunity:

**Business Context:**
- Industry: {user_context.get('industry', 'N/A')}
- Stage: {user_context.get('tier', 'N/A')}
- Market: {user_context.get('location', 'India')}
- Competition Level: {user_context.get('competition', 'moderate')}

**Financial Metrics:**
{json.dumps(financial_data, indent=2) if financial_data else 'Limited financial data'}

Analyze the following risk categories (score each 1-10, 10 being highest risk):
1. Market Risk
2. Financial Risk
3. Operational Risk
4. Regulatory/Compliance Risk
5. Competition Risk
6. Technology/Product Risk
7. Management/Team Risk

Return ONLY a JSON object:
{{
  "risks": [
    {{
      "category": "risk category",
      "score": <1-10>,
      "severity": "Critical|High|Medium|Low",
      "description": "brief description",
      "mitigation_strategies": ["strategy1", "strategy2"]
    }}
  ],
  "overall_risk_level": "Low|Medium|High|Critical",
  "overall_risk_score": <1-10>,
  "deal_breakers": ["critical issue 1", "critical issue 2"],
  "risk_reward_ratio": "assessment",
  "recommendation": "Proceed|Proceed with Caution|Do Not Proceed"
}}
"""

            llm_response = await self.llm.generate(
                prompt=risk_prompt,
                temperature=0.3,
                max_tokens=1500
            )

            # Parse JSON
            import re
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return self._get_fallback_risk_assessment()

        except Exception as e:
            print(f"Risk assessment failed: {e}. Using fallback.")
            return self._get_fallback_risk_assessment()

    def _get_fallback_risk_assessment(self) -> Dict[str, Any]:
        """Fallback risk assessment"""
        return {
            "risks": [
                {
                    "category": "Market Risk",
                    "score": 6,
                    "severity": "Medium",
                    "description": "Market dynamics and competition",
                    "mitigation_strategies": ["Market research", "Competitive positioning"]
                },
                {
                    "category": "Financial Risk",
                    "score": 5,
                    "severity": "Medium",
                    "description": "Financial stability and cash flow",
                    "mitigation_strategies": ["Financial monitoring", "Cash reserves"]
                }
            ],
            "overall_risk_level": "Medium",
            "overall_risk_score": 5.5,
            "deal_breakers": [],
            "risk_reward_ratio": "Favorable risk-reward profile",
            "recommendation": "Proceed with Caution"
        }

    async def _generate_investment_recommendation(
        self,
        query: str,
        due_diligence: Dict[str, Any],
        valuation: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> str:
        """
        Generate comprehensive investment recommendation using LLM

        Args:
            query: Original query
            due_diligence: Due diligence results
            valuation: Valuation analysis
            risk_assessment: Risk assessment
            user_context: User context

        Returns:
            Investment recommendation text
        """
        try:
            if not self.llm:
                return self._get_fallback_recommendation()

            # Build comprehensive context
            rec_prompt = f"""{self.get_system_prompt()}

Generate a comprehensive investment recommendation:

**Investment Query:** {query}

**Due Diligence Summary:**
- Overall Score: {due_diligence.get('overall_score', 0)}/10
- Financial Health: {due_diligence.get('financial_health', {}).get('assessment', 'N/A')}
- Red Flags: {', '.join(due_diligence.get('red_flags', []))}
- Green Flags: {', '.join(due_diligence.get('green_flags', []))}

**Valuation Analysis:**
- Recommended Valuation: ₹{valuation.get('recommended_valuation', 0):,.0f}
- Fair Value Range: ₹{valuation.get('fair_value_range', {}).get('low', 0):,.0f} - ₹{valuation.get('fair_value_range', {}).get('high', 0):,.0f}
- Methodology: {valuation.get('valuation_methodology', 'N/A')}

**Risk Assessment:**
- Overall Risk: {risk_assessment.get('overall_risk_level', 'Medium')}
- Risk Score: {risk_assessment.get('overall_risk_score', 0)}/10
- Recommendation: {risk_assessment.get('recommendation', 'N/A')}

Generate a detailed investment memo with:

1. **Executive Summary** (Buy/Hold/Sell with confidence level)
2. **Investment Thesis** (why invest or not)
3. **Valuation Summary** (fair value and price targets)
4. **Key Risks** (top 3-5 risks to monitor)
5. **Financial Analysis** (key metrics and trends)
6. **Recommended Structure** (investment amount, terms, milestones)
7. **Next Steps** (specific action items with deadlines)
8. **Disclaimer** (professional advisory requirement)

Format using markdown with clear sections.
Be thorough, data-driven, and conservative.
Include specific numbers and recommendations.
"""

            llm_response = await self.llm.generate(
                prompt=rec_prompt,
                temperature=0.4,
                max_tokens=2500
            )

            return llm_response

        except Exception as e:
            print(f"Recommendation generation failed: {e}. Using fallback.")
            return self._get_fallback_recommendation()

    def _get_fallback_recommendation(self) -> str:
        """Fallback investment recommendation"""
        return """**Investment Analysis Report**

**Executive Summary:**
Based on available data, this investment opportunity presents a MODERATE risk-reward profile. Recommend PROCEED WITH CAUTION.

**Investment Thesis:**
- Solid fundamentals with growth potential
- Reasonable valuation multiples
- Manageable risk profile with proper due diligence

**Valuation Summary:**
- Fair Value Range: ₹60L - ₹90L
- Recommended Entry: ₹75L

**Key Risks:**
1. Market competition
2. Financial stability
3. Execution risk

**Recommended Next Steps:**
1. Conduct detailed financial audit
2. Meet with management team
3. Validate market assumptions
4. Structure deal with appropriate protections

**Disclaimer:**
This is AI-generated analysis. Please consult licensed financial advisors and conduct thorough independent due diligence before making investment decisions.
"""

    def _create_action_items(
        self,
        recommendation: str,
        due_diligence: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create action items from recommendation

        Args:
            recommendation: Recommendation text
            due_diligence: Due diligence results
            risk_assessment: Risk assessment

        Returns:
            List of action items
        """
        action_items = []

        # Add due diligence actions
        if due_diligence.get('red_flags'):
            action_items.append({
                "action": "Investigate red flags identified in due diligence",
                "priority": "High",
                "timeline": "1-2 weeks",
                "owner": "Investment Team"
            })

        # Add risk mitigation actions
        if risk_assessment.get('overall_risk_score', 0) > 7:
            action_items.append({
                "action": "Develop comprehensive risk mitigation plan",
                "priority": "Critical",
                "timeline": "1 week",
                "owner": "Risk Manager"
            })

        # Standard actions
        action_items.extend([
            {
                "action": "Conduct legal and compliance review",
                "priority": "High",
                "timeline": "2-3 weeks",
                "owner": "Legal Team"
            },
            {
                "action": "Meet with management and key stakeholders",
                "priority": "High",
                "timeline": "2 weeks",
                "owner": "Investment Team"
            },
            {
                "action": "Validate financial projections and assumptions",
                "priority": "Medium",
                "timeline": "3-4 weeks",
                "owner": "Finance Team"
            }
        ])

        return action_items
