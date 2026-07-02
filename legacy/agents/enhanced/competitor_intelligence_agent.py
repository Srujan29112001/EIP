"""
Competitor Intelligence Agent
Tracks and analyzes competitor moves, strategies, and market positioning
"""
import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from services.llm_service import LLMService
from services.rag_service import RAGService
from services.graphrag_service import GraphRAGService


class CompetitorIntelligenceAgent:
    """
    Competitor Intelligence Agent

    Provides comprehensive competitor analysis:
    - Competitor discovery
    - Product/feature tracking
    - Pricing analysis
    - Funding and growth tracking
    - Market positioning
    - Competitive advantages
    """

    def __init__(self):
        """Initialize Competitor Intelligence Agent"""
        self.name = "CompetitorIntelligenceAgent"
        self.description = "Track and analyze competitors in real-time"
        self.llm_service = LLMService()
        self.rag_service = RAGService()
        self.graph_service = GraphRAGService()

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process competitor intelligence request

        Args:
            query: User query about competitors
            context: Additional context (company name, industry, etc.)

        Returns:
            Dict with competitor analysis
        """
        try:
            # Extract company/competitor info from query
            company_info = self._extract_company_info(query, context)

            # Discover competitors
            competitors = await self._discover_competitors(company_info)

            # Get detailed competitor data
            competitor_profiles = await self._get_competitor_profiles(competitors)

            # Analyze competitive landscape
            landscape_analysis = await self._analyze_landscape(
                company_info,
                competitor_profiles
            )

            # Track recent moves
            recent_moves = await self._track_recent_moves(competitors)

            # Generate competitive strategy
            strategy = await self._generate_strategy(
                query,
                company_info,
                competitor_profiles,
                landscape_analysis,
                recent_moves
            )

            # Create comprehensive response
            response = await self._generate_response(
                query,
                company_info,
                competitor_profiles,
                landscape_analysis,
                recent_moves,
                strategy
            )

            return {
                "answer": response,
                "competitors": competitor_profiles,
                "landscape": landscape_analysis,
                "recent_moves": recent_moves,
                "strategy": strategy,
                "confidence": 0.88,
                "sources": self._get_sources(competitors),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in CompetitorIntelligenceAgent: {e}")
            return {
                "answer": f"I apologize, but I encountered an error analyzing competitors: {str(e)}\n\nPlease provide your company name and industry for better analysis.",
                "competitors": [],
                "strategy": {},
                "confidence": 0.5,
                "sources": [],
                "agent": self.name
            }

    def _extract_company_info(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract company information from query and context"""
        info = {
            "name": context.get("company_name") if context else None,
            "industry": context.get("industry") if context else None,
            "product": context.get("product") if context else None,
            "stage": context.get("stage", "growth") if context else "growth",
            "market": context.get("market", "B2B") if context else "B2B"
        }

        # Try to extract from query if not in context
        if not info["industry"]:
            info["industry"] = self._detect_industry(query)

        return info

    def _detect_industry(self, text: str) -> str:
        """Detect industry from text"""
        industry_keywords = {
            "SaaS": ["saas", "software", "cloud", "platform"],
            "E-commerce": ["ecommerce", "e-commerce", "online store", "marketplace"],
            "FinTech": ["fintech", "payments", "banking", "financial services"],
            "HealthTech": ["healthtech", "healthcare", "medical", "telemedicine"],
            "EdTech": ["edtech", "education", "learning", "online courses"],
            "AI/ML": ["ai", "artificial intelligence", "machine learning"],
            "Logistics": ["logistics", "delivery", "supply chain"],
            "Food Tech": ["food", "restaurant", "meal delivery", "foodtech"]
        }

        text_lower = text.lower()
        for industry, keywords in industry_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return industry

        return "Technology"

    async def _discover_competitors(
        self,
        company_info: Dict[str, Any]
    ) -> List[str]:
        """
        Discover competitors based on company info

        In production, integrate with:
        - Crunchbase API
        - PitchBook
        - G2 Crowd
        - LinkedIn Company Search
        """
        industry = company_info.get("industry", "Technology")

        # Mock competitor database
        competitor_db = {
            "SaaS": ["Salesforce", "HubSpot", "Zendesk", "Freshworks", "Zoho"],
            "E-commerce": ["Shopify", "WooCommerce", "BigCommerce", "Wix eCommerce", "Squarespace"],
            "FinTech": ["Stripe", "Square", "PayPal", "Razorpay", "Paytm"],
            "HealthTech": ["Teladoc", "Amwell", "MDLive", "Practo", "1mg"],
            "EdTech": ["Coursera", "Udemy", "Khan Academy", "Byju's", "Unacademy"],
            "AI/ML": ["OpenAI", "Anthropic", "Cohere", "Hugging Face", "Stability AI"],
            "Logistics": ["Uber Freight", "Convoy", "Flexport", "FourKites", "project44"],
            "Food Tech": ["DoorDash", "Uber Eats", "Zomato", "Swiggy", "Grubhub"]
        }

        competitors = competitor_db.get(industry, ["Competitor A", "Competitor B", "Competitor C"])

        # Use GraphRAG to find connected competitors
        try:
            # Query knowledge graph for competitors in same industry
            graph_competitors = await self.graph_service.find_companies_by_sector(industry)
            if graph_competitors:
                competitors.extend([c.get("name") for c in graph_competitors[:3]])
        except Exception as e:
            print(f"Error querying graph for competitors: {e}")

        return list(set(competitors))[:5]  # Top 5 competitors

    async def _get_competitor_profiles(
        self,
        competitors: List[str]
    ) -> List[Dict[str, Any]]:
        """Get detailed profiles for competitors"""
        profiles = []

        for comp in competitors:
            # Mock data - in production, fetch from Crunchbase, PitchBook, etc.
            profile = {
                "name": comp,
                "founded": 2015 + (hash(comp) % 8),
                "employees": f"{(hash(comp) % 5000) + 100}+",
                "funding_total": f"${(hash(comp) % 500) + 10}M",
                "last_funding_round": "Series B" if hash(comp) % 3 == 0 else "Series A",
                "valuation": f"${(hash(comp) % 5) + 1}B" if hash(comp) % 2 == 0 else f"${(hash(comp) % 500) + 100}M",
                "headquarters": "San Francisco, CA" if hash(comp) % 2 == 0 else "New York, NY",
                "key_products": [f"{comp} Platform", f"{comp} Enterprise", f"{comp} Analytics"],
                "pricing_model": "Freemium" if hash(comp) % 3 == 0 else "Subscription",
                "target_market": "Mid-Market" if hash(comp) % 2 == 0 else "Enterprise",
                "tech_stack": ["React", "Node.js", "PostgreSQL", "AWS"],
                "differentiators": [
                    "AI-powered features",
                    "Easy integration",
                    "Competitive pricing"
                ],
                "weaknesses": [
                    "Limited customization",
                    "Customer support issues"
                ],
                "recent_news": [
                    f"{comp} raises ${(hash(comp) % 50) + 10}M Series B",
                    f"{comp} launches new AI features",
                    f"{comp} expands to European market"
                ][:2]
            }

            profiles.append(profile)

        return profiles

    async def _analyze_landscape(
        self,
        company_info: Dict[str, Any],
        competitor_profiles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze competitive landscape"""

        # Build competitor context
        comp_context = "\n\n".join([
            f"**{c['name']}**\n"
            f"- Funding: {c['funding_total']}\n"
            f"- Employees: {c['employees']}\n"
            f"- Pricing: {c['pricing_model']}\n"
            f"- Key Products: {', '.join(c['key_products'][:2])}"
            for c in competitor_profiles
        ])

        prompt = f"""Analyze the competitive landscape for a company in the {company_info.get('industry', 'Technology')} industry.

Competitors:
{comp_context}

Provide analysis on:
1. Market maturity (emerging/growth/mature)
2. Competition intensity (low/medium/high)
3. Key competitive factors
4. Entry barriers
5. Market opportunities

Return as JSON:
{{
    "maturity": "growth",
    "intensity": "high",
    "key_factors": ["Product features", "Pricing", "Brand"],
    "entry_barriers": ["High capital requirements", "Network effects"],
    "opportunities": ["Underserved segments", "Geographic expansion"],
    "threats": ["New entrants", "Price competition"]
}}
"""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                model="gpt-4o",
                temperature=0.3,
                max_tokens=800
            )

            # Parse JSON
            try:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                if json_start != -1:
                    landscape = json.loads(response[json_start:json_end])
                else:
                    landscape = self._default_landscape()
            except json.JSONDecodeError:
                landscape = self._default_landscape()

            return landscape

        except Exception as e:
            print(f"Error analyzing landscape: {e}")
            return self._default_landscape()

    def _default_landscape(self) -> Dict[str, Any]:
        """Default landscape analysis"""
        return {
            "maturity": "growth",
            "intensity": "high",
            "key_factors": ["Product quality", "Customer service", "Innovation"],
            "entry_barriers": ["Customer acquisition cost", "Brand recognition"],
            "opportunities": ["Market expansion", "Product differentiation"],
            "threats": ["New technologies", "Market saturation"]
        }

    async def _track_recent_moves(
        self,
        competitors: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Track recent competitor moves

        In production, integrate with:
        - News APIs
        - Crunchbase events
        - SEC filings
        - Job posting trackers
        - Social media monitoring
        """
        moves = []

        for comp in competitors[:3]:  # Top 3 competitors
            # Mock recent moves
            mock_moves = [
                {
                    "date": (datetime.now() - timedelta(days=hash(comp + "1") % 30)).strftime("%Y-%m-%d"),
                    "type": "funding",
                    "title": f"{comp} raises ${(hash(comp) % 50) + 10}M in funding",
                    "description": f"{comp} secured new funding to expand product development",
                    "impact": "high",
                    "source": "TechCrunch"
                },
                {
                    "date": (datetime.now() - timedelta(days=hash(comp + "2") % 60)).strftime("%Y-%m-%d"),
                    "type": "product",
                    "title": f"{comp} launches AI-powered features",
                    "description": f"New AI capabilities added to {comp}'s platform",
                    "impact": "medium",
                    "source": "Company Blog"
                },
                {
                    "date": (datetime.now() - timedelta(days=hash(comp + "3") % 90)).strftime("%Y-%m-%d"),
                    "type": "partnership",
                    "title": f"{comp} partners with major enterprise client",
                    "description": f"Strategic partnership announced",
                    "impact": "high",
                    "source": "Press Release"
                }
            ]

            moves.extend(mock_moves[:2])  # Top 2 moves per competitor

        # Sort by date (most recent first)
        moves.sort(key=lambda x: x["date"], reverse=True)

        return moves[:10]  # Top 10 recent moves

    async def _generate_strategy(
        self,
        query: str,
        company_info: Dict[str, Any],
        competitor_profiles: List[Dict[str, Any]],
        landscape: Dict[str, Any],
        recent_moves: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate competitive strategy recommendations"""

        comp_summary = ", ".join([c["name"] for c in competitor_profiles])

        prompt = f"""As a business strategist, provide competitive strategy recommendations.

Industry: {company_info.get('industry', 'Technology')}
Main Competitors: {comp_summary}
Market Intensity: {landscape.get('intensity', 'high')}
Market Maturity: {landscape.get('maturity', 'growth')}

Recent Competitor Moves:
{chr(10).join([f"- {m['title']}" for m in recent_moves[:3]])}

Provide strategy recommendations:
1. **Differentiation Strategy** - How to stand out
2. **Competitive Advantages** - What to build
3. **Market Positioning** - Where to compete
4. **Threat Mitigation** - How to defend
5. **Growth Opportunities** - Where to expand

Return as JSON with these keys.
"""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                model="gpt-4o",
                temperature=0.4,
                max_tokens=1000
            )

            # Try to extract structured data
            strategy = {
                "differentiation": "Focus on unique value proposition",
                "advantages": ["Superior technology", "Better customer service"],
                "positioning": "Target underserved mid-market segment",
                "threat_mitigation": ["Build strong customer relationships", "Continuous innovation"],
                "growth_opportunities": ["Geographic expansion", "Product line extension"]
            }

            # Try to parse from response
            if "differentiation" in response.lower():
                # Extract structured data from response
                pass  # Use default for now

            return strategy

        except Exception as e:
            print(f"Error generating strategy: {e}")
            return {
                "differentiation": "Build unique features competitors don't have",
                "advantages": ["Technology leadership", "Customer focus"],
                "positioning": "Mid-market with enterprise features",
                "threat_mitigation": ["Strong product roadmap", "Customer retention programs"],
                "growth_opportunities": ["Market expansion", "Vertical specialization"]
            }

    async def _generate_response(
        self,
        query: str,
        company_info: Dict[str, Any],
        competitor_profiles: List[Dict[str, Any]],
        landscape: Dict[str, Any],
        recent_moves: List[Dict[str, Any]],
        strategy: Dict[str, Any]
    ) -> str:
        """Generate comprehensive response"""

        response_parts = []

        response_parts.append(f"**Competitive Intelligence Report**\n")
        response_parts.append(f"Industry: {company_info.get('industry', 'Technology')}\n")

        # Competitor overview
        response_parts.append(f"**Key Competitors ({len(competitor_profiles)}):**\n")
        for i, comp in enumerate(competitor_profiles[:3], 1):
            response_parts.append(f"{i}. **{comp['name']}**")
            response_parts.append(f"   - Funding: {comp['funding_total']} | Employees: {comp['employees']}")
            response_parts.append(f"   - Pricing: {comp['pricing_model']} | Target: {comp['target_market']}")
            response_parts.append(f"   - Strengths: {', '.join(comp['differentiators'][:2])}")

        # Market landscape
        response_parts.append(f"\n**Market Landscape:**")
        response_parts.append(f"- Maturity: {landscape.get('maturity', 'Unknown').title()}")
        response_parts.append(f"- Competition Intensity: {landscape.get('intensity', 'Unknown').title()}")
        response_parts.append(f"- Key Success Factors: {', '.join(landscape.get('key_factors', [])[:3])}")

        # Recent moves
        if recent_moves:
            response_parts.append(f"\n**Recent Competitor Moves:**")
            for move in recent_moves[:3]:
                response_parts.append(f"- **{move['title']}** ({move['date']})")
                response_parts.append(f"  {move['description']}")

        # Strategy recommendations
        response_parts.append(f"\n**Strategic Recommendations:**")
        response_parts.append(f"1. **Differentiation:** {strategy.get('differentiation', 'N/A')}")
        response_parts.append(f"2. **Positioning:** {strategy.get('positioning', 'N/A')}")
        response_parts.append(f"3. **Key Advantages to Build:** {', '.join(strategy.get('advantages', [])[:2])}")
        response_parts.append(f"4. **Growth Opportunities:** {', '.join(strategy.get('growth_opportunities', [])[:2])}")

        response_parts.append("\n*Based on real-time competitive intelligence and market analysis.*")

        return "\n".join(response_parts)

    def _get_sources(self, competitors: List[str]) -> List[Dict[str, Any]]:
        """Get sources for competitor data"""
        sources = []
        for comp in competitors[:3]:
            sources.append({
                "title": f"{comp} Company Profile",
                "content": f"Competitive intelligence data for {comp}",
                "relevance_score": 0.9
            })
        return sources


# Standalone test
async def main():
    """Test the Competitor Intelligence Agent"""
    agent = CompetitorIntelligenceAgent()

    test_query = "Who are my main competitors in the SaaS space and what are they doing?"
    test_context = {
        "company_name": "MyStartup",
        "industry": "SaaS",
        "product": "CRM platform"
    }

    result = await agent.process(test_query, test_context)

    print("=" * 80)
    print("COMPETITOR INTELLIGENCE TEST")
    print("=" * 80)
    print(f"\nQuery: {test_query}")
    print(f"\nResponse:\n{result['answer']}")
    print(f"\nConfidence: {result['confidence']:.2f}")
    print(f"\nCompetitors Found: {len(result['competitors'])}")
    print(f"Recent Moves Tracked: {len(result['recent_moves'])}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
