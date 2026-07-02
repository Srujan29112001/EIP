"""
Real Estate Analysis Agent
Comprehensive real estate investment analysis for entrepreneurs and investors
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


class RealEstateAnalysisAgent:
    """
    Real Estate Analysis Agent

    Provides comprehensive real estate analysis including:
    - Property valuation (comparative market analysis)
    - Rental yield calculations
    - Market trend analysis
    - Location scoring
    - REITs analysis
    - Commercial vs residential analysis
    - Cap rate calculations
    - Investment recommendations
    """

    def __init__(self):
        """Initialize Real Estate Analysis Agent"""
        self.name = "RealEstateAnalysisAgent"
        self.description = "Comprehensive real estate investment analysis and market intelligence"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process real estate analysis request

        Args:
            query: User query about real estate
            context: Additional context (budget, location, investment type, etc.)

        Returns:
            Dict with analysis results
        """
        try:
            # Extract key information from query
            analysis_type = self._determine_analysis_type(query)

            # Get property data
            property_data = await self._get_property_data(query, context)

            # Perform appropriate analysis
            if analysis_type == "valuation":
                analysis = await self._property_valuation(property_data, context)
            elif analysis_type == "rental":
                analysis = await self._rental_analysis(property_data, context)
            elif analysis_type == "market_trends":
                analysis = await self._market_trend_analysis(property_data, context)
            elif analysis_type == "location":
                analysis = await self._location_scoring(property_data, context)
            elif analysis_type == "reits":
                analysis = await self._reits_analysis(query, context)
            elif analysis_type == "commercial":
                analysis = await self._commercial_analysis(property_data, context)
            else:
                analysis = await self._comprehensive_analysis(property_data, context)

            # Generate investment recommendations
            recommendations = await self._generate_recommendations(
                query,
                property_data,
                analysis,
                context
            )

            # Create comprehensive response
            response = await self._generate_response(
                query,
                property_data,
                analysis,
                recommendations
            )

            return {
                "answer": response,
                "property_data": property_data,
                "analysis": analysis,
                "recommendations": recommendations,
                "confidence": 0.88,
                "sources": self._get_sources(property_data),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in Real Estate Agent: {str(e)}")
            return self._error_response(str(e))

    def _determine_analysis_type(self, query: str) -> str:
        """Determine type of real estate analysis needed"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["value", "valuation", "price", "worth"]):
            return "valuation"
        elif any(word in query_lower for word in ["rent", "rental", "yield", "income"]):
            return "rental"
        elif any(word in query_lower for word in ["trend", "market", "growth", "appreciation"]):
            return "market_trends"
        elif any(word in query_lower for word in ["location", "area", "neighborhood", "locality"]):
            return "location"
        elif any(word in query_lower for word in ["reit", "real estate fund", "property fund"]):
            return "reits"
        elif any(word in query_lower for word in ["commercial", "office", "retail", "warehouse"]):
            return "commercial"
        else:
            return "comprehensive"

    async def _get_property_data(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get property data (mock implementation - integrate with real estate APIs)"""
        # In production, integrate with:
        # - MagicBricks API
        # - 99acres API
        # - Housing.com API
        # - PropTiger API
        # - Government property records

        return {
            "property_id": "PROP_12345",
            "location": context.get("location", "Bangalore, HSR Layout") if context else "Bangalore, HSR Layout",
            "property_type": context.get("property_type", "Residential Apartment") if context else "Residential Apartment",
            "size_sqft": context.get("size", 1200) if context else 1200,
            "price": context.get("price", 8500000) if context else 8500000,  # INR
            "age_years": 5,
            "amenities": ["Parking", "Gym", "Security", "Park"],
            "nearby_infrastructure": {
                "metro_distance_km": 1.2,
                "schools": 5,
                "hospitals": 3,
                "shopping_malls": 2,
                "tech_parks": 4
            }
        }

    async def _property_valuation(
        self,
        property_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform comparative market analysis for property valuation"""

        # Get comparable properties (mock data)
        comparables = [
            {"size": 1150, "price": 8200000, "age": 4},
            {"size": 1250, "price": 8800000, "age": 6},
            {"size": 1200, "price": 8400000, "age": 5},
        ]

        avg_price_per_sqft = sum(c["price"] / c["size"] for c in comparables) / len(comparables)
        estimated_value = avg_price_per_sqft * property_data["size_sqft"]

        return {
            "method": "Comparative Market Analysis (CMA)",
            "comparable_properties": len(comparables),
            "avg_price_per_sqft": round(avg_price_per_sqft, 2),
            "estimated_value": round(estimated_value, 2),
            "listed_price": property_data["price"],
            "difference_pct": round(((property_data["price"] - estimated_value) / estimated_value) * 100, 2),
            "valuation_verdict": "Fair" if abs((property_data["price"] - estimated_value) / estimated_value) < 0.05 else "Overpriced" if property_data["price"] > estimated_value else "Underpriced"
        }

    async def _rental_analysis(
        self,
        property_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate rental yield and rental income projections"""

        # Market rental rates (mock data - integrate with rental platforms)
        avg_rent_per_sqft = 25  # INR per sqft per month
        estimated_monthly_rent = property_data["size_sqft"] * avg_rent_per_sqft
        annual_rental_income = estimated_monthly_rent * 12

        # Calculate rental yield
        rental_yield_pct = (annual_rental_income / property_data["price"]) * 100

        # Calculate expenses
        maintenance_cost = estimated_monthly_rent * 0.10  # 10% of rent
        property_tax = property_data["price"] * 0.001  # 0.1% annual

        net_rental_income = annual_rental_income - (maintenance_cost * 12) - property_tax
        net_yield_pct = (net_rental_income / property_data["price"]) * 100

        return {
            "estimated_monthly_rent": round(estimated_monthly_rent, 2),
            "annual_rental_income": round(annual_rental_income, 2),
            "gross_rental_yield_pct": round(rental_yield_pct, 2),
            "net_rental_yield_pct": round(net_yield_pct, 2),
            "annual_expenses": {
                "maintenance": round(maintenance_cost * 12, 2),
                "property_tax": round(property_tax, 2)
            },
            "investment_verdict": "Good" if net_yield_pct > 3 else "Average" if net_yield_pct > 2 else "Below Average"
        }

    async def _market_trend_analysis(
        self,
        property_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze market trends for the location"""

        # Historical price data (mock - integrate with real data)
        historical_prices = {
            "2020": 6500,
            "2021": 6800,
            "2022": 7200,
            "2023": 7500,
            "2024": 7800
        }

        # Calculate YoY growth
        yoy_growth_pct = ((7800 - 7500) / 7500) * 100
        cagr_5yr = (((7800 / 6500) ** (1/5)) - 1) * 100

        return {
            "location": property_data["location"],
            "current_avg_price_per_sqft": 7800,
            "yoy_growth_pct": round(yoy_growth_pct, 2),
            "cagr_5yr_pct": round(cagr_5yr, 2),
            "historical_prices": historical_prices,
            "market_sentiment": "Bullish" if yoy_growth_pct > 5 else "Stable" if yoy_growth_pct > 0 else "Bearish",
            "demand_supply_ratio": 1.3,  # >1 = demand > supply
            "upcoming_infrastructure": [
                "Metro Line 4 extension (2026)",
                "New tech park (2025)",
                "Shopping mall (2025)"
            ]
        }

    async def _location_scoring(
        self,
        property_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Score location based on multiple factors"""

        infrastructure = property_data["nearby_infrastructure"]

        # Scoring algorithm (0-100)
        metro_score = max(0, 100 - (infrastructure["metro_distance_km"] * 20))
        schools_score = min(100, infrastructure["schools"] * 15)
        hospitals_score = min(100, infrastructure["hospitals"] * 20)
        malls_score = min(100, infrastructure["shopping_malls"] * 25)
        employment_score = min(100, infrastructure["tech_parks"] * 20)

        total_score = (metro_score + schools_score + hospitals_score + malls_score + employment_score) / 5

        return {
            "overall_score": round(total_score, 1),
            "factors": {
                "public_transport": round(metro_score, 1),
                "education": round(schools_score, 1),
                "healthcare": round(hospitals_score, 1),
                "retail": round(malls_score, 1),
                "employment_hubs": round(employment_score, 1)
            },
            "grade": "A+" if total_score >= 90 else "A" if total_score >= 80 else "B" if total_score >= 70 else "C",
            "strengths": ["Metro connectivity", "Tech hubs nearby", "Good schools"],
            "weaknesses": ["Limited healthcare options"]
        }

    async def _reits_analysis(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze Real Estate Investment Trusts (REITs)"""

        # Mock REIT data - integrate with stock market APIs
        reits = [
            {
                "name": "Embassy Office Parks REIT",
                "ticker": "EMBASSY",
                "price": 380,
                "dividend_yield_pct": 6.5,
                "assets": "Commercial office spaces",
                "occupancy_pct": 95,
                "nav_per_unit": 395
            },
            {
                "name": "Mindspace Business Parks REIT",
                "ticker": "MINDSPACE",
                "price": 320,
                "dividend_yield_pct": 6.2,
                "assets": "IT/ITES office parks",
                "occupancy_pct": 92,
                "nav_per_unit": 335
            }
        ]

        return {
            "available_reits": len(reits),
            "reits": reits,
            "avg_dividend_yield": 6.35,
            "benefits": [
                "Diversification across multiple properties",
                "Professional management",
                "Liquidity (traded on stock exchange)",
                "Lower entry cost vs direct real estate"
            ],
            "risks": [
                "Market volatility",
                "Interest rate sensitivity",
                "Regulatory changes"
            ],
            "recommendation": "Consider 10-15% allocation for diversified real estate exposure"
        }

    async def _commercial_analysis(
        self,
        property_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze commercial real estate"""

        # Commercial-specific metrics
        return {
            "property_type": "Commercial Office",
            "cap_rate_pct": 8.5,  # Capitalization rate
            "noi": 720000,  # Net Operating Income (annual)
            "estimated_value": 8470588,  # NOI / Cap Rate
            "lease_terms": "Triple Net (NNN) - Tenant pays taxes, insurance, maintenance",
            "tenant_profile": "Mix of IT companies and startups",
            "vacancy_risk": "Low (tech hub location)",
            "covenant_strength": "Medium (some startups, some established)",
            "comparison_residential": {
                "commercial_yield": 8.5,
                "residential_yield": 3.2,
                "premium": "Commercial offers 165% higher yield"
            }
        }

    async def _comprehensive_analysis(
        self,
        property_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Comprehensive analysis combining all aspects"""

        valuation = await self._property_valuation(property_data, context)
        rental = await self._rental_analysis(property_data, context)
        trends = await self._market_trend_analysis(property_data, context)
        location = await self._location_scoring(property_data, context)

        return {
            "valuation": valuation,
            "rental_analysis": rental,
            "market_trends": trends,
            "location_score": location
        }

    async def _generate_recommendations(
        self,
        query: str,
        property_data: Dict[str, Any],
        analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate investment recommendations"""

        recommendations = []

        # Based on analysis, provide actionable recommendations
        if "valuation" in analysis:
            if analysis["valuation"]["valuation_verdict"] == "Underpriced":
                recommendations.append("✅ Property appears undervalued by {:.1f}% - good buying opportunity".format(
                    abs(analysis["valuation"]["difference_pct"])
                ))
            elif analysis["valuation"]["valuation_verdict"] == "Overpriced":
                recommendations.append("⚠️ Property is overpriced by {:.1f}% - negotiate or look for alternatives".format(
                    analysis["valuation"]["difference_pct"]
                ))

        if "rental_analysis" in analysis:
            if analysis["rental_analysis"]["net_rental_yield_pct"] > 3:
                recommendations.append("✅ Strong rental yield of {:.1f}% - good for income investors".format(
                    analysis["rental_analysis"]["net_rental_yield_pct"]
                ))

        if "location_score" in analysis:
            if analysis["location_score"]["overall_score"] >= 80:
                recommendations.append("✅ Excellent location score ({}/100) - strong appreciation potential".format(
                    analysis["location_score"]["overall_score"]
                ))

        # Investment strategy recommendations
        recommendations.append("📊 Consider 70-80% home loan to leverage low interest rates")
        recommendations.append("📅 Hold period: 5-7 years for optimal capital appreciation")
        recommendations.append("🏦 Alternative: REITs offer {:.1f}% yield with higher liquidity".format(6.35))

        return recommendations

    async def _generate_response(
        self,
        query: str,
        property_data: Dict[str, Any],
        analysis: Dict[str, Any],
        recommendations: List[str]
    ) -> str:
        """Generate natural language response using LLM"""

        prompt = f"""
You are a real estate investment advisor. Provide a comprehensive but concise analysis based on this data:

Query: {query}

Property Data:
{json.dumps(property_data, indent=2)}

Analysis Results:
{json.dumps(analysis, indent=2)}

Recommendations:
{chr(10).join(recommendations)}

Generate a professional, actionable response (300-400 words) that:
1. Summarizes key findings
2. Provides clear investment verdict
3. Highlights risks and opportunities
4. Gives specific next steps

Be specific with numbers and data-driven.
"""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=500
            )
            return response
        except Exception as e:
            return self._fallback_response(analysis, recommendations)

    def _fallback_response(
        self,
        analysis: Dict[str, Any],
        recommendations: List[str]
    ) -> str:
        """Fallback response if LLM fails"""

        response = "## Real Estate Investment Analysis\n\n"

        if "valuation" in analysis:
            response += f"**Valuation:** {analysis['valuation']['valuation_verdict']} "
            response += f"(Estimated: ₹{analysis['valuation']['estimated_value']:,.0f}, "
            response += f"Listed: ₹{analysis['valuation']['listed_price']:,.0f})\n\n"

        if "rental_analysis" in analysis:
            response += f"**Rental Yield:** {analysis['rental_analysis']['net_rental_yield_pct']:.2f}% "
            response += f"({analysis['rental_analysis']['investment_verdict']})\n\n"

        response += "**Recommendations:**\n"
        for rec in recommendations:
            response += f"- {rec}\n"

        return response

    def _get_sources(self, property_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get data sources"""
        return [
            {"type": "property_listing", "id": property_data.get("property_id", "N/A")},
            {"type": "market_data", "source": "Real Estate Market Analysis"}
        ]

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "answer": f"I encountered an error while analyzing the real estate query: {error}. Please try rephrasing your question or provide more specific details about the property.",
            "error": error,
            "confidence": 0.0,
            "agent": self.name
        }


# Export
__all__ = ["RealEstateAnalysisAgent"]
