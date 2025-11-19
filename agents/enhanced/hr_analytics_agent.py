"""
HR Analytics Agent
Salary budgeting, compensation optimization, ESOP modeling, headcount planning, and attrition prediction
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


class HRAnalyticsAgent:
    """
    HR Analytics & Salary Budgeting Agent

    Provides comprehensive HR analytics including:
    - Salary benchmarking across industries and roles
    - Compensation structure optimization
    - ESOP (Employee Stock Ownership Plan) modeling
    - Headcount planning and workforce analytics
    - Attrition prediction and retention strategies
    - Total rewards optimization
    - Organizational design recommendations
    """

    def __init__(self):
        """Initialize HR Analytics Agent"""
        self.name = "HRAnalyticsAgent"
        self.description = "Comprehensive HR analytics and compensation planning"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

        # Salary benchmarks (India - Annual CTC in INR)
        self.salary_benchmarks = self._initialize_salary_benchmarks()

        # ESOP benchmarks
        self.esop_benchmarks = {
            "seed": {"total_pool": 0.15, "ceo": 0.05, "cto": 0.03, "early_engineer": 0.005},
            "series_a": {"total_pool": 0.10, "vp": 0.01, "senior": 0.003, "mid": 0.001},
            "series_b": {"total_pool": 0.08, "vp": 0.008, "senior": 0.002, "mid": 0.0005}
        }

    def _initialize_salary_benchmarks(self) -> Dict[str, Dict[str, Any]]:
        """Initialize salary benchmark database"""
        return {
            # Engineering roles
            "Software Engineer - Junior": {
                "min": 600000, "median": 900000, "max": 1500000,
                "experience": "0-2 years", "skills": ["Programming", "CS fundamentals"]
            },
            "Software Engineer - Mid": {
                "min": 1200000, "median": 1800000, "max": 3000000,
                "experience": "2-5 years", "skills": ["System design", "Full-stack"]
            },
            "Software Engineer - Senior": {
                "min": 2500000, "median": 4000000, "max": 7000000,
                "experience": "5-8 years", "skills": ["Architecture", "Leadership"]
            },
            "Engineering Manager": {
                "min": 3500000, "median": 5500000, "max": 9000000,
                "experience": "8+ years", "skills": ["Team management", "Technical leadership"]
            },
            "CTO": {
                "min": 6000000, "median": 12000000, "max": 25000000,
                "experience": "10+ years", "skills": ["Technology strategy", "Org building"]
            },

            # Product roles
            "Product Manager - Associate": {
                "min": 1000000, "median": 1500000, "max": 2500000,
                "experience": "0-2 years", "skills": ["Product thinking", "Analytics"]
            },
            "Product Manager - Senior": {
                "min": 2500000, "median": 4000000, "max": 6500000,
                "experience": "5+ years", "skills": ["Product strategy", "Stakeholder management"]
            },
            "VP Product": {
                "min": 5000000, "median": 8500000, "max": 15000000,
                "experience": "10+ years", "skills": ["Product vision", "Team leadership"]
            },

            # Design roles
            "UI/UX Designer - Junior": {
                "min": 500000, "median": 800000, "max": 1200000,
                "experience": "0-2 years", "skills": ["Figma", "Visual design"]
            },
            "UI/UX Designer - Senior": {
                "min": 1500000, "median": 2500000, "max": 4000000,
                "experience": "5+ years", "skills": ["Design systems", "User research"]
            },

            # Sales & Marketing
            "Sales Executive": {
                "min": 400000, "median": 700000, "max": 1200000,
                "experience": "0-3 years", "skills": ["B2B sales", "Cold calling"]
            },
            "Sales Manager": {
                "min": 1500000, "median": 2500000, "max": 4500000,
                "experience": "5+ years", "skills": ["Team management", "Revenue targets"]
            },
            "Marketing Manager": {
                "min": 1200000, "median": 2000000, "max": 3500000,
                "experience": "3-6 years", "skills": ["Digital marketing", "Campaign management"]
            },

            # Operations
            "Operations Manager": {
                "min": 1000000, "median": 1800000, "max": 3000000,
                "experience": "3-6 years", "skills": ["Process optimization", "Analytics"]
            },
            "Finance Manager": {
                "min": 1500000, "median": 2500000, "max": 4000000,
                "experience": "5+ years", "skills": ["Financial planning", "Compliance"]
            },
            "HR Manager": {
                "min": 1200000, "median": 2000000, "max": 3500000,
                "experience": "5+ years", "skills": ["Talent acquisition", "Employee relations"]
            }
        }

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process HR analytics request

        Args:
            query: User query about HR/compensation
            context: Additional context (team size, budget, stage, etc.)

        Returns:
            Dict with HR analytics results
        """
        try:
            # Determine analysis type needed
            analysis_type = self._determine_analysis_type(query)

            # Extract HR context
            hr_context = self._extract_hr_context(query, context)

            # Perform appropriate analysis
            if analysis_type == "salary_benchmark":
                analysis = await self._salary_benchmarking(hr_context)
            elif analysis_type == "compensation_structure":
                analysis = await self._compensation_structure(hr_context)
            elif analysis_type == "esop":
                analysis = await self._esop_modeling(hr_context)
            elif analysis_type == "headcount":
                analysis = await self._headcount_planning(hr_context)
            elif analysis_type == "attrition":
                analysis = await self._attrition_prediction(hr_context)
            else:
                analysis = await self._comprehensive_hr_analytics(hr_context)

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                hr_context,
                analysis,
                analysis_type
            )

            # Create response
            response = await self._generate_response(
                query,
                hr_context,
                analysis,
                recommendations
            )

            return {
                "answer": response,
                "hr_context": hr_context,
                "analysis": analysis,
                "recommendations": recommendations,
                "confidence": 0.88,
                "sources": self._get_sources(),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in HRAnalyticsAgent: {str(e)}")
            return self._error_response(str(e))

    def _determine_analysis_type(self, query: str) -> str:
        """Determine type of HR analysis needed"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["salary", "benchmark", "compensation", "pay"]):
            return "salary_benchmark"
        elif any(word in query_lower for word in ["compensation structure", "pay structure", "bands"]):
            return "compensation_structure"
        elif any(word in query_lower for word in ["esop", "stock option", "equity", "shares"]):
            return "esop"
        elif any(word in query_lower for word in ["headcount", "hiring plan", "workforce planning"]):
            return "headcount"
        elif any(word in query_lower for word in ["attrition", "retention", "turnover", "churn"]):
            return "attrition"
        else:
            return "comprehensive"

    def _extract_hr_context(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract HR context from query and context"""

        if context:
            return {
                "company_stage": context.get("stage", "seed"),
                "team_size": context.get("team_size", 10),
                "monthly_budget": context.get("monthly_budget", 2000000),
                "industry": context.get("industry", "SaaS"),
                "location": context.get("location", "Bangalore"),
                "funding_raised": context.get("funding_raised", 0),
                "current_roles": context.get("current_roles", []),
                "open_positions": context.get("open_positions", []),
                "attrition_rate": context.get("attrition_rate", 15)
            }
        else:
            return {
                "company_stage": "seed",
                "team_size": 10,
                "monthly_budget": 2000000,
                "industry": "SaaS",
                "location": "Bangalore",
                "funding_raised": 0,
                "current_roles": [],
                "open_positions": [],
                "attrition_rate": 15
            }

    async def _salary_benchmarking(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide salary benchmarking data"""

        role_query = context.get("role", "Software Engineer - Mid")

        # Find matching roles
        matching_roles = []
        for role, data in self.salary_benchmarks.items():
            if role_query.lower() in role.lower() or role.lower() in role_query.lower():
                matching_roles.append({
                    "role": role,
                    **data,
                    "location_factor": self._get_location_factor(context["location"])
                })

        # Adjust for location
        for role in matching_roles:
            factor = role["location_factor"]
            role["min_adjusted"] = int(role["min"] * factor)
            role["median_adjusted"] = int(role["median"] * factor)
            role["max_adjusted"] = int(role["max"] * factor)

        # Industry adjustment
        industry_factor = self._get_industry_factor(context["industry"])

        return {
            "type": "salary_benchmark",
            "roles": matching_roles,
            "location": context["location"],
            "location_factor": self._get_location_factor(context["location"]),
            "industry": context["industry"],
            "industry_factor": industry_factor,
            "recommendations": self._salary_recommendations(matching_roles)
        }

    def _get_location_factor(self, location: str) -> float:
        """Get salary adjustment factor for location"""
        location_factors = {
            "Bangalore": 1.0,
            "Mumbai": 1.05,
            "Delhi NCR": 0.95,
            "Hyderabad": 0.90,
            "Pune": 0.90,
            "Chennai": 0.85,
            "Remote": 0.80,
            "Tier 2 Cities": 0.70
        }
        return location_factors.get(location, 1.0)

    def _get_industry_factor(self, industry: str) -> float:
        """Get salary adjustment factor for industry"""
        industry_factors = {
            "FinTech": 1.15,
            "SaaS": 1.10,
            "AI/ML": 1.20,
            "E-commerce": 1.05,
            "HealthTech": 1.00,
            "EdTech": 0.95,
            "Services": 0.90
        }
        return industry_factors.get(industry, 1.0)

    def _salary_recommendations(self, roles: List[Dict[str, Any]]) -> List[str]:
        """Generate salary recommendations"""
        recommendations = []

        if roles:
            role = roles[0]
            recommendations.append(
                f"Offer between ₹{role['median_adjusted']/100000:.1f}L - ₹{role['max_adjusted']/100000:.1f}L to attract top talent"
            )
            recommendations.append(
                f"Budget minimum ₹{role['min_adjusted']/100000:.1f}L for this role"
            )
            recommendations.append(
                "Consider total compensation including ESOP, bonuses, and benefits"
            )

        return recommendations

    async def _compensation_structure(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Design compensation structure"""

        team_size = context["team_size"]
        monthly_budget = context["monthly_budget"]
        annual_budget = monthly_budget * 12

        # Typical team composition for startups
        team_composition = self._generate_team_composition(team_size, context["company_stage"])

        # Allocate budget to roles
        total_allocated = 0
        compensation_plan = []

        for role_info in team_composition:
            role_name = role_info["role"]
            count = role_info["count"]

            # Get benchmark
            benchmark = self.salary_benchmarks.get(role_name, {})
            median_salary = benchmark.get("median", 1500000)

            # Adjust for location and industry
            adjusted_salary = median_salary * self._get_location_factor(context["location"])
            adjusted_salary *= self._get_industry_factor(context["industry"])

            total_for_role = adjusted_salary * count
            total_allocated += total_for_role

            compensation_plan.append({
                "role": role_name,
                "count": count,
                "annual_ctc_per_person": int(adjusted_salary),
                "total_annual_cost": int(total_for_role),
                "monthly_cost": int(total_for_role / 12)
            })

        return {
            "type": "compensation_structure",
            "team_size": team_size,
            "annual_budget": annual_budget,
            "total_allocated": int(total_allocated),
            "budget_utilization": f"{(total_allocated / annual_budget * 100):.1f}%",
            "compensation_plan": compensation_plan,
            "is_feasible": total_allocated <= annual_budget,
            "shortfall": max(0, int(total_allocated - annual_budget))
        }

    def _generate_team_composition(self, team_size: int, stage: str) -> List[Dict[str, Any]]:
        """Generate typical team composition"""

        if stage == "seed" and team_size <= 10:
            return [
                {"role": "CTO", "count": 1},
                {"role": "Software Engineer - Senior", "count": 2},
                {"role": "Software Engineer - Mid", "count": 3},
                {"role": "Product Manager - Associate", "count": 1},
                {"role": "UI/UX Designer - Junior", "count": 1},
                {"role": "Sales Executive", "count": 2}
            ]
        elif stage in ["series_a", "growth"] and team_size <= 30:
            return [
                {"role": "CTO", "count": 1},
                {"role": "Engineering Manager", "count": 2},
                {"role": "Software Engineer - Senior", "count": 5},
                {"role": "Software Engineer - Mid", "count": 10},
                {"role": "Product Manager - Senior", "count": 2},
                {"role": "UI/UX Designer - Senior", "count": 1},
                {"role": "Sales Manager", "count": 1},
                {"role": "Sales Executive", "count": 5},
                {"role": "Marketing Manager", "count": 1},
                {"role": "Operations Manager", "count": 1}
            ]
        else:
            # Default composition
            return [
                {"role": "Software Engineer - Mid", "count": max(1, int(team_size * 0.5))},
                {"role": "Product Manager - Associate", "count": max(1, int(team_size * 0.1))},
                {"role": "Sales Executive", "count": max(1, int(team_size * 0.2))}
            ]

    async def _esop_modeling(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Model ESOP allocation"""

        stage = context["company_stage"]
        team_size = context["team_size"]

        # Get ESOP benchmarks for stage
        esop_data = self.esop_benchmarks.get(stage, self.esop_benchmarks["seed"])

        total_pool_percentage = esop_data["total_pool"] * 100  # 15% for seed
        shares_to_allocate = total_pool_percentage

        # Allocate to roles
        allocations = [
            {
                "level": "Founders",
                "typical_allocation": "60-70% (diluted over time)",
                "vesting": "4 years with 1-year cliff"
            },
            {
                "level": "C-Level (CTO, CPO, CFO)",
                "typical_allocation": f"{esop_data.get('ceo', 0.05) * 100:.1f}% - {esop_data.get('cto', 0.03) * 100:.1f}%",
                "vesting": "4 years with 1-year cliff"
            },
            {
                "level": "VP/Director",
                "typical_allocation": f"{esop_data.get('vp', 0.01) * 100:.2f}% - 0.5%",
                "vesting": "4 years with 1-year cliff"
            },
            {
                "level": "Senior IC",
                "typical_allocation": f"{esop_data.get('senior', 0.003) * 100:.2f}% - 0.15%",
                "vesting": "4 years with 1-year cliff"
            },
            {
                "level": "Mid-level IC",
                "typical_allocation": f"{esop_data.get('mid', 0.001) * 100:.2f}% - 0.05%",
                "vesting": "4 years with 1-year cliff"
            }
        ]

        return {
            "type": "esop",
            "stage": stage,
            "total_pool": f"{total_pool_percentage:.1f}%",
            "allocations": allocations,
            "vesting_schedule": "Standard 4-year vesting with 1-year cliff",
            "recommendations": [
                f"Reserve {total_pool_percentage:.1f}% of equity for employee pool at {stage} stage",
                "Implement 4-year vesting with 1-year cliff as standard",
                "Use option pool to attract senior talent without high cash burn",
                "Refresh grants annually for retention",
                "Consider accelerated vesting for M&A scenarios"
            ]
        }

    async def _headcount_planning(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create headcount plan"""

        current_team = context["team_size"]
        monthly_budget = context["monthly_budget"]
        stage = context["company_stage"]

        # Calculate hiring capacity
        avg_salary_monthly = 150000  # ₹1.8L/month average
        hiring_capacity = int((monthly_budget * 0.7) / avg_salary_monthly)  # 70% of budget

        # Generate hiring plan
        quarters = []
        cumulative = current_team

        for q in range(1, 5):  # 4 quarters
            hires_this_quarter = max(1, int(hiring_capacity * 0.25))
            cumulative += hires_this_quarter

            quarters.append({
                "quarter": f"Q{q}",
                "new_hires": hires_this_quarter,
                "cumulative_headcount": cumulative,
                "monthly_burn": cumulative * avg_salary_monthly,
                "priority_roles": self._get_priority_roles(stage, q)
            })

        return {
            "type": "headcount_planning",
            "current_headcount": current_team,
            "hiring_capacity_annual": hiring_capacity,
            "quarterly_plan": quarters,
            "year_end_headcount": cumulative,
            "avg_cost_per_hire": 50000,  # Recruitment cost
            "total_recruitment_cost": 50000 * hiring_capacity
        }

    def _get_priority_roles(self, stage: str, quarter: int) -> List[str]:
        """Get priority roles for hiring by stage and quarter"""

        if stage == "seed":
            roles_by_quarter = {
                1: ["Software Engineer - Senior", "Product Manager"],
                2: ["Software Engineer - Mid", "Sales Executive"],
                3: ["UI/UX Designer", "Marketing Manager"],
                4: ["Software Engineer - Mid", "Operations Manager"]
            }
        else:
            roles_by_quarter = {
                1: ["Engineering Manager", "VP Product"],
                2: ["Software Engineer - Senior", "Sales Manager"],
                3: ["Product Manager - Senior", "Marketing Manager"],
                4: ["Software Engineer - Mid", "Finance Manager"]
            }

        return roles_by_quarter.get(quarter, ["Software Engineer - Mid"])

    async def _attrition_prediction(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict and analyze attrition"""

        current_attrition = context["attrition_rate"]
        team_size = context["team_size"]

        # Industry benchmarks
        industry_avg = 15  # 15% annual attrition is typical for startups

        # Risk assessment
        risk_level = "Low" if current_attrition < 10 else "Medium" if current_attrition < 20 else "High"

        # Calculate impact
        annual_departures = int(team_size * (current_attrition / 100))
        replacement_cost = annual_departures * 150000  # ₹1.5L per replacement

        # Attrition drivers (common reasons)
        drivers = [
            {
                "driver": "Compensation not competitive",
                "likelihood": "High" if current_attrition > 20 else "Medium",
                "mitigation": "Conduct salary benchmarking, implement market adjustments"
            },
            {
                "driver": "Limited career growth",
                "likelihood": "High",
                "mitigation": "Create career ladders, implement mentorship programs"
            },
            {
                "driver": "Poor work-life balance",
                "likelihood": "Medium",
                "mitigation": "Flexible work arrangements, monitor overtime"
            },
            {
                "driver": "Lack of challenging work",
                "likelihood": "Medium",
                "mitigation": "Rotation programs, innovation time"
            }
        ]

        # Retention strategies
        retention_strategies = [
            "Implement quarterly performance reviews with clear growth paths",
            "Offer ESOP refresh grants to high performers",
            "Create learning & development budget (₹50K/employee/year)",
            "Conduct stay interviews every 6 months",
            "Benchmark and adjust compensation annually",
            "Build strong company culture and values"
        ]

        return {
            "type": "attrition",
            "current_rate": f"{current_attrition}%",
            "industry_benchmark": f"{industry_avg}%",
            "risk_level": risk_level,
            "projected_departures": annual_departures,
            "replacement_cost": replacement_cost,
            "drivers": drivers,
            "retention_strategies": retention_strategies,
            "target_attrition": "< 10% annually"
        }

    async def _comprehensive_hr_analytics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive HR analytics combining multiple analyses"""

        salary = await self._salary_benchmarking(context)
        comp_structure = await self._compensation_structure(context)
        esop = await self._esop_modeling(context)
        headcount = await self._headcount_planning(context)
        attrition = await self._attrition_prediction(context)

        return {
            "type": "comprehensive",
            "salary_benchmarks": salary,
            "compensation_structure": comp_structure,
            "esop": esop,
            "headcount_plan": headcount,
            "attrition_analysis": attrition
        }

    async def _generate_recommendations(
        self,
        context: Dict[str, Any],
        analysis: Dict[str, Any],
        analysis_type: str
    ) -> List[Dict[str, Any]]:
        """Generate HR recommendations"""

        recommendations = []

        # Generic HR recommendations
        recommendations.append({
            "title": "Implement Structured Compensation Bands",
            "description": "Create clear salary bands for each role and level to ensure fairness and transparency",
            "priority": "high",
            "timeline": "1 month",
            "impact": "Improved retention and hiring efficiency"
        })

        if analysis_type == "attrition" and analysis.get("risk_level") == "High":
            recommendations.append({
                "title": "Launch Retention Program",
                "description": "Immediate focus on retention through stay interviews, compensation review, and career development",
                "priority": "critical",
                "timeline": "2 weeks",
                "impact": "Reduce attrition by 30-50%"
            })

        recommendations.append({
            "title": "Set Up HR Analytics Dashboard",
            "description": "Track key metrics: headcount, attrition, time-to-hire, cost-per-hire, diversity",
            "priority": "medium",
            "timeline": "1 month",
            "impact": "Data-driven HR decisions"
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

        prompt = f"""You are an HR analytics expert. Provide comprehensive HR advice based on:

Query: {query}

Company Context:
{json.dumps(context, indent=2)}

Analysis:
{json.dumps(analysis, indent=2)[:1500]}

Recommendations:
{json.dumps(recommendations, indent=2)}

Generate a professional, actionable HR strategy (400-500 words) that:
1. Summarizes the current HR situation
2. Provides specific compensation and hiring guidance
3. Offers retention strategies
4. Includes budget planning insights
5. Gives timeline for implementation

Be specific with numbers and actionable steps."""

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
        """Fallback response if LLM fails"""

        response = "## HR Analytics Report\n\n"
        response += f"**Team Size:** {context['team_size']}\n"
        response += f"**Monthly Budget:** ₹{context['monthly_budget']/100000:.1f}L\n"
        response += f"**Stage:** {context['company_stage'].title()}\n\n"

        response += "**Top Recommendations:**\n"
        for i, rec in enumerate(recommendations[:3], 1):
            response += f"{i}. **{rec['title']}** ({rec['priority']} priority)\n"
            response += f"   {rec['description']}\n\n"

        return response

    def _get_sources(self) -> List[Dict[str, str]]:
        """Get data sources"""
        return [
            {
                "type": "salary_benchmarks",
                "source": "Industry salary surveys and market data for India (2024)"
            },
            {
                "type": "esop_benchmarks",
                "source": "Startup equity compensation benchmarks"
            },
            {
                "type": "hr_best_practices",
                "source": "HR analytics and people operations frameworks"
            }
        ]

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "answer": f"I encountered an error while analyzing HR data: {error}. Please provide details like team size, stage, and budget.",
            "error": error,
            "confidence": 0.0,
            "agent": self.name
        }


# Export
__all__ = ["HRAnalyticsAgent"]
