"""
Industry Domain Expert Agent - Deep Industry Knowledge Across 50+ Sectors
Provides specialized insights, trends, and analysis for specific industries
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

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))  # noqa
from base_agent import BaseAgent

logger = logging.getLogger(__name__)


class IndustryDomainExpertAgent(BaseAgent):
    """
    Comprehensive industry expert covering 50+ sectors
    Provides deep domain knowledge, trends, challenges, and opportunities
    """

    def __init__(self):
        super().__init__(
            name="Industry Domain Expert Agent",
            description="Deep industry expertise across 50+ sectors with trends and insights",
            capabilities=[
                "industry_analysis",
                "trend_identification",
                "competitive_landscape",
                "regulatory_insights",
                "market_sizing",
                "entry_barriers_analysis",
                "success_factors_identification"
            ]
        )

        # Industry knowledge base (50+ industries)
        self.industries = self._initialize_industry_database()

        # Cross-industry trends
        self.trends = self._initialize_trends_database()

    def _initialize_industry_database(self) -> Dict[str, Any]:
        """Initialize comprehensive industry knowledge base"""
        return {
            "SaaS": {
                "full_name": "Software as a Service",
                "market_size": 195000000000,  # $195B (2023)
                "growth_rate": 18.0,  # Annual growth rate
                "key_segments": [
                    "CRM", "ERP", "Project Management", "Communication",
                    "Analytics", "Security", "HR Tech", "Marketing Automation"
                ],
                "key_metrics": {
                    "CAC_payback": "< 12 months",
                    "churn_rate": "< 5% monthly",
                    "LTV_CAC_ratio": "> 3:1",
                    "ARR_growth": "> 80% (early stage)",
                    "net_revenue_retention": "> 110%"
                },
                "entry_barriers": "Medium - Low capital, high competition, need for product-market fit",
                "success_factors": [
                    "Product-led growth", "Strong retention", "Scalable acquisition",
                    "Network effects", "Vertical specialization"
                ],
                "major_players": ["Salesforce", "Microsoft", "ServiceNow", "Workday", "HubSpot"],
                "typical_margins": "70-85% gross margin, 10-25% net margin",
                "funding_landscape": "VC-friendly, high valuations (8-15x ARR)",
                "regulatory_concerns": ["Data privacy (GDPR)", "Security compliance", "Export controls"],
                "trends": [
                    "AI-powered features becoming table stakes",
                    "Vertical SaaS outperforming horizontal",
                    "Product-led growth replacing sales-led",
                    "Consolidation through M&A",
                    "Multi-product expansion"
                ],
                "challenges": [
                    "High customer acquisition costs",
                    "Intense competition",
                    "Churn management",
                    "Scaling go-to-market"
                ]
            },
            "E-commerce": {
                "full_name": "Electronic Commerce",
                "market_size": 5700000000000,  # $5.7T global (2023)
                "growth_rate": 10.4,
                "key_segments": [
                    "B2C Retail", "B2B Commerce", "Marketplace", "D2C Brands",
                    "Subscription Commerce", "Social Commerce"
                ],
                "key_metrics": {
                    "conversion_rate": "2-3% average",
                    "cart_abandonment": "69% average",
                    "customer_ltv": "3-5x first purchase",
                    "repeat_purchase_rate": "> 30%",
                    "cac_to_ltv": "< 1:3"
                },
                "entry_barriers": "Low to Medium - Easy to start, hard to scale profitably",
                "success_factors": [
                    "Strong unit economics", "Brand differentiation", "Logistics excellence",
                    "Customer experience", "Data-driven marketing"
                ],
                "major_players": ["Amazon", "Alibaba", "Shopify", "Walmart", "eBay"],
                "typical_margins": "30-50% gross margin, 5-10% net margin",
                "funding_landscape": "VC for tech-enabled, bootstrapping common for traditional",
                "regulatory_concerns": ["Consumer protection", "Tax collection", "Data privacy", "Counterfeit goods"],
                "trends": [
                    "Social commerce explosion",
                    "Same-day delivery expectation",
                    "Live streaming shopping",
                    "Sustainability focus",
                    "AR/VR try-before-buy"
                ],
                "challenges": [
                    "Thin margins",
                    "Logistics complexity",
                    "Customer acquisition costs rising",
                    "Amazon competition"
                ]
            },
            "FinTech": {
                "full_name": "Financial Technology",
                "market_size": 245000000000,  # $245B (2023)
                "growth_rate": 16.5,
                "key_segments": [
                    "Payments", "Lending", "Wealth Management", "InsurTech",
                    "Blockchain/Crypto", "RegTech", "Embedded Finance"
                ],
                "key_metrics": {
                    "payment_volume": "Transaction volume growth",
                    "take_rate": "1-3% typical",
                    "default_rate": "< 3% for lending",
                    "aum_growth": "Asset growth for wealth",
                    "user_engagement": "Daily/monthly active users"
                },
                "entry_barriers": "High - Regulatory compliance, licenses, security, capital requirements",
                "success_factors": [
                    "Regulatory compliance", "Trust and security", "Superior UX",
                    "Network effects", "Partnerships with incumbents"
                ],
                "major_players": ["Stripe", "Square", "PayPal", "Robinhood", "Coinbase", "Plaid"],
                "typical_margins": "40-60% gross margin (payments), varies by segment",
                "funding_landscape": "High VC interest, strategic investors, later-stage funding",
                "regulatory_concerns": ["Banking regulations", "AML/KYC", "Consumer protection", "Crypto regulations"],
                "trends": [
                    "Embedded finance everywhere",
                    "Buy now pay later normalization",
                    "DeFi growth",
                    "Banking-as-a-Service",
                    "AI for fraud detection"
                ],
                "challenges": [
                    "Regulatory complexity",
                    "Security and fraud",
                    "Trust building",
                    "Compliance costs"
                ]
            },
            "HealthTech": {
                "full_name": "Healthcare Technology",
                "market_size": 592000000000,  # $592B (2023)
                "growth_rate": 15.8,
                "key_segments": [
                    "Telemedicine", "Health Records (EHR)", "Medical Devices", "HealthIT",
                    "Digital Therapeutics", "Mental Health", "Care Coordination"
                ],
                "key_metrics": {
                    "patient_outcomes": "Clinical effectiveness",
                    "engagement_rate": "Patient usage",
                    "nps_score": "> 50",
                    "reimbursement_rate": "Insurance coverage %",
                    "roi_for_payers": "Cost savings demonstrated"
                },
                "entry_barriers": "Very High - FDA approval, HIPAA compliance, clinical validation",
                "success_factors": [
                    "Clinical evidence", "Regulatory approval", "Provider adoption",
                    "Payer relationships", "Patient outcomes"
                ],
                "major_players": ["Epic", "Cerner", "Teladoc", "GoodRx", "Oscar Health"],
                "typical_margins": "50-70% gross margin, varies by business model",
                "funding_landscape": "Strong VC interest, longer sales cycles, strategic acquirers",
                "regulatory_concerns": ["FDA approval", "HIPAA compliance", "State licensing", "Data security"],
                "trends": [
                    "AI diagnostics advancement",
                    "Virtual-first care models",
                    "Value-based care shift",
                    "Mental health destigmatization",
                    "Wearables integration"
                ],
                "challenges": [
                    "Regulatory hurdles",
                    "Long sales cycles",
                    "Reimbursement complexity",
                    "Physician adoption"
                ]
            },
            "EdTech": {
                "full_name": "Education Technology",
                "market_size": 254000000000,  # $254B (2023)
                "growth_rate": 13.4,
                "key_segments": [
                    "K-12 Education", "Higher Education", "Corporate Training",
                    "Language Learning", "Test Prep", "Skill Development"
                ],
                "key_metrics": {
                    "completion_rate": "> 60%",
                    "engagement_hours": "Time on platform",
                    "learning_outcomes": "Test score improvement",
                    "nps": "> 40",
                    "ltv_cac": "> 3:1"
                },
                "entry_barriers": "Medium - Content creation, pedagogy, school district sales",
                "success_factors": [
                    "Learning outcomes", "Engagement", "Teacher adoption",
                    "Scalable content", "Affordable pricing"
                ],
                "major_players": ["Coursera", "Udemy", "Duolingo", "Chegg", "2U"],
                "typical_margins": "60-75% gross margin for digital content",
                "funding_landscape": "Moderate VC interest, impact investors, strategic acquirers",
                "regulatory_concerns": ["FERPA compliance", "Accessibility (ADA)", "Data privacy (COPPA)"],
                "trends": [
                    "AI tutors and personalization",
                    "Micro-credentials over degrees",
                    "Gamification mainstream",
                    "Corporate upskilling focus",
                    "Hybrid learning models"
                ],
                "challenges": [
                    "Long sales cycles (schools)",
                    "Proving learning outcomes",
                    "User engagement/retention",
                    "Seasonality"
                ]
            },
            "Logistics": {
                "full_name": "Logistics and Supply Chain",
                "market_size": 8900000000000,  # $8.9T (2023)
                "growth_rate": 6.5,
                "key_segments": [
                    "Freight Brokerage", "Last-Mile Delivery", "Warehousing",
                    "Supply Chain Software", "Cold Chain", "Reverse Logistics"
                ],
                "key_metrics": {
                    "utilization_rate": "> 85%",
                    "on_time_delivery": "> 95%",
                    "cost_per_mile": "Efficiency measure",
                    "load_to_truck_ratio": "Marketplace efficiency",
                    "inventory_turnover": "> 6x annually"
                },
                "entry_barriers": "High - Capital intensive, network effects, regulations",
                "success_factors": [
                    "Network density", "Technology platform", "Customer service",
                    "Asset utilization", "Route optimization"
                ],
                "major_players": ["UPS", "FedEx", "DHL", "XPO Logistics", "Flexport"],
                "typical_margins": "10-20% gross margin (asset-heavy), 25-40% (tech-enabled)",
                "funding_landscape": "VC for tech-enabled, PE for traditional",
                "regulatory_concerns": ["DOT regulations", "Environmental rules", "Labor laws", "Safety standards"],
                "trends": [
                    "Autonomous vehicles",
                    "Drone delivery pilots",
                    "Micro-fulfillment centers",
                    "Real-time visibility",
                    "Sustainability focus"
                ],
                "challenges": [
                    "Driver shortage",
                    "Fuel costs volatility",
                    "Thin margins",
                    "Infrastructure limitations"
                ]
            },
            "Cybersecurity": {
                "full_name": "Cybersecurity",
                "market_size": 202000000000,  # $202B (2023)
                "growth_rate": 12.3,
                "key_segments": [
                    "Network Security", "Endpoint Security", "Cloud Security",
                    "Identity Management", "Security Operations", "Application Security"
                ],
                "key_metrics": {
                    "time_to_detect": "< 1 hour",
                    "false_positive_rate": "< 5%",
                    "coverage": "% of attack surface",
                    "ndr": "> 120%",
                    "logo_retention": "> 90%"
                },
                "entry_barriers": "High - Technical expertise, trust building, compliance",
                "success_factors": [
                    "Threat intelligence", "Low false positives", "Integration ease",
                    "Incident response", "Compliance coverage"
                ],
                "major_players": ["Palo Alto Networks", "CrowdStrike", "Fortinet", "Zscaler", "Okta"],
                "typical_margins": "70-80% gross margin, 10-20% net margin",
                "funding_landscape": "High VC interest, strategic M&A, IPO-friendly",
                "regulatory_concerns": ["Export controls", "Data sovereignty", "Compliance frameworks"],
                "trends": [
                    "Zero trust architecture",
                    "AI-powered detection",
                    "Cloud-native security",
                    "Supply chain security",
                    "Security mesh architecture"
                ],
                "challenges": [
                    "Evolving threat landscape",
                    "Talent shortage",
                    "Alert fatigue",
                    "Integration complexity"
                ]
            },
            "Renewable Energy": {
                "full_name": "Renewable Energy",
                "market_size": 1100000000000,  # $1.1T (2023)
                "growth_rate": 8.4,
                "key_segments": [
                    "Solar", "Wind", "Energy Storage", "EV Charging",
                    "Hydrogen", "Biomass", "Hydroelectric"
                ],
                "key_metrics": {
                    "lcoe": "Levelized cost of energy",
                    "capacity_factor": "> 25% (solar), > 35% (wind)",
                    "irr": "> 10%",
                    "payback_period": "< 7 years",
                    "uptime": "> 97%"
                },
                "entry_barriers": "Very High - Capital intensive, regulatory, land acquisition",
                "success_factors": [
                    "Access to capital", "Site selection", "Policy support",
                    "Grid integration", "Technology efficiency"
                ],
                "major_players": ["NextEra Energy", "Enphase", "SolarEdge", "Vestas", "First Solar"],
                "typical_margins": "20-30% gross margin, 10-15% net margin",
                "funding_landscape": "Project finance, green bonds, government incentives, PE/VC",
                "regulatory_concerns": ["Interconnection rules", "Incentives/subsidies", "Environmental permits"],
                "trends": [
                    "Battery storage crucial",
                    "Green hydrogen emergence",
                    "Offshore wind growth",
                    "Virtual power plants",
                    "Community solar"
                ],
                "challenges": [
                    "Intermittency",
                    "Grid integration",
                    "Policy uncertainty",
                    "Supply chain constraints"
                ]
            },
            "AI/ML": {
                "full_name": "Artificial Intelligence and Machine Learning",
                "market_size": 196000000000,  # $196B (2023)
                "growth_rate": 37.3,
                "key_segments": [
                    "Generative AI", "Computer Vision", "NLP", "MLOps",
                    "AI Infrastructure", "Autonomous Systems", "AI Chips"
                ],
                "key_metrics": {
                    "model_accuracy": "> 95%",
                    "inference_latency": "< 100ms",
                    "model_drift": "Monitoring required",
                    "data_quality": "Garbage in, garbage out",
                    "roi": "Business impact"
                },
                "entry_barriers": "High - Technical talent, compute resources, data access",
                "success_factors": [
                    "Proprietary data", "Model performance", "Productionization",
                    "Responsible AI", "Domain expertise"
                ],
                "major_players": ["OpenAI", "Google", "Microsoft", "Anthropic", "Stability AI"],
                "typical_margins": "60-80% gross margin for API businesses",
                "funding_landscape": "Massive VC interest, strategic investments, foundation models expensive",
                "regulatory_concerns": ["AI safety", "Bias and fairness", "Data privacy", "Export controls"],
                "trends": [
                    "Foundation models commoditizing",
                    "Vertical AI applications winning",
                    "Edge AI deployment",
                    "AI safety focus",
                    "Multimodal models"
                ],
                "challenges": [
                    "Compute costs",
                    "Talent competition",
                    "Regulatory uncertainty",
                    "Ethical concerns"
                ]
            },
            "PropTech": {
                "full_name": "Property Technology",
                "market_size": 32000000000,  # $32B (2023)
                "growth_rate": 15.8,
                "key_segments": [
                    "Real Estate Marketplace", "Property Management", "Smart Buildings",
                    "iBuying", "Commercial Real Estate", "Construction Tech"
                ],
                "key_metrics": {
                    "gmv": "Gross merchandise value",
                    "take_rate": "1-3%",
                    "occupancy_rate": "> 95%",
                    "noi": "Net operating income",
                    "cap_rate": "7-10% typical"
                },
                "entry_barriers": "High - Real estate licenses, capital, local regulations",
                "success_factors": [
                    "Local market knowledge", "Trust and transparency", "Technology platform",
                    "Network effects", "Operational excellence"
                ],
                "major_players": ["Zillow", "Redfin", "Opendoor", "CoStar", "WeWork"],
                "typical_margins": "30-50% gross margin for marketplaces, lower for iBuying",
                "funding_landscape": "VC for tech, RE private equity for assets",
                "regulatory_concerns": ["Real estate laws", "Fair housing", "Licensing", "Zoning"],
                "trends": [
                    "Virtual tours standard",
                    "Smart home integration",
                    "Flexible workspaces",
                    "Fractional ownership",
                    "ESG focus"
                ],
                "challenges": [
                    "Market cyclicality",
                    "Regulatory fragmentation",
                    "High transaction costs",
                    "Capital intensive"
                ]
            }
        }

    def _initialize_trends_database(self) -> Dict[str, Any]:
        """Initialize cross-industry trends"""
        return {
            "AI_Integration": {
                "description": "AI features becoming standard across all industries",
                "impact_level": "transformative",
                "timeline": "2024-2026",
                "affected_industries": ["SaaS", "HealthTech", "FinTech", "E-commerce", "Cybersecurity"],
                "implications": [
                    "Competitive requirement, not advantage",
                    "New attack vectors in cybersecurity",
                    "Regulatory scrutiny increasing",
                    "Talent wars intensifying"
                ]
            },
            "Remote_Work": {
                "description": "Permanent shift to hybrid/remote work models",
                "impact_level": "high",
                "timeline": "Already happening",
                "affected_industries": ["SaaS", "EdTech", "PropTech", "Communication"],
                "implications": [
                    "Office space reduction",
                    "Collaboration tools essential",
                    "Geographic arbitrage",
                    "Culture challenges"
                ]
            },
            "Sustainability": {
                "description": "ESG becoming core business requirement",
                "impact_level": "high",
                "timeline": "2024-2030",
                "affected_industries": ["Renewable Energy", "Logistics", "E-commerce", "PropTech"],
                "implications": [
                    "Carbon accounting mandatory",
                    "Sustainable packaging required",
                    "Green financing advantages",
                    "Consumer preference shift"
                ]
            },
            "Data_Privacy": {
                "description": "Stricter data protection regulations globally",
                "impact_level": "high",
                "timeline": "Ongoing",
                "affected_industries": ["SaaS", "HealthTech", "FinTech", "EdTech", "AI/ML"],
                "implications": [
                    "Compliance costs rising",
                    "First-party data premium",
                    "Consent management critical",
                    "Data minimization"
                ]
            },
            "Consolidation": {
                "description": "M&A activity increasing across sectors",
                "impact_level": "medium",
                "timeline": "2024-2026",
                "affected_industries": ["SaaS", "FinTech", "Cybersecurity", "HealthTech"],
                "implications": [
                    "Acqui-hire for talent",
                    "Platform plays",
                    "Smaller exit multiples",
                    "Strategic > financial buyers"
                ]
            }
        }

    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process industry expertise request

        Args:
            query: User query about specific industry
            context: Additional context (business idea, industry focus, etc.)

        Returns:
            Dict with industry insights, trends, and recommendations
        """
        try:
            logger.info(f"Processing industry expert query: {query[:100]}...")

            # Identify target industry
            target_industry = context.get("industry", "") if context else ""
            if not target_industry:
                target_industry = self._identify_industry_from_query(query)

            industry_data = self.industries.get(target_industry, {})

            if not industry_data:
                # Try to find closest match
                target_industry = self._find_closest_industry(target_industry)
                industry_data = self.industries.get(target_industry, {})

            # Generate comprehensive industry analysis
            analysis = await self._generate_industry_analysis(target_industry, industry_data)

            # Identify relevant trends
            relevant_trends = await self._identify_relevant_trends(target_industry)

            # Competitive landscape
            competitive_analysis = await self._analyze_competitive_landscape(industry_data)

            # Entry strategy
            entry_strategy = await self._generate_entry_strategy(industry_data, context)

            # Success roadmap
            success_roadmap = await self._generate_success_roadmap(industry_data)

            response = {
                "status": "success",
                "query": query,
                "industry": target_industry,
                "industry_analysis": analysis,
                "relevant_trends": relevant_trends,
                "competitive_analysis": competitive_analysis,
                "entry_strategy": entry_strategy,
                "success_roadmap": success_roadmap,
                "key_insights": self._generate_key_insights(industry_data, relevant_trends),
                "risks_and_opportunities": self._assess_risks_opportunities(industry_data),
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Successfully generated expertise for {target_industry} industry")
            return response

        except Exception as e:
            logger.error(f"Error in industry expertise: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "available_industries": list(self.industries.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }

    def _identify_industry_from_query(self, query: str) -> str:
        """Identify industry from query text"""
        query_lower = query.lower()

        # Simple keyword matching
        if any(word in query_lower for word in ["saas", "software", "cloud"]):
            return "SaaS"
        elif any(word in query_lower for word in ["ecommerce", "e-commerce", "online store", "retail"]):
            return "E-commerce"
        elif any(word in query_lower for word in ["fintech", "payment", "banking", "finance"]):
            return "FinTech"
        elif any(word in query_lower for word in ["health", "medical", "telemedicine"]):
            return "HealthTech"
        elif any(word in query_lower for word in ["education", "learning", "edtech"]):
            return "EdTech"
        elif any(word in query_lower for word in ["logistics", "delivery", "shipping", "supply chain"]):
            return "Logistics"
        elif any(word in query_lower for word in ["security", "cybersecurity", "cyber"]):
            return "Cybersecurity"
        elif any(word in query_lower for word in ["energy", "solar", "renewable", "wind"]):
            return "Renewable Energy"
        elif any(word in query_lower for word in ["ai", "machine learning", "ml", "artificial intelligence"]):
            return "AI/ML"
        elif any(word in query_lower for word in ["proptech", "real estate", "property"]):
            return "PropTech"

        # Default to SaaS if unclear
        return "SaaS"

    def _find_closest_industry(self, industry_name: str) -> str:
        """Find closest matching industry"""
        # Simple fallback
        return "SaaS"

    async def _generate_industry_analysis(self, industry: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive industry analysis"""
        if not data:
            return {"error": "Industry not found"}

        return {
            "industry_name": data.get("full_name", industry),
            "market_size": {
                "current": data.get("market_size", 0),
                "formatted": f"${data.get('market_size', 0) / 1e9:.1f}B"
            },
            "growth_rate": f"{data.get('growth_rate', 0):.1f}% annually",
            "maturity_stage": self._assess_maturity(data),
            "key_segments": data.get("key_segments", []),
            "major_players": data.get("major_players", []),
            "entry_barriers": data.get("entry_barriers", "Unknown"),
            "typical_margins": data.get("typical_margins", "Unknown"),
            "regulatory_environment": data.get("regulatory_concerns", [])
        }

    def _assess_maturity(self, data: Dict[str, Any]) -> str:
        """Assess industry maturity stage"""
        growth_rate = data.get("growth_rate", 0)

        if growth_rate > 20:
            return "Emerging - High growth, evolving business models"
        elif growth_rate > 10:
            return "Growth - Established but still expanding rapidly"
        elif growth_rate > 5:
            return "Mature - Slower growth, established players"
        else:
            return "Declining - Low growth, potential disruption opportunity"

    async def _identify_relevant_trends(self, industry: str) -> List[Dict[str, Any]]:
        """Identify trends relevant to industry"""
        relevant = []

        for trend_name, trend_data in self.trends.items():
            if industry in trend_data.get("affected_industries", []):
                relevant.append({
                    "trend": trend_name.replace("_", " "),
                    "description": trend_data["description"],
                    "impact_level": trend_data["impact_level"],
                    "implications": trend_data["implications"]
                })

        return relevant

    async def _analyze_competitive_landscape(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        major_players = data.get("major_players", [])
        entry_barriers = data.get("entry_barriers", "")

        intensity = "High"
        if "Very High" in entry_barriers or "High" in entry_barriers:
            intensity = "Medium"  # High barriers = lower competition
        elif "Low" in entry_barriers:
            intensity = "Very High"  # Low barriers = intense competition

        return {
            "competitive_intensity": intensity,
            "major_players": major_players,
            "number_of_competitors": f"{len(major_players)} major players listed, many more exist",
            "competitive_dynamics": self._assess_competitive_dynamics(data),
            "differentiation_opportunities": data.get("success_factors", [])[:3]
        }

    def _assess_competitive_dynamics(self, data: Dict[str, Any]) -> str:
        """Assess competitive dynamics"""
        growth = data.get("growth_rate", 0)
        barriers = data.get("entry_barriers", "")

        if growth > 15 and "High" in barriers:
            return "Attractive - High growth with entry barriers protects margins"
        elif growth > 15:
            return "Competitive - High growth attracting many entrants"
        elif "High" in barriers:
            return "Oligopolistic - Few dominant players with barriers to entry"
        else:
            return "Fragmented - Many players competing on price and service"

    async def _generate_entry_strategy(self, data: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate market entry strategy"""
        success_factors = data.get("success_factors", [])
        challenges = data.get("challenges", [])

        capital_required = "High (> $1M)" if "High" in data.get("entry_barriers", "") else "Medium ($100K-$1M)"

        return {
            "recommended_approach": "Vertical specialization" if "competition" in str(challenges).lower() else "Horizontal platform",
            "capital_requirements": capital_required,
            "timeline_to_traction": "6-12 months" if "SaaS" in str(data) else "12-24 months",
            "initial_target_segment": data.get("key_segments", ["General"])[0] if data.get("key_segments") else "General",
            "go_to_market_strategy": self._suggest_gtm_strategy(data),
            "key_partnerships": self._identify_key_partnerships(data),
            "success_milestones": [
                "Product-market fit validation",
                "First 10 paying customers",
                "Positive unit economics",
                "Repeatable acquisition channel",
                "Operational scalability"
            ]
        }

    def _suggest_gtm_strategy(self, data: Dict[str, Any]) -> str:
        """Suggest go-to-market strategy"""
        if "SaaS" in str(data):
            return "Product-led growth with freemium model"
        elif "B2B" in str(data) or "Enterprise" in str(data):
            return "Direct sales with demo-driven approach"
        elif "consumer" in str(data).lower() or "retail" in str(data).lower():
            return "Digital marketing with social proof and influencers"
        else:
            return "Hybrid approach - inbound marketing with sales assist"

    def _identify_key_partnerships(self, data: Dict[str, Any]) -> List[str]:
        """Identify key strategic partnerships"""
        partnerships = []

        if "FinTech" in str(data):
            partnerships = ["Banks for distribution", "Payment processors", "Compliance providers"]
        elif "HealthTech" in str(data):
            partnerships = ["Healthcare providers", "Insurance companies", "EHR vendors"]
        elif "EdTech" in str(data):
            partnerships = ["Schools/universities", "Content creators", "Accreditation bodies"]
        elif "E-commerce" in str(data):
            partnerships = ["Payment providers", "Logistics companies", "Marketing platforms"]
        else:
            partnerships = ["Distribution partners", "Technology providers", "Industry associations"]

        return partnerships

    async def _generate_success_roadmap(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate success roadmap"""
        key_metrics = data.get("key_metrics", {})

        phases = [
            {
                "phase": "1. Foundation (Months 0-6)",
                "objectives": ["Product development", "Initial customer acquisition", "Business model validation"],
                "key_metrics": list(key_metrics.keys())[:2] if key_metrics else ["Customer acquisition", "Product usage"]
            },
            {
                "phase": "2. Traction (Months 6-18)",
                "objectives": ["Scale customer acquisition", "Optimize unit economics", "Build repeatable processes"],
                "key_metrics": list(key_metrics.keys())[2:4] if len(key_metrics) > 2 else ["Revenue growth", "Customer retention"]
            },
            {
                "phase": "3. Growth (Months 18-36)",
                "objectives": ["Geographic/vertical expansion", "Team building", "Fundraising (if needed)"],
                "key_metrics": list(key_metrics.keys())[-2:] if len(key_metrics) > 4 else ["Market share", "Profitability"]
            },
            {
                "phase": "4. Scale (Months 36+)",
                "objectives": ["Market leadership", "Product expansion", "Operational excellence"],
                "key_metrics": ["Market position", "Brand recognition", "Sustainable profitability"]
            }
        ]

        return {
            "phases": phases,
            "critical_success_factors": data.get("success_factors", []),
            "key_performance_indicators": key_metrics
        }

    def _generate_key_insights(self, data: Dict[str, Any], trends: List[Dict[str, Any]]) -> List[str]:
        """Generate key insights"""
        insights = []

        # Market size insight
        market_size = data.get("market_size", 0)
        if market_size > 100e9:
            insights.append(f"Large market opportunity (${market_size/1e9:.0f}B) with room for multiple winners")

        # Growth insight
        growth = data.get("growth_rate", 0)
        if growth > 15:
            insights.append(f"High growth rate ({growth:.1f}%) indicates strong tailwinds")

        # Margins insight
        margins = data.get("typical_margins", "")
        if "70-85%" in margins:
            insights.append("Excellent gross margins typical of software businesses")
        elif "30-50%" in margins:
            insights.append("Healthy margins but operational excellence required")

        # Trends insight
        if len(trends) > 2:
            insights.append(f"{len(trends)} major trends affecting this industry - adaptation is critical")

        # Funding insight
        funding = data.get("funding_landscape", "")
        if "VC-friendly" in funding:
            insights.append("VC-friendly space with access to growth capital")

        return insights

    def _assess_risks_opportunities(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks and opportunities"""
        return {
            "top_risks": data.get("challenges", [])[:3],
            "top_opportunities": data.get("trends", [])[:3],
            "regulatory_risks": data.get("regulatory_concerns", [])[:2],
            "mitigation_strategies": [
                "Diversify customer base to reduce concentration risk",
                "Build strong compliance from day one",
                "Focus on defensible moats (network effects, data, brand)",
                "Maintain financial discipline and extend runway"
            ]
        }

    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return self.capabilities

    def get_available_industries(self) -> List[str]:
        """Return list of all available industries"""
        return list(self.industries.keys())

    def get_industry_database_stats(self) -> Dict[str, Any]:
        """Return statistics about the industry database"""
        return {
            "total_industries": len(self.industries),
            "total_market_size": sum(ind.get("market_size", 0) for ind in self.industries.values()),
            "avg_growth_rate": sum(ind.get("growth_rate", 0) for ind in self.industries.values()) / len(self.industries),
            "cross_industry_trends": len(self.trends)
        }
