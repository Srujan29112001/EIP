"""
ESG Environmental Agent
Carbon footprint calculation, ESG scoring, climate risk assessment, sustainability roadmap, green financing
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


class ESGEnvironmentalAgent:
    """
    ESG & Environmental Impact Agent

    Provides comprehensive ESG analysis including:
    - Carbon footprint calculation (Scope 1, 2, 3)
    - ESG scoring and benchmarking
    - Climate risk assessment
    - Sustainability roadmap creation
    - Green financing opportunities
    - Circular economy recommendations
    - Environmental compliance tracking
    """

    def __init__(self):
        """Initialize ESG Environmental Agent"""
        self.name = "ESGEnvironmentalAgent"
        self.description = "Comprehensive ESG and environmental impact analysis"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

        # ESG frameworks
        self.esg_frameworks = [
            "GRI (Global Reporting Initiative)",
            "SASB (Sustainability Accounting Standards Board)",
            "TCFD (Task Force on Climate-related Financial Disclosures)",
            "CDP (Carbon Disclosure Project)",
            "UN SDGs (Sustainable Development Goals)"
        ]

        # Emission factors (kg CO2e)
        self.emission_factors = {
            "electricity": 0.82,  # kg CO2e per kWh (India grid average)
            "petrol": 2.31,  # kg CO2e per liter
            "diesel": 2.68,  # kg CO2e per liter
            "flight_domestic": 0.255,  # kg CO2e per passenger-km
            "flight_international": 0.195,  # kg CO2e per passenger-km
            "train": 0.041,  # kg CO2e per passenger-km
            "car": 0.192,  # kg CO2e per km
            "paper": 1.06,  # kg CO2e per kg of paper
            "water": 0.298,  # kg CO2e per cubic meter
            "cloud_computing": 0.5  # kg CO2e per GB data
        }

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process ESG analysis request

        Args:
            query: User query about ESG/environment
            context: Business context

        Returns:
            Dict with ESG analysis results
        """
        try:
            # Determine analysis type
            analysis_type = self._determine_analysis_type(query)

            # Extract business context
            business_context = self._extract_business_context(query, context)

            # Perform analysis
            if analysis_type == "carbon_footprint":
                analysis = await self._calculate_carbon_footprint(business_context)
            elif analysis_type == "esg_scoring":
                analysis = await self._esg_scoring(business_context)
            elif analysis_type == "climate_risk":
                analysis = await self._climate_risk_assessment(business_context)
            elif analysis_type == "sustainability_roadmap":
                analysis = await self._sustainability_roadmap(business_context)
            elif analysis_type == "green_financing":
                analysis = await self._green_financing_opportunities(business_context)
            else:
                analysis = await self._comprehensive_esg_analysis(business_context)

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
                "confidence": 0.85,
                "sources": self._get_sources(),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in ESGEnvironmentalAgent: {str(e)}")
            return self._error_response(str(e))

    def _determine_analysis_type(self, query: str) -> str:
        """Determine type of ESG analysis"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["carbon", "emissions", "footprint", "ghg"]):
            return "carbon_footprint"
        elif any(word in query_lower for word in ["esg score", "sustainability score", "rating"]):
            return "esg_scoring"
        elif any(word in query_lower for word in ["climate risk", "physical risk", "transition risk"]):
            return "climate_risk"
        elif any(word in query_lower for word in ["roadmap", "sustainability plan", "net zero"]):
            return "sustainability_roadmap"
        elif any(word in query_lower for word in ["green financing", "green bonds", "sustainability linked"]):
            return "green_financing"
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
                "company_name": context.get("company_name", "Company"),
                "industry": context.get("industry", "Technology"),
                "team_size": context.get("team_size", 50),
                "office_space_sqft": context.get("office_space", 5000),
                "annual_revenue": context.get("revenue", 10000000),
                "electricity_kwh_month": context.get("electricity", 5000),
                "business_travel_km_month": context.get("travel", 10000),
                "supply_chain_emissions": context.get("supply_chain_emissions", 0),
                "data_storage_gb": context.get("data_storage", 1000),
                "geography": context.get("geography", "India")
            }
        else:
            return {
                "company_name": "Company",
                "industry": "Technology",
                "team_size": 50,
                "office_space_sqft": 5000,
                "annual_revenue": 10000000,
                "electricity_kwh_month": 5000,
                "business_travel_km_month": 10000,
                "supply_chain_emissions": 0,
                "data_storage_gb": 1000,
                "geography": "India"
            }

    async def _calculate_carbon_footprint(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate carbon footprint (Scope 1, 2, 3)"""

        # Scope 1: Direct emissions (company vehicles, on-site fuel combustion)
        scope1_sources = []
        scope1_total = 0

        # Assuming minimal for tech companies
        vehicle_emissions = 0  # Tech companies rarely own vehicles
        scope1_total += vehicle_emissions

        # Scope 2: Indirect emissions from purchased electricity
        scope2_sources = []
        electricity_monthly = context["electricity_kwh_month"]
        electricity_annual = electricity_monthly * 12
        electricity_emissions = electricity_annual * self.emission_factors["electricity"]

        scope2_sources.append({
            "source": "Office Electricity",
            "consumption": f"{electricity_annual:,.0f} kWh/year",
            "emissions_kg_co2e": electricity_emissions,
            "emissions_tonnes": electricity_emissions / 1000
        })
        scope2_total = electricity_emissions

        # Scope 3: Indirect emissions from value chain
        scope3_sources = []
        scope3_total = 0

        # Employee commute (assuming)
        avg_commute_km_per_employee_day = 20
        working_days = 240
        total_commute_km = context["team_size"] * avg_commute_km_per_employee_day * working_days
        commute_emissions = total_commute_km * self.emission_factors["car"]
        scope3_sources.append({
            "source": "Employee Commute",
            "activity": f"{total_commute_km:,.0f} km/year",
            "emissions_kg_co2e": commute_emissions,
            "emissions_tonnes": commute_emissions / 1000
        })
        scope3_total += commute_emissions

        # Business travel
        business_travel_annual = context["business_travel_km_month"] * 12
        travel_emissions = business_travel_annual * self.emission_factors["flight_domestic"]
        scope3_sources.append({
            "source": "Business Travel (Flights)",
            "activity": f"{business_travel_annual:,.0f} km/year",
            "emissions_kg_co2e": travel_emissions,
            "emissions_tonnes": travel_emissions / 1000
        })
        scope3_total += travel_emissions

        # Cloud/data center
        data_storage = context["data_storage_gb"]
        cloud_emissions = data_storage * self.emission_factors["cloud_computing"] * 12
        scope3_sources.append({
            "source": "Cloud Computing & Data Storage",
            "activity": f"{data_storage:,.0f} GB",
            "emissions_kg_co2e": cloud_emissions,
            "emissions_tonnes": cloud_emissions / 1000
        })
        scope3_total += cloud_emissions

        # Supply chain
        if context["supply_chain_emissions"] > 0:
            scope3_total += context["supply_chain_emissions"]

        # Total footprint
        total_emissions_kg = scope1_total + scope2_total + scope3_total
        total_emissions_tonnes = total_emissions_kg / 1000

        # Per employee and per revenue
        per_employee_tonnes = total_emissions_tonnes / context["team_size"]
        per_revenue_tonnes = total_emissions_tonnes / (context["annual_revenue"] / 1000000)  # per million revenue

        return {
            "type": "carbon_footprint",
            "scope1": {
                "total_kg_co2e": scope1_total,
                "total_tonnes_co2e": scope1_total / 1000,
                "sources": scope1_sources or [{"source": "None", "emissions_tonnes": 0}]
            },
            "scope2": {
                "total_kg_co2e": scope2_total,
                "total_tonnes_co2e": scope2_total / 1000,
                "sources": scope2_sources
            },
            "scope3": {
                "total_kg_co2e": scope3_total,
                "total_tonnes_co2e": scope3_total / 1000,
                "sources": scope3_sources
            },
            "total_footprint": {
                "total_kg_co2e": total_emissions_kg,
                "total_tonnes_co2e": total_emissions_tonnes,
                "per_employee_tonnes": per_employee_tonnes,
                "per_million_revenue_tonnes": per_revenue_tonnes
            },
            "breakdown": {
                "scope1_percentage": (scope1_total / total_emissions_kg * 100) if total_emissions_kg > 0 else 0,
                "scope2_percentage": (scope2_total / total_emissions_kg * 100) if total_emissions_kg > 0 else 0,
                "scope3_percentage": (scope3_total / total_emissions_kg * 100) if total_emissions_kg > 0 else 0
            },
            "benchmarks": {
                "tech_industry_average_per_employee": "3-5 tonnes CO2e",
                "your_performance": "Good" if per_employee_tonnes < 4 else "Average" if per_employee_tonnes < 6 else "High"
            }
        }

    async def _esg_scoring(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate ESG score"""

        # Environmental score (based on carbon footprint)
        # Assuming lower emissions = higher score
        carbon_footprint = await self._calculate_carbon_footprint(context)
        per_employee = carbon_footprint["total_footprint"]["per_employee_tonnes"]

        if per_employee < 3:
            env_score = 9
        elif per_employee < 5:
            env_score = 7
        else:
            env_score = 5

        # Social score (based on team practices - mock data)
        social_factors = {
            "diversity_inclusion": 7,  # out of 10
            "employee_wellbeing": 8,
            "community_engagement": 6,
            "fair_labor_practices": 9
        }
        social_score = sum(social_factors.values()) / len(social_factors)

        # Governance score
        governance_factors = {
            "board_independence": 7,
            "transparency": 8,
            "ethical_conduct": 9,
            "risk_management": 7
        }
        governance_score = sum(governance_factors.values()) / len(governance_factors)

        # Overall ESG score
        overall_esg = (env_score + social_score + governance_score) / 3

        # Rating
        if overall_esg >= 8.5:
            rating = "AAA (Leader)"
        elif overall_esg >= 7.5:
            rating = "AA (Advanced)"
        elif overall_esg >= 6.5:
            rating = "A (Good)"
        else:
            rating = "BBB (Average)"

        return {
            "type": "esg_scoring",
            "overall_score": round(overall_esg, 1),
            "rating": rating,
            "scores": {
                "environmental": {
                    "score": env_score,
                    "factors": {
                        "carbon_footprint": env_score,
                        "resource_efficiency": 7,
                        "waste_management": 6
                    }
                },
                "social": {
                    "score": round(social_score, 1),
                    "factors": social_factors
                },
                "governance": {
                    "score": round(governance_score, 1),
                    "factors": governance_factors
                }
            },
            "peer_comparison": {
                "industry_average": 6.8,
                "your_performance": "Above Average" if overall_esg > 6.8 else "Below Average"
            }
        }

    async def _climate_risk_assessment(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess climate-related risks"""

        # Physical risks
        physical_risks = [
            {
                "risk": "Extreme Weather Events",
                "likelihood": "Medium",
                "impact": "Medium",
                "description": "Floods, heatwaves disrupting operations",
                "mitigation": "Business continuity planning, remote work capabilities"
            },
            {
                "risk": "Water Scarcity",
                "likelihood": "High" if context["geography"] in ["India", "Middle East"] else "Low",
                "impact": "Low" if context["industry"] == "Technology" else "High",
                "description": "Water availability issues in certain regions",
                "mitigation": "Water-efficient operations, location diversification"
            }
        ]

        # Transition risks (policy, technology, market)
        transition_risks = [
            {
                "risk": "Carbon Pricing",
                "likelihood": "High",
                "impact": "Medium",
                "description": "Potential carbon taxes in India by 2030",
                "mitigation": "Reduce emissions now to minimize future costs"
            },
            {
                "risk": "Reputation Risk",
                "likelihood": "Medium",
                "impact": "High",
                "description": "Customers preferring sustainable brands",
                "mitigation": "Transparent ESG reporting, net-zero commitments"
            },
            {
                "risk": "Regulatory Changes",
                "likelihood": "High",
                "impact": "Medium",
                "description": "SEBI mandating ESG disclosures for all listed companies",
                "mitigation": "Start ESG reporting now, ahead of mandate"
            }
        ]

        # Overall risk level
        high_risks = sum(1 for r in physical_risks + transition_risks if r["likelihood"] == "High" and r["impact"] == "High")
        overall_risk = "High" if high_risks > 1 else "Medium"

        return {
            "type": "climate_risk",
            "overall_risk_level": overall_risk,
            "physical_risks": physical_risks,
            "transition_risks": transition_risks,
            "recommended_actions": [
                "Conduct detailed climate scenario analysis (2°C and 4°C warming)",
                "Develop climate adaptation strategy",
                "Set science-based emissions reduction targets",
                "Implement TCFD-aligned disclosures"
            ]
        }

    async def _sustainability_roadmap(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create sustainability roadmap"""

        roadmap = {
            "vision": "Achieve net-zero emissions by 2040",
            "milestones": [
                {
                    "year": 2024,
                    "milestone": "Baseline & Quick Wins",
                    "targets": [
                        "Measure complete carbon footprint (Scope 1, 2, 3)",
                        "Switch to renewable energy for offices (100%)",
                        "Implement waste segregation and recycling",
                        "Set up ESG governance structure"
                    ],
                    "expected_reduction": "15-20% emissions"
                },
                {
                    "year": 2025,
                    "milestone": "Operational Efficiency",
                    "targets": [
                        "Reduce business travel by 30% (virtual meetings)",
                        "Optimize data center usage (cloud efficiency)",
                        "Sustainable procurement policy",
                        "Employee sustainability training"
                    ],
                    "expected_reduction": "Additional 20%"
                },
                {
                    "year": 2030,
                    "milestone": "Value Chain Engagement",
                    "targets": [
                        "50% reduction from 2024 baseline",
                        "Engage suppliers on emissions reduction",
                        "Circular economy initiatives",
                        "Green product portfolio (50% of revenue)"
                    ],
                    "expected_reduction": "50% total reduction"
                },
                {
                    "year": 2040,
                    "milestone": "Net Zero",
                    "targets": [
                        "90% absolute emissions reduction",
                        "High-quality carbon offsets for remaining 10%",
                        "Climate positive (remove more than emit)",
                        "Industry leadership in sustainability"
                    ],
                    "expected_reduction": "100% net zero"
                }
            ],
            "investment_required": {
                "2024_2025": "₹10-20 lakh (initial setup)",
                "2025_2030": "₹50 lakh - 1 Cr (operational changes)",
                "2030_2040": "₹2-5 Cr (major transitions, offsets)"
            }
        }

        return {
            "type": "sustainability_roadmap",
            "roadmap": roadmap
        }

    async def _green_financing_opportunities(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify green financing opportunities"""

        financing_options = [
            {
                "type": "Green Bonds",
                "description": "Bonds specifically for green projects",
                "eligibility": "Companies with renewable energy, clean transport, or sustainable projects",
                "advantages": ["Lower interest rates", "Investor appeal", "ESG credentials"],
                "amount": "₹25 Cr+ typically",
                "providers": ["SEBI-registered entities", "International markets"]
            },
            {
                "type": "Sustainability-Linked Loans",
                "description": "Loans with interest rates tied to ESG performance",
                "eligibility": "Any company willing to commit to ESG targets",
                "advantages": ["Interest rate discount if targets met", "Flexible use of funds"],
                "amount": "₹10 Cr+",
                "providers": ["HDFC", "ICICI", "Axis Bank", "Yes Bank"]
            },
            {
                "type": "Climate Finance from IFC/ADB",
                "description": "International climate finance for developing countries",
                "eligibility": "Projects with clear climate impact",
                "advantages": ["Concessional rates", "Long tenures", "Technical assistance"],
                "amount": "$5M+",
                "providers": ["IFC", "ADB", "Green Climate Fund"]
            },
            {
                "type": "Venture Capital (ESG-focused)",
                "description": "VC funds focused on climate tech and sustainability",
                "eligibility": "Climate tech, clean energy, sustainable products",
                "advantages": ["Equity funding", "Strategic support", "Network"],
                "amount": "₹2 Cr - ₹50 Cr",
                "providers": ["Omnivore", "Elevar Equity", "Aavishkaar Capital"]
            }
        ]

        # Determine eligibility
        if context["annual_revenue"] > 250000000:  # > ₹25 Cr
            eligible = ["Green Bonds", "Sustainability-Linked Loans", "Climate Finance"]
        elif context["annual_revenue"] > 100000000:  # > ₹10 Cr
            eligible = ["Sustainability-Linked Loans", "Climate Finance"]
        else:
            eligible = ["Venture Capital (ESG-focused)"]

        return {
            "type": "green_financing",
            "financing_options": financing_options,
            "eligible_for": eligible,
            "recommendation": f"Based on revenue of ₹{context['annual_revenue']/10000000:.1f} Cr, you're eligible for: {', '.join(eligible)}"
        }

    async def _comprehensive_esg_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive ESG analysis"""

        carbon = await self._calculate_carbon_footprint(context)
        esg_score = await self._esg_scoring(context)
        climate_risk = await self._climate_risk_assessment(context)

        return {
            "type": "comprehensive",
            "carbon_footprint": carbon,
            "esg_scoring": esg_score,
            "climate_risk": climate_risk
        }

    async def _generate_recommendations(
        self,
        context: Dict[str, Any],
        analysis: Dict[str, Any],
        analysis_type: str
    ) -> List[Dict[str, Any]]:
        """Generate ESG recommendations"""

        recommendations = []

        recommendations.append({
            "title": "Switch to 100% Renewable Energy",
            "description": "Purchase renewable energy certificates (RECs) or PPAs to offset all electricity emissions",
            "priority": "high",
            "cost": "₹2-5 lakh annually",
            "impact": "Eliminate 20-30% of total emissions"
        })

        recommendations.append({
            "title": "Implement Remote Work Policy",
            "description": "Reduce office days by 40% to cut commute emissions",
            "priority": "medium",
            "cost": "Nil (cost savings)",
            "impact": "Reduce employee commute emissions by 40%"
        })

        recommendations.append({
            "title": "Start ESG Reporting",
            "description": "Publish annual sustainability report aligned with GRI standards",
            "priority": "high",
            "cost": "₹5-10 lakh (consultant support)",
            "impact": "Transparency, investor appeal, regulatory readiness"
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

        prompt = f"""You are an ESG and sustainability expert. Provide insights based on:

Query: {query}

Context:
{json.dumps(context, indent=2)}

Analysis:
{json.dumps(analysis, indent=2)[:1500]}

Recommendations:
{json.dumps(recommendations, indent=2)}

Generate a professional ESG analysis (400-500 words) that:
1. Summarizes carbon footprint and ESG performance
2. Identifies climate risks and opportunities
3. Provides actionable sustainability recommendations
4. Outlines path to net-zero
5. Highlights green financing options

Be specific with numbers and timelines."""

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

        response = "## ESG & Environmental Analysis\n\n"
        response += f"**Company:** {context['company_name']}\n"
        response += f"**Industry:** {context['industry']}\n\n"

        if "total_footprint" in analysis:
            total = analysis["total_footprint"]["total_tonnes_co2e"]
            response += f"**Carbon Footprint:** {total:.1f} tonnes CO2e/year\n\n"

        response += "**Recommendations:**\n"
        for i, rec in enumerate(recommendations, 1):
            response += f"{i}. **{rec['title']}**\n"
            response += f"   {rec['description']}\n"
            response += f"   Impact: {rec['impact']}\n\n"

        return response

    def _get_sources(self) -> List[Dict[str, str]]:
        """Get sources"""
        return [
            {"type": "framework", "source": "GRI, SASB, TCFD ESG frameworks"},
            {"type": "data", "source": "IPCC emission factors, India grid emissions"}
        ]

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Error response"""
        return {
            "answer": f"Error in ESG analysis: {error}",
            "error": error,
            "confidence": 0.0,
            "agent": self.name
        }


# Export
__all__ = ["ESGEnvironmentalAgent"]
