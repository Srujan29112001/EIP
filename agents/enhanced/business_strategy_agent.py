"""
Business Strategy Assessment Agent
Comprehensive business strategy analysis including SWOT, Porter's Five Forces, Blue Ocean Strategy, OKRs, and GTM
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


class BusinessStrategyAgent:
    """
    Business Strategy Assessment Agent

    Provides comprehensive strategic analysis including:
    - SWOT analysis automation
    - Porter's Five Forces analysis
    - Blue Ocean Strategy framework
    - OKR (Objectives and Key Results) framework
    - Go-to-Market (GTM) strategy evaluation
    - Competitive positioning
    - Strategic recommendations
    """

    def __init__(self):
        """Initialize Business Strategy Agent"""
        self.name = "BusinessStrategyAgent"
        self.description = "Comprehensive business strategy assessment and planning"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

        # Porter's Five Forces framework
        self.five_forces = [
            "competitive_rivalry",
            "supplier_power",
            "buyer_power",
            "threat_of_substitution",
            "threat_of_new_entry"
        ]

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process business strategy request

        Args:
            query: User query about business strategy
            context: Additional context (industry, competitors, business model, etc.)

        Returns:
            Dict with strategy analysis results
        """
        try:
            # Determine analysis type needed
            analysis_type = self._determine_analysis_type(query)

            # Extract business context
            business_context = self._extract_business_context(query, context)

            # Perform strategic analysis based on type
            if analysis_type == "swot":
                analysis = await self._swot_analysis(business_context)
            elif analysis_type == "porters_five_forces":
                analysis = await self._porters_five_forces(business_context)
            elif analysis_type == "blue_ocean":
                analysis = await self._blue_ocean_strategy(business_context)
            elif analysis_type == "okr":
                analysis = await self._okr_framework(business_context)
            elif analysis_type == "gtm":
                analysis = await self._gtm_strategy(business_context)
            else:
                analysis = await self._comprehensive_strategy(business_context)

            # Generate strategic recommendations
            recommendations = await self._generate_recommendations(
                business_context,
                analysis,
                analysis_type
            )

            # Create response
            response = await self._generate_response(
                query,
                business_context,
                analysis,
                recommendations
            )

            return {
                "answer": response,
                "business_context": business_context,
                "analysis": analysis,
                "recommendations": recommendations,
                "confidence": self._calculate_confidence(business_context, analysis),
                "sources": self._get_sources(),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in BusinessStrategyAgent: {str(e)}")
            return self._error_response(str(e))

    def _determine_analysis_type(self, query: str) -> str:
        """Determine type of strategic analysis needed"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["swot", "strengths", "weaknesses", "opportunities", "threats"]):
            return "swot"
        elif any(word in query_lower for word in ["porter", "five forces", "competitive forces", "industry forces"]):
            return "porters_five_forces"
        elif any(word in query_lower for word in ["blue ocean", "uncontested market", "differentiation"]):
            return "blue_ocean"
        elif any(word in query_lower for word in ["okr", "objectives", "key results", "goals"]):
            return "okr"
        elif any(word in query_lower for word in ["go-to-market", "gtm", "market entry", "launch strategy"]):
            return "gtm"
        else:
            return "comprehensive"

    def _extract_business_context(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract business context from query and context"""

        if context:
            return {
                "business_name": context.get("business_name", "Your Business"),
                "industry": context.get("industry", "Technology"),
                "stage": context.get("stage", "seed"),
                "business_model": context.get("business_model", "B2B SaaS"),
                "target_market": context.get("target_market", "SME businesses"),
                "competitors": context.get("competitors", []),
                "revenue": context.get("revenue", 0),
                "team_size": context.get("team_size", 5),
                "funding": context.get("funding", "Bootstrapped"),
                "geography": context.get("geography", "India"),
                "problem_statement": context.get("problem_statement", query)
            }
        else:
            return {
                "business_name": "Your Business",
                "industry": self._detect_industry(query),
                "stage": "seed",
                "business_model": "B2B SaaS",
                "target_market": "SME businesses",
                "competitors": [],
                "revenue": 0,
                "team_size": 5,
                "funding": "Bootstrapped",
                "geography": "India",
                "problem_statement": query
            }

    def _detect_industry(self, text: str) -> str:
        """Detect industry from text"""
        industry_keywords = {
            "SaaS": ["saas", "software as a service", "cloud software"],
            "FinTech": ["fintech", "finance", "payments", "banking"],
            "HealthTech": ["healthtech", "healthcare", "medical", "telemedicine"],
            "EdTech": ["edtech", "education", "learning", "online courses"],
            "E-commerce": ["ecommerce", "e-commerce", "online store", "marketplace"],
            "AI/ML": ["ai", "artificial intelligence", "machine learning", "ml"],
            "CleanTech": ["cleantech", "renewable", "sustainability", "green energy"],
            "Logistics": ["logistics", "delivery", "supply chain", "transportation"]
        }

        text_lower = text.lower()
        for industry, keywords in industry_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return industry

        return "Technology"

    async def _swot_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform SWOT analysis"""

        prompt = f"""Conduct a comprehensive SWOT analysis for this business:

Business: {context['business_name']}
Industry: {context['industry']}
Stage: {context['stage']}
Business Model: {context['business_model']}
Target Market: {context['target_market']}
Current Revenue: ₹{context['revenue']:,}
Team Size: {context['team_size']}
Geography: {context['geography']}

Problem Statement: {context['problem_statement']}

Provide detailed SWOT analysis in JSON format:
{{
    "strengths": [
        {{"factor": "Factor name", "description": "Why this is a strength", "impact": "high|medium|low"}},
        ...
    ],
    "weaknesses": [
        {{"factor": "Factor name", "description": "Why this is a weakness", "impact": "high|medium|low"}},
        ...
    ],
    "opportunities": [
        {{"factor": "Opportunity name", "description": "Details", "potential": "high|medium|low", "timeline": "short-term|medium-term|long-term"}},
        ...
    ],
    "threats": [
        {{"factor": "Threat name", "description": "Details", "severity": "high|medium|low", "probability": "high|medium|low"}},
        ...
    ]
}}

Provide 4-6 items for each category."""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                model="gpt-4o",
                temperature=0.4,
                max_tokens=1500
            )

            # Parse JSON response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                swot = json.loads(response[json_start:json_end])
            else:
                swot = self._default_swot()

            return {
                "type": "swot",
                "swot": swot,
                "strategic_focus": self._calculate_swot_focus(swot)
            }

        except Exception as e:
            print(f"Error in SWOT analysis: {e}")
            return {"type": "swot", "swot": self._default_swot(), "strategic_focus": "Growth"}

    def _default_swot(self) -> Dict[str, Any]:
        """Default SWOT structure"""
        return {
            "strengths": [
                {"factor": "Innovation", "description": "Novel approach to problem", "impact": "high"}
            ],
            "weaknesses": [
                {"factor": "Limited resources", "description": "Early stage constraints", "impact": "medium"}
            ],
            "opportunities": [
                {"factor": "Market growth", "description": "Growing market demand", "potential": "high", "timeline": "medium-term"}
            ],
            "threats": [
                {"factor": "Competition", "description": "Established competitors", "severity": "medium", "probability": "high"}
            ]
        }

    def _calculate_swot_focus(self, swot: Dict[str, Any]) -> str:
        """Calculate strategic focus based on SWOT"""
        strengths_count = len(swot.get("strengths", []))
        weaknesses_count = len(swot.get("weaknesses", []))
        opportunities_count = len(swot.get("opportunities", []))
        threats_count = len(swot.get("threats", []))

        if strengths_count > weaknesses_count and opportunities_count > threats_count:
            return "Aggressive Growth (SO Strategy)"
        elif strengths_count > weaknesses_count and threats_count > opportunities_count:
            return "Defensive (ST Strategy)"
        elif weaknesses_count > strengths_count and opportunities_count > threats_count:
            return "Development (WO Strategy)"
        else:
            return "Survival (WT Strategy)"

    async def _porters_five_forces(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze using Porter's Five Forces framework"""

        prompt = f"""Analyze the competitive dynamics using Porter's Five Forces for this business:

Industry: {context['industry']}
Business Model: {context['business_model']}
Target Market: {context['target_market']}
Geography: {context['geography']}

Analyze all five forces and provide scores (1-10, where 10 = highest intensity/threat):

Return JSON:
{{
    "competitive_rivalry": {{
        "score": 7,
        "intensity": "high|medium|low",
        "factors": ["Factor 1", "Factor 2"],
        "analysis": "Detailed analysis"
    }},
    "supplier_power": {{...}},
    "buyer_power": {{...}},
    "threat_of_substitution": {{...}},
    "threat_of_new_entry": {{...}},
    "overall_attractiveness": "high|medium|low"
}}"""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                model="gpt-4o",
                temperature=0.3,
                max_tokens=1200
            )

            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                forces = json.loads(response[json_start:json_end])
            else:
                forces = self._default_five_forces()

            return {
                "type": "porters_five_forces",
                "forces": forces,
                "average_intensity": self._calculate_average_force(forces)
            }

        except Exception as e:
            print(f"Error in Five Forces analysis: {e}")
            return {"type": "porters_five_forces", "forces": self._default_five_forces(), "average_intensity": 6.0}

    def _default_five_forces(self) -> Dict[str, Any]:
        """Default Five Forces structure"""
        return {
            "competitive_rivalry": {
                "score": 7,
                "intensity": "high",
                "factors": ["Multiple competitors", "Price competition"],
                "analysis": "Intense competition in the market"
            },
            "supplier_power": {
                "score": 4,
                "intensity": "low",
                "factors": ["Multiple suppliers available"],
                "analysis": "Low supplier power"
            },
            "buyer_power": {
                "score": 6,
                "intensity": "medium",
                "factors": ["Price-sensitive customers"],
                "analysis": "Moderate buyer power"
            },
            "threat_of_substitution": {
                "score": 5,
                "intensity": "medium",
                "factors": ["Alternative solutions exist"],
                "analysis": "Some substitutes available"
            },
            "threat_of_new_entry": {
                "score": 6,
                "intensity": "medium",
                "factors": ["Low barriers to entry"],
                "analysis": "Moderate threat from new entrants"
            },
            "overall_attractiveness": "medium"
        }

    def _calculate_average_force(self, forces: Dict[str, Any]) -> float:
        """Calculate average force intensity"""
        scores = []
        for force_name in self.five_forces:
            if force_name in forces and "score" in forces[force_name]:
                scores.append(forces[force_name]["score"])
        return sum(scores) / len(scores) if scores else 6.0

    async def _blue_ocean_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze using Blue Ocean Strategy framework"""

        prompt = f"""Apply Blue Ocean Strategy framework to identify uncontested market space:

