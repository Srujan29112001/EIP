"""
Regulator Analysis Agent
Monitors SEBI, RBI, CCI, industry-specific regulators, regulatory risk assessment, and compliance calendar
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


class RegulatorAnalysisAgent:
    """
    Regulator Analysis Agent

    Provides comprehensive regulatory intelligence including:
    - SEBI (Securities and Exchange Board of India) monitoring
    - RBI (Reserve Bank of India) regulations
    - CCI (Competition Commission of India) analysis
    - Industry-specific regulators (IRDAI, TRAI, FSSAI, etc.)
    - Regulatory risk assessment
    - Compliance calendar and deadline tracking
    - Recent regulatory changes impact analysis
    """

    def __init__(self):
        """Initialize Regulator Analysis Agent"""
        self.name = "RegulatorAnalysisAgent"
        self.description = "Comprehensive regulatory monitoring and compliance analysis"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

        # Initialize regulators database
        self.regulators_db = self._initialize_regulators_db()

        # Compliance categories
        self.compliance_categories = [
            "incorporation", "taxation", "labor", "financial",
            "data_privacy", "industry_specific", "environmental"
        ]

    def _initialize_regulators_db(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive regulators database"""
        return {
            # Financial Regulators
            "SEBI": {
                "full_name": "Securities and Exchange Board of India",
                "jurisdiction": "Securities markets, listed companies, mutual funds, portfolio managers",
                "key_regulations": [
                    "SEBI (ICDR) Regulations, 2018 - IPO, FPO regulations",
                    "SEBI (LODR) Regulations, 2015 - Listing obligations",
                    "SEBI (AIF) Regulations, 2012 - Alternative Investment Funds",
                    "SEBI (VCF) Regulations, 1996 - Venture Capital Funds",
                    "SEBI (Substantial Acquisition of Shares and Takeovers) Regulations, 2011"
                ],
                "relevance_for_startups": {
                    "pre_ipo": "High - for companies planning IPO in 2-3 years",
                    "fundraising": "High - if raising from AIFs, VCFs, or institutional investors",
                    "esop": "Medium - ESOP regulations for unlisted companies"
                },
                "recent_changes": [
                    "2024: Relaxation in IPO lock-in norms for anchor investors",
                    "2023: New SEBI framework for SME IPOs",
                    "2023: Stricter disclosure norms for listed companies"
                ],
                "compliance_frequency": "Quarterly and Annual (for listed entities)",
                "penalties": "Monetary penalties, trading restrictions, debarment",
                "website": "https://www.sebi.gov.in"
            },

            "RBI": {
                "full_name": "Reserve Bank of India",
                "jurisdiction": "Banking, NBFCs, payment systems, foreign exchange, credit information",
                "key_regulations": [
                    "RBI Master Directions on PPIs (Prepaid Payment Instruments)",
                    "FEMA (Foreign Exchange Management Act) - foreign investments",
                    "Payment and Settlement Systems Act, 2007",
                    "RBI (NBFC) Directions - for loan/credit companies",
                    "KYC Master Direction"
                ],
                "relevance_for_startups": {
                    "fintech": "Critical - must comply with PPI, PA, NBFC norms",
                    "foreign_funding": "High - FDI/FEMA compliance for foreign investors",
                    "payments": "High - if handling payments/wallets"
                },
                "recent_changes": [
                    "2024: New UPI transaction limits and security norms",
                    "2023: Account Aggregator framework operationalized",
                    "2023: Stricter KYC norms for digital lending",
                    "2023: Ban on certain digital lending apps"
                ],
                "compliance_frequency": "Varies by activity - monthly to annual",
                "penalties": "Monetary fines, license cancellation, criminal prosecution",
                "website": "https://www.rbi.org.in"
            },

            "CCI": {
                "full_name": "Competition Commission of India",
                "jurisdiction": "Anti-competitive practices, mergers and acquisitions, cartels",
                "key_regulations": [
                    "Competition Act, 2002",
                    "Combination Regulations (Merger Control)",
                    "Anti-competitive agreements regulations",
                    "Abuse of dominant position provisions"
                ],
                "relevance_for_startups": {
                    "ma": "High - for M&A deals above threshold (₹2000 Cr assets or ₹6000 Cr turnover)",
                    "marketplace": "Medium - for platform/marketplace businesses",
                    "dominant_position": "Low initially, High after achieving market dominance"
                },
                "recent_changes": [
                    "2023: New merger control thresholds - deal value test introduced",
                    "2023: Increased scrutiny of digital platforms",
                    "2022: Penalties on e-commerce giants for anti-competitive practices"
                ],
                "compliance_frequency": "Transaction-based (M&A approval), or investigation-based",
                "penalties": "Up to 10% of turnover for anti-competitive practices",
                "website": "https://www.cci.gov.in"
            },

            # Industry-Specific Regulators
            "IRDAI": {
                "full_name": "Insurance Regulatory and Development Authority of India",
                "jurisdiction": "Insurance sector - life, general, health insurance",
                "key_regulations": [
                    "IRDAI (Registration of Corporate Agents) Regulations",
                    "IRDAI (Insurance Brokers) Regulations",
                    "IRDAI (Web Aggregators) Regulations, 2017",
                    "InsurTech sandbox regulations"
                ],
                "relevance_for_startups": {
                    "insurtech": "Critical - mandatory license/registration",
                    "aggregators": "High - web aggregator license required",
                    "brokers": "High - broker license for insurance sales"
                },
                "recent_changes": [
                    "2024: New regulations for health insurance portability",
                    "2023: Sandbox for InsurTech innovations",
                    "2022: Revised commission structure for agents"
                ],
                "compliance_frequency": "Annual, Quarterly reporting",
                "penalties": "License suspension, monetary penalties",
                "website": "https://www.irdai.gov.in"
            },

            "TRAI": {
                "full_name": "Telecom Regulatory Authority of India",
                "jurisdiction": "Telecommunications, broadcasting, cable services",
                "key_regulations": [
                    "TRAI (Telecommunications Tariff) Order",
                    "Telecom Commercial Communications Customer Preference Regulations (DND)",
                    "Broadcasting and Cable Services regulations",
                    "Net Neutrality regulations"
                ],
                "relevance_for_startups": {
                    "telecom": "Critical - telecom operators, VoIP services",
                    "ott": "Medium - OTT communication services",
                    "marketing": "High - if sending commercial SMS/calls (DND compliance)"
                },
                "recent_changes": [
                    "2024: New framework for OTT communication services",
                    "2023: Stricter DND and SMS spam regulations",
                    "2023: Blockchain-based DLT for commercial messages"
                ],
                "compliance_frequency": "Ongoing for DND, periodic for others",
                "penalties": "Financial penalties, service suspension",
                "website": "https://www.trai.gov.in"
            },

            "FSSAI": {
                "full_name": "Food Safety and Standards Authority of India",
                "jurisdiction": "Food safety, manufacturing, storage, distribution",
                "key_regulations": [
                    "Food Safety and Standards Act, 2006",
                    "FSSAI License and Registration requirements",
                    "Food labeling and packaging regulations",
                    "E-commerce food business regulations"
                ],
                "relevance_for_startups": {
                    "foodtech": "Critical - mandatory FSSAI license",
                    "delivery": "High - food aggregators need license",
                    "manufacturing": "Critical - for food manufacturing units"
                },
                "recent_changes": [
                    "2024: New norms for quick commerce food delivery",
                    "2023: Enhanced labeling requirements for packaged foods",
                    "2022: Specific regulations for food e-commerce"
                ],
                "compliance_frequency": "Annual license renewal, ongoing compliance",
                "penalties": "Fines up to ₹10 lakh, imprisonment, business closure",
                "website": "https://www.fssai.gov.in"
            },

            "MeitY": {
                "full_name": "Ministry of Electronics and Information Technology",
                "jurisdiction": "IT, electronics, digital services, data protection, cybersecurity",
                "key_regulations": [
                    "Information Technology Act, 2000",
                    "IT (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021",
                    "Digital Personal Data Protection Act, 2023",
                    "Cybersecurity regulations"
                ],
                "relevance_for_startups": {
                    "all_digital": "High - data protection compliance for all",
                    "social_media": "Critical - intermediary compliance",
                    "ecommerce": "High - consumer protection, data privacy"
                },
                "recent_changes": [
                    "2023: Digital Personal Data Protection Act enacted",
                    "2023: New IT Rules for online gaming",
                    "2022: Cybersecurity directions for VPN providers"
                ],
                "compliance_frequency": "Ongoing compliance, incident reporting within 6 hours",
                "penalties": "Up to ₹250 crore or 4% of global turnover under DPDP Act",
                "website": "https://www.meity.gov.in"
            },

            "MCA": {
                "full_name": "Ministry of Corporate Affairs",
                "jurisdiction": "Company incorporation, corporate governance, compliance",
                "key_regulations": [
                    "Companies Act, 2013",
                    "LLP Act, 2008",
                    "Annual ROC filings (AOC-4, MGT-7, etc.)",
                    "Director KYC and DIN regulations"
                ],
                "relevance_for_startups": {
                    "all_companies": "Critical - mandatory compliance for all Pvt Ltd/LLPs",
                    "governance": "High - board meetings, AGM, statutory filings"
                },
                "recent_changes": [
                    "2024: Simplified incorporation process",
                    "2023: New DIN KYC requirements",
                    "2023: Revised CSR norms (for companies with ₹5Cr+ profit)"
                ],
                "compliance_frequency": "Annual (AOC-4, MGT-7), Event-based (SH-7, DIR-12)",
                "penalties": "Late fees, director disqualification, company strike-off",
                "website": "https://www.mca.gov.in"
            }
        }

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process regulatory analysis request

        Args:
            query: User query about regulations
            context: Business context (industry, activities, stage, etc.)

        Returns:
            Dict with regulatory analysis results
        """
        try:
            # Extract business context
            business_context = self._extract_business_context(query, context)

            # Identify applicable regulators
            applicable_regulators = await self._identify_regulators(business_context)

            # Assess regulatory risk
            risk_assessment = await self._assess_regulatory_risk(
                business_context,
                applicable_regulators
            )

            # Generate compliance calendar
            compliance_calendar = self._generate_compliance_calendar(
                applicable_regulators,
                business_context
            )

            # Analyze recent regulatory changes
            recent_changes_impact = await self._analyze_recent_changes(
                applicable_regulators,
                business_context
            )

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                business_context,
                risk_assessment,
                applicable_regulators
            )

            # Create response
            response = await self._generate_response(
                query,
                business_context,
                applicable_regulators,
                risk_assessment,
                compliance_calendar,
                recommendations
            )

            return {
                "answer": response,
                "applicable_regulators": applicable_regulators,
                "risk_assessment": risk_assessment,
                "compliance_calendar": compliance_calendar,
                "recent_changes": recent_changes_impact,
                "recommendations": recommendations,
                "confidence": 0.90,
                "sources": self._get_sources(applicable_regulators),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in RegulatorAnalysisAgent: {str(e)}")
            return self._error_response(str(e))

    def _extract_business_context(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract business context"""

        if context:
            return {
                "industry": context.get("industry", "Technology"),
                "business_model": context.get("business_model", "B2B SaaS"),
                "activities": context.get("activities", ["Software development"]),
                "stage": context.get("stage", "seed"),
                "revenue": context.get("revenue", 0),
                "entity_type": context.get("entity_type", "Private Limited"),
                "foreign_funding": context.get("foreign_funding", False),
                "listed": context.get("listed", False),
                "planning_ipo": context.get("planning_ipo", False),
                "handles_payments": context.get("handles_payments", False),
                "data_handling": context.get("data_handling", True)
            }
        else:
            return {
                "industry": self._detect_industry(query),
                "business_model": "B2B SaaS",
                "activities": ["Software development"],
                "stage": "seed",
                "revenue": 0,
                "entity_type": "Private Limited",
                "foreign_funding": False,
                "listed": False,
                "planning_ipo": False,
                "handles_payments": "payment" in query.lower() or "fintech" in query.lower(),
                "data_handling": True
            }

    def _detect_industry(self, text: str) -> str:
        """Detect industry from text"""
        industry_keywords = {
            "FinTech": ["fintech", "payments", "lending", "banking", "nbfc"],
            "InsurTech": ["insurance", "insurtech"],
            "FoodTech": ["food", "restaurant", "delivery", "zomato", "swiggy"],
            "HealthTech": ["health", "medical", "telemedicine", "hospital"],
            "EdTech": ["education", "edtech", "learning"],
            "E-commerce": ["ecommerce", "marketplace", "online store"],
            "SaaS": ["saas", "software", "b2b software"],
            "Telecom": ["telecom", "voip", "communication"]
        }

        text_lower = text.lower()
        for industry, keywords in industry_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return industry

        return "Technology"

    async def _identify_regulators(
        self,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify applicable regulators based on business context"""

        applicable = []

        # MCA - applies to all companies/LLPs
        if context["entity_type"] in ["Private Limited", "Public Limited", "LLP"]:
            regulator = self.regulators_db["MCA"].copy()
            regulator["applicability"] = "Mandatory"
            regulator["priority"] = "Critical"
            applicable.append(regulator)

        # MeitY - applies to all digital businesses
        if context["data_handling"] or context["industry"] != "Manufacturing":
            regulator = self.regulators_db["MeitY"].copy()
            regulator["applicability"] = "High - Data Protection Compliance"
            regulator["priority"] = "High"
            applicable.append(regulator)

        # Industry-specific
        if context["industry"] == "FinTech" or context["handles_payments"]:
            regulator = self.regulators_db["RBI"].copy()
            regulator["applicability"] = "Critical - FinTech operations"
            regulator["priority"] = "Critical"
            applicable.append(regulator)

        if context["planning_ipo"] or context["listed"]:
            regulator = self.regulators_db["SEBI"].copy()
            regulator["applicability"] = "Critical - IPO/Listed company"
            regulator["priority"] = "Critical"
            applicable.append(regulator)

        if context["industry"] == "InsurTech":
            regulator = self.regulators_db["IRDAI"].copy()
            regulator["applicability"] = "Critical - Insurance operations"
            regulator["priority"] = "Critical"
            applicable.append(regulator)

        if context["industry"] == "FoodTech":
            regulator = self.regulators_db["FSSAI"].copy()
            regulator["applicability"] = "Critical - Food business"
            regulator["priority"] = "Critical"
            applicable.append(regulator)

        if context["industry"] == "Telecom":
            regulator = self.regulators_db["TRAI"].copy()
            regulator["applicability"] = "Critical - Telecom services"
            regulator["priority"] = "Critical"
            applicable.append(regulator)

        # CCI - for large M&A or dominant players
        if context["revenue"] > 200000000 or context["stage"] in ["growth", "expansion"]:
            regulator = self.regulators_db["CCI"].copy()
            regulator["applicability"] = "Medium - M&A approval may be needed"
            regulator["priority"] = "Medium"
            applicable.append(regulator)

        return applicable

    async def _assess_regulatory_risk(
        self,
        context: Dict[str, Any],
        regulators: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess regulatory risk"""

        risk_score = 0
        risk_factors = []

        # Count critical regulators
        critical_count = sum(1 for r in regulators if r.get("priority") == "Critical")
        risk_score += critical_count * 2

        # Industry-specific risks
        high_risk_industries = ["FinTech", "InsurTech", "FoodTech", "HealthTech"]
        if context["industry"] in high_risk_industries:
            risk_score += 3
            risk_factors.append(f"{context['industry']} is highly regulated")

        # Foreign funding
        if context["foreign_funding"]:
            risk_score += 2
            risk_factors.append("Foreign funding requires FEMA compliance")

        # Payments handling
        if context["handles_payments"]:
            risk_score += 2
            risk_factors.append("Payment handling requires RBI compliance")

        # Data handling
        if context["data_handling"]:
            risk_score += 1
            risk_factors.append("Data handling requires DPDP Act compliance")

        # Risk level
        if risk_score >= 8:
            risk_level = "High"
        elif risk_score >= 5:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "critical_regulators": critical_count,
            "total_regulators": len(regulators),
            "recommended_action": self._get_risk_action(risk_level)
        }

    def _get_risk_action(self, risk_level: str) -> str:
        """Get recommended action based on risk level"""
        actions = {
            "High": "Engage regulatory compliance consultant immediately. Set up compliance team. Budget ₹5-10L annually for compliance.",
            "Medium": "Hire part-time compliance officer or consultant. Implement compliance tracking system. Budget ₹2-5L annually.",
            "Low": "Educate founders on basic compliance. Use compliance software. Budget ₹50K-1L annually."
        }
        return actions.get(risk_level, "Monitor regulatory changes")

    def _generate_compliance_calendar(
        self,
        regulators: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate compliance calendar"""

        calendar = {
            "monthly": [],
            "quarterly": [],
            "annual": [],
            "event_based": []
        }

        # MCA - Annual filings
        if any(r.get("full_name") == "Ministry of Corporate Affairs" for r in regulators):
            calendar["annual"].append({
                "compliance": "AOC-4 (Financial Statements)",
                "deadline": "Within 30 days of AGM",
                "regulator": "MCA",
                "penalty": "₹100/day delay"
            })
            calendar["annual"].append({
                "compliance": "MGT-7 (Annual Return)",
                "deadline": "Within 60 days of AGM",
                "regulator": "MCA",
                "penalty": "₹100/day delay"
            })
            calendar["annual"].append({
                "compliance": "Income Tax Return filing",
                "deadline": "September 30",
                "regulator": "Income Tax Department",
                "penalty": "Interest + penalty"
            })

        # GST - Monthly/Quarterly
        calendar["monthly"].append({
            "compliance": "GST Returns (GSTR-1, GSTR-3B)",
            "deadline": "10th and 20th of next month",
            "regulator": "GST Department",
            "penalty": "Late fee + interest"
        })

        # TDS - Quarterly
        calendar["quarterly"].append({
            "compliance": "TDS Return filing",
            "deadline": "31st of next month after quarter",
            "regulator": "Income Tax Department",
            "penalty": "₹200/day delay"
        })

        # PF/ESI - Monthly
        if context.get("team_size", 0) > 0:
            calendar["monthly"].append({
                "compliance": "PF & ESI payment",
                "deadline": "15th of next month",
                "regulator": "EPFO / ESIC",
                "penalty": "Interest + damages"
            })

        # RBI - if applicable
        if any(r.get("full_name") == "Reserve Bank of India" for r in regulators):
            calendar["annual"].append({
                "compliance": "FLA Return (if foreign investment)",
                "deadline": "July 15 (annual)",
                "regulator": "RBI",
                "penalty": "Penalty up to ₹1 lakh"
            })

        # Event-based
        calendar["event_based"].append({
            "compliance": "DIR-12 (Director appointment/resignation)",
            "deadline": "Within 30 days of event",
            "regulator": "MCA",
            "penalty": "₹5,000 penalty"
        })
        calendar["event_based"].append({
            "compliance": "SH-7 (Allotment of shares)",
            "deadline": "Within 30 days of allotment",
            "regulator": "MCA",
            "penalty": "Late fees"
        })

        return calendar

    async def _analyze_recent_changes(
        self,
        regulators: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze recent regulatory changes and their impact"""

        changes = []

        for regulator in regulators:
            recent_changes = regulator.get("recent_changes", [])
            for change in recent_changes[:2]:  # Top 2 changes per regulator
                changes.append({
                    "regulator": regulator.get("full_name"),
                    "change": change,
                    "impact": "High" if "new" in change.lower() or "stricter" in change.lower() else "Medium",
                    "action_required": "Review and ensure compliance"
                })

        # Sort by impact
        changes.sort(key=lambda x: 0 if x["impact"] == "High" else 1)

        return changes[:5]  # Top 5 changes

    async def _generate_recommendations(
        self,
        context: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        regulators: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate regulatory recommendations"""

        recommendations = []

        # Based on risk level
        if risk_assessment["risk_level"] == "High":
            recommendations.append({
                "title": "Engage Regulatory Compliance Consultant",
                "description": "Given high regulatory risk, engage a specialized compliance consultant for your industry",
                "priority": "critical",
                "timeline": "Immediate",
                "estimated_cost": "₹5-10L annually"
            })

        # Compliance management system
        recommendations.append({
            "title": "Implement Compliance Management System",
            "description": "Use software like Leegality, Complianceship, or Zoho Compliance to track all compliance deadlines",
            "priority": "high",
            "timeline": "1 month",
            "estimated_cost": "₹50K-2L annually"
        })

        # Regular audits
        if context["revenue"] > 10000000:  # > 1 Cr
            recommendations.append({
                "title": "Schedule Annual Compliance Audit",
                "description": "Conduct comprehensive compliance audit to identify gaps and ensure adherence",
                "priority": "medium",
                "timeline": "Annual",
                "estimated_cost": "₹1-3L per audit"
            })

        return recommendations

    async def _generate_response(
        self,
        query: str,
        context: Dict[str, Any],
        regulators: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any],
        compliance_calendar: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> str:
        """Generate comprehensive response"""

        response_parts = []

        response_parts.append("## Regulatory Analysis Report\n")
        response_parts.append(f"**Industry:** {context['industry']}")
        response_parts.append(f"**Business Model:** {context['business_model']}")
        response_parts.append(f"**Entity Type:** {context['entity_type']}\n")

        # Risk assessment
        response_parts.append(f"### Regulatory Risk: {risk_assessment['risk_level']}")
        response_parts.append(f"**Risk Score:** {risk_assessment['risk_score']}/10")
        response_parts.append(f"**Critical Regulators:** {risk_assessment['critical_regulators']}")
        response_parts.append(f"**Total Applicable Regulators:** {risk_assessment['total_regulators']}\n")

        response_parts.append("**Key Risk Factors:**")
        for factor in risk_assessment['risk_factors']:
            response_parts.append(f"• {factor}")
        response_parts.append("")

        # Applicable regulators
        response_parts.append(f"### {len(regulators)} Applicable Regulators:\n")
        for i, reg in enumerate(regulators, 1):
            response_parts.append(f"**{i}. {reg['full_name']} ({reg.get('applicability', 'Applicable')})**")
            response_parts.append(f"   Priority: {reg.get('priority', 'Medium')}")
            response_parts.append(f"   Website: {reg.get('website', 'N/A')}")
            response_parts.append(f"   Key Regulations:")
            for kr in reg.get('key_regulations', [])[:2]:
                response_parts.append(f"   • {kr}")
            response_parts.append("")

        # Compliance calendar highlights
        response_parts.append("### 📅 Compliance Calendar (Key Deadlines):\n")
        response_parts.append("**Monthly:**")
        for comp in compliance_calendar.get('monthly', [])[:3]:
            response_parts.append(f"• {comp['compliance']} - Due: {comp['deadline']}")

        response_parts.append("\n**Annual:**")
        for comp in compliance_calendar.get('annual', [])[:3]:
            response_parts.append(f"• {comp['compliance']} - Due: {comp['deadline']}")

        # Recommendations
        response_parts.append("\n### Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            response_parts.append(f"{i}. **{rec['title']}** ({rec['priority']} priority)")
            response_parts.append(f"   {rec['description']}")
            response_parts.append(f"   Timeline: {rec['timeline']} | Cost: {rec.get('estimated_cost', 'Varies')}\n")

        response_parts.append(f"\n**Action Required:** {risk_assessment['recommended_action']}")

        response_parts.append("\n*Note: Regulatory landscape changes frequently. Please verify current requirements on official regulator websites.*")

        return "\n".join(response_parts)

    def _get_sources(self, regulators: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Get sources"""
        sources = []
        for reg in regulators:
            sources.append({
                "title": reg.get("full_name", "Regulator"),
                "url": reg.get("website", ""),
                "type": "regulatory_authority"
            })
        return sources

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "answer": f"I encountered an error while analyzing regulatory requirements: {error}. Please provide details like industry, business activities, and entity type.",
            "error": error,
            "confidence": 0.0,
            "agent": self.name
        }


# Export
__all__ = ["RegulatorAnalysisAgent"]
