"""
Human Basic Needs Agent
Maslow's hierarchy mapping, market sizing for necessity vs luxury, basic needs gap analysis, affordability analysis
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


class HumanNeedsAgent:
    """
    Human Basic Needs Agent

    Analyzes businesses through lens of human needs:
    - Maslow's Hierarchy of Needs mapping
    - Market sizing for necessity vs. luxury products
    - Basic needs gap analysis (unmet needs identification)
    - Affordability analysis and price sensitivity
    - Bottom of Pyramid (BoP) market opportunities
    - Need-based product positioning
    - Recession resistance analysis
    """

    def __init__(self):
        """Initialize Human Needs Agent"""
        self.name = "HumanNeedsAgent"
        self.description = "Human needs analysis and market opportunity assessment"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

        # Maslow's hierarchy levels
        self.maslows_hierarchy = {
            "physiological": {
                "level": 1,
                "description": "Basic survival needs",
                "needs": ["Food", "Water", "Shelter", "Clothing", "Sleep", "Healthcare"],
                "market_size": "Largest - everyone needs",
                "price_sensitivity": "High",
                "recession_resistance": "Very High",
                "examples": ["Food delivery", "Water purifiers", "Housing", "Basic clothing", "Healthcare"]
            },
            "safety": {
                "level": 2,
                "description": "Security and protection",
                "needs": ["Physical safety", "Financial security", "Health security", "Employment", "Property"],
                "market_size": "Very Large",
                "price_sensitivity": "High",
                "recession_resistance": "High",
                "examples": ["Insurance", "Security systems", "Banking", "Job platforms", "Legal services"]
            },
            "love_belonging": {
                "level": 3,
                "description": "Social connections and relationships",
                "needs": ["Friendship", "Family", "Intimacy", "Community", "Belonging"],
                "market_size": "Large",
                "price_sensitivity": "Medium",
                "recession_resistance": "Medium",
                "examples": ["Social media", "Dating apps", "Community platforms", "Event platforms"]
            },
            "esteem": {
                "level": 4,
                "description": "Respect, status, recognition",
                "needs": ["Self-esteem", "Status", "Recognition", "Achievement", "Respect"],
                "market_size": "Medium",
                "price_sensitivity": "Medium-Low",
                "recession_resistance": "Medium-Low",
                "examples": ["Luxury goods", "Education credentials", "Professional networking", "Awards"]
            },
            "self_actualization": {
                "level": 5,
                "description": "Personal growth and fulfillment",
                "needs": ["Creativity", "Problem solving", "Purpose", "Authenticity", "Growth"],
                "market_size": "Smaller",
                "price_sensitivity": "Low",
                "recession_resistance": "Low",
                "examples": ["Personal coaching", "Creative tools", "Meditation apps", "Self-help"]
            }
        }

        # Income segments (India context)
        self.income_segments = {
            "bottom_of_pyramid": {
                "annual_income_range": "< ₹3 lakh",
                "population": "60% of India (800M people)",
                "purchasing_power": "Very Limited",
                "focus_needs": ["Physiological", "Safety"],
                "business_opportunity": "High volume, ultra-low margins, innovative delivery",
                "examples": ["Jio", "Patanjali", "Microfinance", "Low-cost housing"]
            },
            "lower_middle": {
                "annual_income_range": "₹3-6 lakh",
                "population": "20% of India (270M people)",
                "purchasing_power": "Limited",
                "focus_needs": ["Physiological", "Safety", "Love/Belonging"],
                "business_opportunity": "Aspiration-driven, value-conscious",
                "examples": ["Affordable smartphones", "Two-wheelers", "Budget brands"]
            },
            "middle": {
                "annual_income_range": "₹6-15 lakh",
                "population": "15% of India (200M people)",
                "purchasing_power": "Moderate",
                "focus_needs": ["Safety", "Love/Belonging", "Esteem"],
                "business_opportunity": "Quality seekers, brand conscious",
                "examples": ["E-commerce", "Branded products", "Education", "Health insurance"]
            },
            "upper_middle": {
                "annual_income_range": "₹15-30 lakh",
                "population": "4% of India (50M people)",
                "purchasing_power": "Good",
                "focus_needs": ["Love/Belonging", "Esteem", "Self-actualization"],
                "business_opportunity": "Premium products, experiences",
                "examples": ["International travel", "Luxury goods", "Premium education"]
            },
            "affluent": {
                "annual_income_range": "> ₹30 lakh",
                "population": "1% of India (13M people)",
                "purchasing_power": "High",
                "focus_needs": ["Esteem", "Self-actualization"],
                "business_opportunity": "Ultra-premium, exclusivity",
                "examples": ["Luxury cars", "Private banking", "Concierge services"]
            }
        }

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process human needs analysis request

        Args:
            query: User query about needs/market
            context: Business context

        Returns:
            Dict with needs analysis results
        """
        try:
            # Determine analysis type
            analysis_type = self._determine_analysis_type(query)

            # Extract business context
            business_context = self._extract_business_context(query, context)

            # Perform analysis
            if analysis_type == "maslow_mapping":
                analysis = await self._map_to_maslows_hierarchy(business_context)
            elif analysis_type == "market_sizing":
                analysis = await self._market_sizing_necessity_vs_luxury(business_context)
            elif analysis_type == "affordability":
                analysis = await self._affordability_analysis(business_context)
            elif analysis_type == "gap_analysis":
                analysis = await self._needs_gap_analysis(business_context)
            else:
                analysis = await self._comprehensive_needs_analysis(business_context)

            # Generate recommendations
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
                "analysis": analysis,
                "recommendations": recommendations,
                "confidence": 0.87,
                "sources": self._get_sources(),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in HumanNeedsAgent: {str(e)}")
            return self._error_response(str(e))

    def _determine_analysis_type(self, query: str) -> str:
        """Determine type of needs analysis"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["maslow", "hierarchy", "needs level"]):
            return "maslow_mapping"
        elif any(word in query_lower for word in ["market size", "tam", "necessity", "luxury"]):
            return "market_sizing"
        elif any(word in query_lower for word in ["afford", "price", "income", "purchasing power"]):
            return "affordability"
        elif any(word in query_lower for word in ["gap", "unmet needs", "opportunity"]):
            return "gap_analysis"
        else:
            return "comprehensive"

    def _extract_business_context(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract business context"""

        if context:
            return {
                "product": context.get("product", "Product"),
                "industry": context.get("industry", "Technology"),
                "target_segment": context.get("target_segment", "middle"),
                "price_point": context.get("price_point", 1000),
                "geography": context.get("geography", "India"),
                "problem_solving": context.get("problem", query)
            }
        else:
            return {
                "product": "Product",
                "industry": self._detect_industry(query),
                "target_segment": "middle",
                "price_point": 1000,
                "geography": "India",
                "problem_solving": query
            }

    def _detect_industry(self, text: str) -> str:
        """Detect industry"""
        industry_keywords = {
            "Food": ["food", "meal", "restaurant", "delivery"],
            "Housing": ["housing", "real estate", "shelter", "home"],
            "Healthcare": ["health", "medical", "doctor", "hospital"],
            "Education": ["education", "learning", "school", "training"],
            "Finance": ["finance", "banking", "insurance", "money"],
            "Transportation": ["transport", "mobility", "ride", "delivery"]
        }

        text_lower = text.lower()
        for industry, keywords in industry_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return industry

        return "Technology"

    async def _map_to_maslows_hierarchy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Map product/service to Maslow's hierarchy"""

        # Analyze which level(s) the product addresses
        product = context["product"]
        industry = context["industry"]

        # Industry to needs mapping
        industry_mapping = {
            "Food": ["physiological"],
            "Housing": ["physiological", "safety"],
            "Healthcare": ["physiological", "safety"],
            "Finance": ["safety"],
            "Education": ["safety", "esteem", "self_actualization"],
            "Social Media": ["love_belonging"],
            "Luxury": ["esteem"],
            "Technology": ["safety", "esteem"]
        }

        primary_levels = industry_mapping.get(industry, ["safety"])

        # Get details for each level
        needs_addressed = []
        for level in primary_levels:
            level_data = self.maslows_hierarchy[level].copy()
            level_data["level_name"] = level
            needs_addressed.append(level_data)

        # Calculate market potential
        primary_level = needs_addressed[0]
        market_potential = {
            "market_size": primary_level["market_size"],
            "recession_resistance": primary_level["recession_resistance"],
            "price_sensitivity": primary_level["price_sensitivity"],
            "competitive_intensity": "High" if primary_level["level"] <= 2 else "Medium"
        }

        return {
            "type": "maslow_mapping",
            "primary_need_level": primary_levels[0],
            "needs_addressed": needs_addressed,
            "market_potential": market_potential,
            "strategic_insight": self._get_strategic_insight(primary_levels[0])
        }

    def _get_strategic_insight(self, level: str) -> str:
        """Get strategic insight based on needs level"""
        insights = {
            "physiological": "Largest market but high price sensitivity. Focus on volume and efficiency. Recession-resistant.",
            "safety": "Large market with good willingness to pay for security. Build trust and reliability.",
            "love_belonging": "Medium market, network effects critical. Focus on community and engagement.",
            "esteem": "Smaller market but higher margins. Brand and status matter more than price.",
            "self_actualization": "Niche market, low price sensitivity. Focus on transformation and results."
        }
        return insights.get(level, "Focus on clear value proposition")

    async def _market_sizing_necessity_vs_luxury(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market size for necessity vs luxury positioning"""

        # Determine if product is necessity or luxury
        industry = context["industry"]
        price_point = context["price_point"]

        necessity_industries = ["Food", "Housing", "Healthcare", "Education", "Finance"]
        is_necessity = industry in necessity_industries

        # Market sizing for India
        india_population = 1400000000  # 1.4 billion

        if is_necessity:
            # Necessity products - larger market
            addressable_segments = ["bottom_of_pyramid", "lower_middle", "middle"]
            tam = int(india_population * 0.95)  # 95% need necessities
            market_type = "Necessity"
        else:
            # Luxury/discretionary - smaller but higher margin
            addressable_segments = ["middle", "upper_middle", "affluent"]
            tam = int(india_population * 0.20)  # 20% can afford luxuries
            market_type = "Luxury/Discretionary"

        # Calculate SAM and SOM
        sam = int(tam * 0.30)  # Serviceable available market (30% of TAM)
        som = int(sam * 0.05)  # Serviceable obtainable market (5% of SAM)

        # Calculate revenue potential
        avg_transaction_value = price_point
        purchase_frequency_annual = 12 if is_necessity else 2

        annual_revenue_potential = som * avg_transaction_value * purchase_frequency_annual

        return {
            "type": "market_sizing",
            "market_type": market_type,
            "is_necessity": is_necessity,
            "addressable_segments": addressable_segments,
            "tam": tam,
            "sam": sam,
            "som": som,
            "annual_revenue_potential": annual_revenue_potential,
            "characteristics": {
                "price_sensitivity": "High" if is_necessity else "Low",
                "recession_impact": "Low" if is_necessity else "High",
                "competition": "Intense" if is_necessity else "Moderate",
                "margins": "Low" if is_necessity else "High"
            }
        }

    async def _affordability_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze affordability across income segments"""

        price_point = context["price_point"]
        geography = context["geography"]

        # Affordability by segment
        affordability_analysis = []

        for segment_name, segment_data in self.income_segments.items():
            # Calculate affordability
            income_range = segment_data["annual_income_range"]

            # Extract median income (rough estimate)
            if ">" in income_range:
                median_income = 4000000  # ₹40 lakh
            elif "-" in income_range:
                parts = income_range.replace("₹", "").replace(" lakh", "").split("-")
                median_income = (float(parts[0]) + float(parts[1])) / 2 * 100000
            else:
                median_income = 200000  # ₹2 lakh

            # Calculate affordability percentage
            affordability_percentage = (price_point / median_income) * 100

            # Determine affordability level
            if affordability_percentage < 1:
                affordability_level = "Highly Affordable"
            elif affordability_percentage < 5:
                affordability_level = "Affordable"
            elif affordability_percentage < 10:
                affordability_level = "Stretch Purchase"
            else:
                affordability_level = "Not Affordable"

            affordability_analysis.append({
                "segment": segment_name,
                "income_range": income_range,
                "population": segment_data["population"],
                "median_income": median_income,
                "price_as_percentage": f"{affordability_percentage:.2f}%",
                "affordability_level": affordability_level,
                "addressable": affordability_percentage < 10
            })

        # Count addressable segments
        addressable_count = sum(1 for a in affordability_analysis if a["addressable"])

        return {
            "type": "affordability",
            "price_point": price_point,
            "affordability_by_segment": affordability_analysis,
            "addressable_segments_count": addressable_count,
            "recommendation": self._get_affordability_recommendation(price_point, affordability_analysis)
        }

    def _get_affordability_recommendation(
        self,
        price_point: float,
        analysis: List[Dict[str, Any]]
    ) -> str:
        """Get affordability recommendation"""

        addressable_count = sum(1 for a in analysis if a["addressable"])

        if addressable_count == 0:
            return "Price point too high for most segments. Consider reducing price or targeting ultra-premium segment only."
        elif addressable_count <= 2:
            return "Limited addressable market. Ensure target segment has strong willingness to pay."
        else:
            return "Good affordability across multiple segments. Focus on value communication."

    async def _needs_gap_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify unmet needs and gaps"""

        # Identify gaps in basic needs (India context)
        unmet_needs = [
            {
                "need": "Affordable Healthcare",
                "level": "Physiological/Safety",
                "gap_description": "80% of India lacks health insurance, out-of-pocket healthcare costs",
                "market_size": "Massive (1.1B people)",
                "existing_solutions": "Government hospitals (overburdened), private (expensive)",
                "opportunity": "Affordable health insurance, telemedicine, generic medicines",
                "examples": ["Aarogya", "1mg", "PharmEasy"]
            },
            {
                "need": "Quality Education",
                "level": "Safety/Esteem",
                "gap_description": "Limited access to quality education in Tier 2/3 cities",
                "market_size": "Large (200M students)",
                "existing_solutions": "Government schools (quality issues), private (expensive)",
                "opportunity": "Affordable EdTech, skill development, online degrees",
                "examples": ["BYJU'S", "Unacademy", "upGrad"]
            },
            {
                "need": "Financial Inclusion",
                "level": "Safety",
                "gap_description": "190M Indians still unbanked, limited access to credit",
                "market_size": "Large (190M people)",
                "existing_solutions": "Traditional banks (exclusionary), moneylenders (exploitative)",
                "opportunity": "Digital payments, microfinance, neo-banks",
                "examples": ["Paytm", "PhonePe", "Micro-lending apps"]
            },
            {
                "need": "Affordable Housing",
                "level": "Physiological",
                "gap_description": "Housing shortage of 29M units, unaffordable in cities",
                "market_size": "Massive (29M units)",
                "existing_solutions": "Real estate (unaffordable), slums (poor quality)",
                "opportunity": "Affordable housing finance, co-living, modular housing",
                "examples": ["PMAY", "Stanza Living", "Housing.com"]
            }
        ]

        return {
            "type": "gap_analysis",
            "unmet_needs": unmet_needs,
            "total_opportunities": len(unmet_needs),
            "recommendation": "Focus on solving basic needs (physiological, safety) for BoP market in India - massive opportunity with social impact"
        }

    async def _comprehensive_needs_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive needs analysis"""

        maslow = await self._map_to_maslows_hierarchy(context)
        market_sizing = await self._market_sizing_necessity_vs_luxury(context)
        affordability = await self._affordability_analysis(context)

        return {
            "type": "comprehensive",
            "maslow_mapping": maslow,
            "market_sizing": market_sizing,
            "affordability": affordability
        }

    async def _generate_recommendations(
        self,
        context: Dict[str, Any],
        analysis: Dict[str, Any],
        analysis_type: str
    ) -> List[Dict[str, Any]]:
        """Generate recommendations"""

        recommendations = []

        # Based on needs level
        if "primary_need_level" in analysis:
            level = analysis["primary_need_level"]
            if level in ["physiological", "safety"]:
                recommendations.append({
                    "title": "Focus on Volume and Efficiency",
                    "description": f"Your product addresses {level} needs - focus on high volume, low margins, and operational efficiency",
                    "priority": "high"
                })

        # Based on affordability
        if "addressable_segments_count" in analysis:
            count = analysis["addressable_segments_count"]
            if count < 2:
                recommendations.append({
                    "title": "Reconsider Pricing Strategy",
                    "description": "Limited addressable market. Consider tiered pricing or freemium to expand reach",
                    "priority": "high"
                })

        recommendations.append({
            "title": "Consider Bottom of Pyramid Market",
            "description": "60% of India (800M people) is an untapped market. Ultra-low prices with volume can be very profitable",
            "priority": "medium"
        })

        return recommendations

    async def _generate_response(
        self,
        query: str,
        context: Dict[str, Any],
        analysis: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> str:
        """Generate response"""

        prompt = f"""You are a human needs and market analysis expert. Provide insights based on:

Query: {query}

Context:
{json.dumps(context, indent=2)}

Analysis:
{json.dumps(analysis, indent=2)[:1500]}

Recommendations:
{json.dumps(recommendations, indent=2)}

Generate a professional analysis (400-500 words) that:
1. Maps product to Maslow's hierarchy
2. Assesses market size (necessity vs luxury)
3. Analyzes affordability and target segments
4. Identifies unmet needs opportunities
5. Provides strategic recommendations

Be specific with numbers and actionable insights."""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                temperature=0.5,
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
        """Fallback response"""

        response = "## Human Needs Analysis\n\n"
        response += f"**Product:** {context['product']}\n"
        response += f"**Industry:** {context['industry']}\n\n"

        if "market_type" in analysis:
            response += f"**Market Type:** {analysis['market_type']}\n"
            response += f"**TAM:** {analysis.get('tam', 0):,} people\n\n"

        response += "**Recommendations:**\n"
        for i, rec in enumerate(recommendations, 1):
            response += f"{i}. **{rec['title']}**\n"
            response += f"   {rec['description']}\n\n"

        return response

    def _get_sources(self) -> List[Dict[str, str]]:
        """Get sources"""
        return [
            {"type": "theory", "source": "Maslow's Hierarchy of Needs"},
            {"type": "market_data", "source": "India income distribution and demographics"}
        ]

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Error response"""
        return {
            "answer": f"Error analyzing needs: {error}",
            "error": error,
            "confidence": 0.0,
            "agent": self.name
        }


# Export
__all__ = ["HumanNeedsAgent"]