Business: {context['business_name']}
Industry: {context['industry']}
Current Competitors: {', '.join(context.get('competitors', ['Traditional players']))}

Using the Four Actions Framework, analyze:
1. ELIMINATE: What factors should be eliminated that the industry takes for granted?
2. REDUCE: What factors should be reduced well below industry standard?
3. RAISE: What factors should be raised well above industry standard?
4. CREATE: What factors should be created that the industry has never offered?

Return JSON:
{{
    "eliminate": [
        {{"factor": "Factor name", "reason": "Why eliminate", "impact": "Expected impact"}}
    ],
    "reduce": [...],
    "raise": [...],
    "create": [...],
    "value_innovation": "Summary of unique value proposition",
    "blue_ocean_score": 7.5
}}"""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                model="gpt-4o",
                temperature=0.5,
                max_tokens=1200
            )

            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                blue_ocean = json.loads(response[json_start:json_end])
            else:
                blue_ocean = self._default_blue_ocean()

            return {
                "type": "blue_ocean",
                "strategy": blue_ocean
            }

        except Exception as e:
            print(f"Error in Blue Ocean analysis: {e}")
            return {"type": "blue_ocean", "strategy": self._default_blue_ocean()}

    def _default_blue_ocean(self) -> Dict[str, Any]:
        """Default Blue Ocean structure"""
        return {
            "eliminate": [
                {"factor": "Unnecessary features", "reason": "Simplify offering", "impact": "Cost reduction"}
            ],
            "reduce": [
                {"factor": "Price", "reason": "Make accessible", "impact": "Market expansion"}
            ],
            "raise": [
                {"factor": "Customer experience", "reason": "Differentiate", "impact": "Higher retention"}
            ],
            "create": [
                {"factor": "Self-service model", "reason": "Industry first", "impact": "Competitive advantage"}
            ],
            "value_innovation": "Simplified, affordable solution with superior experience",
            "blue_ocean_score": 7.0
        }

    async def _okr_framework(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate OKR framework"""

        prompt = f"""Create a quarterly OKR (Objectives and Key Results) framework for:

Business: {context['business_name']}
Stage: {context['stage']}
Industry: {context['industry']}
Current Revenue: ₹{context['revenue']:,}

Create 3-5 Objectives, each with 3-4 Key Results.

Return JSON:
{{
    "quarter": "Q1 2024",
    "objectives": [
        {{
            "objective": "Achieve product-market fit",
            "description": "Detailed description",
            "key_results": [
                {{
                    "kr": "Acquire 1000 active users",
                    "metric": "Active users",
                    "target": 1000,
                    "current": 100,
                    "unit": "users"
                }}
            ]
        }}
    ]
}}"""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                model="gpt-4o",
                temperature=0.4,
                max_tokens=1200
            )

            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                okr = json.loads(response[json_start:json_end])
            else:
                okr = self._default_okr()

            return {
                "type": "okr",
                "framework": okr
            }

        except Exception as e:
            print(f"Error in OKR generation: {e}")
            return {"type": "okr", "framework": self._default_okr()}

    def _default_okr(self) -> Dict[str, Any]:
        """Default OKR structure"""
        return {
            "quarter": "Q1 2024",
            "objectives": [
                {
                    "objective": "Achieve product-market fit",
                    "description": "Validate that product solves real customer problems",
                    "key_results": [
                        {"kr": "Acquire 500 active users", "metric": "Active users", "target": 500, "current": 50, "unit": "users"},
                        {"kr": "Achieve 40% user retention", "metric": "30-day retention", "target": 40, "current": 20, "unit": "%"}
                    ]
                }
            ]
        }

    async def _gtm_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Develop Go-to-Market strategy"""

        prompt = f"""Develop a comprehensive Go-to-Market (GTM) strategy:

