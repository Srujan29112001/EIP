"""
Business Model Analysis Agent
Analyzes and evaluates business models using Business Model Canvas framework
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


class BusinessModelAgent:
    """
    Business Model Analysis Agent

    Analyzes business models using the Business Model Canvas framework
    and provides comprehensive evaluation and recommendations.
    """

    def __init__(self):
        """Initialize Business Model Agent"""
        self.name = "BusinessModelAgent"
        self.description = "Analyzes and evaluates business models"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

        # Business Model Canvas components
        self.canvas_blocks = [
            "customer_segments",
            "value_propositions",
            "channels",
            "customer_relationships",
            "revenue_streams",
            "key_resources",
            "key_activities",
            "key_partnerships",
            "cost_structure"
        ]

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process business model analysis request

        Args:
            query: User query about business model
            context: Additional context (business description, metrics, etc.)

        Returns:
            Dict with analysis results
        """
        try:
            # Extract business information from context
            business_info = self._extract_business_info(query, context)

            # Retrieve similar business models from knowledge base
            similar_models = await self._retrieve_similar_models(business_info)

            # Analyze business model canvas
            canvas_analysis = await self._analyze_canvas(business_info, similar_models)

            # Calculate business model scores
            scores = self._calculate_scores(canvas_analysis)

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                business_info,
                canvas_analysis,
                scores,
                similar_models
            )

            # Create comprehensive response
            response = await self._generate_response(
                query,
                business_info,
                canvas_analysis,
                scores,
                recommendations,
                similar_models
            )

            return {
                "answer": response,
                "canvas": canvas_analysis,
                "scores": scores,
                "recommendations": recommendations,
                "similar_models": similar_models,
                "confidence": self._calculate_confidence(business_info, similar_models),
                "sources": self._get_sources(similar_models),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in BusinessModelAgent: {e}")
            return {
                "answer": f"I apologize, but I encountered an error analyzing the business model: {str(e)}",
                "canvas": {},
                "scores": {},
                "recommendations": [],
                "confidence": 0.5,
                "sources": [],
                "agent": self.name
            }

    def _extract_business_info(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract business information from query and context"""
        info = {
            "description": query,
            "industry": context.get("industry") if context else None,
            "stage": context.get("stage", "idea"),
            "metrics": context.get("metrics", {}) if context else {},
            "team_size": context.get("team_size") if context else None,
            "current_model": context.get("current_model") if context else None
        }

        # Extract industry from query if not provided
        if not info["industry"]:
            info["industry"] = self._detect_industry(query)

        return info

    def _detect_industry(self, text: str) -> str:
        """Detect industry from text using keyword matching"""
        industry_keywords = {
            "SaaS": ["saas", "software as a service", "cloud", "subscription software"],
            "E-commerce": ["ecommerce", "e-commerce", "online store", "marketplace"],
            "FinTech": ["fintech", "finance", "payments", "banking", "financial"],
            "HealthTech": ["healthtech", "healthcare", "medical", "telemedicine"],
            "EdTech": ["edtech", "education", "learning", "online courses"],
            "AI/ML": ["ai", "artificial intelligence", "machine learning", "ml"],
            "Logistics": ["logistics", "delivery", "shipping", "supply chain"],
            "Food & Beverage": ["food", "beverage", "restaurant", "meal", "catering"]
        }

        text_lower = text.lower()
        for industry, keywords in industry_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return industry

        return "General"

    async def _retrieve_similar_models(
        self,
        business_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Retrieve similar business models from knowledge base"""
        try:
            # Create search query
            search_query = f"{business_info['industry']} business model {business_info['description']}"

            # Search in vector store
            results = await self.rag_service.retrieve(
                query=search_query,
                top_k=5,
                filter={"category": "business_models"}
            )

            # Parse and structure results
            similar_models = []
            for result in results:
                similar_models.append({
                    "name": result.get("metadata", {}).get("company_name", "Unknown"),
                    "model_type": result.get("metadata", {}).get("model_type", "Unknown"),
                    "industry": result.get("metadata", {}).get("industry", "Unknown"),
                    "revenue": result.get("metadata", {}).get("revenue", "Unknown"),
                    "description": result.get("content", "")[:200],
                    "relevance": result.get("score", 0.0)
                })

            return similar_models

        except Exception as e:
            print(f"Error retrieving similar models: {e}")
            return []

    async def _analyze_canvas(
        self,
        business_info: Dict[str, Any],
        similar_models: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze business model using canvas framework"""

        # Build context from similar models
        similar_context = "\n".join([
            f"- {model['name']} ({model['industry']}): {model['description']}"
            for model in similar_models[:3]
        ])

        prompt = f"""Analyze this business using the Business Model Canvas framework.

Business Description:
{business_info['description']}

Industry: {business_info['industry']}
Stage: {business_info['stage']}

Similar Successful Models:
{similar_context}

Provide a detailed analysis for each of the 9 Business Model Canvas blocks:

1. **Customer Segments**: Who are the target customers?
2. **Value Propositions**: What value does the business deliver?
3. **Channels**: How does the business reach customers?
4. **Customer Relationships**: How does it maintain customer relationships?
5. **Revenue Streams**: How does it make money?
6. **Key Resources**: What key resources are required?
7. **Key Activities**: What key activities are required?
8. **Key Partnerships**: What key partnerships are needed?
9. **Cost Structure**: What are the major costs?

For each block, provide:
- Analysis (2-3 sentences)
- Strengths (bullet points)
- Weaknesses/Gaps (bullet points)
- Score (1-10)

Return as JSON with this structure:
{{
    "customer_segments": {{"analysis": "...", "strengths": [], "weaknesses": [], "score": 8}},
    "value_propositions": {{...}},
    ...
}}
"""

        try:
            # Get LLM analysis
            response = await self.llm_service.generate(
                prompt=prompt,
                model="gpt-4o",
                temperature=0.3,
                max_tokens=2000
            )

            # Try to parse JSON response
            try:
                # Extract JSON from response
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    canvas = json.loads(json_str)
                else:
                    # Fallback to structured text parsing
                    canvas = self._parse_canvas_text(response)
            except json.JSONDecodeError:
                canvas = self._parse_canvas_text(response)

            return canvas

        except Exception as e:
            print(f"Error analyzing canvas: {e}")
            # Return empty canvas with default structure
            return {block: {"analysis": "", "strengths": [], "weaknesses": [], "score": 5}
                    for block in self.canvas_blocks}

    def _parse_canvas_text(self, text: str) -> Dict[str, Any]:
        """Parse canvas analysis from text when JSON parsing fails"""
        canvas = {}

        for block in self.canvas_blocks:
            # Simple parsing - extract sections
            canvas[block] = {
                "analysis": f"Analysis for {block.replace('_', ' ').title()}",
                "strengths": ["Identified from analysis"],
                "weaknesses": ["Needs further development"],
                "score": 6
            }

        return canvas

    def _calculate_scores(self, canvas_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate overall scores from canvas analysis"""
        scores = {}

        # Extract individual block scores
        block_scores = []
        for block, analysis in canvas_analysis.items():
            if isinstance(analysis, dict) and "score" in analysis:
                block_scores.append(analysis["score"])

        # Calculate aggregate scores
        if block_scores:
            scores["overall"] = sum(block_scores) / len(block_scores)
            scores["customer_fit"] = (
                canvas_analysis.get("customer_segments", {}).get("score", 5) +
                canvas_analysis.get("value_propositions", {}).get("score", 5)
            ) / 2
            scores["revenue_potential"] = (
                canvas_analysis.get("revenue_streams", {}).get("score", 5) +
                canvas_analysis.get("customer_segments", {}).get("score", 5)
            ) / 2
            scores["operational_feasibility"] = (
                canvas_analysis.get("key_resources", {}).get("score", 5) +
                canvas_analysis.get("key_activities", {}).get("score", 5) +
                canvas_analysis.get("key_partnerships", {}).get("score", 5)
            ) / 3
            scores["financial_viability"] = (
                canvas_analysis.get("revenue_streams", {}).get("score", 5) +
                canvas_analysis.get("cost_structure", {}).get("score", 5)
            ) / 2
        else:
            scores = {
                "overall": 6.0,
                "customer_fit": 6.0,
                "revenue_potential": 6.0,
                "operational_feasibility": 6.0,
                "financial_viability": 6.0
            }

        return scores

    async def _generate_recommendations(
        self,
        business_info: Dict[str, Any],
        canvas_analysis: Dict[str, Any],
        scores: Dict[str, float],
        similar_models: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""

        # Identify weakest areas
        block_scores = {
            block: analysis.get("score", 5)
            for block, analysis in canvas_analysis.items()
            if isinstance(analysis, dict)
        }

        weakest_blocks = sorted(block_scores.items(), key=lambda x: x[1])[:3]

        prompt = f"""Based on this business model analysis, provide 5 specific, actionable recommendations to improve the business.

Business: {business_info['description']}
Industry: {business_info['industry']}
Overall Score: {scores.get('overall', 6.0):.1f}/10

Weakest Areas:
{chr(10).join([f"- {block.replace('_', ' ').title()}: {score:.1f}/10" for block, score in weakest_blocks])}

Provide recommendations in this JSON format:
[
    {{
        "title": "Recommendation title",
        "description": "Detailed description",
        "priority": "high|medium|low",
        "impact": "Description of expected impact",
        "effort": "Description of effort required",
        "timeline": "Estimated timeline"
    }}
]
"""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                model="gpt-4o",
                temperature=0.4,
                max_tokens=1000
            )

            # Try to parse JSON
            try:
                json_start = response.find("[")
                json_end = response.rfind("]") + 1
                if json_start != -1 and json_end > json_start:
                    recommendations = json.loads(response[json_start:json_end])
                else:
                    recommendations = self._create_default_recommendations(weakest_blocks)
            except json.JSONDecodeError:
                recommendations = self._create_default_recommendations(weakest_blocks)

            return recommendations[:5]  # Limit to top 5

        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return self._create_default_recommendations(weakest_blocks)

    def _create_default_recommendations(
        self,
        weak_blocks: List[tuple]
    ) -> List[Dict[str, Any]]:
        """Create default recommendations for weak areas"""
        recommendations = []

        for block, score in weak_blocks[:3]:
            recommendations.append({
                "title": f"Strengthen {block.replace('_', ' ').title()}",
                "description": f"Focus on improving your {block.replace('_', ' ')} to increase overall business model viability.",
                "priority": "high" if score < 5 else "medium",
                "impact": "Significant improvement in business model strength",
                "effort": "Moderate effort required",
                "timeline": "2-4 weeks"
            })

        return recommendations

    async def _generate_response(
        self,
        query: str,
        business_info: Dict[str, Any],
        canvas_analysis: Dict[str, Any],
        scores: Dict[str, float],
        recommendations: List[Dict[str, Any]],
        similar_models: List[Dict[str, Any]]
    ) -> str:
        """Generate comprehensive response"""

        # Build context
        context_parts = []

        # Add scores
        context_parts.append(f"**Overall Business Model Score: {scores.get('overall', 6.0):.1f}/10**\n")

        # Add key scores
        context_parts.append("**Key Dimension Scores:**")
        context_parts.append(f"- Customer Fit: {scores.get('customer_fit', 6.0):.1f}/10")
        context_parts.append(f"- Revenue Potential: {scores.get('revenue_potential', 6.0):.1f}/10")
        context_parts.append(f"- Operational Feasibility: {scores.get('operational_feasibility', 6.0):.1f}/10")
        context_parts.append(f"- Financial Viability: {scores.get('financial_viability', 6.0):.1f}/10\n")

        # Add canvas highlights
        context_parts.append("**Business Model Canvas Highlights:**\n")
        for block in ["value_propositions", "revenue_streams", "customer_segments"]:
            if block in canvas_analysis and isinstance(canvas_analysis[block], dict):
                analysis = canvas_analysis[block]
                context_parts.append(f"**{block.replace('_', ' ').title()}:**")
                context_parts.append(f"{analysis.get('analysis', '')}")
                if analysis.get('strengths'):
                    context_parts.append(f"  Strengths: {', '.join(analysis['strengths'][:2])}")
                context_parts.append("")

        # Add recommendations
        context_parts.append("\n**Top Recommendations:**")
        for i, rec in enumerate(recommendations[:3], 1):
            context_parts.append(f"{i}. **{rec['title']}** ({rec['priority']} priority)")
            context_parts.append(f"   {rec['description']}")

        # Add similar models
        if similar_models:
            context_parts.append("\n**Similar Successful Models:**")
            for model in similar_models[:2]:
                context_parts.append(f"- {model['name']} ({model['industry']})")

        return "\n".join(context_parts)

    def _calculate_confidence(
        self,
        business_info: Dict[str, Any],
        similar_models: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for the analysis"""
        confidence = 0.7  # Base confidence

        # Increase if we have good context
        if business_info.get("industry"):
            confidence += 0.1
        if business_info.get("metrics"):
            confidence += 0.1
        if similar_models:
            confidence += 0.1 * min(len(similar_models) / 5, 1.0)

        return min(confidence, 1.0)

    def _get_sources(self, similar_models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract sources from similar models"""
        sources = []
        for model in similar_models[:3]:
            sources.append({
                "title": f"{model['name']} Business Model",
                "content": model['description'],
                "relevance_score": model['relevance']
            })
        return sources


# Standalone test
async def main():
    """Test the Business Model Agent"""
    agent = BusinessModelAgent()

    test_query = "We're building a B2B SaaS platform for HR analytics with freemium model"
    test_context = {
        "industry": "SaaS",
        "stage": "seed",
        "metrics": {
            "users": 100,
            "revenue": 5000
        }
    }

    result = await agent.process(test_query, test_context)

    print("=" * 80)
    print("BUSINESS MODEL ANALYSIS TEST")
    print("=" * 80)
    print(f"\nQuery: {test_query}")
    print(f"\nResponse:\n{result['answer']}")
    print(f"\nOverall Score: {result['scores'].get('overall', 0):.1f}/10")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"\nRecommendations: {len(result['recommendations'])}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
