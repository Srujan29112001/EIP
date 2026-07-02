"""
Distribution Agent
Handles customer acquisition and distribution strategy queries
"""
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent


class DistributionAgent(BaseAgent):
    """
    Distribution Agent - Customer acquisition & distribution strategy

    Purpose: Help entrepreneurs reach their target customers effectively

    Capabilities:
    - Multi-channel distribution strategies
    - Customer acquisition cost estimation
    - Partnership opportunities identification
    - Growth projections and scaling strategies
    """

    def __init__(self, config=None):
        super().__init__(config)
        self.agent_name = "Distribution Agent"

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Distribution Agent"""
        return """You are a Distribution Strategy Expert AI Agent for entrepreneurs.

Your expertise includes:
1. Customer Acquisition Strategies
   - B2B vs B2C distribution channels
   - Digital marketing (SEO, SEM, social media, content marketing)
   - Traditional channels (retail, partnerships, direct sales)
   - Marketplace strategies (Amazon, Shopify, etc.)

2. Channel Analysis
   - Cost-benefit analysis of different channels
   - ROI projections for each distribution method
   - Customer acquisition cost (CAC) optimization
   - Lifetime value (LTV) to CAC ratio analysis

3. Market Penetration
   - Geographic expansion strategies
   - Segment-specific targeting
   - Partnership and alliance opportunities
   - Referral and viral growth tactics

4. Execution Planning
   - Phased rollout strategies
   - Resource allocation across channels
   - Timeline and milestone setting
   - Performance metrics and KPIs

When responding:
- Provide specific, actionable distribution strategies
- Include cost estimates and ROI projections where possible
- Suggest a prioritized roadmap
- Reference successful case studies when relevant
- Consider the user's business stage and resources