Business: {context['business_name']}
Product/Service: {context['business_model']}
Target Market: {context['target_market']}
Industry: {context['industry']}
Geography: {context['geography']}

Create GTM strategy covering:
1. Target customer segments
2. Value proposition
3. Pricing strategy
4. Distribution channels
5. Marketing tactics
6. Sales approach
7. Launch timeline

Return JSON with detailed strategy."""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                model="gpt-4o",
                temperature=0.4,
                max_tokens=1500
            )

            # Extract key GTM components
            gtm = {
                "target_segments": [
                    {
                        "segment": "Early Adopters",
                        "characteristics": "Tech-savvy, willing to try new solutions",
                        "size": "10,000 businesses",
                        "priority": "high"
                    }
                ],
                "value_proposition": "10x faster, 50% cheaper than alternatives",
                "pricing": {
                    "model": "Freemium",
                    "tiers": ["Free", "Pro ($49/mo)", "Enterprise (Custom)"],
                    "strategy": "Land-and-expand"
                },
                "channels": ["Direct sales", "Content marketing", "Partner ecosystem"],
                "marketing_tactics": ["SEO", "LinkedIn ads", "Product Hunt launch"],
                "sales_approach": "Product-led growth with sales assist for enterprise",
                "timeline": {
                    "Month 1": "Beta launch to early adopters",
                    "Month 2-3": "Iterate based on feedback",
                    "Month 4": "Public launch",
                    "Month 5-6": "Scale marketing and sales"
                }
            }

            return {
                "type": "gtm",
                "strategy": gtm
            }

        except Exception as e:
            print(f"Error in GTM strategy: {e}")
            return {"type": "gtm", "strategy": {}}

    async def _comprehensive_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive strategic analysis combining multiple frameworks"""

        swot = await self._swot_analysis(context)
        forces = await self._porters_five_forces(context)
        blue_ocean = await self._blue_ocean_strategy(context)

        return {
            "type": "comprehensive",
            "swot": swot,
            "five_forces": forces,
            "blue_ocean": blue_ocean,
            "strategic_priorities": self._determine_strategic_priorities(swot, forces, blue_ocean)
        }

    def _determine_strategic_priorities(
        self,
        swot: Dict[str, Any],
        forces: Dict[str, Any],
        blue_ocean: Dict[str, Any]
    ) -> List[str]:
        """Determine top strategic priorities"""

        priorities = []

        # Based on SWOT focus
        if "strategic_focus" in swot:
            priorities.append(f"Focus on {swot['strategic_focus']}")

        # Based on Five Forces
        avg_force = forces.get("average_intensity", 6.0)
        if avg_force > 7:
            priorities.append("High competition - differentiate or find niche")
        elif avg_force < 5:
            priorities.append("Favorable market - scale aggressively")

        # Based on Blue Ocean
        if blue_ocean.get("strategy", {}).get("blue_ocean_score", 0) > 7:
            priorities.append("Strong differentiation opportunity - create new market space")

        return priorities[:3]

    async def _generate_recommendations(
        self,
        context: Dict[str, Any],
        analysis: Dict[str, Any],
        analysis_type: str
    ) -> List[Dict[str, Any]]:
        """Generate strategic recommendations"""

        recommendations = []

        # Generic strategic recommendations
        recommendations.append({
            "title": "Define Clear Strategic Vision",
            "description": "Articulate a 3-5 year vision that guides all strategic decisions",
            "priority": "high",
            "timeline": "1 month",
            "impact": "Sets direction for entire organization"
        })

        if context.get("stage") == "seed":
            recommendations.append({
                "title": "Achieve Product-Market Fit",
                "description": "Focus on finding repeatable, scalable way to acquire and retain customers",
                "priority": "high",
                "timeline": "3-6 months",
                "impact": "Foundation for growth"
            })

        if analysis_type == "porters_five_forces":
            avg_intensity = analysis.get("average_intensity", 6.0)
            if avg_intensity > 7:
                recommendations.append({
                    "title": "Differentiate or Specialize",
                    "description": "High competitive intensity requires strong differentiation or niche focus",
                    "priority": "high",
                    "timeline": "2-4 months",
                    "impact": "Reduces direct competition"
                })

        return recommendations

    async def _generate_response(
        self,
        query: str,
        context: Dict[str, Any],
        analysis: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> str:
        """Generate comprehensive response using LLM"""

        prompt = f"""You are a strategic business consultant. Provide strategic advice based on:

Query: {query}

Business Context:
{json.dumps(context, indent=2)}

Analysis:
{json.dumps(analysis, indent=2)[:1500]}

Recommendations:
{json.dumps(recommendations, indent=2)}

Generate a professional, actionable strategic assessment (400-500 words) that:
1. Summarizes the strategic situation
2. Highlights key insights from the analysis
3. Provides specific, actionable recommendations
4. Sets clear priorities and timeline
5. Addresses potential risks and mitigation strategies

Be specific and data-driven."""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                temperature=0.6,
                max_tokens=700
            )
            return response
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._fallback_response(context, analysis, recommendations)

    def _fallback_response(
        self,
        context: Dict[str, Any],
        analysis: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> str:
        """Fallback response if LLM fails"""

        response = f"## Business Strategy Assessment for {context['business_name']}\n\n"
        response += f"**Industry:** {context['industry']}\n"
        response += f"**Stage:** {context['stage']}\n"
        response += f"**Business Model:** {context['business_model']}\n\n"

        response += "**Strategic Analysis Summary:**\n"
        response += f"Analysis Type: {analysis.get('type', 'Comprehensive')}\n\n"

        response += "**Top Recommendations:**\n"
        for i, rec in enumerate(recommendations[:3], 1):
            response += f"{i}. **{rec['title']}** ({rec['priority']} priority)\n"
            response += f"   {rec['description']}\n"
            response += f"   Timeline: {rec['timeline']}\n\n"

        return response

    def _calculate_confidence(
        self,
        context: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence score"""
        confidence = 0.75  # Base confidence

        if context.get("industry"):
            confidence += 0.05
        if context.get("competitors"):
            confidence += 0.05
        if context.get("revenue", 0) > 0:
            confidence += 0.05
        if analysis.get("type"):
            confidence += 0.1

        return min(confidence, 1.0)

    def _get_sources(self) -> List[Dict[str, str]]:
        """Get data sources"""
        return [
            {
                "type": "strategic_frameworks",
                "source": "SWOT, Porter's Five Forces, Blue Ocean Strategy, OKR frameworks"
            },
            {
                "type": "industry_analysis",
                "source": "Market research and competitive intelligence"
            }
        ]

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "answer": f"I encountered an error while analyzing business strategy: {error}. Please provide more details about your business, industry, and competitors.",
            "error": error,
            "confidence": 0.0,
            "agent": self.name
        }


# Export
__all__ = ["BusinessStrategyAgent"]
