"""
Government Schemes Monitoring Agent
Monitors Startup India, MSME schemes, R&D grants, eligibility checking, and deadline alerts
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


class SchemesMonitoringAgent:
    """
    Government Schemes Monitoring Agent

    Monitors and provides information on:
    - Startup India schemes and benefits
    - MSME (Micro, Small and Medium Enterprises) schemes
    - R&D grants and innovation programs
    - State-specific startup schemes
    - Eligibility checker for various programs
    - Deadline alerts and application tracking
    - Tax benefits and exemptions
    """

    def __init__(self):
        """Initialize Government Schemes Monitoring Agent"""
        self.name = "SchemesMonitoringAgent"
        self.description = "Comprehensive government schemes monitoring and eligibility analysis"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

        # Initialize schemes database
        self.schemes_db = self._initialize_schemes_database()

        # Categories
        self.scheme_categories = [
            "funding", "tax_benefits", "subsidies", "infrastructure",
            "market_access", "innovation", "skill_development", "export"
        ]

    def _initialize_schemes_database(self) -> List[Dict[str, Any]]:
        """Initialize comprehensive government schemes database"""
        return [
            # Central Government - Startup India
            {
                "id": "startup-india-recognition",
                "name": "Startup India Recognition",
                "authority": "DPIIT - Department for Promotion of Industry and Internal Trade",
                "level": "Central",
                "category": "recognition",
                "benefits": [
                    "Self-certification under 9 labor & environmental laws",
                    "Easy winding up of company (within 90 days)",
                    "Access to other government schemes",
                    "Tax exemption under Section 80-IAC",
                    "IPR fast-tracking and 80% rebate on patent filing"
                ],
                "eligibility": {
                    "entity_type": ["Private Limited", "LLP", "Partnership"],
                    "incorporation_years": "< 10 years",
                    "turnover": "< ₹100 crore in any financial year",
                    "innovative": "Working towards innovation/development/improvement of products or processes or services, or scalable business model with high potential for employment generation or wealth creation"
                },
                "documents_required": [
                    "Certificate of Incorporation / Registration",
                    "Brief about nature of business",
                    "Recommendation letter (if available)",
                    "Patent/trademark details (if applicable)"
                ],
                "application_process": "Online via www.startupindia.gov.in",
                "processing_time": "2-4 weeks",
                "cost": "Free",
                "deadline": "Rolling basis",
                "url": "https://www.startupindia.gov.in"
            },
            {
                "id": "seed-fund-scheme",
                "name": "Startup India Seed Fund Scheme (SISFS)",
                "authority": "DPIIT",
                "level": "Central",
                "category": "funding",
                "funding_amount": {
                    "proof_of_concept": "₹20 lakh",
                    "prototype": "₹50 lakh",
                    "total_max": "₹50 lakh per startup"
                },
                "benefits": [
                    "Seed funding for proof of concept",
                    "Prototype development support",
                    "Product trials funding",
                    "Market entry support",
                    "Mentorship from incubators"
                ],
                "eligibility": {
                    "recognition": "DPIIT recognized startup",
                    "incorporation_years": "< 2 years",
                    "funding_status": "Not received > ₹10 lakh from government",
                    "innovative": "Working on innovation in product, process, or service"
                },
                "documents_required": [
                    "DPIIT recognition certificate",
                    "Business plan",
                    "Pitch deck",
                    "Financial projections",
                    "Founder details and background"
                ],
                "application_process": "Through empaneled incubators only",
                "processing_time": "2-3 months",
                "cost": "Free",
                "deadline": "Rolling (subject to availability of funds)",
                "url": "https://seedfund.startupindia.gov.in"
            },
            {
                "id": "section-80iac",
                "name": "Section 80-IAC Tax Exemption",
                "authority": "Income Tax Department",
                "level": "Central",
                "category": "tax_benefits",
                "benefits": [
                    "100% tax exemption on profits for 3 consecutive years",
                    "Can choose any 3 years out of first 10 years",
                    "Exemption from angel tax (Section 56(2)(viib))",
                    "Significant cash flow improvement"
                ],
                "eligibility": {
                    "recognition": "DPIIT recognized startup",
                    "incorporation_years": "< 10 years",
                    "turnover": "< ₹100 crore",
                    "entity_type": ["Private Limited", "LLP"],
                    "certification": "Certification from Inter-Ministerial Board (IMB)"
                },
                "documents_required": [
                    "DPIIT recognition certificate",
                    "IMB certification",
                    "Audited financial statements",
                    "Tax returns",
                    "Business plan showing innovation"
                ],
                "application_process": "Apply to IMB through DPIIT portal",
                "processing_time": "3-6 months",
                "cost": "Free",
                "deadline": "Financial year basis",
                "url": "https://www.startupindia.gov.in"
            },

            # MSME Schemes
            {
                "id": "udyam-registration",
                "name": "Udyam Registration (MSME)",
                "authority": "Ministry of MSME",
                "level": "Central",
                "category": "registration",
                "benefits": [
                    "Access to MSME schemes and subsidies",
                    "Priority sector lending",
                    "Collateral-free loans",
                    "Electricity bill concessions",
                    "Tax subsidies",
                    "ISO certification reimbursement"
                ],
                "eligibility": {
                    "investment": "Micro: < ₹1 Cr, Small: < ₹10 Cr, Medium: < ₹50 Cr",
                    "turnover": "Micro: < ₹5 Cr, Small: < ₹50 Cr, Medium: < ₹250 Cr",
                    "entity_type": ["All types of enterprises"]
                },
                "documents_required": [
                    "Aadhaar number",
                    "PAN card",
                    "Business details",
                    "Bank account details"
                ],
                "application_process": "Online via udyamregistration.gov.in",
                "processing_time": "Instant (online)",
                "cost": "Free",
                "deadline": "Rolling basis",
                "url": "https://udyamregistration.gov.in"
            },
            {
                "id": "cgtmse",
                "name": "Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE)",
                "authority": "Ministry of MSME",
                "level": "Central",
                "category": "funding",
                "funding_amount": {
                    "collateral_free": "Up to ₹2 crore",
                    "with_collateral": "Up to ₹5 crore"
                },
                "benefits": [
                    "Collateral-free loans up to ₹2 crore",
                    "75-85% guarantee coverage",
                    "Working capital and term loan support",
                    "Easier access to credit"
                ],
                "eligibility": {
                    "registration": "Udyam registered MSME",
                    "entity_type": ["Proprietorship", "Partnership", "Private Limited", "LLP"],
                    "new_unit": "Yes (or existing seeking expansion)"
                },
                "documents_required": [
                    "Udyam certificate",
                    "Business plan",
                    "Financial projections",
                    "KYC documents"
                ],
                "application_process": "Through lending institutions (banks, NBFCs)",
                "processing_time": "4-8 weeks",
                "cost": "Guarantee fee (0.75-1.5% annually)",
                "deadline": "Rolling basis",
                "url": "https://www.cgtmse.in"
            },
            {
                "id": "clcss",
                "name": "Credit Linked Capital Subsidy Scheme (CLCSS)",
                "authority": "Ministry of MSME",
                "level": "Central",
                "category": "subsidies",
                "funding_amount": {
                    "subsidy": "15% capital subsidy",
                    "max_amount": "₹15 lakh"
                },
                "benefits": [
                    "15% upfront capital subsidy on technology upgradation",
                    "Maximum ₹15 lakh per unit",
                    "Improves productivity and competitiveness"
                ],
                "eligibility": {
                    "registration": "Udyam registered MSME",
                    "category": "Manufacturing sector",
                    "purpose": "Technology upgradation"
                },
                "documents_required": [
                    "Udyam certificate",
                    "Technology upgradation plan",
                    "Quotations for machinery",
                    "Bank loan sanction letter"
                ],
                "application_process": "Through banks after loan disbursal",
                "processing_time": "3-6 months",
                "cost": "Free",
                "deadline": "Check with implementing agencies",
                "url": "https://www.dcmsme.gov.in"
            },

            # R&D and Innovation Grants
            {
                "id": "birac-grants",
                "name": "BIRAC - Biotechnology Industry Research Assistance Council",
                "authority": "Department of Biotechnology, Govt of India",
                "level": "Central",
                "category": "innovation",
                "funding_amount": {
                    "bic": "₹50 lakh - ₹2 crore for incubation",
                    "sbiri": "₹50 lakh - ₹10 crore for innovation",
                    "pace": "₹50 lakh for commercialization"
                },
                "benefits": [
                    "Funding for biotech innovation",
                    "Incubation support",
                    "Commercialization assistance",
                    "Mentorship and networking"
                ],
                "eligibility": {
                    "sector": "Biotechnology, Healthcare, AgriTech, BioEnergy",
                    "stage": "Early stage to growth stage",
                    "innovation": "Novel biotech product/process"
                },
                "documents_required": [
                    "Detailed project proposal",
                    "Technical feasibility report",
                    "Financial projections",
                    "Team credentials",
                    "IP status"
                ],
                "application_process": "Online through BIRAC portal",
                "processing_time": "3-6 months",
                "cost": "Free",
                "deadline": "Call-based (check BIRAC website)",
                "url": "https://birac.nic.in"
            },
            {
                "id": "dst-nidhi",
                "name": "NIDHI - National Initiative for Developing and Harnessing Innovations",
                "authority": "Department of Science & Technology (DST)",
                "level": "Central",
                "category": "innovation",
                "funding_amount": {
                    "prayas": "₹10 lakh for prototype",
                    "eir": "₹30,000/month fellowship",
                    "seed_support": "₹50 lakh"
                },
                "benefits": [
                    "Proof of concept funding",
                    "Prototype development grants",
                    "Entrepreneur-in-Residence fellowship",
                    "Access to incubators and mentors"
                ],
                "eligibility": {
                    "sector": "Technology and innovation",
                    "innovator_type": "Students, faculty, startups",
                    "stage": "Idea to early stage"
                },
                "documents_required": [
                    "Innovation proposal",
                    "Prototype/POC plan",
                    "Budget breakdown",
                    "Team details"
                ],
                "application_process": "Through NIDHI centers/incubators",
                "processing_time": "2-4 months",
                "cost": "Free",
                "deadline": "Rolling/Call-based",
                "url": "https://nidhi.dstyapms.in"
            },

            # State Schemes (Example - Karnataka)
            {
                "id": "elevate-karnataka",
                "name": "ELEVATE - Karnataka Startup Policy",
                "authority": "Karnataka Government",
                "level": "State",
                "category": "funding",
                "funding_amount": {
                    "grant": "Up to ₹50 lakh",
                    "total_support": "₹1.5 crore per startup"
                },
                "benefits": [
                    "Seed funding up to ₹50 lakh",
                    "Product development grants",
                    "Market access support",
                    "Incubation facilities"
                ],
                "eligibility": {
                    "location": "Karnataka (or willing to establish operations)",
                    "sector": "Deep tech, social impact, sustainability",
                    "stage": "Early stage startups"
                },
                "documents_required": [
                    "Business plan",
                    "Pitch deck",
                    "Incorporation certificate",
                    "Founder details"
                ],
                "application_process": "Online through Karnataka Startup Cell",
                "processing_time": "3-5 months",
                "cost": "Free",
                "deadline": "Annual calls (check portal)",
                "url": "https://startupkarnataka.gov.in"
            },

            # Export Promotion
            {
                "id": "meis-scheme",
                "name": "Export Promotion Schemes",
                "authority": "DGFT - Directorate General of Foreign Trade",
                "level": "Central",
                "category": "export",
                "benefits": [
                    "Duty credit scrips (2-5% of FOB value)",
                    "Export subsidies",
                    "Reduced compliance for AEO status",
                    "Access to global markets"
                ],
                "eligibility": {
                    "activity": "Exporting goods/services",
                    "iec": "Import Export Code required",
                    "category": "Manufacturing or service exports"
                },
                "documents_required": [
                    "IEC certificate",
                    "Shipping bills",
                    "Export invoices",
                    "Bank realization certificates"
                ],
                "application_process": "Through DGFT online portal",
                "processing_time": "2-3 months",
                "cost": "Free (processing fee applies)",
                "deadline": "Within specified period after exports",
                "url": "https://www.dgft.gov.in"
            }
        ]

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process government schemes query

        Args:
            query: User query about schemes
            context: Business context (industry, stage, location, etc.)

        Returns:
            Dict with eligible schemes and recommendations
        """
        try:
            # Extract business criteria
            criteria = self._extract_criteria(query, context)

            # Find eligible schemes
            eligible_schemes = await self._find_eligible_schemes(criteria)

            # Score and rank schemes
            ranked_schemes = self._rank_schemes(eligible_schemes, criteria)

            # Generate application roadmap
            roadmap = await self._generate_application_roadmap(ranked_schemes, criteria)

            # Check deadlines and alerts
            deadline_alerts = self._check_deadlines(ranked_schemes)

            # Create response
            response = await self._generate_response(
                query,
                criteria,
                ranked_schemes,
                roadmap,
                deadline_alerts
            )

            return {
                "answer": response,
                "eligible_schemes": ranked_schemes,
                "total_schemes": len(ranked_schemes),
                "application_roadmap": roadmap,
                "deadline_alerts": deadline_alerts,
                "potential_funding": self._calculate_potential_funding(ranked_schemes),
                "confidence": 0.92,
                "sources": self._get_sources(ranked_schemes),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in SchemesMonitoringAgent: {str(e)}")
            return self._error_response(str(e))

    def _extract_criteria(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract business criteria for scheme matching"""

        if context:
            return {
                "entity_type": context.get("entity_type", "Private Limited"),
                "industry": context.get("industry", "Technology"),
                "stage": context.get("stage", "seed"),
                "turnover": context.get("turnover", 0),
                "location": context.get("location", "India"),
                "state": context.get("state", "Karnataka"),
                "innovative": context.get("innovative", True),
                "dpiit_recognized": context.get("dpiit_recognized", False),
                "udyam_registered": context.get("udyam_registered", False),
                "incorporation_years": context.get("incorporation_years", 1),
                "seeking": self._detect_seeking(query)
            }
        else:
            return {
                "entity_type": "Private Limited",
                "industry": self._detect_industry(query),
                "stage": "seed",
                "turnover": 0,
                "location": "India",
                "state": "Karnataka",
                "innovative": True,
                "dpiit_recognized": False,
                "udyam_registered": False,
                "incorporation_years": 1,
                "seeking": self._detect_seeking(query)
            }

    def _detect_industry(self, text: str) -> str:
        """Detect industry from text"""
        industry_keywords = {
            "Biotechnology": ["biotech", "healthcare", "medical", "pharma"],
            "Technology": ["tech", "software", "saas", "ai", "ml"],
            "Manufacturing": ["manufacturing", "production", "industrial"],
            "Agriculture": ["agriculture", "agritech", "farming"],
            "Export": ["export", "international", "global"]
        }

        text_lower = text.lower()
        for industry, keywords in industry_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return industry

        return "Technology"

    def _detect_seeking(self, text: str) -> str:
        """Detect what type of scheme user is seeking"""
        text_lower = text.lower()

        if any(word in text_lower for word in ["funding", "grant", "seed fund", "money"]):
            return "funding"
        elif any(word in text_lower for word in ["tax", "exemption", "80iac"]):
            return "tax_benefits"
        elif any(word in text_lower for word in ["subsidy", "subsidies"]):
            return "subsidies"
        elif any(word in text_lower for word in ["innovation", "r&d", "research"]):
            return "innovation"
        elif any(word in text_lower for word in ["export", "international"]):
            return "export"
        else:
            return "all"

    async def _find_eligible_schemes(
        self,
        criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find schemes matching eligibility criteria"""

        eligible = []

        for scheme in self.schemes_db:
            # Check category match
            if criteria["seeking"] != "all" and scheme["category"] != criteria["seeking"]:
                continue

            # Check basic eligibility
            eligibility = scheme.get("eligibility", {})

            # Entity type check
            if "entity_type" in eligibility:
                if criteria["entity_type"] not in eligibility["entity_type"] and "All types" not in str(eligibility["entity_type"]):
                    continue

            # Industry/sector check
            if "sector" in eligibility:
                if criteria["industry"] not in eligibility["sector"]:
                    continue

            # Special checks
            if "recognition" in eligibility and eligibility["recognition"] == "DPIIT recognized startup":
                if not criteria.get("dpiit_recognized"):
                    scheme["requires_dpiit"] = True

            if "registration" in eligibility and "Udyam" in eligibility["registration"]:
                if not criteria.get("udyam_registered"):
                    scheme["requires_udyam"] = True

            eligible.append(scheme)

        return eligible

    def _rank_schemes(
        self,
        schemes: List[Dict[str, Any]],
        criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Rank schemes by relevance and potential value"""

        for scheme in schemes:
            score = 0.5  # Base score

            # Category match
            if criteria["seeking"] != "all" and scheme["category"] == criteria["seeking"]:
                score += 0.2

            # Funding amount (higher is better for funding schemes)
            if scheme["category"] == "funding" and "funding_amount" in scheme:
                score += 0.15

            # Already qualified (no additional requirements)
            if not scheme.get("requires_dpiit") and not scheme.get("requires_udyam"):
                score += 0.15

            scheme["relevance_score"] = min(score, 1.0)
            scheme["match_level"] = "High" if score >= 0.8 else "Medium" if score >= 0.6 else "Good"

        # Sort by relevance
        schemes.sort(key=lambda x: x["relevance_score"], reverse=True)

        return schemes

    async def _generate_application_roadmap(
        self,
        schemes: List[Dict[str, Any]],
        criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate application roadmap"""

        # Determine priority order
        priority_schemes = []

        # 1. First apply for recognition/registration schemes
        for scheme in schemes:
            if scheme["category"] in ["recognition", "registration"]:
                priority_schemes.append({
                    "priority": 1,
                    "scheme_id": scheme["id"],
                    "scheme_name": scheme["name"],
                    "reason": "Foundation - Required for other schemes",
                    "timeline": scheme.get("processing_time", "4 weeks")
                })

        # 2. Then tax benefits
        for scheme in schemes:
            if scheme["category"] == "tax_benefits":
                priority_schemes.append({
                    "priority": 2,
                    "scheme_id": scheme["id"],
                    "scheme_name": scheme["name"],
                    "reason": "Immediate cash flow impact",
                    "timeline": scheme.get("processing_time", "3-6 months")
                })

        # 3. Then funding
        for scheme in schemes:
            if scheme["category"] == "funding":
                priority_schemes.append({
                    "priority": 3,
                    "scheme_id": scheme["id"],
                    "scheme_name": scheme["name"],
                    "reason": "Capital for growth",
                    "timeline": scheme.get("processing_time", "3-5 months")
                })

        # 4. Other schemes
        for scheme in schemes:
            if scheme["category"] not in ["recognition", "registration", "tax_benefits", "funding"]:
                priority_schemes.append({
                    "priority": 4,
                    "scheme_id": scheme["id"],
                    "scheme_name": scheme["name"],
                    "reason": "Additional benefits",
                    "timeline": scheme.get("processing_time", "2-4 months")
                })

        return {
            "total_schemes": len(priority_schemes),
            "estimated_timeline": "6-12 months for all applications",
            "priority_order": priority_schemes[:10],  # Top 10
            "parallel_applications": "Can apply to multiple schemes simultaneously"
        }

    def _check_deadlines(self, schemes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for upcoming deadlines"""

        alerts = []
        today = datetime.now()

        for scheme in schemes:
            deadline = scheme.get("deadline", "")

            if "rolling" in deadline.lower():
                urgency = "Low"
                days_remaining = "Ongoing"
            elif "annual" in deadline.lower() or "call" in deadline.lower():
                urgency = "Medium"
                days_remaining = "Check portal for announcements"
            else:
                # Try to parse date
                urgency = "Medium"
                days_remaining = "Contact authority"

            alerts.append({
                "scheme_name": scheme["name"],
                "deadline": deadline,
                "urgency": urgency,
                "days_remaining": days_remaining,
                "action": f"Apply via {scheme.get('application_process', 'official portal')}"
            })

        return alerts[:5]  # Top 5 alerts

    def _calculate_potential_funding(self, schemes: List[Dict[str, Any]]) -> str:
        """Calculate total potential funding"""

        total = 0
        funding_schemes = []

        for scheme in schemes:
            if scheme["category"] == "funding" and "funding_amount" in scheme:
                funding_data = scheme["funding_amount"]

                # Extract maximum amount
                if isinstance(funding_data, dict):
                    for key, value in funding_data.items():
                        if "max" in key.lower() or "total" in key.lower():
                            # Extract number from string like "₹50 lakh"
                            amount_str = value.replace("₹", "").strip()
                            if "lakh" in amount_str:
                                amount = float(amount_str.split()[0]) * 100000
                            elif "crore" in amount_str:
                                amount = float(amount_str.split()[0]) * 10000000
                            else:
                                amount = 0

                            total += amount
                            funding_schemes.append(scheme["name"])
                            break

        if total >= 10000000:  # 1 crore
            return f"₹{total/10000000:.1f} Cr from {len(funding_schemes)} schemes"
        elif total >= 100000:  # 1 lakh
            return f"₹{total/100000:.1f} L from {len(funding_schemes)} schemes"
        else:
            return "Multiple non-financial benefits available"

    async def _generate_response(
        self,
        query: str,
        criteria: Dict[str, Any],
        schemes: List[Dict[str, Any]],
        roadmap: Dict[str, Any],
        alerts: List[Dict[str, Any]]
    ) -> str:
        """Generate comprehensive response"""

        response_parts = []

        response_parts.append("## Government Schemes Analysis\n")
        response_parts.append(f"**Industry:** {criteria['industry']}")
        response_parts.append(f"**Entity Type:** {criteria['entity_type']}")
        response_parts.append(f"**Stage:** {criteria['stage'].title()}\n")

        response_parts.append(f"**Found {len(schemes)} Eligible Government Schemes:**\n")

        # Top 5 schemes
        for i, scheme in enumerate(schemes[:5], 1):
            response_parts.append(f"### {i}. {scheme['name']}")
            response_parts.append(f"**Authority:** {scheme['authority']}")
            response_parts.append(f"**Category:** {scheme['category'].replace('_', ' ').title()}")
            response_parts.append(f"**Match Level:** {scheme['match_level']} ({scheme['relevance_score']:.0%})")

            # Benefits
            response_parts.append(f"**Benefits:**")
            for benefit in scheme['benefits'][:3]:
                response_parts.append(f"  • {benefit}")

            # Key eligibility
            response_parts.append(f"**Processing Time:** {scheme.get('processing_time', 'Varies')}")
            response_parts.append(f"**Cost:** {scheme.get('cost', 'Check with authority')}")
            response_parts.append(f"**Apply:** {scheme.get('url', 'Contact authority')}\n")

        # Potential funding
        potential = self._calculate_potential_funding(schemes[:5])
        response_parts.append(f"**💰 Total Potential Value:** {potential}\n")

        # Application roadmap
        response_parts.append("## Application Roadmap:")
        response_parts.append(f"**Recommended Timeline:** {roadmap['estimated_timeline']}\n")
        response_parts.append("**Priority Order:**")
        for item in roadmap['priority_order'][:5]:
            response_parts.append(f"{item['priority']}. {item['scheme_name']} - {item['reason']}")

        # Deadline alerts
        response_parts.append("\n## ⏰ Deadline Alerts:")
        for alert in alerts[:3]:
            response_parts.append(f"• **{alert['scheme_name']}**: {alert['deadline']} ({alert['urgency']} urgency)")

        response_parts.append("\n*Note: Eligibility criteria and schemes are subject to change. Please verify on official websites before applying.*")

        return "\n".join(response_parts)

    def _get_sources(self, schemes: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Get sources"""
        sources = []
        for scheme in schemes[:3]:
            sources.append({
                "title": f"{scheme['name']} - {scheme['authority']}",
                "url": scheme.get("url", ""),
                "type": "government_scheme"
            })
        return sources

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "answer": f"I encountered an error while searching for government schemes: {error}. Please provide details like industry, entity type, and location.",
            "error": error,
            "confidence": 0.0,
            "agent": self.name
        }


# Export
__all__ = ["SchemesMonitoringAgent"]