Always structure your response with:
1. **Distribution Strategy Overview**
2. **Recommended Channels** (with priority ranking)
3. **Cost & ROI Analysis**
4. **Implementation Roadmap**
5. **Key Metrics to Track**
"""

    async def process(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process distribution-related queries with comprehensive LLM-powered analysis

        Args:
            query: User query about distribution/customer acquisition
            context: User context (business type, stage, budget, etc.)

        Returns:
            Distribution strategy and recommendations
        """
        # Extract user context
        user_context = context or {}
        business_type = user_context.get("business_type", "unknown")
        user_tier = user_context.get("tier", "aspiring")
        budget = user_context.get("marketing_budget", 0)

        # Step 1: Retrieve relevant distribution case studies from RAG
        retrieved_docs = await self._retrieve_context(
            f"distribution strategy customer acquisition {business_type} {query}"
        )

        # Step 2: Analyze channels and estimate CAC for each
        channel_analysis = await self._analyze_distribution_channels(
            query, user_context, retrieved_docs
        )

        # Step 3: Generate comprehensive distribution strategy
        strategy_text = await self._generate_distribution_strategy(
            query, user_context, channel_analysis, retrieved_docs
        )

        # Step 4: Create implementation roadmap
        roadmap = await self._create_implementation_roadmap(
            channel_analysis, user_context
        )

        # Step 5: Calculate projected ROI for recommended channels
        roi_projections = self._calculate_roi_projections(
            channel_analysis, budget
        )

        # Format sources
        sources = self._format_sources(retrieved_docs)

        return {
            "agent": self.agent_name,
            "answer": strategy_text,
            "sources": sources,
            "channel_analysis": channel_analysis,
            "implementation_roadmap": roadmap,
            "roi_projections": roi_projections,
            "metadata": {
                "business_type": business_type,
                "user_tier": user_tier,
                "query_type": "distribution_strategy",
                "channels_analyzed": len(channel_analysis.get("channels", []))
            }
        }

    def _build_context(
        self,
        query: str,
        user_context: Dict[str, Any],
        retrieved_docs: List[Dict]
    ) -> str:
        """Build context string for LLM"""
        context_parts = []

        # Add user context
        if user_context:
            context_parts.append(f"User Context:")
            context_parts.append(f"- Business Type: {user_context.get('business_type', 'N/A')}")
            context_parts.append(f"- Stage: {user_context.get('tier', 'N/A')}")
            context_parts.append(f"- Budget Range: {user_context.get('budget', 'N/A')}")
            context_parts.append("")

        # Add retrieved documents
        if retrieved_docs:
            context_parts.append("Relevant Distribution Strategies:")
            for i, doc in enumerate(retrieved_docs[:3], 1):
                context_parts.append(f"\n{i}. {doc.get('title', 'Case Study')}")
                context_parts.append(doc.get('content', '')[:500])
            context_parts.append("")

        # Add query
        context_parts.append(f"Query: {query}")

        return "\n".join(context_parts)

    def _get_distribution_templates(self) -> Dict[str, Any]:
        """Get distribution strategy templates"""
        return {
            "b2b_saas": {
                "primary_channels": ["Content Marketing", "LinkedIn Outreach", "Partnerships"],
                "cac_range": "$200-$1000",
                "timeline": "6-12 months to scale"
            },
            "b2c_ecommerce": {
                "primary_channels": ["Social Media Ads", "Influencer Marketing", "SEO"],
                "cac_range": "$20-$100",
                "timeline": "3-6 months to scale"
            },
            "marketplace": {
                "primary_channels": ["Amazon/Flipkart", "Own Website", "Social Commerce"],
                "cac_range": "$10-$50",
                "timeline": "2-4 months to scale"
            }
        }

    async def _analyze_distribution_channels(
        self,
        query: str,
        user_context: Dict[str, Any],
        retrieved_docs: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze distribution channels using LLM

        Args:
            query: User query
            user_context: User context
            retrieved_docs: Retrieved documents from RAG

        Returns:
            Channel analysis with CAC estimates and recommendations
        """
        try:
            if not self.llm:
                return self._get_fallback_channel_analysis()

            # Build context from retrieved documents
            docs_context = "\n\n".join([
                f"**{doc.get('metadata', {}).get('title', 'Case Study')}**\n{doc.get('content', '')[:400]}"
                for doc in retrieved_docs[:3]
            ]) if retrieved_docs else "No case studies available"

            # Build LLM prompt
            analysis_prompt = f"""{self.get_system_prompt()}

Analyze distribution channels for this business:

**Business Context:**
- Type: {user_context.get('business_type', 'N/A')}
- Industry: {user_context.get('industry', 'N/A')}
- Target Market: {user_context.get('target_market', 'B2C')}
- Stage: {user_context.get('tier', 'early-stage')}
- Monthly Budget: ₹{user_context.get('marketing_budget', 100000):,.0f}
- Current Customers: {user_context.get('current_customers', 0)}

**Query:** {query}

**Distribution Case Studies:**
{docs_context}

Analyze and recommend the top 5 distribution channels for this business.
For each channel, estimate:
1. Customer Acquisition Cost (CAC)
2. Expected conversion rate
3. Time to see results
4. Effort level (Low/Medium/High)
5. Scalability potential (1-10)

Return ONLY a JSON object:
{{
  "recommended_priority": "organic|paid|hybrid",
  "channels": [
    {{
      "name": "channel name",
      "type": "organic|paid|partnership",
      "cac_estimate": <number in INR>,
      "conversion_rate": <decimal, e.g., 0.02 for 2%>,
      "time_to_results": "X weeks/months",
      "effort": "Low|Medium|High",
      "scalability": <1-10>,
      "monthly_budget_needed": <number in INR>,
      "expected_monthly_customers": <number>,
      "pros": ["pro1", "pro2"],
      "cons": ["con1", "con2"],
      "priority": "High|Medium|Low"
    }}
  ],
  "rationale": "brief explanation of recommendations"
}}
"""

            llm_response = await self.llm.generate(
                prompt=analysis_prompt,
                temperature=0.4,
                max_tokens=2000
            )

            # Parse JSON response
            import json
            import re
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return self._get_fallback_channel_analysis()

        except Exception as e:
            print(f"Channel analysis failed: {e}. Using fallback.")
            return self._get_fallback_channel_analysis()

    def _get_fallback_channel_analysis(self) -> Dict[str, Any]:
        """Fallback channel analysis"""
        return {
            "recommended_priority": "hybrid",
            "channels": [
                {
                    "name": "Content Marketing & SEO",
                    "type": "organic",
                    "cac_estimate": 500,
                    "conversion_rate": 0.03,
                    "time_to_results": "3-6 months",
                    "effort": "High",
                    "scalability": 9,
                    "monthly_budget_needed": 30000,
                    "expected_monthly_customers": 60,
                    "pros": ["Long-term value", "Low ongoing cost", "Builds authority"],
                    "cons": ["Slow initial results", "Requires expertise"],
                    "priority": "High"
                },
                {
                    "name": "Social Media Ads",
                    "type": "paid",
                    "cac_estimate": 1500,
                    "conversion_rate": 0.02,
                    "time_to_results": "1-2 weeks",
                    "effort": "Medium",
                    "scalability": 8,
                    "monthly_budget_needed": 50000,
                    "expected_monthly_customers": 33,
                    "pros": ["Quick results", "Precise targeting", "Scalable"],
                    "cons": ["Ongoing cost", "Ad fatigue"],
                    "priority": "High"
                },
                {
                    "name": "Partnerships & Referrals",
                    "type": "partnership",
                    "cac_estimate": 800,
                    "conversion_rate": 0.08,
                    "time_to_results": "2-3 months",
                    "effort": "Medium",
                    "scalability": 7,
                    "monthly_budget_needed": 20000,
                    "expected_monthly_customers": 25,
                    "pros": ["High quality leads", "Cost-effective", "Trust transfer"],
                    "cons": ["Takes time to build", "Dependent on partners"],
                    "priority": "Medium"
                }
            ],
            "rationale": "Hybrid approach recommended - combine organic growth with paid acquisition"
        }

    async def _generate_distribution_strategy(
        self,
        query: str,
        user_context: Dict[str, Any],
        channel_analysis: Dict[str, Any],
        retrieved_docs: List[Dict]
    ) -> str:
        """
        Generate comprehensive distribution strategy using LLM

        Args:
            query: User query
            user_context: User context
            channel_analysis: Channel analysis results
            retrieved_docs: Retrieved documents

        Returns:
            Distribution strategy text
        """
        try:
            if not self.llm:
                return self._get_fallback_strategy()

            # Build channel summary
            import json
            channels_summary = json.dumps(channel_analysis, indent=2)

            # Build LLM prompt
            strategy_prompt = f"""{self.get_system_prompt()}

Create a comprehensive distribution strategy based on this analysis:

**Business Context:**
- Type: {user_context.get('business_type', 'N/A')}
- Industry: {user_context.get('industry', 'N/A')}
- Stage: {user_context.get('tier', 'early-stage')}
- Monthly Budget: ₹{user_context.get('marketing_budget', 100000):,.0f}

**User Query:** {query}

**Channel Analysis:**
```json
{channels_summary}
```

Generate a detailed distribution strategy with:

1. **Executive Summary** (3-4 sentences)
2. **Recommended Channel Mix** (prioritized list with allocation %)
3. **Month-by-Month Execution Plan** (first 6 months)
4. **Budget Allocation** across channels
5. **Expected Results** (customers acquired, CAC, ROI by month 6)
6. **Key Success Metrics** to track
7. **Risk Mitigation** strategies
8. **Optimization Tactics** for each channel

Format using clear markdown sections.
Be specific with numbers and percentages.
Make it actionable for an entrepreneur to implement immediately.
"""

            llm_response = await self.llm.generate(
                prompt=strategy_prompt,
                temperature=0.5,
                max_tokens=2500
            )

            return llm_response

        except Exception as e:
            print(f"Strategy generation failed: {e}. Using fallback.")
            return self._get_fallback_strategy()

    def _get_fallback_strategy(self) -> str:
        """Fallback distribution strategy"""
        return """**Distribution Strategy**

**Executive Summary:**
A hybrid distribution approach is recommended, combining organic content marketing with targeted paid advertising and strategic partnerships.

**Recommended Channel Mix:**
1. Content Marketing & SEO (40% effort) - Long-term foundation
2. Social Media Ads (35% budget) - Quick customer acquisition
3. Partnerships (25% effort) - High-quality leads

**Implementation Roadmap:**
- Month 1-2: Set up content creation, launch initial ad campaigns
- Month 3-4: Optimize campaigns, develop partnership outreach
- Month 5-6: Scale successful channels, test new tactics

**Budget Allocation:**
- Content Creation: 30%
- Paid Advertising: 50%
- Partnerships & Tools: 20%

**Expected Results:**
- Month 1-2: 20-30 customers
- Month 3-4: 40-60 customers
- Month 5-6: 80-120 customers
"""

    async def _create_implementation_roadmap(
        self,
        channel_analysis: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create implementation roadmap using LLM

        Args:
            channel_analysis: Channel analysis
            user_context: User context

        Returns:
            Implementation roadmap with tasks and milestones
        """
        try:
            if not self.llm:
                return self._get_fallback_roadmap()

            import json
            channels_json = json.dumps(channel_analysis.get("channels", [])[:3], indent=2)

            roadmap_prompt = f"""Create a 6-month implementation roadmap for these distribution channels:

**Channels:**
```json
{channels_json}
```

**Budget:** ₹{user_context.get('marketing_budget', 100000):,.0f}/month

Create a month-by-month roadmap with specific tasks.

Return ONLY a JSON array:
[
  {{
    "month": 1,
    "focus": "brief description",
    "tasks": [
      {{
        "task": "specific task",
        "channel": "channel name",
        "deadline": "week X",
        "effort": "X hours",
        "expected_outcome": "specific metric"
      }}
    ]
  }}
]
"""

            llm_response = await self.llm.generate(
                prompt=roadmap_prompt,
                temperature=0.3,
                max_tokens=1500
            )

            # Parse JSON
            import re
            json_match = re.search(r'\[.*\]', llm_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return self._get_fallback_roadmap()

        except Exception as e:
            print(f"Roadmap generation failed: {e}. Using fallback.")
            return self._get_fallback_roadmap()

    def _get_fallback_roadmap(self) -> List[Dict[str, Any]]:
        """Fallback implementation roadmap"""
        return [
            {
                "month": 1,
                "focus": "Foundation & Setup",
                "tasks": [
                    {
                        "task": "Set up content calendar and create first 10 blog posts",
                        "channel": "Content Marketing",
                        "deadline": "Week 4",
                        "effort": "40 hours",
                        "expected_outcome": "Content foundation for SEO"
                    },
                    {
                        "task": "Launch initial social media ad campaigns (3 variations)",
                        "channel": "Social Media Ads",
                        "deadline": "Week 2",
                        "effort": "20 hours",
                        "expected_outcome": "First 10-15 customers"
                    }
                ]
            },
            {
                "month": 2,
                "focus": "Optimization & Scaling",
                "tasks": [
                    {
                        "task": "Analyze ad performance and optimize top performers",
                        "channel": "Social Media Ads",
                        "deadline": "Week 2",
                        "effort": "15 hours",
                        "expected_outcome": "20% improvement in CAC"
                    }
                ]
            }
        ]

    def _calculate_roi_projections(
        self,
        channel_analysis: Dict[str, Any],
        budget: float
    ) -> Dict[str, Any]:
        """
        Calculate ROI projections for recommended channels

        Args:
            channel_analysis: Channel analysis
            budget: Monthly budget

        Returns:
            ROI projections
        """
        channels = channel_analysis.get("channels", [])
        if not channels:
            return {"total_customers": 0, "total_revenue": 0, "roi": 0}

        # Calculate based on channel estimates
        total_customers = 0
        total_spend = 0

        for channel in channels[:3]:  # Top 3 channels
            if channel.get("priority") == "High":
                monthly_budget = channel.get("monthly_budget_needed", 0)
                customers = channel.get("expected_monthly_customers", 0)

                total_customers += customers
                total_spend += monthly_budget

        # Assume average customer lifetime value
        avg_ltv = 10000  # ₹10,000 per customer (conservative estimate)
        total_revenue = total_customers * avg_ltv
        roi = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0

        return {
            "total_customers_month_6": int(total_customers * 3),  # Scaled over 6 months
            "total_spend_6_months": int(total_spend * 6),
            "projected_revenue_6_months": int(total_revenue * 3),
            "roi_percentage": round(roi, 1),
            "avg_cac": int(total_spend / total_customers) if total_customers > 0 else 0,
            "ltv_cac_ratio": round(avg_ltv / (total_spend / total_customers), 2) if total_customers > 0 else 0
        }
