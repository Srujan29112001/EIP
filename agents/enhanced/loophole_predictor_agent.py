"""
Loophole Predictor Agent - Legal Optimization Opportunities Identifier
Analyzes tax codes, regulations, and legal frameworks to find legitimate optimization opportunities
"""

import os
import sys
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.base.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class LoopholePredictorAgent(BaseAgent):
    """
    Advanced agent for identifying legal optimization opportunities
    Focuses on tax, regulatory, and compliance optimization within legal boundaries
    """

    def __init__(self):
        super().__init__(
            name="Loophole Predictor Agent",
            description="Identifies legal optimization opportunities in tax codes and regulations",
            capabilities=[
                "tax_optimization_analysis",
                "regulatory_loophole_identification",
                "legal_structure_optimization",
                "deduction_maximization",
                "tax_credit_discovery",
                "compliance_safe_strategies"
            ]
        )

        # Tax optimization database (legal deductions and credits)
        self.tax_optimizations = self._initialize_tax_optimizations()

        # Regulatory frameworks by jurisdiction
        self.regulatory_frameworks = self._initialize_regulatory_frameworks()

        # Legal structure advantages
        self.structure_benefits = self._initialize_structure_benefits()

    def _initialize_tax_optimizations(self) -> List[Dict[str, Any]]:
        """Initialize database of legal tax optimization opportunities"""
        return [
            {
                "id": "rd_tax_credit",
                "name": "R&D Tax Credit",
                "type": "tax_credit",
                "jurisdiction": ["USA", "UK", "Canada", "Australia"],
                "description": "Tax credit for qualified research and development expenses",
                "potential_savings": "6-10% of qualified R&D expenses",
                "eligibility": {
                    "industries": ["technology", "manufacturing", "biotech", "engineering"],
                    "activities": ["software development", "product design", "process improvement"],
                    "min_revenue": 0
                },
                "compliance_requirements": [
                    "Detailed project documentation",
                    "Time tracking for R&D activities",
                    "Contemporaneous records"
                ],
                "risk_level": "low",
                "complexity": "medium"
            },
            {
                "id": "section_179",
                "name": "Section 179 Deduction",
                "type": "deduction",
                "jurisdiction": ["USA"],
                "description": "Immediate expensing of equipment and software purchases",
                "potential_savings": "Up to $1.16M in 2023",
                "eligibility": {
                    "asset_types": ["equipment", "machinery", "software", "vehicles"],
                    "business_use": "50% or more",
                    "min_revenue": 0
                },
                "compliance_requirements": [
                    "Assets placed in service during tax year",
                    "Form 4562 filing",
                    "Recapture if business use drops below 50%"
                ],
                "risk_level": "low",
                "complexity": "low"
            },
            {
                "id": "qsbs_exclusion",
                "name": "Qualified Small Business Stock (QSBS) Exclusion",
                "type": "capital_gains_exclusion",
                "jurisdiction": ["USA"],
                "description": "Exclude up to 100% of capital gains on QSBS sale",
                "potential_savings": "Up to $10M or 10x basis (whichever is greater)",
                "eligibility": {
                    "company_type": "C-Corporation",
                    "gross_assets": "Under $50M at issuance",
                    "holding_period": "5 years minimum",
                    "active_business": "80% of assets in active trade"
                },
                "compliance_requirements": [
                    "Stock issued after August 10, 1993",
                    "Original issuance (not secondary market)",
                    "Active business requirement maintained"
                ],
                "risk_level": "low",
                "complexity": "high"
            },
            {
                "id": "home_office_deduction",
                "name": "Home Office Deduction",
                "type": "deduction",
                "jurisdiction": ["USA", "UK", "Canada"],
                "description": "Deduct portion of home expenses for business use",
                "potential_savings": "10-30% of home expenses",
                "eligibility": {
                    "space_requirements": "Regular and exclusive business use",
                    "business_types": ["self-employed", "contractor", "sole_proprietor"],
                    "min_revenue": 0
                },
                "compliance_requirements": [
                    "Calculate square footage percentage",
                    "Maintain records of expenses",
                    "Can use simplified method ($5/sq ft up to 300 sq ft)"
                ],
                "risk_level": "medium",
                "complexity": "low"
            },
            {
                "id": "patent_box",
                "name": "Patent Box Regime",
                "type": "tax_reduction",
                "jurisdiction": ["UK", "Netherlands", "Ireland", "Belgium"],
                "description": "Reduced tax rate on profits from patented inventions",
                "potential_savings": "Effective 10% tax rate (UK)",
                "eligibility": {
                    "ip_types": ["patents", "certain copyrights"],
                    "development": "Substantial R&D activity required",
                    "ownership": "Direct or exclusive license"
                },
                "compliance_requirements": [
                    "Nexus calculation for qualifying profits",
                    "Streaming election",
                    "Annual reporting"
                ],
                "risk_level": "low",
                "complexity": "high"
            },
            {
                "id": "cost_segregation",
                "name": "Cost Segregation Study",
                "type": "depreciation_acceleration",
                "jurisdiction": ["USA"],
                "description": "Accelerate depreciation by reclassifying building components",
                "potential_savings": "20-40% of building cost in first year",
                "eligibility": {
                    "asset_types": ["real estate", "commercial property", "renovations"],
                    "ownership": "Owned or leased",
                    "min_building_value": 500000
                },
                "compliance_requirements": [
                    "Engineering-based analysis",
                    "IRS audit defense documentation",
                    "Form 3115 for retroactive studies"
                ],
                "risk_level": "low",
                "complexity": "high"
            },
            {
                "id": "employee_retention_credit",
                "name": "Employee Retention Credit",
                "type": "tax_credit",
                "jurisdiction": ["USA"],
                "description": "Credit for retaining employees during COVID-19",
                "potential_savings": "Up to $7,000 per employee per quarter",
                "eligibility": {
                    "time_period": "Q1 2021 - Q3 2021",
                    "conditions": ["Revenue decline", "Government shutdown order"],
                    "min_employees": 1
                },
                "compliance_requirements": [
                    "Form 941-X for retroactive claims",
                    "Document revenue decline or shutdown",
                    "Exclude PPP loan amounts"
                ],
                "risk_level": "medium",
                "complexity": "high"
            },
            {
                "id": "startup_costs_deduction",
                "name": "Startup Costs Deduction",
                "type": "deduction",
                "jurisdiction": ["USA", "UK", "Canada"],
                "description": "Deduct business startup and organizational costs",
                "potential_savings": "Up to $5,000 immediately, rest amortized over 15 years",
                "eligibility": {
                    "cost_types": ["market research", "legal fees", "incorporation costs"],
                    "timing": "Before business begins",
                    "max_immediate_deduction": 5000
                },
                "compliance_requirements": [
                    "Must elect deduction on first return",
                    "Costs must be reasonable",
                    "Document business startup nature"
                ],
                "risk_level": "low",
                "complexity": "low"
            }
        ]

    def _initialize_regulatory_frameworks(self) -> Dict[str, Any]:
        """Initialize regulatory frameworks by jurisdiction"""
        return {
            "USA": {
                "federal": {
                    "tax_code": "IRC",
                    "key_sections": ["179", "174", "41", "1202", "195"],
                    "regulatory_bodies": ["IRS", "SEC", "FTC"],
                    "compliance_intensity": "high"
                },
                "state": {
                    "variations": "high",
                    "key_differences": ["sales_tax", "income_tax", "nexus_rules"],
                    "favorable_states": ["Delaware", "Nevada", "Wyoming", "Texas"]
                }
            },
            "UK": {
                "tax_system": "territorial",
                "key_regimes": ["Patent Box", "R&D Relief", "EIS", "SEIS"],
                "regulatory_bodies": ["HMRC", "FCA"],
                "compliance_intensity": "medium"
            },
            "Ireland": {
                "corporate_tax_rate": "12.5%",
                "key_benefits": ["IP regimes", "R&D credits", "low tax rate"],
                "regulatory_bodies": ["Revenue Commissioners"],
                "compliance_intensity": "medium"
            },
            "Singapore": {
                "corporate_tax_rate": "17%",
                "key_benefits": ["Startup exemption", "PIC scheme", "tax holidays"],
                "regulatory_bodies": ["IRAS"],
                "compliance_intensity": "low"
            }
        }

    def _initialize_structure_benefits(self) -> Dict[str, Any]:
        """Initialize legal structure optimization benefits"""
        return {
            "C_Corporation": {
                "tax_advantages": [
                    "QSBS eligibility",
                    "Unlimited shareholders",
                    "Stock option flexibility"
                ],
                "disadvantages": [
                    "Double taxation on dividends",
                    "More complex compliance"
                ],
                "best_for": ["VC-backed startups", "high-growth companies"]
            },
            "S_Corporation": {
                "tax_advantages": [
                    "Pass-through taxation",
                    "Self-employment tax savings",
                    "QBI deduction eligible"
                ],
                "disadvantages": [
                    "Max 100 shareholders",
                    "Only US residents",
                    "One class of stock"
                ],
                "best_for": ["Small businesses", "family businesses"]
            },
            "LLC": {
                "tax_advantages": [
                    "Flexible taxation (disregarded, partnership, or corporate)",
                    "QBI deduction eligible",
                    "Self-employment tax strategies"
                ],
                "disadvantages": [
                    "Not eligible for QSBS",
                    "Harder to raise VC funding"
                ],
                "best_for": ["Service businesses", "real estate", "flexibility"]
            },
            "Partnership": {
                "tax_advantages": [
                    "Pass-through taxation",
                    "Flexible profit allocation",
                    "Step-up in basis on death"
                ],
                "disadvantages": [
                    "Unlimited liability (GP)",
                    "Self-employment taxes"
                ],
                "best_for": ["Professional services", "joint ventures"]
            }
        }

    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process loophole prediction request

        Args:
            query: User query about legal optimization
            context: Additional context (business info, jurisdiction, etc.)

        Returns:
            Dict with identified opportunities, strategies, and compliance requirements
        """
        try:
            logger.info(f"Processing loophole prediction query: {query[:100]}...")

            # Extract business information from context
            business_info = context.get("business_info", {}) if context else {}
            jurisdiction = context.get("jurisdiction", "USA") if context else "USA"

            # Identify applicable optimizations
            applicable_optimizations = await self._identify_optimizations(
                business_info, jurisdiction, query
            )

            # Analyze legal structure optimization
            structure_recommendations = await self._analyze_structure_optimization(
                business_info, applicable_optimizations
            )

            # Generate compliance strategy
            compliance_strategy = await self._generate_compliance_strategy(
                applicable_optimizations
            )

            # Calculate potential savings
            savings_analysis = await self._calculate_savings(
                business_info, applicable_optimizations
            )

            # Generate implementation roadmap
            implementation_plan = await self._generate_implementation_plan(
                applicable_optimizations
            )

            response = {
                "status": "success",
                "query": query,
                "jurisdiction": jurisdiction,
                "applicable_optimizations": applicable_optimizations,
                "structure_recommendations": structure_recommendations,
                "compliance_strategy": compliance_strategy,
                "savings_analysis": savings_analysis,
                "implementation_plan": implementation_plan,
                "risk_assessment": self._assess_risk(applicable_optimizations),
                "next_steps": self._generate_next_steps(applicable_optimizations),
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Successfully identified {len(applicable_optimizations)} optimization opportunities")
            return response

        except Exception as e:
            logger.error(f"Error in loophole prediction: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _identify_optimizations(
        self,
        business_info: Dict[str, Any],
        jurisdiction: str,
        query: str
    ) -> List[Dict[str, Any]]:
        """Identify applicable tax and regulatory optimizations"""
        applicable = []

        industry = business_info.get("industry", "").lower()
        revenue = business_info.get("revenue", 0)
        structure = business_info.get("structure", "").upper()
        employees = business_info.get("employees", 0)

        for optimization in self.tax_optimizations:
            # Check jurisdiction match
            if jurisdiction not in optimization.get("jurisdiction", []):
                continue

            # Check eligibility criteria
            eligibility = optimization.get("eligibility", {})

            # Industry check
            eligible_industries = eligibility.get("industries", [])
            if eligible_industries and industry not in eligible_industries:
                continue

            # Revenue check
            min_revenue = eligibility.get("min_revenue", 0)
            if revenue < min_revenue:
                continue

            # Structure check
            required_structure = eligibility.get("company_type", "")
            if required_structure and structure != required_structure:
                continue

            # Add to applicable list
            applicable.append(optimization)

        return applicable

    async def _analyze_structure_optimization(
        self,
        business_info: Dict[str, Any],
        optimizations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze if current legal structure is optimal"""
        current_structure = business_info.get("structure", "LLC")
        stage = business_info.get("stage", "early")
        funding_goal = business_info.get("funding_goal", "bootstrapped")

        # Check if QSBS-eligible opportunities exist
        has_qsbs = any(opt.get("id") == "qsbs_exclusion" for opt in optimizations)

        recommendations = []

        if has_qsbs and current_structure != "C_Corporation":
            recommendations.append({
                "action": "Consider converting to C-Corporation",
                "reason": "Enable QSBS eligibility for potential $10M+ tax-free exit",
                "timing": "Before next funding round",
                "priority": "high"
            })

        if current_structure == "LLC" and funding_goal == "VC":
            recommendations.append({
                "action": "Convert to C-Corporation",
                "reason": "VCs strongly prefer C-Corps for investment",
                "timing": "Before raising Series A",
                "priority": "high"
            })

        return {
            "current_structure": current_structure,
            "optimal_structure": "C_Corporation" if has_qsbs or funding_goal == "VC" else current_structure,
            "recommendations": recommendations,
            "structure_benefits": self.structure_benefits.get(current_structure, {})
        }

    async def _generate_compliance_strategy(
        self,
        optimizations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate compliance strategy for identified optimizations"""
        all_requirements = []
        documentation_needed = []
        filing_requirements = []

        for opt in optimizations:
            requirements = opt.get("compliance_requirements", [])
            all_requirements.extend(requirements)

            # Categorize requirements
            for req in requirements:
                if "document" in req.lower() or "record" in req.lower():
                    documentation_needed.append({
                        "optimization": opt["name"],
                        "requirement": req
                    })
                elif "form" in req.lower() or "filing" in req.lower():
                    filing_requirements.append({
                        "optimization": opt["name"],
                        "requirement": req
                    })

        return {
            "total_requirements": len(all_requirements),
            "documentation_needed": documentation_needed,
            "filing_requirements": filing_requirements,
            "recommended_tools": [
                "Tax compliance software",
                "Document management system",
                "Professional tax advisor"
            ],
            "audit_defense_strategy": self._generate_audit_defense_strategy(optimizations)
        }

    def _generate_audit_defense_strategy(self, optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate audit defense strategy"""
        high_risk = [opt for opt in optimizations if opt.get("risk_level") == "high"]
        medium_risk = [opt for opt in optimizations if opt.get("risk_level") == "medium"]

        return {
            "risk_summary": {
                "high_risk_optimizations": len(high_risk),
                "medium_risk_optimizations": len(medium_risk)
            },
            "defense_priorities": [
                "Maintain contemporaneous documentation",
                "Use reputable tax professionals",
                "Keep detailed time tracking for R&D",
                "Retain all receipts and invoices",
                "Document business purpose for all deductions"
            ],
            "recommended_insurance": "Tax audit defense insurance" if high_risk or len(medium_risk) > 2 else "Optional"
        }

    async def _calculate_savings(
        self,
        business_info: Dict[str, Any],
        optimizations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate potential tax savings"""
        revenue = business_info.get("revenue", 0)
        expenses = business_info.get("expenses", {})

        total_potential_savings = 0
        savings_breakdown = []

        for opt in optimizations:
            potential_savings = opt.get("potential_savings", "")

            # Estimate savings amount
            estimated_savings = self._estimate_savings_amount(
                opt, revenue, expenses
            )

            total_potential_savings += estimated_savings

            savings_breakdown.append({
                "optimization": opt["name"],
                "estimated_savings": estimated_savings,
                "description": potential_savings,
                "confidence": "high" if opt.get("risk_level") == "low" else "medium"
            })

        return {
            "total_potential_savings": total_potential_savings,
            "savings_breakdown": savings_breakdown,
            "effective_tax_rate_reduction": min(total_potential_savings / max(revenue, 1) * 100, 50),
            "roi_on_implementation": "300-500% typical ROI on tax planning costs"
        }

    def _estimate_savings_amount(
        self,
        optimization: Dict[str, Any],
        revenue: float,
        expenses: Dict[str, Any]
    ) -> float:
        """Estimate savings amount for an optimization"""
        opt_type = optimization.get("type")
        opt_id = optimization.get("id")

        # R&D Tax Credit: assume 6% of qualified expenses
        if opt_id == "rd_tax_credit":
            rd_expenses = expenses.get("research_development", revenue * 0.15)
            return rd_expenses * 0.06

        # Section 179: assume $50k in equipment purchases
        elif opt_id == "section_179":
            equipment = expenses.get("equipment", 50000)
            return equipment * 0.21  # Corporate tax rate

        # QSBS: highly variable, use conservative estimate
        elif opt_id == "qsbs_exclusion":
            return 2000000  # Conservative $2M in capital gains savings

        # Home office: assume 15% of home expenses
        elif opt_id == "home_office_deduction":
            return 5000  # Typical savings

        # Patent box: 10% effective rate difference
        elif opt_id == "patent_box":
            ip_revenue = revenue * 0.3  # Assume 30% from IP
            return ip_revenue * 0.09  # 19% vs 10% rate

        # Cost segregation: 20% of building value in year 1
        elif opt_id == "cost_segregation":
            return 100000  # Typical first-year acceleration benefit

        # ERC: $7k per employee per quarter
        elif opt_id == "employee_retention_credit":
            return 7000 * expenses.get("employees", 5) * 3  # 3 quarters

        # Startup costs: $5k immediate
        elif opt_id == "startup_costs_deduction":
            return 5000 * 0.21  # Corporate tax rate

        return 0

    async def _generate_implementation_plan(
        self,
        optimizations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate step-by-step implementation plan"""
        plan = []

        # Sort by priority: low complexity + high savings first
        sorted_opts = sorted(
            optimizations,
            key=lambda x: (x.get("complexity") == "low", x.get("risk_level") == "low"),
            reverse=True
        )

        for i, opt in enumerate(sorted_opts, 1):
            plan.append({
                "step": i,
                "optimization": opt["name"],
                "complexity": opt.get("complexity"),
                "timeline": self._estimate_timeline(opt),
                "required_resources": self._estimate_resources(opt),
                "dependencies": opt.get("compliance_requirements", [])[:2]  # Top 2 requirements
            })

        return plan

    def _estimate_timeline(self, optimization: Dict[str, Any]) -> str:
        """Estimate implementation timeline"""
        complexity = optimization.get("complexity")
        if complexity == "low":
            return "1-2 weeks"
        elif complexity == "medium":
            return "1-2 months"
        else:
            return "3-6 months"

    def _estimate_resources(self, optimization: Dict[str, Any]) -> List[str]:
        """Estimate required resources"""
        complexity = optimization.get("complexity")
        resources = ["Tax advisor consultation"]

        if complexity in ["medium", "high"]:
            resources.append("CPA or tax attorney")

        if optimization.get("id") == "cost_segregation":
            resources.append("Engineering firm for cost segregation study")

        if optimization.get("id") == "rd_tax_credit":
            resources.append("R&D tax credit specialist")

        return resources

    def _assess_risk(self, optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess overall risk of optimization strategy"""
        risk_counts = {"low": 0, "medium": 0, "high": 0}

        for opt in optimizations:
            risk_level = opt.get("risk_level", "medium")
            risk_counts[risk_level] += 1

        overall_risk = "low"
        if risk_counts["high"] > 0:
            overall_risk = "high"
        elif risk_counts["medium"] > 2:
            overall_risk = "medium"

        return {
            "overall_risk": overall_risk,
            "risk_distribution": risk_counts,
            "audit_probability": "5-10%" if overall_risk == "low" else "10-25%",
            "mitigation_strategy": "Work with experienced tax professionals and maintain excellent documentation"
        }

    def _generate_next_steps(self, optimizations: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable next steps"""
        if not optimizations:
            return ["No immediate optimizations identified", "Consider consulting with tax advisor"]

        return [
            f"Review {len(optimizations)} identified optimization opportunities with your tax advisor",
            "Prioritize low-complexity, high-savings opportunities for immediate implementation",
            "Set up documentation systems for compliance requirements",
            "Schedule quarterly reviews to identify new opportunities",
            "Consider engaging specialists for complex optimizations (R&D credits, cost segregation)"
        ]

    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return self.capabilities

    def get_optimization_database_stats(self) -> Dict[str, Any]:
        """Return statistics about the optimization database"""
        return {
            "total_optimizations": len(self.tax_optimizations),
            "by_type": {
                "tax_credit": len([o for o in self.tax_optimizations if o["type"] == "tax_credit"]),
                "deduction": len([o for o in self.tax_optimizations if o["type"] == "deduction"]),
                "other": len([o for o in self.tax_optimizations if o["type"] not in ["tax_credit", "deduction"]])
            },
            "jurisdictions_covered": len(self.regulatory_frameworks),
            "structure_types": len(self.structure_benefits)
        }
