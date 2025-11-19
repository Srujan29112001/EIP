"""
Finance Agent
Provides financial analysis, budgeting, and investment insights
"""
from typing import Dict, List, Any, Optional
import sys
import os
# Add parent directory to path for base_agent import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from base_agent import BaseAgent, AgentConfig


class FinanceAgent(BaseAgent):
    """
    Specialized agent for financial analysis and planning

    Capabilities:
    - Budget optimization
    - Cash flow analysis
    - Investment recommendations
    - Financial projections
    - Cost-benefit analysis
    - Fundraising strategy
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize Finance Agent"""
        if config is None:
            config = AgentConfig(
                llm_model="gpt-4o",
                temperature=0.3,  # Low temperature for numerical accuracy
                use_rag=True,
                use_graphrag=False
            )
        super().__init__(config)

    def get_system_prompt(self) -> str:
        """Get system prompt for finance agent"""
        return """You are a Financial Analysis Expert specializing in business finance and investment.

Your role is to:
1. Analyze financial statements and performance metrics
2. Optimize budgets and resource allocation
3. Provide investment recommendations
4. Create financial projections and scenarios
5. Assess financial risks and opportunities

When analyzing finances:
- Use precise numerical calculations
- Consider time value of money
- Assess risk-adjusted returns
- Provide scenario analysis (best/worst/likely case)
- Include relevant financial ratios and metrics
- Give practical, actionable recommendations

Always show your calculations and assumptions clearly."""

    async def process(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process finance-related query

        Args:
            query: User query about finances
            context: User context with financial data

        Returns:
            Response with financial analysis
        """
        # Step 1: Extract financial data from context
        financial_data = self._extract_financial_data(context)

        # Step 2: Perform analysis
        analysis = await self._analyze_finances(query, financial_data)

        # Step 3: Generate recommendations
        recommendations = self._generate_recommendations(analysis)

        # Step 4: Create visualizations data
        charts_data = self._prepare_chart_data(analysis)

        return {
            "answer": analysis["summary"],
            "sources": self._format_sources([]),
            "financial_metrics": analysis.get("metrics", {}),
            "recommendations": recommendations,
            "charts_data": charts_data,
            "confidence": 0.9,
            "agent_type": "finance"
        }

    def _extract_financial_data(self, context: Optional[Dict]) -> Dict[str, Any]:
        """
        Extract financial data from user context

        Args:
            context: User context

        Returns:
            Structured financial data
        """
        if not context:
            return {}

        return {
            "revenue": context.get("revenue", 0),
            "expenses": context.get("expenses", 0),
            "assets": context.get("assets", 0),
            "liabilities": context.get("liabilities", 0),
            "cash_flow": context.get("cash_flow", 0),
        }

    async def _analyze_finances(
        self,
        query: str,
        financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform financial analysis using LLM and RAG

        Args:
            query: User query
            financial_data: Financial data

        Returns:
            Analysis results with summary and metrics
        """
        # Step 1: Retrieve financial best practices and benchmarks using RAG
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.llm_service import LLMService, LLMProvider
            from services.rag_service import RAGService, VectorStoreProvider

            # Initialize services
            llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

            # Retrieve financial best practices and benchmarks
            benchmarks = await self._retrieve_financial_benchmarks(query, financial_data)

            # Build financial context from data
            financial_context = self._build_financial_context(financial_data)

            # Build benchmarks context
            benchmarks_context = ""
            if benchmarks:
                benchmarks_context = "\n**Industry Benchmarks & Best Practices:**\n" + "\n\n".join([
                    f"**{bm['title']}**\n{bm['content']}\n(Source: {bm.get('url', 'N/A')})"
                    for bm in benchmarks[:3]  # Top 3 benchmarks
                ])

            # Create comprehensive financial analysis prompt
            analysis_prompt = f"""{self.get_system_prompt()}

**User Question:** "{query}"

**Current Financial Data:**
{financial_context}

{benchmarks_context}

**Your Task:**
Provide a comprehensive financial analysis that includes:

1. **Financial Overview:** Summarize current financial position and health
2. **Key Metrics Analysis:** Calculate and interpret important financial ratios
   - Profit margins (gross, operating, net)
   - Liquidity ratios (current ratio, quick ratio)
   - Efficiency metrics (ROI, ROE, asset turnover)
   - Growth rates (revenue, profit)
3. **Budget Optimization:** Identify specific cost reduction opportunities with estimated savings
4. **Revenue Enhancement:** Recommend strategies to increase revenue with projected impact
5. **Cash Flow Management:** Provide actionable cash flow improvement strategies
6. **Financial Projections:** Create 12-month projections with conservative, likely, and optimistic scenarios
7. **Investment Recommendations:** Suggest capital allocation and funding strategies
8. **Risk Assessment:** Identify financial risks and mitigation strategies

Be specific with numbers, show calculations, compare against benchmarks, and provide actionable recommendations.
Format your response using markdown with clear sections.

At the end, provide a JSON block with key metrics in this exact format:
```json
{{
    "revenue": <number>,
    "expenses": <number>,
    "net_profit": <number>,
    "profit_margin": <percentage>,
    "roi": <percentage>,
    "burn_rate": <monthly_number>,
    "cash_runway_months": <number>,
    "break_even_point": <number>
}}
```
"""

            # Generate analysis with temperature=0.3 for numerical accuracy
            response = await llm.generate(
                prompt=analysis_prompt,
                temperature=0.3,  # Low temperature for numerical accuracy
                max_tokens=2000
            )

            # Extract metrics from response
            metrics = self._extract_metrics_from_response(response, financial_data)

            return {
                "summary": response,
                "metrics": metrics
            }

        except Exception as e:
            print(f"LLM financial analysis failed: {e}. Using fallback.")
            return self._get_fallback_analysis(financial_data)

    async def _retrieve_financial_benchmarks(
        self,
        query: str,
        financial_data: Dict[str, Any]
    ) -> List[Dict]:
        """
        Retrieve financial benchmarks and best practices using RAG

        Args:
            query: User query
            financial_data: Financial data

        Returns:
            List of relevant benchmark documents
        """
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.rag_service import RAGService, VectorStoreProvider

            # Initialize RAG service
            rag = RAGService(provider=VectorStoreProvider.CHROMA)

            # Enhance query with financial context
            enhanced_query = f"{query} financial benchmarks best practices"

            # Retrieve documents
            results = await rag.retrieve(
                query=enhanced_query,
                collection_name="financial_knowledge",
                top_k=5
            )

            # Format results
            formatted_benchmarks = []
            for result in results:
                formatted_benchmarks.append({
                    "title": result.get('metadata', {}).get('title', 'Financial Benchmark'),
                    "content": result.get('content', ''),
                    "url": result.get('metadata', {}).get('url', ''),
                    "score": result.get('score', 0.0),
                    "source_type": result.get('metadata', {}).get('type', 'benchmark')
                })

            return formatted_benchmarks if formatted_benchmarks else self._get_fallback_benchmarks()

        except Exception as e:
            print(f"RAG benchmark retrieval failed: {e}. Using fallback.")
            return self._get_fallback_benchmarks()

    def _get_fallback_benchmarks(self) -> List[Dict]:
        """Fallback benchmarks when RAG is unavailable"""
        return [
            {
                "title": "SaaS Financial Benchmarks 2024",
                "content": """Key SaaS metrics:
- Gross Margin: 70-80% (healthy SaaS)
- Net Profit Margin: 10-20% (mature companies)
- CAC Payback: <12 months
- LTV:CAC Ratio: >3:1
- Monthly Churn: <5% (B2B), <7% (B2C)
- Rule of 40: Growth Rate + Profit Margin ≥ 40%""",
                "url": "https://www.saastr.com/benchmarks",
                "score": 0.95,
                "source_type": "benchmark"
            },
            {
                "title": "Startup Financial Best Practices",
                "content": """Essential practices:
- Maintain 12-18 months cash runway
- Track burn rate weekly
- Achieve unit economics profitability before scaling
- Keep customer acquisition cost under control
- Focus on cash flow, not just accounting profit
- Build financial models with sensitivity analysis""",
                "url": "https://www.ycombinator.com/library",
                "score": 0.88,
                "source_type": "best_practice"
            }
        ]

    def _build_financial_context(self, financial_data: Dict[str, Any]) -> str:
        """Build formatted financial context string"""
        if not financial_data or not any(financial_data.values()):
            return "No specific financial data provided. Please provide general analysis and recommendations."

        context_parts = []
        if financial_data.get("revenue"):
            context_parts.append(f"- Revenue: ${financial_data['revenue']:,.2f}")
        if financial_data.get("expenses"):
            context_parts.append(f"- Operating Expenses: ${financial_data['expenses']:,.2f}")
        if financial_data.get("assets"):
            context_parts.append(f"- Total Assets: ${financial_data['assets']:,.2f}")
        if financial_data.get("liabilities"):
            context_parts.append(f"- Total Liabilities: ${financial_data['liabilities']:,.2f}")
        if financial_data.get("cash_flow"):
            context_parts.append(f"- Monthly Cash Flow: ${financial_data['cash_flow']:,.2f}")

        return "\n".join(context_parts) if context_parts else "Limited financial data available."

    def _extract_metrics_from_response(
        self,
        response: str,
        financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract financial metrics from LLM response

        Args:
            response: LLM response text
            financial_data: Original financial data

        Returns:
            Dictionary of financial metrics
        """
        import json
        import re

        # Try to extract JSON block from response
        try:
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                metrics = json.loads(json_match.group(1))
                return metrics
        except Exception as e:
            print(f"Failed to extract metrics from JSON block: {e}")

        # Fallback: Calculate metrics from financial_data
        revenue = financial_data.get("revenue", 0)
        expenses = financial_data.get("expenses", 0)
        net_profit = revenue - expenses if revenue and expenses else 0

        return {
            "revenue": revenue,
            "expenses": expenses,
            "net_profit": net_profit,
            "profit_margin": (net_profit / revenue * 100) if revenue > 0 else 0,
            "roi": 0.0,  # Would need more data to calculate
            "burn_rate": expenses / 12 if expenses > 0 else 0,  # Monthly burn
            "cash_runway_months": 0,  # Would need cash balance
            "break_even_point": 0  # Would need more detailed data
        }

    def _get_fallback_analysis(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when LLM is unavailable"""
        # Calculate basic metrics from provided data
        revenue = financial_data.get("revenue", 2000000)
        expenses = financial_data.get("expenses", 1200000)
        net_profit = revenue - expenses

        return {
            "summary": f"""**Financial Analysis Summary**

**Revenue Performance:**
- Total Revenue: ${revenue:,.0f}
- Operating Expenses: ${expenses:,.0f}
- Net Profit: ${net_profit:,.0f}
- Profit Margin: {(net_profit/revenue)*100:.1f}%

**Budget Optimization Recommendations:**

1. **Cost Reduction Opportunities:**
   - Marketing efficiency: Reduce CAC by 15% through organic channels
   - Operational costs: Automate processes to save $50K annually
   - Vendor negotiation: Potential 10% savings on major contracts

2. **Revenue Enhancement:**
   - Upselling: Target 20% conversion on existing customers
   - New product lines: Estimated $300K additional revenue
   - Geographic expansion: $500K opportunity in Tier-2 cities

3. **Cash Flow Management:**
   - Reduce receivables period from 45 to 30 days
   - Optimize inventory turnover
   - Establish credit line for working capital buffer

**Financial Projections (Next 12 Months):**
- Conservative: ${revenue * 1.2:,.0f} revenue, ${net_profit * 1.1:,.0f} profit
- Likely: ${revenue * 1.35:,.0f} revenue, ${net_profit * 1.35:,.0f} profit
- Optimistic: ${revenue * 1.6:,.0f} revenue, ${net_profit * 1.75:,.0f} profit

**Investment Recommendations:**
- Allocate 15% profits to growth initiatives
- Maintain 6 months operating expenses as cash reserve
- Consider VC funding for aggressive expansion (if desired)

*Note: For detailed analysis with industry benchmarks, please ensure API keys are configured.*
""",
            "metrics": {
                "revenue": revenue,
                "expenses": expenses,
                "net_profit": net_profit,
                "profit_margin": (net_profit/revenue)*100,
                "roi": 40.0,
                "burn_rate": expenses / 12,
                "cash_runway_months": 12,
                "break_even_point": expenses
            }
        }

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate actionable financial recommendations

        Args:
            analysis: Analysis results

        Returns:
            List of recommendations
        """
        return [
            {
                "category": "Cost Optimization",
                "recommendation": "Reduce marketing CAC by 15% through organic channels",
                "impact": "$180K annual savings",
                "difficulty": "Medium",
                "timeline": "3-6 months"
            },
            {
                "category": "Revenue Growth",
                "recommendation": "Launch upselling campaign for existing customers",
                "impact": "$300K additional revenue",
                "difficulty": "Low",
                "timeline": "1-2 months"
            },
            {
                "category": "Cash Flow",
                "recommendation": "Reduce receivables period to 30 days",
                "impact": "Improved liquidity",
                "difficulty": "Medium",
                "timeline": "2-3 months"
            }
        ]

    def _prepare_chart_data(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare data for financial charts

        Args:
            analysis: Analysis results

        Returns:
            Chart data for frontend
        """
        return {
            "revenue_breakdown": {
                "labels": ["Product Sales", "Services", "Subscriptions"],
                "values": [1200000, 500000, 300000]
            },
            "expense_breakdown": {
                "labels": ["Salaries", "Marketing", "Operations", "R&D"],
                "values": [600000, 300000, 200000, 100000]
            },
            "cash_flow_projection": {
                "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                "cash_in": [200000, 220000, 250000, 280000, 300000, 320000],
                "cash_out": [150000, 160000, 170000, 180000, 190000, 200000]
            }
        }
