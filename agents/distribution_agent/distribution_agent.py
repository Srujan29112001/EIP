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
        Process distribution-related queries

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

        # Retrieve relevant distribution case studies
        retrieved_docs = await self._retrieve_context(query)

        # Build context for LLM
        context_str = self._build_context(query, user_context, retrieved_docs)

        # Generate response using LLM
        response = await self._generate_response(query, context_str)

        # Format sources
        sources = self._format_sources(retrieved_docs)

        return {
            "agent": self.agent_name,
            "answer": response,
            "sources": sources,
            "metadata": {
                "business_type": business_type,
                "user_tier": user_tier,
                "query_type": "distribution_strategy"
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
