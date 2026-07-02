"""
Marketing Strategy Agent
Comprehensive marketing strategy and growth hacking for entrepreneurs
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


class MarketingStrategyAgent:
    """
    Marketing Strategy Agent

    Provides comprehensive marketing strategy including:
    - Marketing channel analysis (digital, traditional, social)
    - CAC (Customer Acquisition Cost) calculations
    - LTV (Lifetime Value) projections
    - Marketing funnel optimization
    - Content strategy recommendations
    - SEO/SEM analysis
    - Growth hacking strategies
    - Brand positioning advice
    - Influencer marketing recommendations
    - A/B testing frameworks
    """

    def __init__(self):
        """Initialize Marketing Strategy Agent"""
        self.name = "MarketingStrategyAgent"
        self.description = "Comprehensive marketing strategy and customer acquisition optimization"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process marketing strategy request

        Args:
            query: User query about marketing strategy
            context: Additional context (business type, budget, target audience, etc.)

        Returns:
            Dict with strategy results
        """
        try:
            # Determine strategy type needed
            strategy_type = self._determine_strategy_type(query)

            # Get business context
            business_context = self._extract_business_context(query, context)

            # Perform appropriate analysis
            if strategy_type == "channel_analysis":
                analysis = await self._channel_analysis(business_context)
            elif strategy_type == "cac_ltv":
                analysis = await self._cac_ltv_analysis(business_context)
            elif strategy_type == "funnel":
                analysis = await self._funnel_optimization(business_context)
            elif strategy_type == "content":
                analysis = await self._content_strategy(business_context)
            elif strategy_type == "seo_sem":
                analysis = await self._seo_sem_analysis(business_context)
            elif strategy_type == "growth_hacking":
                analysis = await self._growth_hacking_strategies(business_context)
            elif strategy_type == "brand":
                analysis = await self._brand_positioning(business_context)
            elif strategy_type == "influencer":
                analysis = await self._influencer_marketing(business_context)
            else:
                analysis = await self._comprehensive_strategy(business_context)

            # Generate actionable recommendations
            recommendations = await self._generate_recommendations(
                query,
                business_context,
                analysis
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
                "business_context": business_context,
                "analysis": analysis,
                "recommendations": recommendations,
                "confidence": 0.87,
                "sources": self._get_sources(),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in Marketing Strategy Agent: {str(e)}")
            return self._error_response(str(e))

    def _determine_strategy_type(self, query: str) -> str:
        """Determine type of marketing strategy needed"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["channel", "platform", "where to market"]):
            return "channel_analysis"
        elif any(word in query_lower for word in ["cac", "customer acquisition cost", "ltv", "lifetime value"]):
            return "cac_ltv"
        elif any(word in query_lower for word in ["funnel", "conversion", "optimization"]):
            return "funnel"
        elif any(word in query_lower for word in ["content", "blog", "social media posts"]):
            return "content"
        elif any(word in query_lower for word in ["seo", "sem", "google", "search"]):
            return "seo_sem"
        elif any(word in query_lower for word in ["growth hack", "viral", "rapid growth"]):
            return "growth_hacking"
        elif any(word in query_lower for word in ["brand", "positioning", "identity"]):
            return "brand"
        elif any(word in query_lower for word in ["influencer", "ambassador", "collaboration"]):
            return "influencer"
        else:
            return "comprehensive"

    def _extract_business_context(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract business context from query and context"""

        if context:
            return {
                "business_type": context.get("business_type", "SaaS B2B"),
                "target_audience": context.get("target_audience", "SME business owners"),
                "monthly_budget": context.get("budget", 50000),
                "current_customers": context.get("customers", 100),
                "avg_deal_size": context.get("deal_size", 50000),
                "sales_cycle_days": context.get("sales_cycle", 30),
                "current_channels": context.get("channels", ["Organic Search", "Referrals"]),
                "geography": context.get("geography", "India")
            }
        else:
            # Default context
            return {
                "business_type": "SaaS B2B",
                "target_audience": "SME business owners",
                "monthly_budget": 50000,
                "current_customers": 100,
                "avg_deal_size": 50000,
                "sales_cycle_days": 30,
                "current_channels": ["Organic Search", "Referrals"],
                "geography": "India"
            }

    async def _channel_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze marketing channels and recommend best fit"""

        # Channel database with cost and effectiveness
        channels = {
            "Google Ads (SEM)": {
                "cac": 5000,
                "conversion_rate": 2.5,
                "time_to_roi": "1-2 months",
                "scalability": "High",
                "best_for": ["B2B SaaS", "E-commerce"],
                "pros": ["Intent-based", "Fast results", "Scalable"],
                "cons": ["Expensive", "Competitive"]
            },
            "LinkedIn Ads": {
                "cac": 8000,
                "conversion_rate": 3.5,
                "time_to_roi": "2-3 months",
                "scalability": "Medium",
                "best_for": ["B2B", "Enterprise sales"],
                "pros": ["Professional targeting", "High-quality leads"],
                "cons": ["High cost", "Smaller audience"]
            },
            "Content Marketing (SEO)": {
                "cac": 2000,
                "conversion_rate": 1.8,
                "time_to_roi": "6-12 months",
                "scalability": "Very High",
                "best_for": ["All businesses"],
                "pros": ["Long-term value", "Low ongoing cost", "Builds authority"],
                "cons": ["Slow results", "Requires consistency"]
            },
            "Meta Ads (Facebook/Instagram)": {
                "cac": 3000,
                "conversion_rate": 1.5,
                "time_to_roi": "1-3 months",
                "scalability": "High",
                "best_for": ["B2C", "E-commerce", "D2C"],
                "pros": ["Large audience", "Visual content", "Retargeting"],
                "cons": ["B2B limited", "Ad fatigue"]
            },
            "Email Marketing": {
                "cac": 500,
                "conversion_rate": 4.0,
                "time_to_roi": "Immediate",
                "scalability": "High",
                "best_for": ["Retention", "Upselling"],
                "pros": ["Cheapest", "Direct communication", "High ROI"],
                "cons": ["Requires existing list", "Deliverability issues"]
            },
            "Referral Program": {
                "cac": 1500,
                "conversion_rate": 8.0,
                "time_to_roi": "1-2 months",
                "scalability": "Medium",
                "best_for": ["Product-led growth"],
                "pros": ["High trust", "Low cost", "Viral potential"],
                "cons": ["Requires great product", "Network effects needed"]
            },
            "Influencer Marketing": {
                "cac": 4000,
                "conversion_rate": 2.0,
                "time_to_roi": "1-2 months",
                "scalability": "Medium",
                "best_for": ["B2C", "D2C", "Lifestyle brands"],
                "pros": ["Authentic reach", "Brand awareness"],
                "cons": ["Hard to measure", "Influencer dependency"]
            }
        }

        # Recommend channels based on business type and budget
        business_type = context["business_type"]
        budget = context["monthly_budget"]

        recommended_channels = []
        for channel, data in channels.items():
            if business_type in data["best_for"] or "All businesses" in data["best_for"]:
                if data["cac"] * 10 <= budget:  # Can afford at least 10 acquisitions
                    recommended_channels.append({
                        "channel": channel,
                        "priority": "High" if data["conversion_rate"] > 3 else "Medium",
                        **data
                    })

        return {
            "all_channels": channels,
            "recommended_channels": sorted(
                recommended_channels,
                key=lambda x: x["conversion_rate"],
                reverse=True
            )[:5],
            "budget_allocation": self._calculate_budget_allocation(recommended_channels, budget)
        }

    def _calculate_budget_allocation(
        self,
        channels: List[Dict[str, Any]],
        total_budget: float
    ) -> Dict[str, float]:
        """Calculate optimal budget allocation across channels"""

        if not channels:
            return {}

        # Allocate based on conversion rate (weighted)
        total_weight = sum(c["conversion_rate"] for c in channels)

        allocation = {}
        for channel in channels:
            weight = channel["conversion_rate"] / total_weight
            allocation[channel["channel"]] = round(total_budget * weight, 2)

        return allocation

    async def _cac_ltv_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate CAC and LTV metrics"""

        # Current metrics
        monthly_marketing_spend = context["monthly_budget"]
        new_customers_per_month = 20  # Assumption
        current_cac = monthly_marketing_spend / new_customers_per_month if new_customers_per_month > 0 else 0

        # LTV calculation
        avg_deal_size = context["avg_deal_size"]
        avg_customer_lifetime_months = 24  # Assumption: 2 years
        gross_margin = 0.70  # 70% margin assumption
        ltv = avg_deal_size * (avg_customer_lifetime_months / context["sales_cycle_days"] * 30) * gross_margin

        # LTV:CAC ratio
        ltv_cac_ratio = ltv / current_cac if current_cac > 0 else 0

        # Payback period
        monthly_recurring_revenue = avg_deal_size / (context["sales_cycle_days"] / 30)
        payback_months = current_cac / (monthly_recurring_revenue * gross_margin) if monthly_recurring_revenue > 0 else 0

        return {
            "current_cac": round(current_cac, 2),
            "ltv": round(ltv, 2),
            "ltv_cac_ratio": round(ltv_cac_ratio, 2),
            "payback_period_months": round(payback_months, 2),
            "benchmarks": {
                "good_ltv_cac_ratio": 3.0,
                "acceptable_ltv_cac_ratio": 1.5,
                "good_payback_months": 12,
                "acceptable_payback_months": 18
            },
            "verdict": {
                "ltv_cac": "Excellent" if ltv_cac_ratio >= 3 else "Good" if ltv_cac_ratio >= 1.5 else "Needs Improvement",
                "payback": "Excellent" if payback_months <= 12 else "Acceptable" if payback_months <= 18 else "Too Long"
            },
            "recommendations": [
                "Target LTV:CAC ratio of 3:1 or higher",
                "Aim for payback period under 12 months",
                "Focus on retention to increase LTV"
            ]
        }

    async def _funnel_optimization(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and optimize marketing funnel"""

        # Mock funnel data (integrate with analytics tools like Google Analytics, Mixpanel)
        funnel_stages = {
            "awareness": {"visitors": 10000, "conversion_to_next": 0.30},
            "interest": {"visitors": 3000, "conversion_to_next": 0.25},
            "consideration": {"visitors": 750, "conversion_to_next": 0.40},
            "intent": {"visitors": 300, "conversion_to_next": 0.50},
            "purchase": {"visitors": 150, "conversion_to_next": 1.0}
        }

        # Calculate drop-off rates
        funnel_analysis = []
        for stage, data in funnel_stages.items():
            drop_off_rate = 1 - data["conversion_to_next"]
            funnel_analysis.append({
                "stage": stage,
                "visitors": data["visitors"],
                "conversion_rate": data["conversion_to_next"],
                "drop_off_rate": round(drop_off_rate, 2),
                "opportunity": "High" if drop_off_rate > 0.6 else "Medium" if drop_off_rate > 0.4 else "Low"
            })

        return {
            "funnel_stages": funnel_analysis,
            "overall_conversion": round((150 / 10000) * 100, 2),
            "biggest_drop_offs": [
                {"stage": "Awareness → Interest", "drop_off": 70, "fix": "Improve value proposition, better targeting"},
                {"stage": "Interest → Consideration", "drop_off": 75, "fix": "Case studies, social proof, testimonials"}
            ],
            "optimization_tactics": [
                "A/B test landing page headlines",
                "Add video testimonials at consideration stage",
                "Implement exit-intent popups with offers",
                "Create retargeting campaigns for drop-offs",
                "Optimize page load speed (target <2 seconds)"
            ]
        }

    async def _content_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content marketing strategy"""

        business_type = context["business_type"]
        audience = context["target_audience"]

        content_pillars = [
            {
                "pillar": "Thought Leadership",
                "formats": ["Blog posts", "LinkedIn articles", "Whitepapers"],
                "frequency": "2-3 times/week",
                "goal": "Build authority and trust",
                "topics": ["Industry trends", "Expert insights", "Research findings"]
            },
            {
                "pillar": "Educational Content",
                "formats": ["How-to guides", "Tutorials", "Webinars"],
                "frequency": "Weekly",
                "goal": "Solve customer problems",
                "topics": ["Product tutorials", "Best practices", "Common mistakes"]
            },
            {
                "pillar": "Social Proof",
                "formats": ["Case studies", "Customer stories", "Video testimonials"],
                "frequency": "Bi-weekly",
                "goal": "Build credibility",
                "topics": ["Success stories", "ROI demonstrations", "Before/after"]
            },
            {
                "pillar": "Engagement Content",
                "formats": ["Polls", "Infographics", "Memes", "Short videos"],
                "frequency": "Daily",
                "goal": "Increase visibility and engagement",
                "topics": ["Industry news reactions", "Relatable content", "Quick tips"]
            }
        ]

        return {
            "content_pillars": content_pillars,
            "distribution_channels": {
                "Owned": ["Blog", "Email newsletter", "YouTube channel"],
                "Earned": ["Guest posts", "PR", "Organic social shares"],
                "Paid": ["Sponsored content", "Native ads", "Boosted posts"]
            },
            "seo_strategy": {
                "keyword_research": "Focus on long-tail keywords with 100-1000 search volume",
                "on_page": "Optimize title tags, meta descriptions, headers, internal linking",
                "off_page": "Build backlinks through guest posting, HARO, digital PR"
            },
            "content_calendar": "Create 30-day content calendar with mix of all pillars"
        }

    async def _seo_sem_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """SEO and SEM strategy"""

        return {
            "seo_strategy": {
                "technical_seo": [
                    "Site speed optimization (target: <2s load time)",
                    "Mobile-first design and testing",
                    "XML sitemap and robots.txt configuration",
                    "SSL certificate (HTTPS)",
                    "Fix broken links and 404 errors",
                    "Implement schema markup for rich snippets"
                ],
                "on_page_seo": [
                    "Keyword research using Ahrefs/SEMrush",
                    "Optimize title tags (60 chars) and meta descriptions (160 chars)",
                    "Use H1, H2, H3 hierarchy properly",
                    "Internal linking strategy",
                    "Image alt text optimization",
                    "Content depth (aim for 1500+ words for pillar content)"
                ],
                "off_page_seo": [
                    "Build high-quality backlinks (DA 40+)",
                    "Guest posting on industry blogs",
                    "HARO (Help a Reporter Out) for PR links",
                    "Create shareable infographics",
                    "Podcast appearances and collaborations"
                ],
                "local_seo": [
                    "Google My Business optimization",
                    "Local citations (Justdial, Sulekha, etc.)",
                    "Location-specific landing pages",
                    "Customer reviews and ratings"
                ]
            },
            "sem_strategy": {
                "google_ads": {
                    "campaign_types": ["Search ads", "Display ads", "Remarketing"],
                    "keyword_strategy": "Focus on high-intent keywords (bottom of funnel)",
                    "bid_strategy": "Start with manual CPC, then move to automated bidding",
                    "quality_score": "Aim for 7+ by improving ad relevance and landing pages",
                    "budget_recommendation": f"₹{context['monthly_budget'] * 0.4:.0f}/month (40% of total budget)"
                },
                "linkedin_ads": {
                    "campaign_types": ["Sponsored content", "InMail", "Text ads"],
                    "targeting": "Job title, company size, industry, seniority",
                    "best_for": "B2B lead generation, enterprise sales",
                    "budget_recommendation": f"₹{context['monthly_budget'] * 0.3:.0f}/month (30% of total budget)"
                }
            },
            "tracking": {
                "google_analytics": "Set up goals, e-commerce tracking, UTM parameters",
                "google_search_console": "Monitor search performance, index coverage, submit sitemaps",
                "conversion_tracking": "Track form submissions, purchases, sign-ups"
            }
        }

    async def _growth_hacking_strategies(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Growth hacking tactics for rapid scaling"""

        return {
            "viral_loops": [
                {
                    "tactic": "Referral Program",
                    "mechanism": "Give reward to both referrer and referee",
                    "example": "Dropbox (500MB free space for each referral)",
                    "implementation": "Offer ₹500 credit to both parties on successful referral"
                },
                {
                    "tactic": "Product-Led Growth",
                    "mechanism": "Build shareability into product",
                    "example": "Calendly (meeting links shared = free promotion)",
                    "implementation": "Add 'Powered by [YourBrand]' to free tier outputs"
                },
                {
                    "tactic": "Social Proof Widgets",
                    "mechanism": "Display recent customer actions on website",
                    "example": "Booking.com ('5 people viewing this hotel')",
                    "implementation": "Show live signup notifications on homepage"
                }
            ],
            "acquisition_hacks": [
                "Launch on Product Hunt, Hacker News, Reddit",
                "Create comparison pages (vs. competitors) for SEO",
                "Scrape competitor's social media followers, engage with them",
                "Reverse engineer competitor backlinks, get similar ones",
                "Cold outreach on LinkedIn with personalized video messages"
            ],
            "retention_hacks": [
                "Onboarding email drip campaigns (Day 1, 3, 7, 14, 30)",
                "Behavioral triggers (e.g., 'You haven't logged in for 7 days')",
                "Feature usage milestones with gamification",
                "Community building (Slack/Discord group for users)",
                "Regular product updates and changelog"
            ],
            "revenue_hacks": [
                "Annual prepayment discount (10-20% off) for better cash flow",
                "Usage-based pricing to attract small customers, upsell later",
                "Add-on features for quick revenue boost",
                "Strategic price increase with grandfathering for existing customers",
                "Implement exit surveys to reduce churn"
            ],
            "case_studies": [
                {
                    "company": "Airbnb",
                    "hack": "Craigslist integration for free listings",
                    "result": "10x growth in first year"
                },
                {
                    "company": "Hotmail",
                    "hack": "'PS: I Love You' signature in every email",
                    "result": "12 million users in 18 months"
                }
            ]
        }

    async def _brand_positioning(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Brand positioning and identity strategy"""

        return {
            "positioning_framework": {
                "target_audience": context["target_audience"],
                "category": "Define your category (create new if needed)",
                "differentiation": "What makes you unique vs. competitors?",
                "proof_points": "Evidence that backs up your claims",
                "brand_promise": "What value do you consistently deliver?"
            },
            "positioning_statement_template":
                f"For {context['target_audience']} who [NEED], "
                f"[YOUR BRAND] is a {context['business_type']} that [UNIQUE VALUE]. "
                f"Unlike [COMPETITORS], we [DIFFERENTIATION].",
            "brand_archetypes": [
                {"archetype": "The Hero", "example": "Nike", "personality": "Brave, inspiring, empowering"},
                {"archetype": "The Sage", "example": "Google", "personality": "Knowledgeable, trusted, wise"},
                {"archetype": "The Rebel", "example": "Harley-Davidson", "personality": "Disruptive, bold, unconventional"},
                {"archetype": "The Caregiver", "example": "Johnson & Johnson", "personality": "Nurturing, protective, generous"}
            ],
            "brand_elements": {
                "visual_identity": ["Logo", "Color palette", "Typography", "Imagery style"],
                "voice_and_tone": ["Formal vs. casual", "Humorous vs. serious", "Technical vs. simple"],
                "messaging_pillars": ["Primary message", "Supporting messages", "Proof points"],
                "brand_story": ["Founder's journey", "Problem you're solving", "Vision for future"]
            },
            "competitive_positioning": {
                "perceptual_map": "Create 2x2 map (e.g., Price vs. Quality) and position vs. competitors",
                "differentiation_strategy": [
                    "Cost leadership (cheapest option)",
                    "Differentiation (unique features)",
                    "Focus/Niche (specific segment)"
                ]
            }
        }

    async def _influencer_marketing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Influencer marketing strategy"""

        return {
            "influencer_tiers": [
                {
                    "tier": "Nano-influencers",
                    "followers": "1K - 10K",
                    "engagement_rate": "5-10%",
                    "cost_per_post": "₹2,000 - ₹10,000",
                    "best_for": "Niche audiences, high trust",
                    "recommendation": "Start here for testing"
                },
                {
                    "tier": "Micro-influencers",
                    "followers": "10K - 100K",
                    "engagement_rate": "3-7%",
                    "cost_per_post": "₹10,000 - ₹1,00,000",
                    "best_for": "Targeted campaigns, good ROI",
                    "recommendation": "Best bang for buck"
                },
                {
                    "tier": "Macro-influencers",
                    "followers": "100K - 1M",
                    "engagement_rate": "1-3%",
                    "cost_per_post": "₹1,00,000 - ₹10,00,000",
                    "best_for": "Brand awareness, reach",
                    "recommendation": "Use sparingly"
                }
            ],
            "selection_criteria": [
                "Engagement rate > follower count",
                "Audience demographics match your target",
                "Content quality and authenticity",
                "Past brand collaborations (check for credibility)",
                "Comments quality (real vs. bot)"
            ],
            "campaign_types": [
                {
                    "type": "Sponsored Post",
                    "description": "Influencer creates content featuring your product",
                    "pricing": "Per post or per campaign"
                },
                {
                    "type": "Affiliate Partnership",
                    "description": "Pay commission on sales generated",
                    "pricing": "10-20% of sale value"
                },
                {
                    "type": "Brand Ambassador",
                    "description": "Long-term partnership with exclusive content",
                    "pricing": "Monthly retainer"
                },
                {
                    "type": "Product Seeding",
                    "description": "Send free products for organic mentions",
                    "pricing": "Free products only (low cost)"
                }
            ],
            "platforms": {
                "Instagram": "Visual content, lifestyle, fashion, food, travel",
                "YouTube": "In-depth reviews, tutorials, unboxing",
                "LinkedIn": "B2B, thought leadership, professional services",
                "Twitter": "Tech, news, commentary, real-time events"
            },
            "measurement": {
                "metrics": ["Reach", "Impressions", "Engagement rate", "Click-through rate", "Conversions"],
                "roi_calculation": "Revenue generated / Influencer cost",
                "tracking": "Use UTM parameters and unique discount codes"
            }
        }

    async def _comprehensive_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive marketing strategy combining all elements"""

        channel_analysis = await self._channel_analysis(context)
        cac_ltv = await self._cac_ltv_analysis(context)
        funnel = await self._funnel_optimization(context)
        content = await self._content_strategy(context)

        return {
            "channels": channel_analysis,
            "economics": cac_ltv,
            "funnel": funnel,
            "content": content,
            "6_month_roadmap": {
                "Month 1-2": [
                    "Set up analytics and tracking",
                    "Launch referral program",
                    "Start content marketing (blog + SEO)",
                    "Test top 3 paid channels with small budget"
                ],
                "Month 3-4": [
                    "Double down on best-performing channel",
                    "Implement marketing automation",
                    "A/B test landing pages and funnels",
                    "Launch influencer partnerships"
                ],
                "Month 5-6": [
                    "Scale winning channels",
                    "Optimize for LTV (retention campaigns)",
                    "Expand to additional channels",
                    "Build brand partnerships"
                ]
            }
        }

    async def _generate_recommendations(
        self,
        query: str,
        context: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable marketing recommendations"""

        recommendations = []

        # Budget-based recommendations
        budget = context["monthly_budget"]
        if budget < 50000:
            recommendations.append("💡 Focus on low-cost, high-ROI tactics: SEO, referrals, content marketing")
        elif budget < 200000:
            recommendations.append("💡 Test 2-3 paid channels with 40% budget, invest 60% in organic growth")
        else:
            recommendations.append("💡 Diversify across 5+ channels to reduce dependency risk")

        # Business type recommendations
        if "B2B" in context["business_type"]:
            recommendations.append("🎯 Prioritize LinkedIn, content marketing, and account-based marketing (ABM)")
        elif "B2C" in context["business_type"]:
            recommendations.append("🎯 Focus on Instagram, Facebook, influencer marketing, and viral tactics")

        # Growth recommendations
        recommendations.append("📈 Implement weekly growth experiments - test, measure, iterate")
        recommendations.append("🔄 Build retention loops before scaling acquisition (fix leaky bucket first)")
        recommendations.append("📊 Track North Star Metric and optimize for it relentlessly")

        return recommendations

    async def _generate_response(
        self,
        query: str,
        context: Dict[str, Any],
        analysis: Dict[str, Any],
        recommendations: List[str]
    ) -> str:
        """Generate natural language response using LLM"""

        prompt = f"""
You are a marketing strategy expert. Provide a comprehensive marketing strategy based on this data:

Query: {query}

Business Context:
{json.dumps(context, indent=2)}

Analysis:
{json.dumps(analysis, indent=2)}

Recommendations:
{chr(10).join(recommendations)}

Generate a professional, actionable marketing strategy (400-500 words) that:
1. Summarizes the current situation
2. Recommends top 3 marketing channels to focus on
3. Provides specific tactics to implement
4. Sets realistic expectations for ROI and timeline
5. Highlights common mistakes to avoid

Be specific with numbers, timelines, and concrete actions.
"""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=600
            )
            return response
        except Exception as e:
            return self._fallback_response(context, analysis, recommendations)

    def _fallback_response(
        self,
        context: Dict[str, Any],
        analysis: Dict[str, Any],
        recommendations: List[str]
    ) -> str:
        """Fallback response if LLM fails"""

        response = "## Marketing Strategy Overview\n\n"
        response += f"**Business Type:** {context['business_type']}\n"
        response += f"**Monthly Budget:** ₹{context['monthly_budget']:,}\n\n"

        if "recommended_channels" in analysis:
            response += "**Recommended Channels:**\n"
            for channel in analysis["recommended_channels"][:3]:
                response += f"- {channel['channel']}: CAC ₹{channel['cac']}, "
                response += f"Conversion {channel['conversion_rate']}%\n"
            response += "\n"

        response += "**Key Recommendations:**\n"
        for rec in recommendations:
            response += f"{rec}\n"

        return response

    def _get_sources(self) -> List[Dict[str, str]]:
        """Get data sources"""
        return [
            {"type": "marketing_research", "source": "Industry benchmarks and best practices"},
            {"type": "channel_data", "source": "Marketing channel analysis"}
        ]

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "answer": f"I encountered an error while developing the marketing strategy: {error}. Please provide more details about your business and marketing goals.",
            "error": error,
            "confidence": 0.0,
            "agent": self.name
        }


# Export
__all__ = ["MarketingStrategyAgent"]
