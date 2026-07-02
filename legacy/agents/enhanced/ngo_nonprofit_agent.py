"""
NGO & Non-Profit Advisory Agent
NGO formation, fundraising strategies, impact measurement, 80G/12A tax exemptions, FCRA compliance
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


class NGONonProfitAgent:
    """
    NGO & Non-Profit Advisory Agent

    Provides comprehensive guidance for NGOs and non-profits:
    - NGO formation (Trust, Society, Section 8 Company)
    - Fundraising strategies and grant applications
    - Impact measurement and social metrics
    - 80G and 12A tax exemption processes
    - FCRA (Foreign Contribution Regulation Act) compliance
    - CSR funding opportunities
    - Governance and board management
    - Sustainability and scaling strategies
    """

    def __init__(self):
        """Initialize NGO Non-Profit Agent"""
        self.name = "NGONonProfitAgent"
        self.description = "Comprehensive NGO and non-profit advisory"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

        # NGO structures
        self.ngo_structures = self._initialize_ngo_structures()

        # Funding sources
        self.funding_sources = [
            "Individual donations", "Corporate CSR", "Foundations/Grants",
            "Government schemes", "Crowdfunding", "Social enterprises"
        ]

    def _initialize_ngo_structures(self) -> Dict[str, Dict[str, Any]]:
        """Initialize NGO legal structures"""
        return {
            "trust": {
                "name": "Public Charitable Trust",
                "governing_act": "Indian Trusts Act, 1882 (or state-specific acts)",
                "minimum_members": "2 trustees minimum",
                "formation_document": "Trust Deed",
                "registration_authority": "Charity Commissioner / Sub-Registrar",
                "advantages": [
                    "Simple to form",
                    "Less compliance compared to Society",
                    "Flexible management",
                    "Can hold property"
                ],
                "disadvantages": [
                    "Trustees have unlimited liability",
                    "Less democratic (no membership structure)",
                    "Harder to change trustees"
                ],
                "best_for": "Family trusts, endowments, small NGOs with stable trustees",
                "registration_time": "1-2 months",
                "registration_cost": "₹10,000 - ₹30,000",
                "annual_compliance": "Annual accounts filing with Charity Commissioner"
            },
            "society": {
                "name": "Registered Society",
                "governing_act": "Societies Registration Act, 1860 (or state acts)",
                "minimum_members": "7 members minimum",
                "formation_document": "Memorandum of Association and Rules & Regulations",
                "registration_authority": "Registrar of Societies (state-level)",
                "advantages": [
                    "Democratic structure with General Body",
                    "Easy to add/remove members",
                    "Well-established legal framework",
                    "Limited liability for members"
                ],
                "disadvantages": [
                    "More compliance requirements",
                    "Annual General Meeting mandatory",
                    "Dissolution process complex"
                ],
                "best_for": "Community-based organizations, membership organizations, larger NGOs",
                "registration_time": "2-4 months",
                "registration_cost": "₹5,000 - ₹20,000",
                "annual_compliance": "AGM, annual filing with Registrar, audit (if income > ₹10 lakh)"
            },
            "section_8_company": {
                "name": "Section 8 Company (under Companies Act, 2013)",
                "governing_act": "Companies Act, 2013, Section 8",
                "minimum_members": "2 directors minimum (like Pvt Ltd)",
                "formation_document": "Memorandum and Articles of Association",
                "registration_authority": "Ministry of Corporate Affairs (MCA)",
                "advantages": [
                    "Corporate structure with limited liability",
                    "Better credibility for funding",
                    "Can have 'limited' in name exempt",
                    "Professional governance",
                    "Can convert to for-profit later (with permission)"
                ],
                "disadvantages": [
                    "Highest compliance burden",
                    "Annual filings with MCA (like companies)",
                    "More expensive to maintain",
                    "Stricter regulations"
                ],
                "best_for": "Large NGOs, foundations, NGOs seeking international funding, professional non-profits",
                "registration_time": "2-3 months",
                "registration_cost": "₹30,000 - ₹60,000",
                "annual_compliance": "MCA annual filings (AOC-4, MGT-7), DIN KYC, board meetings"
            }
        }

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process NGO advisory request

        Args:
            query: User query about NGO/non-profit
            context: NGO context

        Returns:
            Dict with advisory results
        """
        try:
            # Determine advisory type
            advisory_type = self._determine_advisory_type(query)

            # Extract NGO context
            ngo_context = self._extract_ngo_context(query, context)

            # Perform analysis
            if advisory_type == "formation":
                analysis = await self._ngo_formation_guide(ngo_context)
            elif advisory_type == "fundraising":
                analysis = await self._fundraising_strategy(ngo_context)
            elif advisory_type == "impact_measurement":
                analysis = await self._impact_measurement_framework(ngo_context)
            elif advisory_type == "tax_exemption":
                analysis = await self._tax_exemption_guide(ngo_context)
            elif advisory_type == "fcra":
                analysis = await self._fcra_compliance_guide(ngo_context)
            elif advisory_type == "csr":
                analysis = await self._csr_funding_strategy(ngo_context)
            else:
                analysis = await self._comprehensive_ngo_advisory(ngo_context)

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                ngo_context,
                analysis,
                advisory_type
            )

            # Create response
            response = await self._generate_response(
                query,
                ngo_context,
                analysis,
                recommendations
            )

            return {
                "answer": response,
                "analysis": analysis,
                "recommendations": recommendations,
                "confidence": 0.88,
                "sources": self._get_sources(),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in NGONonProfitAgent: {str(e)}")
            return self._error_response(str(e))

    def _determine_advisory_type(self, query: str) -> str:
        """Determine advisory type"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["form", "register", "setup", "start ngo", "structure"]):
            return "formation"
        elif any(word in query_lower for word in ["fundraising", "funding", "donation", "grant"]):
            return "fundraising"
        elif any(word in query_lower for word in ["impact", "measurement", "metrics", "outcomes"]):
            return "impact_measurement"
        elif any(word in query_lower for word in ["80g", "12a", "tax exemption", "tax"]):
            return "tax_exemption"
        elif any(word in query_lower for word in ["fcra", "foreign", "international funding"]):
            return "fcra"
        elif any(word in query_lower for word in ["csr", "corporate social responsibility"]):
            return "csr"
        else:
            return "comprehensive"

    def _extract_ngo_context(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract NGO context"""

        if context:
            return {
                "ngo_name": context.get("ngo_name", "NGO"),
                "cause_area": context.get("cause_area", "Education"),
                "stage": context.get("stage", "planning"),
                "structure": context.get("structure", "not_decided"),
                "annual_budget": context.get("budget", 1000000),
                "team_size": context.get("team_size", 5),
                "beneficiaries": context.get("beneficiaries", 100),
                "geography": context.get("geography", "India"),
                "has_80g_12a": context.get("has_80g_12a", False),
                "has_fcra": context.get("has_fcra", False),
                "years_operating": context.get("years", 0)
            }
        else:
            return {
                "ngo_name": "NGO",
                "cause_area": "Education",
                "stage": "planning",
                "structure": "not_decided",
                "annual_budget": 1000000,
                "team_size": 5,
                "beneficiaries": 100,
                "geography": "India",
                "has_80g_12a": False,
                "has_fcra": False,
                "years_operating": 0
            }

    async def _ngo_formation_guide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Guide for NGO formation"""

        # Recommend structure based on context
        budget = context["annual_budget"]
        stage = context["stage"]

        if budget < 1000000:  # < ₹10 lakh
            recommended_structure = "trust"
            rationale = "Small budget - Trust is simplest and cheapest to form and maintain"
        elif budget < 5000000:  # < ₹50 lakh
            recommended_structure = "society"
            rationale = "Medium budget - Society provides good balance of governance and compliance"
        else:
            recommended_structure = "section_8_company"
            rationale = "Large budget - Section 8 provides professional structure, better for scaling and international funding"

        recommended = self.ngo_structures[recommended_structure].copy()
        recommended["recommendation"] = rationale

        # Formation process
        formation_process = {
            "step_1": {
                "action": "Define Purpose and Objectives",
                "details": [
                    "Clearly articulate cause and mission",
                    "Define specific objectives (measurable)",
                    "Identify target beneficiaries",
                    "Draft vision and mission statements"
                ],
                "timeline": "1-2 weeks"
            },
            "step_2": {
                "action": "Choose Legal Structure",
                "details": [
                    f"Recommended: {recommended_structure.title()}",
                    "Gather founding members/trustees/directors",
                    "Draft governing document (Trust Deed/MoA)"
                ],
                "timeline": "1 week"
            },
            "step_3": {
                "action": "Register the NGO",
                "details": [
                    f"Apply to {recommended['registration_authority']}",
                    "Submit required documents",
                    "Pay registration fees",
                    "Obtain registration certificate"
                ],
                "timeline": recommended["registration_time"]
            },
            "step_4": {
                "action": "Post-Registration Compliances",
                "details": [
                    "Open bank account in NGO name",
                    "Obtain PAN card",
                    "Register under Income Tax (12A, 80G)",
                    "Set up accounting system"
                ],
                "timeline": "1-2 months"
            },
            "step_5": {
                "action": "Operational Setup",
                "details": [
                    "Recruit initial team",
                    "Set up office/workspace",
                    "Develop programs and activities",
                    "Begin fundraising"
                ],
                "timeline": "2-3 months"
            }
        }

        return {
            "type": "formation",
            "recommended_structure": recommended,
            "all_structures": self.ngo_structures,
            "formation_process": formation_process,
            "total_timeline": "4-7 months from idea to operational NGO",
            "estimated_cost": f"₹{recommended['registration_cost']}"
        }

    async def _fundraising_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fundraising strategy for NGOs"""

        budget_needed = context["annual_budget"]
        years_operating = context["years_operating"]
        has_80g = context["has_80g_12a"]

        # Funding sources with strategies
        funding_strategies = {
            "individual_donations": {
                "potential": "20-40% of total funding",
                "strategies": [
                    "Create compelling donation page on website",
                    "Monthly giving program (recurring donors)",
                    "Crowdfunding campaigns for specific projects",
                    "Donor appreciation and stewardship",
                    "Email campaigns with impact stories"
                ],
                "tools": ["Razorpay", "Instamojo", "Ketto", "Milaap"],
                "prerequisite": "80G registration for tax deduction appeal",
                "avg_donation": "₹500 - ₹5,000 per donor"
            },
            "corporate_csr": {
                "potential": "30-50% of total funding",
                "strategies": [
                    "Identify companies with CSR budgets in your cause area",
                    "Develop detailed project proposals (budget, timeline, impact)",
                    "Build relationships with CSR managers",
                    "Showcase impact and past success",
                    "Apply through CSR portals"
                ],
                "companies": ["Tata Trusts", "Infosys Foundation", "HCL Foundation", "Wipro Cares"],
                "prerequisite": "2-3 years track record, 80G/12A, strong impact metrics",
                "avg_grant": "₹5 lakh - ₹50 lakh"
            },
            "foundations_grants": {
                "potential": "20-40% of total funding",
                "strategies": [
                    "Research foundations aligned with your cause",
                    "Tailor proposals to funder priorities",
                    "Build long-term relationships",
                    "Provide detailed impact reports",
                    "Consider multi-year grants"
                ],
                "foundations": ["Bill & Melinda Gates Foundation", "Ford Foundation", "Azim Premji Foundation", "Give India"],
                "prerequisite": "Strong track record, measurable impact, financial transparency",
                "avg_grant": "₹10 lakh - ₹1 crore"
            },
            "government_schemes": {
                "potential": "10-30% of total funding",
                "strategies": [
                    "Monitor government schemes in your sector",
                    "Build capacity to manage government grants",
                    "Ensure compliance with government norms",
                    "Maintain detailed documentation"
                ],
                "schemes": ["NITI Aayog NGO Darpan", "Ministry grants", "State schemes"],
                "prerequisite": "Registration, clean audit reports, past experience",
                "avg_grant": "₹5 lakh - ₹50 lakh"
            },
            "earned_income": {
                "potential": "10-20% of total funding",
                "strategies": [
                    "Fee-based services (training, consulting)",
                    "Social enterprise model",
                    "Product sales (handicrafts, etc.)",
                    "Event income"
                ],
                "examples": ["Akshaya Patra (meal subscriptions)", "Goonj (collection drives)"],
                "prerequisite": "Business skills, initial investment",
                "sustainability": "High - reduces donor dependency"
            }
        }

        # Fundraising roadmap based on stage
        if years_operating < 1:
            roadmap = {
                "year_1": {
                    "focus": "Individual donations and small grants",
                    "target": "₹5-10 lakh",
                    "activities": ["Website with donation page", "Crowdfunding campaign", "Small foundation grants"]
                }
            }
        elif years_operating < 3:
            roadmap = {
                "year_2_3": {
                    "focus": "CSR funding and medium grants",
                    "target": "₹20-50 lakh",
                    "activities": ["Apply for CSR funding", "Foundation grants", "Recurring donor program"]
                }
            }
        else:
            roadmap = {
                "year_3_plus": {
                    "focus": "Diversified funding with earned income",
                    "target": "₹50 lakh - ₹5 crore",
                    "activities": ["Major CSR partnerships", "International grants", "Social enterprise", "FCRA for foreign funding"]
                }
            }

        return {
            "type": "fundraising",
            "budget_needed": budget_needed,
            "funding_strategies": funding_strategies,
            "fundraising_roadmap": roadmap,
            "key_advice": [
                "Diversify funding sources (don't depend on one donor)",
                "Invest in fundraising (10-15% of budget)",
                "Track and showcase impact meticulously",
                "Build donor relationships, not just transactions",
                "Get 80G/12A ASAP - increases donations significantly"
            ]
        }

    async def _impact_measurement_framework(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Impact measurement framework"""

        cause_area = context["cause_area"]

        # Impact measurement frameworks
        frameworks = {
            "logic_model": {
                "description": "Maps inputs → activities → outputs → outcomes → impact",
                "use_case": "Planning and explaining your theory of change",
                "example": {
                    "inputs": "₹10 lakh, 5 teachers, classroom",
                    "activities": "After-school tutoring for underprivileged children",
                    "outputs": "500 children tutored, 2000 hours of tutoring",
                    "outcomes": "80% improvement in test scores",
                    "impact": "Higher school completion rates, better life opportunities"
                }
            },
            "social_return_on_investment": {
                "description": "Monetizes social impact (SROI ratio)",
                "use_case": "Demonstrating value for money to funders",
                "example": "₹1 invested → ₹4 of social value created",
                "calculation": "Total social value / Total investment"
            },
            "outcome_harvesting": {
                "description": "Collect evidence of outcomes without predefined indicators",
                "use_case": "Complex, emergent impacts that are hard to predict",
                "method": "Document stories and evidence of change"
            },
            "randomized_control_trials": {
                "description": "Gold standard - compare intervention vs control group",
                "use_case": "Proving causality for research and evidence-based policy",
                "challenge": "Expensive, requires expertise"
            }
        }

        # Metrics by cause area
        metrics_by_cause = {
            "Education": [
                "Students enrolled/graduated",
                "Learning outcomes (test scores improvement)",
                "Attendance rates",
                "School completion rates",
                "Employment after graduation"
            ],
            "Healthcare": [
                "Patients treated",
                "Lives saved",
                "Disease prevalence reduction",
                "Healthcare access (waiting times)",
                "Cost per treatment"
            ],
            "Livelihood": [
                "Jobs created",
                "Income increase (baseline vs endline)",
                "Poverty reduction (households above poverty line)",
                "Skills trained",
                "Business started/sustained"
            ],
            "Environment": [
                "Trees planted (and survived)",
                "Carbon sequestered (tonnes CO2)",
                "Waste diverted from landfills",
                "Water saved/cleaned",
                "Species protected"
            ]
        }

        recommended_metrics = metrics_by_cause.get(cause_area, [
            "Beneficiaries reached",
            "Services delivered",
            "Outcomes achieved",
            "Long-term impact"
        ])

        return {
            "type": "impact_measurement",
            "frameworks": frameworks,
            "recommended_metrics": recommended_metrics,
            "measurement_process": [
                "1. Define theory of change (how your activities lead to impact)",
                "2. Identify key indicators (output, outcome, impact)",
                "3. Set baselines (measure before intervention)",
                "4. Collect data regularly (monthly/quarterly)",
                "5. Analyze and report (annual impact reports)",
                "6. Use data for improvement (course corrections)"
            ],
            "tools": [
                "Google Forms for surveys",
                "CommCare for field data collection",
                "Salesforce for NGOs (free/discounted)",
                "Impact Cloud for impact management"
            ]
        }

    async def _tax_exemption_guide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Guide for 80G and 12A tax exemptions"""

        has_80g_12a = context["has_80g_12a"]
        years_operating = context["years_operating"]

        # 12A and 80G overview
        exemptions = {
            "12A_registration": {
                "benefit": "Income tax exemption for the NGO",
                "what_it_means": "NGO's income is exempt from income tax",
                "eligibility": [
                    "Registered NGO (Trust/Society/Section 8)",
                    "Charitable/religious/educational objects",
                    "Activities must be genuine"
                ],
                "validity": "Valid perpetually (or till cancelled)",
                "application_process": [
                    "File Form 10A with Income Tax Department",
                    "Submit Trust Deed/MoA, Registration Certificate",
                    "Submit activity and financial details",
                    "Obtain 12A registration certificate"
                ],
                "timeline": "2-6 months",
                "renewal": "Not required (unless cancelled)"
            },
            "80G_registration": {
                "benefit": "Tax deduction for donors",
                "what_it_means": "Donors can claim 50% or 100% tax deduction on donations",
                "importance": "Critical for fundraising - donors prefer 80G NGOs",
                "eligibility": [
                    "Must have 12A registration first",
                    "Charitable activities for at least 1 year",
                    "Clean financial records"
                ],
                "validity": "Valid perpetually (or till cancelled)",
                "application_process": [
                    "File Form 10G with Income Tax Department",
                    "Must have 12A already",
                    "Submit audited accounts for past year",
                    "Obtain 80G approval certificate"
                ],
                "timeline": "3-6 months after 12A",
                "renewal": "Not required (unless cancelled)"
            }
        }

        # Application checklist
        application_checklist = {
            "documents_required": [
                "Registration certificate (Trust/Society/Section 8)",
                "Trust Deed / MoA & Rules",
                "PAN card of NGO",
                "Audited financial statements (if operating for 1+ year)",
                "List of trustees/directors with PAN and Aadhaar",
                "Activity report",
                "Bank account details"
            ],
            "process": [
                "1. Ensure NGO has been active for at least 1 year (for 80G)",
                "2. Prepare all documents",
                "3. File Form 10A for 12A online on Income Tax e-filing portal",
                "4. Wait for 12A approval (2-6 months)",
                "5. File Form 10G for 80G",
                "6. Wait for 80G approval (3-6 months)"
            ],
            "common_mistakes": [
                "Applying for 80G before getting 12A",
                "Incomplete documentation",
                "Not filing IT returns regularly",
                "Activities not matching stated objectives"
            ]
        }

        # Benefits of having 80G/12A
        benefits = {
            "for_ngo": [
                "Exemption from income tax on surplus",
                "Credibility with donors and funders",
                "Access to CSR funding (many require 80G)",
                "Better visibility and trust"
            ],
            "for_donors": [
                "50% or 100% tax deduction on donations (under Section 80G)",
                "Reduces donor's taxable income",
                "Example: Donate ₹10,000 → Save ₹3,000 in tax (for 30% bracket)"
            ]
        }

        return {
            "type": "tax_exemption",
            "has_exemptions": has_80g_12a,
            "exemptions": exemptions,
            "application_checklist": application_checklist,
            "benefits": benefits,
            "recommendation": "Get 12A and 80G ASAP - critical for fundraising" if not has_80g_12a else "Maintain compliance to keep exemptions"
        }

    async def _fcra_compliance_guide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """FCRA (Foreign Contribution Regulation Act) guide"""

        has_fcra = context["has_fcra"]
        years_operating = context["years_operating"]

        fcra_guide = {
            "what_is_fcra": "Foreign Contribution (Regulation) Act - governs foreign funding to NGOs in India",
            "why_needed": "To receive foreign donations/grants, NGO must have FCRA registration",
            "eligibility": [
                "NGO must be registered (Trust/Society/Section 8)",
                "Active for at least 3 years",
                "Spent at least ₹15 lakh on charitable activities in last 3 years",
                "Not on government adverse list",
                "Definite cultural, economic, educational, religious, or social program"
            ],
            "types": {
                "fcra_registration": {
                    "validity": "5 years (renewable)",
                    "use": "Regular foreign funding",
                    "process": "Apply via FCRA online portal"
                },
                "fc_prior_permission": {
                    "validity": "One-time for specific donation",
                    "use": "Occasional foreign donation",
                    "process": "Apply 45 days before receiving funds"
                }
            },
            "application_process": [
                "1. Ensure 3 years of operations and ₹15 lakh expenditure",
                "2. Gather documents (registration, financials, activity reports)",
                "3. Apply online at fcraonline.nic.in",
                "4. Open FCRA designated bank account (only SBI authorized branches)",
                "5. Wait for approval (6-12 months)",
                "6. Receive FCRA registration certificate"
            ],
            "compliance_requirements": [
                "Maintain separate FCRA bank account",
                "File annual FCRA returns (FC-4) by Dec 31",
                "Audit by chartered accountant",
                "Spend 100% of administrative expenses from domestic sources (max 20% from FCRA)",
                "Renewal every 5 years",
                "Inform within 15 days of change in address/objectives"
            ],
            "recent_changes_2020": [
                "Aadhaar mandatory for office bearers",
                "Reduced administrative expense limit to 20% (from 50%)",
                "Only SBI branches for FCRA account",
                "No sub-granting to other NGOs",
                "Stricter compliance monitoring"
            ],
            "challenges": [
                "Increased scrutiny and cancellations",
                "Long approval times (6-12 months)",
                "Heavy compliance burden",
                "Risk of cancellation for minor violations"
            ]
        }

        recommendation = ""
        if years_operating < 3:
            recommendation = "Not eligible yet - operate for 3 years first and spend ₹15L+ on programs"
        elif has_fcra:
            recommendation = "Ensure strict compliance - file FC-4 annually, maintain separate account, audit"
        else:
            recommendation = "If you need foreign funding, apply for FCRA. Otherwise, focus on domestic fundraising (simpler)"

        return {
            "type": "fcra",
            "has_fcra": has_fcra,
            "eligible": years_operating >= 3,
            "guide": fcra_guide,
            "recommendation": recommendation
        }

    async def _csr_funding_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """CSR funding strategy"""

        # CSR landscape in India
        csr_overview = {
            "total_csr_spend_india": "₹25,000+ crore annually (2023)",
            "companies_spending_csr": "20,000+ companies",
            "legal_requirement": "Companies with ₹5Cr+ profit or ₹1000Cr+ turnover or ₹5Cr+ net worth must spend 2% profit on CSR",
            "top_sectors": ["Education", "Healthcare", "Livelihood", "Rural Development", "Environment"],
            "top_companies": [
                "Reliance Industries (₹900+ Cr)",
                "TCS (₹600+ Cr)",
                "HDFC Bank (₹500+ Cr)",
                "Infosys (₹450+ Cr)",
                "ITC (₹400+ Cr)"
            ]
        }

        # How to access CSR funding
        strategy = {
            "step_1_research": {
                "action": "Identify companies aligned with your cause",
                "resources": [
                    "CSR Box - database of CSR spending",
                    "Company websites - CSR policy sections",
                    "NGO Darpan portal",
                    "CSR mandate portal"
                ]
            },
            "step_2_prepare": {
                "action": "Get your house in order",
                "requirements": [
                    "80G/12A registration (mandatory for most companies)",
                    "2-3 years track record",
                    "Strong impact metrics and case studies",
                    "Professional proposal writing capability",
                    "Audited financial statements"
                ]
            },
            "step_3_proposal": {
                "action": "Develop compelling CSR proposal",
                "elements": [
                    "Executive summary (1 page)",
                    "Problem statement (data-backed)",
                    "Your solution and theory of change",
                    "Detailed budget (itemized)",
                    "Timeline and milestones",
                    "Impact metrics (quantified)",
                    "Your track record and credentials"
                ]
            },
            "step_4_outreach": {
                "action": "Build relationships with CSR teams",
                "channels": [
                    "Direct application on company CSR portal",
                    "Networking events and CSR conferences",
                    "LinkedIn outreach to CSR managers",
                    "Through CSR intermediaries (foundations)",
                    "Referrals from board members"
                ]
            },
            "step_5_reporting": {
                "action": "Regular impact reporting",
                "deliverables": [
                    "Quarterly progress reports",
                    "Financial utilization statements",
                    "Impact assessment (baseline vs endline)",
                    "Case studies and beneficiary stories",
                    "Final impact report"
                ]
            }
        }

        # CSR application tips
        tips = [
            "Focus on Schedule VII activities (as per Companies Act)",
            "Quantify impact (numbers matter - lives touched, outcomes achieved)",
            "Be realistic with budget and timeline",
            "Highlight innovation and scalability",
            "Build long-term relationships (multi-year funding > one-time grants)",
            "Apply early (CSR budgets allocated at start of financial year)",
            "Follow up persistently but professionally"
        ]

        return {
            "type": "csr",
            "csr_overview": csr_overview,
            "strategy": strategy,
            "tips": tips,
            "success_factors": [
                "Alignment with company's CSR focus areas",
                "Strong track record and credibility",
                "Clear, measurable impact",
                "Professional proposal and reporting",
                "Relationship building with CSR team"
            ]
        }

    async def _comprehensive_ngo_advisory(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive NGO advisory"""

        formation = await self._ngo_formation_guide(context)
        fundraising = await self._fundraising_strategy(context)
        tax = await self._tax_exemption_guide(context)

        return {
            "type": "comprehensive",
            "formation": formation,
            "fundraising": fundraising,
            "tax_exemptions": tax
        }

    async def _generate_recommendations(
        self,
        context: Dict[str, Any],
        analysis: Dict[str, Any],
        advisory_type: str
    ) -> List[Dict[str, Any]]:
        """Generate recommendations"""

        recommendations = []

        # Based on 80G/12A status
        if not context["has_80g_12a"]:
            recommendations.append({
                "title": "Apply for 12A and 80G Registration Immediately",
                "description": "Critical for fundraising - donors prefer tax-deductible donations",
                "priority": "critical",
                "timeline": "6-12 months total",
                "impact": "3-5x increase in individual donations"
            })

        # Based on years of operation
        years = context["years_operating"]
        if years >= 3 and not context["has_fcra"]:
            recommendations.append({
                "title": "Consider FCRA Registration for Foreign Funding",
                "description": "You're eligible for FCRA. Apply if you need international grants.",
                "priority": "medium",
                "timeline": "6-12 months",
                "impact": "Access to international foundations and donors"
            })

        recommendations.append({
            "title": "Implement Robust Impact Measurement",
            "description": "Track and showcase impact meticulously - it's your currency for fundraising",
            "priority": "high",
            "tools": ["Impact Cloud", "Salesforce for Nonprofits", "Google Forms"],
            "impact": "Better fundraising success rate"
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

        prompt = f"""You are an NGO and non-profit advisory expert. Provide guidance based on:

Query: {query}

NGO Context:
{json.dumps(context, indent=2)}

Analysis:
{json.dumps(analysis, indent=2)[:1500]}

Recommendations:
{json.dumps(recommendations, indent=2)}

Generate professional advisory (400-500 words) that:
1. Guides on NGO formation and structure
2. Provides fundraising strategies
3. Explains tax exemptions (80G/12A)
4. Discusses impact measurement
5. Offers FCRA and CSR funding guidance

Be practical and actionable."""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                temperature=0.5,
                max_tokens=700
            )
            return response
        except Exception as e:
            return self._fallback_response(context, analysis, recommendations)

    def _fallback_response(
        self,
        context: Dict[str, Any],
        analysis: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> str:
        """Fallback response"""

        response = "## NGO Advisory\n\n"
        response += f"**NGO:** {context['ngo_name']}\n"
        response += f"**Cause:** {context['cause_area']}\n\n"

        response += "**Recommendations:**\n"
        for i, rec in enumerate(recommendations, 1):
            response += f"{i}. **{rec['title']}** ({rec['priority']} priority)\n"
            response += f"   {rec['description']}\n\n"

        return response

    def _get_sources(self) -> List[Dict[str, str]]:
        """Get sources"""
        return [
            {"type": "legal", "source": "Companies Act 2013, Societies Act, Income Tax Act"},
            {"type": "regulatory", "source": "FCRA regulations, CSR rules"}
        ]

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Error response"""
        return {
            "answer": f"Error in NGO advisory: {error}",
            "error": error,
            "confidence": 0.0,
            "agent": self.name
        }


# Export
__all__ = ["NGONonProfitAgent"]
