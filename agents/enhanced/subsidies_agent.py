"""
Subsidies Analyzer Agent
Discover government subsidies, grants, and incentives for businesses
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


class SubsidiesAnalyzerAgent:
    """
    Subsidies Analyzer Agent

    Helps entrepreneurs discover and apply for:
    - Government subsidies
    - Grants and incentives
    - Tax credits
    - Funding programs
    - Business support schemes
    """

    def __init__(self):
        """Initialize Subsidies Analyzer Agent"""
        self.name = "SubsidiesAnalyzerAgent"
        self.description = "Discover government subsidies and grants"
        self.llm_service = LLMService()
        self.rag_service = RAGService()
        self.graph_service = GraphRAGService()

        # Initialize subsidy database (in production, fetch from APIs)
        self.subsidies_db = self._initialize_subsidies_db()

    def _initialize_subsidies_db(self) -> List[Dict[str, Any]]:
        """Initialize subsidies database with common schemes"""
        return [
            # India - Startup India
            {
                "id": "startup-india-seed",
                "title": "Startup India Seed Fund Scheme",
                "country": "India",
                "government_body": "Department for Promotion of Industry and Internal Trade (DPIIT)",
                "amount_max": 2000000,  # INR 20 lakh
                "amount_currency": "INR",
                "amount_display": "₹20 lakh",
                "type": "seed_funding",
                "industry": ["Technology", "Manufacturing", "Services"],
                "stage": ["idea", "seed"],
                "eligibility": {
                    "entity_type": ["Private Limited", "LLP"],
                    "registration": "DPIIT recognized startup",
                    "age": "< 2 years",
                    "revenue": "< ₹25 crore"
                },
                "benefits": [
                    "Proof of concept validation",
                    "Prototype development",
                    "Product trials",
                    "Market entry",
                    "Commercialization"
                ],
                "deadline": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
                "application_url": "https://www.startupindia.gov.in",
                "requirements": ["DPIIT recognition", "Business plan", "Pitch deck"]
            },
            # India - MSME
            {
                "id": "msme-credit-guarantee",
                "title": "Credit Guarantee Fund Scheme for Micro and Small Enterprises (CGTMSE)",
                "country": "India",
                "government_body": "Ministry of MSME",
                "amount_max": 50000000,  # ₹5 crore
                "amount_currency": "INR",
                "amount_display": "₹5 crore",
                "type": "credit_guarantee",
                "industry": ["All"],
                "stage": ["seed", "growth", "expansion"],
                "eligibility": {
                    "entity_type": ["Proprietorship", "Partnership", "Private Limited"],
                    "registration": "Udyam Registration",
                    "turnover": "< ₹50 crore"
                },
                "benefits": [
                    "Collateral-free loans up to ₹2 crore",
                    "75-85% guarantee coverage",
                    "Working capital support",
                    "Term loan guarantee"
                ],
                "deadline": "Rolling",
                "application_url": "https://www.cgtmse.in",
                "requirements": ["Udyam certificate", "Business plan", "Financial projections"]
            },
            # India - Technology
            {
                "id": "technology-development-fund",
                "title": "Technology Development Fund (TDF)",
                "country": "India",
                "government_body": "Department of Defense Production",
                "amount_max": 100000000,  # ₹10 crore
                "amount_currency": "INR",
                "amount_display": "₹10 crore",
                "type": "grant",
                "industry": ["Technology", "Defense", "AI/ML"],
                "stage": ["growth", "expansion"],
                "eligibility": {
                    "entity_type": ["Private Limited"],
                    "registration": "Indian entity",
                    "focus": "Defense/strategic technology"
                },
                "benefits": [
                    "90% funding for development",
                    "IP rights retention",
                    "Fast-track procurement"
                ],
                "deadline": (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d"),
                "application_url": "https://www.mod.gov.in",
                "requirements": ["Technical proposal", "Prototype plan", "Team credentials"]
            },
            # India - Section 80IAC
            {
                "id": "section-80iac-tax-exemption",
                "title": "Section 80-IAC Tax Exemption for Startups",
                "country": "India",
                "government_body": "Income Tax Department",
                "amount_max": 0,  # Tax exemption, not direct funding
                "amount_currency": "INR",
                "amount_display": "100% tax exemption",
                "type": "tax_credit",
                "industry": ["All"],
                "stage": ["seed", "growth"],
                "eligibility": {
                    "entity_type": ["Private Limited", "LLP"],
                    "registration": "DPIIT recognized startup",
                    "age": "< 10 years",
                    "turnover": "< ₹100 crore"
                },
                "benefits": [
                    "100% profit tax exemption for 3 consecutive years",
                    "Choose any 3 years out of first 10 years",
                    "No tax on angel investments"
                ],
                "deadline": "Annual (Financial Year)",
                "application_url": "https://www.incometax.gov.in",
                "requirements": ["DPIIT recognition", "Tax returns", "Audit reports"]
            },
            # US - SBIR
            {
                "id": "us-sbir-grant",
                "title": "Small Business Innovation Research (SBIR)",
                "country": "USA",
                "government_body": "Small Business Administration (SBA)",
                "amount_max": 1000000,  # $1M
                "amount_currency": "USD",
                "amount_display": "$1M",
                "type": "grant",
                "industry": ["Technology", "Healthcare", "Defense"],
                "stage": ["seed", "growth"],
                "eligibility": {
                    "entity_type": ["Corporation", "LLC"],
                    "registration": "US-based small business",
                    "employees": "< 500",
                    "ownership": "51% US citizens"
                },
                "benefits": [
                    "Phase I: $150K for feasibility",
                    "Phase II: $1M for development",
                    "Non-dilutive funding",
                    "Government customer access"
                ],
                "deadline": "Rolling",
                "application_url": "https://www.sbir.gov",
                "requirements": ["Research proposal", "Budget", "Team qualifications"]
            }
        ]

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process subsidies discovery request

        Args:
            query: User query about subsidies
            context: Business context (industry, stage, location, etc.)

        Returns:
            Dict with eligible subsidies and recommendations
        """
        try:
            # Extract business criteria from query and context
            criteria = self._extract_criteria(query, context)

            # Search for eligible subsidies
            eligible_subsidies = await self._find_eligible_subsidies(criteria)

            # Calculate eligibility scores
            scored_subsidies = self._score_subsidies(eligible_subsidies, criteria)

            # Generate application strategy
            strategy = await self._generate_application_strategy(
                query,
                criteria,
                scored_subsidies
            )

            # Create comprehensive response
            response = await self._generate_response(
                query,
                criteria,
                scored_subsidies,
                strategy
            )

            return {
                "answer": response,
                "subsidies": scored_subsidies,
                "total_potential_funding": self._calculate_total_funding(scored_subsidies),
                "application_strategy": strategy,
                "confidence": 0.90,
                "sources": self._get_sources(scored_subsidies),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in SubsidiesAnalyzerAgent: {e}")
            return {
                "answer": f"I apologize, but I encountered an error finding subsidies: {str(e)}\n\nPlease provide your industry, business stage, and location for better results.",
                "subsidies": [],
                "total_potential_funding": 0,
                "confidence": 0.5,
                "sources": [],
                "agent": self.name
            }

    def _extract_criteria(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract business criteria for subsidy matching"""
        criteria = {
            "industry": context.get("industry") if context else self._detect_industry(query),
            "stage": context.get("stage", "seed") if context else "seed",
            "country": context.get("country", "India") if context else "India",
            "entity_type": context.get("entity_type", "Private Limited") if context else None,
            "revenue": context.get("revenue") if context else None,
            "employees": context.get("employees") if context else None,
            "registration": context.get("registration") if context else None
        }

        return criteria

    def _detect_industry(self, text: str) -> str:
        """Detect industry from text"""
        industry_keywords = {
            "Technology": ["tech", "software", "saas", "ai", "ml", "cloud"],
            "Manufacturing": ["manufacturing", "production", "factory"],
            "Healthcare": ["health", "medical", "pharma", "biotech"],
            "Education": ["education", "edtech", "learning", "training"],
            "Agriculture": ["agriculture", "agritech", "farming"],
            "Services": ["services", "consulting", "professional services"]
        }

        text_lower = text.lower()
        for industry, keywords in industry_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return industry

        return "All"

    async def _find_eligible_subsidies(
        self,
        criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find subsidies matching eligibility criteria"""
        eligible = []

        for subsidy in self.subsidies_db:
            # Filter by country
            if criteria.get("country") and subsidy["country"] != criteria["country"]:
                continue

            # Filter by industry
            if criteria.get("industry"):
                if "All" not in subsidy["industry"] and criteria["industry"] not in subsidy["industry"]:
                    continue

            # Filter by stage
            if criteria.get("stage"):
                if criteria["stage"] not in subsidy["stage"]:
                    continue

            eligible.append(subsidy)

        return eligible

    def _score_subsidies(
        self,
        subsidies: List[Dict[str, Any]],
        criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Score subsidies based on fit and potential value"""
        scored = []

        for subsidy in subsidies:
            score = 0.5  # Base score

            # Industry match
            if criteria.get("industry") in subsidy["industry"]:
                score += 0.2

            # Stage match
            if criteria.get("stage") in subsidy["stage"]:
                score += 0.2

            # Amount (higher is better)
            if subsidy["amount_max"] > 1000000:
                score += 0.1

            # Check eligibility requirements
            eligibility = subsidy.get("eligibility", {})
            entity_match = criteria.get("entity_type") in eligibility.get("entity_type", [])
            if entity_match:
                score += 0.1

            # Add score to subsidy
            subsidy_with_score = subsidy.copy()
            subsidy_with_score["eligibility_score"] = min(score, 1.0)
            subsidy_with_score["match_level"] = "High" if score >= 0.8 else "Medium" if score >= 0.6 else "Low"

            scored.append(subsidy_with_score)

        # Sort by score
        scored.sort(key=lambda x: x["eligibility_score"], reverse=True)

        return scored

    async def _generate_application_strategy(
        self,
        query: str,
        criteria: Dict[str, Any],
        subsidies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate application strategy"""

        top_subsidies = subsidies[:3]

        prompt = f"""Create an application strategy for these government subsidies/grants:

Business Profile:
- Industry: {criteria.get('industry', 'Technology')}
- Stage: {criteria.get('stage', 'seed')}
- Country: {criteria.get('country', 'India')}

Eligible Subsidies:
{chr(10).join([f"- {s['title']}: {s['amount_display']} ({s['type']})" for s in top_subsidies])}

Provide strategy for:
1. Priority order (which to apply first)
2. Timeline (application schedule)
3. Preparation requirements
4. Success tips

Return as JSON:
{{
    "priority_order": ["subsidy_id_1", "subsidy_id_2"],
    "timeline": "3-6 months",
    "key_documents": ["Document 1", "Document 2"],
    "success_tips": ["Tip 1", "Tip 2"]
}}
"""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                model="gpt-4o",
                temperature=0.3,
                max_tokens=600
            )

            # Try to parse JSON
            try:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                if json_start != -1:
                    strategy = json.loads(response[json_start:json_end])
                else:
                    strategy = self._default_strategy(subsidies)
            except json.JSONDecodeError:
                strategy = self._default_strategy(subsidies)

            return strategy

        except Exception as e:
            print(f"Error generating strategy: {e}")
            return self._default_strategy(subsidies)

    def _default_strategy(self, subsidies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Default application strategy"""
        return {
            "priority_order": [s["id"] for s in subsidies[:3]],
            "timeline": "3-6 months",
            "key_documents": [
                "Business registration certificate",
                "Business plan",
                "Financial projections",
                "Tax returns",
                "Pitch deck"
            ],
            "success_tips": [
                "Apply early - many schemes are first-come-first-served",
                "Ensure all documentation is complete",
                "Highlight innovation and impact",
                "Show clear use of funds",
                "Follow up regularly on application status"
            ]
        }

    async def _generate_response(
        self,
        query: str,
        criteria: Dict[str, Any],
        subsidies: List[Dict[str, Any]],
        strategy: Dict[str, Any]
    ) -> str:
        """Generate comprehensive response"""

        response_parts = []

        response_parts.append(f"**Government Subsidies & Grants Analysis**\n")
        response_parts.append(f"Location: {criteria.get('country', 'India')}")
        response_parts.append(f"Industry: {criteria.get('industry', 'Technology')}")
        response_parts.append(f"Stage: {criteria.get('stage', 'Seed')}\n")

        response_parts.append(f"**Found {len(subsidies)} Eligible Programs:**\n")

        # Top subsidies
        for i, subsidy in enumerate(subsidies[:5], 1):
            response_parts.append(f"{i}. **{subsidy['title']}**")
            response_parts.append(f"   - Amount: {subsidy['amount_display']}")
            response_parts.append(f"   - Type: {subsidy['type'].replace('_', ' ').title()}")
            response_parts.append(f"   - Eligibility Match: {subsidy['match_level']} ({subsidy['eligibility_score']:.0%})")
            response_parts.append(f"   - Deadline: {subsidy['deadline']}")
            response_parts.append(f"   - Benefits: {', '.join(subsidy['benefits'][:2])}")
            response_parts.append(f"   - Apply: {subsidy['application_url']}\n")

        # Total potential funding
        total = self._calculate_total_funding(subsidies[:5])
        response_parts.append(f"**Total Potential Funding: {total}**\n")

        # Application strategy
        response_parts.append(f"**Application Strategy:**")
        response_parts.append(f"- Timeline: {strategy.get('timeline', '3-6 months')}")
        response_parts.append(f"- Priority Order: Apply in order listed above")
        response_parts.append(f"\n**Key Documents Needed:**")
        for doc in strategy.get('key_documents', [])[:5]:
            response_parts.append(f"- {doc}")

        response_parts.append(f"\n**Success Tips:**")
        for tip in strategy.get('success_tips', [])[:3]:
            response_parts.append(f"✓ {tip}")

        response_parts.append("\n*Based on current government schemes. Eligibility criteria may change. Please verify on official websites.*")

        return "\n".join(response_parts)

    def _calculate_total_funding(self, subsidies: List[Dict[str, Any]]) -> str:
        """Calculate total potential funding"""
        total_inr = 0
        total_usd = 0

        for subsidy in subsidies:
            if subsidy["amount_currency"] == "INR":
                total_inr += subsidy["amount_max"]
            elif subsidy["amount_currency"] == "USD":
                total_usd += subsidy["amount_max"]

        parts = []
        if total_inr > 0:
            if total_inr >= 10000000:  # 1 crore
                parts.append(f"₹{total_inr/10000000:.1f} Cr")
            else:
                parts.append(f"₹{total_inr/100000:.1f} L")

        if total_usd > 0:
            parts.append(f"${total_usd/1000000:.1f}M")

        return " + ".join(parts) if parts else "₹0"

    def _get_sources(self, subsidies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get sources for subsidies"""
        sources = []
        for subsidy in subsidies[:3]:
            sources.append({
                "title": f"{subsidy['title']} - {subsidy['government_body']}",
                "content": f"Official government subsidy/grant program",
                "url": subsidy.get("application_url"),
                "relevance_score": subsidy.get("eligibility_score", 0.8)
            })
        return sources


# Standalone test
async def main():
    """Test the Subsidies Analyzer Agent"""
    agent = SubsidiesAnalyzerAgent()

    test_query = "What subsidies and grants are available for my technology startup in India?"
    test_context = {
        "industry": "Technology",
        "stage": "seed",
        "country": "India",
        "entity_type": "Private Limited"
    }

    result = await agent.process(test_query, test_context)

    print("=" * 80)
    print("SUBSIDIES ANALYZER TEST")
    print("=" * 80)
    print(f"\nQuery: {test_query}")
    print(f"\nResponse:\n{result['answer']}")
    print(f"\nTotal Potential: {result['total_potential_funding']}")
    print(f"Subsidies Found: {len(result['subsidies'])}")
    print(f"Confidence: {result['confidence']:.2f}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
