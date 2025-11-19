"""
Philanthropy & Impact Investing Agent
Strategic philanthropy and impact investment advisory for entrepreneurs and investors
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


class PhilanthropyImpactAgent:
    """
    Philanthropy & Impact Investing Agent

    Provides comprehensive philanthropy and impact investing advisory including:
    - Impact investing frameworks and strategies
    - ESG integration in investment portfolios
    - CSR (Corporate Social Responsibility) strategy development
    - Charitable giving tax optimization
    - Foundation setup (private vs public)
    - Grant-making strategies and best practices
    - Impact measurement (SROI - Social Return on Investment)
    - Effective altruism principles and application
    - Blended finance structures
    - SDG (Sustainable Development Goals) alignment
    """

    def __init__(self):
        """Initialize Philanthropy & Impact Investing Agent"""
        self.name = "PhilanthropyImpactAgent"
        self.description = "Strategic philanthropy and impact investment advisory"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process philanthropy/impact investing request"""
        try:
            analysis_type = self._determine_analysis_type(query)
            user_context = self._extract_user_context(query, context)

            if analysis_type == "impact_investing":
                analysis = await self._impact_investing_analysis(user_context)
            elif analysis_type == "csr":
                analysis = await self._csr_strategy(user_context)
            elif analysis_type == "foundation":
                analysis = await self._foundation_setup(user_context)
            elif analysis_type == "effective_altruism":
                analysis = await self._effective_altruism_analysis(user_context)
            elif analysis_type == "impact_measurement":
                analysis = await self._impact_measurement(user_context)
            elif analysis_type == "charitable_giving":
                analysis = await self._charitable_giving_strategy(user_context)
            else:
                analysis = await self._comprehensive_strategy(user_context)

            recommendations = self._generate_recommendations(analysis, user_context)
            response = await self._generate_response(query, analysis, recommendations)

            return {
                "answer": response,
                "analysis": analysis,
                "recommendations": recommendations,
                "confidence": 0.88,
                "agent": self.name
            }
        except Exception as e:
            return self._error_response(str(e))

    def _determine_analysis_type(self, query: str) -> str:
        """Determine type of philanthropy analysis needed"""
        query_lower = query.lower()
        if any(word in query_lower for word in ["impact invest", "social impact", "esg invest"]):
            return "impact_investing"
        elif any(word in query_lower for word in ["csr", "corporate social", "company social"]):
            return "csr"
        elif any(word in query_lower for word in ["foundation", "trust", "endowment"]):
            return "foundation"
        elif any(word in query_lower for word in ["effective altruism", "maximize impact", "ea"]):
            return "effective_altruism"
        elif any(word in query_lower for word in ["measure impact", "sroi", "social return"]):
            return "impact_measurement"
        elif any(word in query_lower for word in ["donate", "donation", "charity", "giving"]):
            return "charitable_giving"
        return "comprehensive"

    def _extract_user_context(self, query: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract user context"""
        if context:
            return {
                "net_worth": context.get("net_worth", 10000000),  # ₹1 Cr default
                "annual_income": context.get("annual_income", 5000000),  # ₹50L default
                "company_revenue": context.get("company_revenue", 50000000),  # ₹5 Cr default
                "cause_areas": context.get("cause_areas", ["Education", "Healthcare"]),
                "risk_appetite": context.get("risk_appetite", "Medium"),
                "time_horizon": context.get("time_horizon", "10+ years")
            }
        return {
            "net_worth": 10000000,
            "annual_income": 5000000,
            "company_revenue": 50000000,
            "cause_areas": ["Education", "Healthcare"],
            "risk_appetite": "Medium",
            "time_horizon": "10+ years"
        }

    async def _impact_investing_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze impact investing opportunities and strategies"""
        return {
            "definition": "Impact investing targets measurable social/environmental impact alongside financial returns",
            "spectrum": {
                "traditional_investing": {
                    "financial_return": "Market rate",
                    "impact": "Minimal/negative screening only",
                    "example": "S&P 500 index fund"
                },
                "esg_investing": {
                    "financial_return": "Market rate",
                    "impact": "Moderate (ESG factors integrated)",
                    "example": "ESG-screened mutual funds"
                },
                "impact_investing": {
                    "financial_return": "Market rate to below-market (intentional)",
                    "impact": "High (intentional, measured)",
                    "example": "Microfinance funds, renewable energy projects"
                },
                "philanthropy": {
                    "financial_return": "None (capital deployed)",
                    "impact": "Very high (grants, donations)",
                    "example": "Charitable donations, grants"
                }
            },
            "investment_vehicles": [
                {
                    "vehicle": "Impact Funds",
                    "description": "Professionally managed funds focused on specific impact themes",
                    "min_investment": "₹25L-1Cr",
                    "examples": "Aavishkaar Capital, Lok Capital, Unitus Ventures",
                    "themes": ["Financial inclusion", "Affordable healthcare", "Clean energy"],
                    "expected_returns": "12-18% IRR",
                    "impact_focus": "High"
                },
                {
                    "vehicle": "Social Bonds",
                    "description": "Bonds financing projects with social/environmental benefits",
                    "min_investment": "₹10L+",
                    "examples": "Green bonds, Social Impact Bonds",
                    "themes": ["Renewable energy", "Affordable housing"],
                    "expected_returns": "6-9% (lower risk)",
                    "impact_focus": "Medium-High"
                },
                {
                    "vehicle": "Direct Impact Startups",
                    "description": "Angel/seed investments in impact startups",
                    "min_investment": "₹5L-50L",
                    "examples": "Edtech, Healthtech, Agritech startups",
                    "themes": "Varies widely",
                    "expected_returns": "High variance (0-50x)",
                    "impact_focus": "Very High (but risky)"
                },
                {
                    "vehicle": "ESG Public Equities",
                    "description": "Publicly traded stocks with strong ESG ratings",
                    "min_investment": "₹10K+",
                    "examples": "Nifty 100 ESG Index, SBI Magnum Equity ESG Fund",
                    "themes": "Broad (environmental, social, governance)",
                    "expected_returns": "Market rate (8-12%)",
                    "impact_focus": "Medium"
                }
            ],
            "frameworks": {
                "iris_plus": "Standard metrics for impact measurement (operated by GIIN)",
                "impact_management_project": "Five dimensions of impact (What, Who, How Much, Contribution, Risk)",
                "sdg_alignment": "17 UN Sustainable Development Goals for categorization",
                "giirs": "Global Impact Investing Rating System (like Morningstar for impact)"
            },
            "recommended_allocation": self._calculate_impact_allocation(context)
        }

    def _calculate_impact_allocation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate recommended allocation to impact investments"""
        net_worth = context["net_worth"]
        risk_appetite = context["risk_appetite"]

        # Allocation guidelines
        if risk_appetite == "Low":
            impact_pct = 5
        elif risk_appetite == "Medium":
            impact_pct = 10
        else:  # High
            impact_pct = 20

        impact_allocation = net_worth * (impact_pct / 100)

        return {
            "total_portfolio": net_worth,
            "impact_allocation_pct": impact_pct,
            "impact_allocation_amount": impact_allocation,
            "breakdown": {
                "impact_funds": impact_allocation * 0.50,
                "social_bonds": impact_allocation * 0.30,
                "direct_startups": impact_allocation * 0.20
            },
            "rationale": f"{impact_pct}% allocation balances impact goals with {risk_appetite} risk appetite"
        }

    async def _csr_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Develop CSR strategy for companies"""
        company_revenue = context["company_revenue"]

        # CSR mandate in India
        csr_mandatory = company_revenue >= 10000000  # ₹10 Cr+ revenue
        csr_amount = max(0, (company_revenue * 0.02)) if csr_mandatory else 0  # 2% of average net profit (simplified)

        return {
            "legal_requirement": {
                "companies_act_2013": "Section 135 mandates CSR for qualifying companies",
                "criteria": {
                    "net_worth": "≥ ₹500 Cr OR",
                    "turnover": "≥ ₹1,000 Cr OR",
                    "net_profit": "≥ ₹5 Cr"
                },
                "spend_mandate": "2% of average net profit of preceding 3 years",
                "your_company": {
                    "csr_mandatory": csr_mandatory,
                    "estimated_csr_budget": csr_amount,
                    "compliance": "CSR Committee required if mandatory"
                }
            },
            "csr_themes": [
                {
                    "theme": "Education",
                    "schedule_vii_activity": "Promoting education (Item ii)",
                    "example_projects": ["Scholarship programs", "School infrastructure", "Teacher training"],
                    "impact_metrics": ["Students benefited", "Literacy rate improvement"]
                },
                {
                    "theme": "Healthcare",
                    "schedule_vii_activity": "Promoting healthcare (Item i)",
                    "example_projects": ["Medical camps", "Sanitation projects", "Nutrition programs"],
                    "impact_metrics": ["Patients treated", "Disease prevention"]
                },
                {
                    "theme": "Environmental Sustainability",
                    "schedule_vii_activity": "Environmental sustainability (Item iv)",
                    "example_projects": ["Tree plantation", "Renewable energy", "Waste management"],
                    "impact_metrics": ["Trees planted", "CO2 offset", "Waste recycled"]
                },
                {
                    "theme": "Rural Development",
                    "schedule_vii_activity": "Rural development (Item x)",
                    "example_projects": ["Infrastructure", "Livelihood programs", "Skill development"],
                    "impact_metrics": ["Villages covered", "Income increase"]
                },
                {
                    "theme": "Skill Development",
                    "schedule_vii_activity": "Vocational skills (Item ii)",
                    "example_projects": ["Vocational training", "Employability programs"],
                    "impact_metrics": ["People trained", "Employment rate"]
                }
            ],
            "implementation_models": {
                "in_house": {
                    "description": "Company directly implements CSR projects",
                    "pros": ["Full control", "Brand alignment"],
                    "cons": ["Resource intensive", "Requires expertise"],
                    "best_for": "Large companies with dedicated CSR teams"
                },
                "through_ngos": {
                    "description": "Partner with registered NGOs/Section 8 companies",
                    "pros": ["Leverage expertise", "Wider reach", "Tax benefits"],
                    "cons": ["Less control", "Need to verify NGO credentials"],
                    "best_for": "Most companies - scalable and compliant"
                },
                "foundation": {
                    "description": "Set up own CSR foundation (Section 8 company/trust)",
                    "pros": ["Legacy building", "Tax advantages", "Dedicated focus"],
                    "cons": ["Setup cost", "Governance overhead"],
                    "best_for": "Companies with long-term CSR commitment (₹10Cr+ annual CSR)"
                }
            },
            "reporting_compliance": [
                "Annual CSR report in Board's report",
                "Disclosure on company website",
                "Format as per Companies (CSR Policy) Rules",
                "Impact assessment for projects >₹1 Cr"
            ]
        }

    async def _foundation_setup(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Guide for setting up a philanthropic foundation"""
        net_worth = context["net_worth"]

        return {
            "foundation_types": [
                {
                    "type": "Private Trust",
                    "registration": "Under Indian Trusts Act, 1882",
                    "setup_cost": "₹50K - 2L",
                    "governance": "Trustees (minimum 2)",
                    "taxation": "12A + 80G registration for tax exemption",
                    "best_for": "Family foundations, long-term philanthropy",
                    "min_corpus": "₹10L+ recommended",
                    "pros": ["Flexible", "Privacy", "Perpetual existence"],
                    "cons": ["State-specific rules", "Revocation difficult"]
                },
                {
                    "type": "Section 8 Company",
                    "registration": "Under Companies Act, 2013",
                    "setup_cost": "₹1-3L",
                    "governance": "Board of Directors (minimum 2)",
                    "taxation": "12A + 80G registration",
                    "best_for": "Professional foundations, CSR implementation",
                    "min_corpus": "₹1L (no minimum capital)",
                    "pros": ["Corporate structure", "Limited liability", "Easier fundraising"],
                    "cons": ["More regulatory compliance", "MCA filings"]
                },
                {
                    "type": "Society",
                    "registration": "Under Societies Registration Act, 1860",
                    "setup_cost": "₹30K - 1L",
                    "governance": "Executive Committee (minimum 7 members)",
                    "taxation": "12A + 80G registration",
                    "best_for": "Community-driven initiatives",
                    "min_corpus": "No minimum",
                    "pros": ["Democratic", "Member-driven"],
                    "cons": ["More members required", "Governance complexity"]
                }
            ],
            "tax_benefits": {
                "12a_registration": {
                    "benefit": "Income tax exemption for the trust/foundation",
                    "process": "Apply to Income Tax Commissioner",
                    "validity": "Perpetual (subject to compliance)"
                },
                "80g_registration": {
                    "benefit": "Donors can claim 50% tax deduction on donations",
                    "process": "Apply to Income Tax Commissioner",
                    "validity": "Perpetual (subject to compliance)",
                    "importance": "Critical for attracting individual donors"
                },
                "fcra_registration": {
                    "benefit": "Can receive foreign contributions",
                    "process": "Apply to Ministry of Home Affairs",
                    "requirement": "Foundation must be >3 years old",
                    "importance": "Needed for international funding"
                }
            },
            "grant_making_strategy": {
                "proactive": {
                    "description": "Foundation identifies issues and funds solutions",
                    "approach": "Define focus areas → Invite proposals → Select grantees",
                    "example": "Bill & Melinda Gates Foundation model",
                    "resource_intensive": "High"
                },
                "responsive": {
                    "description": "Respond to applications from NGOs/individuals",
                    "approach": "Publish guidelines → Accept proposals → Evaluate",
                    "example": "Most community foundations",
                    "resource_intensive": "Medium"
                },
                "venture_philanthropy": {
                    "description": "Long-term partnerships with deep engagement",
                    "approach": "Multi-year grants + capacity building + measurement",
                    "example": "Acumen Fund model",
                    "resource_intensive": "Very High"
                }
            },
            "corpus_deployment": {
                "spend_down": "Deploy entire corpus over fixed period (e.g., 10 years)",
                "perpetual": "Preserve corpus, spend only investment returns (~5-8% annually)",
                "hybrid": "Mix of corpus spending + endowment building"
            },
            "recommendation_for_you": self._foundation_recommendation(net_worth)
        }

    def _foundation_recommendation(self, net_worth: float) -> Dict[str, Any]:
        """Recommend foundation structure based on net worth"""
        if net_worth < 5000000:  # <₹50L
            return {
                "recommendation": "Start with donor-advised fund or partner with existing foundations",
                "rationale": "Setting up own foundation not cost-effective at this scale"
            }
        elif net_worth < 50000000:  # ₹50L-5Cr
            return {
                "recommendation": "Private Trust or Section 8 Company",
                "structure": "Section 8 Company (more professional)",
                "initial_corpus": "₹10-25L",
                "model": "Responsive grant-making",
                "focus": "1-2 cause areas maximum"
            }
        else:  # ₹5Cr+
            return {
                "recommendation": "Section 8 Company with professional management",
                "initial_corpus": "₹50L-2Cr",
                "model": "Proactive or venture philanthropy",
                "team": "Hire full-time program manager",
                "focus": "2-3 cause areas with deep impact"
            }

    async def _effective_altruism_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze using effective altruism principles"""
        return {
            "core_principles": [
                {
                    "principle": "Evidence-based giving",
                    "description": "Fund only proven interventions with measurable impact",
                    "example": "GiveWell top charities (malaria nets, deworming)"
                },
                {
                    "principle": "Cost-effectiveness",
                    "description": "Maximize lives saved / suffering reduced per rupee",
                    "example": "₹3,000 saves a life (malaria prevention) vs ₹30L (guide dog)"
                },
                {
                    "principle": "Neglectedness",
                    "description": "Fund areas that others overlook",
                    "example": "Global health in LMICs vs local arts (already well-funded)"
                },
                {
                    "principle": "Counterfactual impact",
                    "description": "What wouldn't happen without your donation?",
                    "example": "Funding gap-filling vs duplicating existing efforts"
                }
            ],
            "top_cause_areas_ea": [
                {
                    "cause": "Global Health & Poverty",
                    "rationale": "High cost-effectiveness, clear evidence",
                    "top_orgs": ["Against Malaria Foundation", "GiveDirectly", "Deworm the World"],
                    "cost_per_life_saved": "₹2,500-5,000"
                },
                {
                    "cause": "Animal Welfare",
                    "rationale": "Massive scale, highly neglected",
                    "top_orgs": ["The Humane League", "Good Food Institute"],
                    "impact": "Reduce suffering of billions of animals"
                },
                {
                    "cause": "Long-term Future / Existential Risk",
                    "rationale": "Low probability but infinite impact",
                    "top_orgs": ["Future of Humanity Institute", "AI safety research"],
                    "impact": "Ensure human survival"
                }
            ],
            "qaly_daly_framework": {
                "qaly": "Quality-Adjusted Life Year - standard health economics metric",
                "daly": "Disability-Adjusted Life Year - WHO metric",
                "cost_per_qaly": {
                    "highly_cost_effective": "< ₹83K per QALY",
                    "cost_effective": "₹83K - 4.2L per QALY",
                    "not_cost_effective": "> ₹4.2L per QALY"
                }
            },
            "your_donation_impact": self._calculate_ea_impact(context)
        }

    def _calculate_ea_impact(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate impact using EA principles"""
        donation_amount = context["net_worth"] * 0.10  # Assume 10% giving

        return {
            "donation_amount": donation_amount,
            "scenarios": [
                {
                    "intervention": "Malaria bed nets (Against Malaria Foundation)",
                    "cost_per_net": 500,
                    "nets_distributed": donation_amount / 500,
                    "lives_saved": (donation_amount / 500) * 0.001,  # 1 in 1000 nets saves a life
                    "cost_per_life": 500000
                },
                {
                    "intervention": "Cash transfers (GiveDirectly)",
                    "transfer_per_household": 75000,
                    "households_helped": donation_amount / 75000,
                    "lives_improved": donation_amount / 75000,
                    "multiplier_effect": "₹1 donated = ₹1.15 to recipients (FX + targeting efficiency)"
                },
                {
                    "intervention": "Local charity (example: building park)",
                    "cost": donation_amount,
                    "beneficiaries": 1000,
                    "cost_per_beneficiary": donation_amount / 1000,
                    "note": "Much less cost-effective but local impact"
                }
            ],
            "recommendation": "For maximum impact, donate 70% to global health, 20% to animal welfare, 10% to local causes"
        }

    async def _impact_measurement(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Impact measurement frameworks"""
        return {
            "sroi_framework": {
                "definition": "Social Return on Investment - Monetize social value created",
                "calculation": "SROI = Net Present Value of benefits / Investment",
                "example": {
                    "investment": 1000000,  # ₹10L
                    "outcomes": {
                        "lives_saved": 2,
                        "value_per_life": 7000000,  # Value of Statistical Life (India)
                        "total_value": 14000000
                    },
                    "sroi_ratio": "14:1 (₹14 social value per ₹1 invested)"
                },
                "challenges": "Subjective valuation, attribution problems"
            },
            "theory_of_change": {
                "definition": "Map inputs → activities → outputs → outcomes → impact",
                "example": {
                    "inputs": "₹10L + 2 teachers",
                    "activities": "After-school tutoring program",
                    "outputs": "200 students tutored, 1000 sessions",
                    "outcomes": "Test scores improved by 20%",
                    "impact": "Higher college admission rates, better life outcomes"
                }
            },
            "iris_metrics": {
                "definition": "Standardized impact metrics catalog (by GIIN)",
                "categories": ["Financial", "Operational", "Product", "Sector-specific", "Social/Environmental"],
                "example_metrics": [
                    "PD5226: Number of low-income clients served",
                    "OI3262: Client retention rate",
                    "PI6070: Greenhouse gas emissions avoided"
                ]
            },
            "sdg_mapping": {
                "definition": "Align projects to UN's 17 Sustainable Development Goals",
                "top_sdgs_india": [
                    "SDG 1: No Poverty",
                    "SDG 3: Good Health and Well-being",
                    "SDG 4: Quality Education",
                    "SDG 8: Decent Work and Economic Growth",
                    "SDG 13: Climate Action"
                ]
            }
        }

    async def _charitable_giving_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Charitable giving and tax optimization"""
        annual_income = context["annual_income"]
        giving_pct = 10  # 10% of income
        donation_amount = annual_income * (giving_pct / 100)

        return {
            "giving_guideline": {
                "traditional": "10% of income (tithe concept)",
                "buffett_gates_pledge": "Majority of wealth over lifetime",
                "earning_to_give": "Maximize income, donate most (EA concept)",
                "your_recommendation": f"{giving_pct}% of income = ₹{donation_amount:,.0f}/year"
            },
            "tax_optimization": {
                "section_80g": {
                    "deduction": "50% or 100% of donation amount",
                    "conditions": "NGO must have 80G registration",
                    "tax_saved": donation_amount * 0.30 * 0.50,  # Assume 30% tax bracket, 50% deduction
                    "effective_cost": donation_amount - (donation_amount * 0.30 * 0.50)
                },
                "section_80gga": {
                    "deduction": "100% (for scientific research or rural development)",
                    "tax_saved": donation_amount * 0.30,
                    "effective_cost": donation_amount * 0.70
                },
                "csr_donations": {
                    "deduction": "Not deductible under 80G",
                    "note": "CSR spend is separate, not personal tax deduction"
                }
            },
            "giving_vehicles": [
                {
                    "vehicle": "Direct donations",
                    "pros": ["Simple", "Immediate impact"],
                    "cons": ["Less strategic", "No ongoing engagement"],
                    "best_for": "Small amounts (<₹1L/year)"
                },
                {
                    "vehicle": "Donor-Advised Fund (DAF)",
                    "pros": ["Immediate tax deduction", "Flexible timing of grants", "Professional management"],
                    "cons": ["Not common in India", "Management fees"],
                    "best_for": "₹10L-1Cr+ donations"
                },
                {
                    "vehicle": "Private Foundation",
                    "pros": ["Legacy building", "Full control", "Multi-generational"],
                    "cons": ["Setup cost", "Ongoing compliance"],
                    "best_for": "₹1Cr+ annual giving over many years"
                }
            ],
            "diversification": {
                "cause_areas": "2-3 areas maximum (focus > spread thin)",
                "giving_stages": {
                    "60%": "Proven, scalable interventions",
                    "30%": "Promising newer organizations",
                    "10%": "Experimental/high-risk high-reward"
                },
                "geographic": "Consider 70% global need, 30% local impact"
            }
        }

    async def _comprehensive_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive philanthropy and impact strategy"""
        impact_investing = await self._impact_investing_analysis(context)
        foundation = await self._foundation_setup(context)
        ea = await self._effective_altruism_analysis(context)

        return {
            "impact_investing": impact_investing,
            "foundation_setup": foundation,
            "effective_altruism": ea,
            "integrated_strategy": {
                "capital_deployment": {
                    "grants": "40% (pure philanthropy, no return expectation)",
                    "impact_investments": "40% (market-rate or concessionary returns)",
                    "traditional_investments_esg": "20% (market-rate with ESG integration)"
                },
                "cause_allocation": {
                    "education": "35%",
                    "healthcare": "30%",
                    "climate_environment": "20%",
                    "poverty_livelihood": "15%"
                },
                "timeline": {
                    "year_1": "Set up foundation/structure, define focus areas",
                    "year_2-3": "Build portfolio, test interventions, measure impact",
                    "year_4-5": "Scale what works, build partnerships",
                    "year_6+": "Sustain and deepen impact, consider succession"
                }
            }
        }

    def _generate_recommendations(
        self,
        analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations"""
        recommendations = []
        net_worth = context["net_worth"]

        if net_worth < 5000000:
            recommendations.append("💡 Start with direct donations to vetted NGOs (80G registered)")
        elif net_worth < 50000000:
            recommendations.append("💡 Consider Section 8 company if annual giving >₹10L")
        else:
            recommendations.append("💡 Set up private foundation for long-term legacy building")

        recommendations.extend([
            "🎯 Focus on 2-3 cause areas maximum for deeper impact",
            "📊 Measure impact using SROI or Theory of Change frameworks",
            "💰 Optimize tax savings using 80G/80GGA deductions",
            "🌍 Consider global health causes for maximum lives saved per rupee (EA approach)",
            "🔄 Diversify: 60% proven interventions, 30% promising, 10% experimental",
            "📈 Track outcomes quarterly, adjust strategy annually"
        ])

        return recommendations

    async def _generate_response(
        self,
        query: str,
        analysis: Dict[str, Any],
        recommendations: List[str]
    ) -> str:
        """Generate response using LLM"""
        prompt = f"""
You are a philanthropy and impact investing advisor. Provide comprehensive guidance based on this data:

Query: {query}
Analysis: {json.dumps(analysis, indent=2)}
Recommendations: {chr(10).join(recommendations)}

Generate a professional, inspiring response (400-500 words) that:
1. Honors the user's philanthropic intent
2. Provides concrete, actionable strategy
3. Balances heart (passion) with head (effectiveness)
4. Explains tax benefits and financial aspects
5. Inspires long-term commitment to impact

Be specific, empathetic, and empowering.
"""
        try:
            return await self.llm_service.generate(prompt=prompt, temperature=0.7, max_tokens=600)
        except:
            return self._fallback_response(analysis, recommendations)

    def _fallback_response(self, analysis: Dict[str, Any], recommendations: List[str]) -> str:
        """Fallback response"""
        response = "## Philanthropy & Impact Investing Strategy\n\n"
        response += "Your commitment to creating positive social impact is admirable. "
        response += "Here's a strategic approach:\n\n"
        response += "**Key Recommendations:**\n"
        for rec in recommendations:
            response += f"{rec}\n"
        return response

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Error response"""
        return {
            "answer": f"Error analyzing philanthropy query: {error}. Please provide details about your giving goals.",
            "error": error,
            "confidence": 0.0,
            "agent": self.name
        }


__all__ = ["PhilanthropyImpactAgent"]
