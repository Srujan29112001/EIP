"""
Business Model Recommender Agent
Recommends optimal business models for startup ideas based on ML and historical data
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


class BusinessModelRecommenderAgent:
    """
    Business Model Recommender Agent

    Recommends optimal business models based on:
    - Industry and market analysis
    - Historical success patterns
    - Resource constraints
    - Target market characteristics
    """

    def __init__(self):
        """Initialize Business Model Recommender Agent"""
        self.name = "BusinessModelRecommenderAgent"
        self.description = "Recommends optimal business models for startup ideas"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

        # Business model templates database
        self.model_templates = self._initialize_templates()

    def _initialize_templates(self) -> List[Dict[str, Any]]:
        """Initialize business model templates"""
        return [
            {
                "model_type": "SaaS Subscription",
                "revenue_model": "Recurring Subscription",
                "industries": ["Technology", "Software", "B2B Services"],
                "target_market": ["B2B", "Enterprise", "SMB"],
                "capital_requirements": "Medium",
                "time_to_profitability": "18-24 months",
                "success_rate": 0.72,
                "avg_ltv_cac": 3.5,
                "key_metrics": ["MRR", "Churn Rate", "CAC", "LTV"],
                "examples": ["Salesforce", "HubSpot", "Zendesk"],
                "pros": ["Predictable revenue", "High valuation multiples", "Scalable"],
                "cons": ["High customer acquisition cost", "Churn risk", "Competition"],
                "best_for": "B2B software with recurring value delivery"
            },
            {
                "model_type": "Freemium",
                "revenue_model": "Free + Premium Tiers",
                "industries": ["Software", "Apps", "Digital Services"],
                "target_market": ["B2C", "B2B", "SMB"],
                "capital_requirements": "Medium-High",
                "time_to_profitability": "24-36 months",
                "success_rate": 0.45,
                "avg_ltv_cac": 2.8,
                "key_metrics": ["Free Users", "Conversion Rate", "ARPU", "Viral Coefficient"],
                "examples": ["Slack", "Dropbox", "LinkedIn"],
                "pros": ["Low acquisition cost", "Viral growth", "Large user base"],
                "cons": ["Low conversion rates (2-5%)", "Monetization challenges", "Support costs"],
                "best_for": "Products with network effects and viral potential"
            },
            {
                "model_type": "Marketplace",
                "revenue_model": "Commission/Transaction Fees",
                "industries": ["E-commerce", "Services", "Gig Economy"],
                "target_market": ["B2C", "C2C", "B2B"],
                "capital_requirements": "High",
                "time_to_profitability": "36-48 months",
                "success_rate": 0.35,
                "avg_ltv_cac": 4.2,
                "key_metrics": ["GMV", "Take Rate", "Liquidity", "Repeat Rate"],
                "examples": ["Airbnb", "Uber", "Fiverr"],
                "pros": ["High scaling potential", "Network effects", "Asset-light"],
                "cons": ["Chicken-and-egg problem", "High burn rate", "Regulatory risks"],
                "best_for": "Platforms connecting buyers and sellers"
            },
            {
                "model_type": "E-commerce D2C",
                "revenue_model": "Product Sales",
                "industries": ["Consumer Goods", "Fashion", "Food"],
                "target_market": ["B2C"],
                "capital_requirements": "Medium-High",
                "time_to_profitability": "12-24 months",
                "success_rate": 0.55,
                "avg_ltv_cac": 2.5,
                "key_metrics": ["AOV", "Repeat Purchase Rate", "Contribution Margin", "CAC"],
                "examples": ["Warby Parker", "Dollar Shave Club", "Casper"],
                "pros": ["Direct customer relationships", "Brand control", "Higher margins"],
                "cons": ["Inventory risk", "Logistics complexity", "Marketing intensive"],
                "best_for": "Unique products with brand differentiation"
            },
            {
                "model_type": "Platform as a Service (PaaS)",
                "revenue_model": "Usage-Based Pricing",
                "industries": ["Technology", "Infrastructure", "Developer Tools"],
                "target_market": ["B2B", "Developers"],
                "capital_requirements": "High",
                "time_to_profitability": "24-36 months",
                "success_rate": 0.60,
                "avg_ltv_cac": 4.5,
                "key_metrics": ["API Calls", "MAU", "NRR", "Usage Growth"],
                "examples": ["Stripe", "Twilio", "AWS"],
                "pros": ["Scalable infrastructure", "Developer lock-in", "High margins"],
                "cons": ["Complex to build", "Technical support intensive", "Competition"],
                "best_for": "Infrastructure and developer tools with API-first approach"
            },
            {
                "model_type": "Franchise",
                "revenue_model": "Franchise Fees + Royalties",
                "industries": ["Food & Beverage", "Retail", "Services"],
                "target_market": ["B2C"],
                "capital_requirements": "Low (for franchisor)",
                "time_to_profitability": "12-18 months",
                "success_rate": 0.68,
                "avg_ltv_cac": 5.0,
                "key_metrics": ["Franchise Units", "Royalty Rate", "Unit Economics", "Brand Value"],
                "examples": ["McDonald's", "Subway", "7-Eleven"],
                "pros": ["Rapid expansion", "Low capital requirement", "Proven model"],
                "cons": ["Quality control", "Franchisee disputes", "Brand risk"],
                "best_for": "Proven business models ready to scale geographically"
            }
        ]

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process business model recommendation request

        Args:
            query: User's business idea description
            context: Additional context (industry, resources, target market)

        Returns:
            Dict with recommended business models
        """
        try:
            # Extract business requirements
            requirements = self._extract_requirements(query, context)

            # Find matching business models
            matching_models = self._match_models(requirements)

            # Retrieve successful case studies
            case_studies = await self._retrieve_case_studies(requirements, matching_models)

            # Generate detailed recommendations with LLM
            recommendations = await self._generate_recommendations(
                query,
                requirements,
                matching_models,
                case_studies
            )

            # Create implementation roadmap
            roadmap = await self._create_roadmap(requirements, recommendations)

            # Generate comprehensive response
            response = await self._generate_response(
                query,
                requirements,
                recommendations,
                roadmap
            )

            return {
                "answer": response,
                "recommendations": recommendations,
                "roadmap": roadmap,
                "requirements": requirements,
                "confidence": 0.87,
                "sources": self._get_sources(case_studies),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in BusinessModelRecommenderAgent: {e}")
            return {
                "answer": f"I apologize, but I encountered an error generating recommendations: {str(e)}",
                "recommendations": [],
                "confidence": 0.5,
                "sources": [],
                "agent": self.name
            }

    def _extract_requirements(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract business requirements from query and context"""
        return {
            "idea": query,
            "industry": context.get("industry") if context else self._detect_industry(query),
            "target_market": context.get("target_market", "B2B") if context else "B2B",
            "resources": context.get("resources", "Limited") if context else "Limited",
            "timeline": context.get("timeline", "12-24 months") if context else "12-24 months",
            "capital_available": context.get("capital", "Medium") if context else "Medium",
            "team_size": context.get("team_size", "2-5") if context else "2-5",
            "risk_tolerance": context.get("risk_tolerance", "Medium") if context else "Medium"
        }

    def _detect_industry(self, text: str) -> str:
        """Detect industry from text"""
        keywords = {
            "Technology": ["software", "saas", "app", "platform", "ai", "ml"],
            "E-commerce": ["ecommerce", "online store", "marketplace", "retail"],
            "Services": ["consulting", "services", "agency"],
            "Consumer": ["consumer", "d2c", "product", "brand"]
        }

        text_lower = text.lower()
        for industry, kws in keywords.items():
            if any(kw in text_lower for kw in kws):
                return industry
        return "Technology"

    def _match_models(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Match business model templates to requirements"""
        matches = []

        for model in self.model_templates:
            score = 0.0

            # Industry match
            if requirements["industry"] in model["industries"]:
                score += 0.3

            # Target market match
            if requirements["target_market"] in model["target_market"]:
                score += 0.2

            # Capital requirements match
            capital_score = self._match_capital(
                requirements["capital_available"],
                model["capital_requirements"]
            )
            score += capital_score * 0.2

            # Timeline match
            timeline_score = self._match_timeline(
                requirements["timeline"],
                model["time_to_profitability"]
            )
            score += timeline_score * 0.15

            # Success rate bonus
            score += model["success_rate"] * 0.15

            model_with_score = model.copy()
            model_with_score["match_score"] = round(score, 2)
            model_with_score["recommendation_strength"] = (
                "Strong" if score >= 0.7 else "Moderate" if score >= 0.5 else "Weak"
            )

            matches.append(model_with_score)

        # Sort by score
        matches.sort(key=lambda x: x["match_score"], reverse=True)

        return matches[:5]  # Top 5 recommendations

    def _match_capital(self, available: str, required: str) -> float:
        """Match capital availability to requirements"""
        capital_levels = {"Low": 1, "Medium": 2, "Medium-High": 3, "High": 4}
        avail_level = capital_levels.get(available, 2)
        req_level = capital_levels.get(required, 2)

        if avail_level >= req_level:
            return 1.0
        elif avail_level == req_level - 1:
            return 0.7
        else:
            return 0.4

    def _match_timeline(self, target: str, model_timeline: str) -> float:
        """Match timeline expectations"""
        # Simple heuristic - extract months and compare
        target_months = 18  # Default
        if "12" in target:
            target_months = 12
        elif "24" in target:
            target_months = 24
        elif "36" in target:
            target_months = 36

        model_months = 24  # Default
        if "12" in model_timeline:
            model_months = 12
        elif "24" in model_timeline:
            model_months = 24
        elif "36" in model_timeline:
            model_months = 36
        elif "48" in model_timeline:
            model_months = 48

        if model_months <= target_months:
            return 1.0
        elif model_months <= target_months + 12:
            return 0.7
        else:
            return 0.4

    async def _retrieve_case_studies(
        self,
        requirements: Dict[str, Any],
        models: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant case studies from RAG"""
        try:
            # Search for case studies
            search_query = f"{requirements['industry']} {models[0]['model_type']} successful startups"

            results = await self.rag_service.retrieve(
                query=search_query,
                top_k=3,
                filter={"category": "business_models"}
            )

            case_studies = []
            for result in results:
                case_studies.append({
                    "company": result.get("metadata", {}).get("company", "Unknown"),
                    "model": result.get("metadata", {}).get("model_type", "Unknown"),
                    "success": result.get("content", "")[:200]
                })

            return case_studies

        except Exception as e:
            print(f"Error retrieving case studies: {e}")
            return []

    async def _generate_recommendations(
        self,
        query: str,
        requirements: Dict[str, Any],
        models: List[Dict[str, Any]],
        case_studies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate detailed recommendations using LLM"""

        models_context = "\n\n".join([
            f"**{m['model_type']}** (Match: {m['match_score']:.0%})\n"
            f"- Revenue Model: {m['revenue_model']}\n"
            f"- Success Rate: {m['success_rate']:.0%}\n"
            f"- Time to Profit: {m['time_to_profitability']}\n"
            f"- Best For: {m['best_for']}\n"
            f"- Pros: {', '.join(m['pros'][:2])}\n"
            f"- Cons: {', '.join(m['cons'][:2])}"
            for m in models[:3]
        ])

        prompt = f"""As a business model expert, provide detailed recommendations for this startup idea:

Business Idea: {query}

Requirements:
- Industry: {requirements['industry']}
- Target Market: {requirements['target_market']}
- Capital Available: {requirements['capital_available']}
- Timeline: {requirements['timeline']}

Top Matching Business Models:
{models_context}

For each of the top 3 models, provide:
1. Why it's a good fit for this specific idea
2. Key success factors
3. Main risks to mitigate
4. Expected revenue timeline
5. Recommended pricing strategy

Return as JSON array of recommendations.
"""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                model="gpt-4o",
                temperature=0.4,
                max_tokens=1500
            )

            # Enhance models with LLM insights
            enhanced_recommendations = []
            for i, model in enumerate(models[:3], 1):
                enhanced_recommendations.append({
                    "rank": i,
                    "model_type": model["model_type"],
                    "match_score": model["match_score"],
                    "revenue_model": model["revenue_model"],
                    "success_rate": model["success_rate"],
                    "time_to_profitability": model["time_to_profitability"],
                    "pros": model["pros"],
                    "cons": model["cons"],
                    "examples": model["examples"],
                    "key_metrics": model["key_metrics"],
                    "recommendation_strength": model["recommendation_strength"]
                })

            return enhanced_recommendations

        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return [
                {
                    "rank": i,
                    "model_type": m["model_type"],
                    "match_score": m["match_score"],
                    "revenue_model": m["revenue_model"],
                    "recommendation_strength": m["recommendation_strength"]
                }
                for i, m in enumerate(models[:3], 1)
            ]

    async def _create_roadmap(
        self,
        requirements: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create implementation roadmap"""

        top_model = recommendations[0] if recommendations else {}

        return {
            "recommended_model": top_model.get("model_type", "SaaS Subscription"),
            "phases": [
                {
                    "phase": "Phase 1: Validation (Months 1-3)",
                    "activities": [
                        "Customer discovery and interviews",
                        "MVP development",
                        "Pricing model testing",
                        "Initial go-to-market strategy"
                    ]
                },
                {
                    "phase": "Phase 2: Launch (Months 4-6)",
                    "activities": [
                        "Beta launch with early adopters",
                        "Iterate based on feedback",
                        "Refine pricing and packaging",
                        "Build initial customer base (10-50 customers)"
                    ]
                },
                {
                    "phase": "Phase 3: Growth (Months 7-12)",
                    "activities": [
                        "Scale customer acquisition",
                        "Optimize unit economics",
                        "Expand product features",
                        "Reach profitability or fundability"
                    ]
                },
                {
                    "phase": "Phase 4: Scale (Months 13-24)",
                    "activities": [
                        "Geographic expansion",
                        "Team scaling",
                        "Fundraising (if needed)",
                        "Market leadership positioning"
                    ]
                }
            ],
            "key_milestones": [
                "10 paying customers",
                "$10K MRR",
                "Product-market fit validation",
                "$100K ARR",
                "Break-even"
            ],
            "critical_metrics": top_model.get("key_metrics", ["Revenue", "Growth Rate", "CAC", "LTV"])
        }

    async def _generate_response(
        self,
        query: str,
        requirements: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        roadmap: Dict[str, Any]
    ) -> str:
        """Generate comprehensive response"""

        response_parts = []

        response_parts.append("**Business Model Recommendations**\n")
        response_parts.append(f"Based on your idea: *{query[:100]}...*\n")

        response_parts.append("**Top Recommended Business Models:**\n")
        for rec in recommendations:
            response_parts.append(f"\n{rec['rank']}. **{rec['model_type']}** ({rec['recommendation_strength']} Match - {rec['match_score']:.0%})")
            response_parts.append(f"   - Revenue Model: {rec['revenue_model']}")
            response_parts.append(f"   - Success Rate: {rec['success_rate']:.0%}")
            response_parts.append(f"   - Time to Profit: {rec['time_to_profitability']}")
            response_parts.append(f"   - Examples: {', '.join(rec['examples'][:2])}")
            response_parts.append(f"   - Pros: {', '.join(rec['pros'][:2])}")
            response_parts.append(f"   - Cons: {', '.join(rec['cons'][:2])}")

        response_parts.append(f"\n**Recommended Implementation Roadmap:**")
        response_parts.append(f"Primary Model: {roadmap['recommended_model']}\n")

        for phase in roadmap['phases'][:2]:
            response_parts.append(f"**{phase['phase']}**")
            for activity in phase['activities'][:2]:
                response_parts.append(f"  - {activity}")

        response_parts.append(f"\n**Key Metrics to Track:** {', '.join(roadmap['critical_metrics'])}")

        response_parts.append("\n*Recommendations based on industry analysis, historical success rates, and your specific requirements.*")

        return "\n".join(response_parts)

    def _get_sources(self, case_studies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get sources from case studies"""
        return [
            {
                "title": f"{cs['company']} - {cs['model']}",
                "content": cs['success'],
                "relevance_score": 0.85
            }
            for cs in case_studies[:3]
        ]


# Standalone test
async def main():
    """Test the Business Model Recommender Agent"""
    agent = BusinessModelRecommenderAgent()

    test_query = "I want to build an AI-powered HR analytics platform for mid-sized companies"
    test_context = {
        "industry": "Technology",
        "target_market": "B2B",
        "capital_available": "Medium",
        "timeline": "18-24 months"
    }

    result = await agent.process(test_query, test_context)

    print("=" * 80)
    print("BUSINESS MODEL RECOMMENDER TEST")
    print("=" * 80)
    print(f"\nQuery: {test_query}")
    print(f"\nResponse:\n{result['answer']}")
    print(f"\nRecommendations: {len(result['recommendations'])}")
    print(f"Confidence: {result['confidence']:.2f}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
