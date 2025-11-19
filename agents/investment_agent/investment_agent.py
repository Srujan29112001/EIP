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
        Process investment-related queries

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

        # Retrieve relevant investment knowledge
        retrieved_docs = await self._retrieve_context(query)

        # Build comprehensive context
        context_str = self._build_context(query, user_context, retrieved_docs, financial_data)

        # Generate analysis using LLM
        response = await self._generate_response(query, context_str)

        # Format sources
        sources = self._format_sources(retrieved_docs)

        return {
            "agent": self.agent_name,
            "answer": response,
            "sources": sources,
            "metadata": {
                "user_tier": user_tier,
                "has_financial_data": financial_data is not None,
                "query_type": "investment_analysis",
                "documents_analyzed": len(documents)
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
        """Assess investment risk level"""
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
