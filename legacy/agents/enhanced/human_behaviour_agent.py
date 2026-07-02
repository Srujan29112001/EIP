"""
Human Behaviour Analysis Agent
Behavioral economics, consumer decision-making, cognitive biases, nudge theory, customer persona creation
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


class HumanBehaviourAgent:
    """
    Human Behaviour Analysis Agent

    Applies behavioral science to business including:
    - Behavioral economics principles
    - Consumer decision-making models
    - Cognitive biases and heuristics
    - Nudge theory applications
    - Customer persona creation using psychology
    - Persuasion techniques
    - Behavioral segmentation
    - Choice architecture design
    """

    def __init__(self):
        """Initialize Human Behaviour Agent"""
        self.name = "HumanBehaviourAgent"
        self.description = "Behavioral economics and psychology applied to business"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

        # Cognitive biases database
        self.cognitive_biases = self._initialize_cognitive_biases()

        # Decision-making models
        self.decision_models = [
            "rational_choice", "bounded_rationality", "prospect_theory",
            "dual_process", "heuristics", "emotional_decision"
        ]

    def _initialize_cognitive_biases(self) -> Dict[str, Dict[str, Any]]:
        """Initialize cognitive biases database"""
        return {
            "anchoring": {
                "name": "Anchoring Bias",
                "description": "People rely heavily on the first piece of information (anchor) when making decisions",
                "business_application": "Pricing strategy - show original price before discount",
                "example": "₹10,000 ~~₹15,000~~ (33% off) - anchors customer to ₹15,000",
                "how_to_use": [
                    "Display original price prominently before showing discount",
                    "Show most expensive option first to anchor expectations",
                    "Use precise numbers (₹9,997 feels more researched than ₹10,000)"
                ]
            },
            "social_proof": {
                "name": "Social Proof / Bandwagon Effect",
                "description": "People follow the behavior of others, especially in uncertain situations",
                "business_application": "Show user counts, testimonials, reviews",
                "example": "Join 1,00,000+ businesses using our product",
                "how_to_use": [
                    "Display customer count and growth metrics",
                    "Show real-time activity ('5 people viewing this')",
                    "Highlight popular choices ('Most popular plan')",
                    "Use customer testimonials and case studies"
                ]
            },
            "scarcity": {
                "name": "Scarcity Principle",
                "description": "People value things more when they're rare or running out",
                "business_application": "Limited-time offers, limited inventory",
                "example": "Only 3 seats left at this price!",
                "how_to_use": [
                    "Time-limited offers ('Offer ends in 24 hours')",
                    "Quantity limits ('Only 5 left in stock')",
                    "Exclusive access ('Available to first 100 customers')",
                    "Seasonal availability"
                ]
            },
            "loss_aversion": {
                "name": "Loss Aversion",
                "description": "People prefer avoiding losses over acquiring equivalent gains (losses hurt 2x more than gains feel good)",
                "business_application": "Frame messaging around what customer will lose",
                "example": "Don't miss out on 30% savings (vs. Save 30%)",
                "how_to_use": [
                    "Emphasize what they'll lose if they don't act",
                    "Free trial: 'Cancel anytime' reduces perceived risk",
                    "Money-back guarantee removes loss fear",
                    "Frame as protecting what they have"
                ]
            },
            "reciprocity": {
                "name": "Reciprocity Principle",
                "description": "People feel obligated to return favors",
                "business_application": "Give free value first, then ask for sale",
                "example": "Free eBook, then pitch paid course",
                "how_to_use": [
                    "Offer free trial, freemium, or free content",
                    "Provide unexpected bonuses",
                    "Give personalized recommendations",
                    "Help customers succeed before asking for money"
                ]
            },
            "commitment_consistency": {
                "name": "Commitment & Consistency",
                "description": "People want to be consistent with past behaviors and commitments",
                "business_application": "Start with small commitment, build to larger ones",
                "example": "Email signup → Free trial → Paid plan",
                "how_to_use": [
                    "Progressive profiling (ask for more info gradually)",
                    "Get small 'yes' first (e.g., quiz, email signup)",
                    "Remind users of their stated goals/values",
                    "Use onboarding to build investment in product"
                ]
            },
            "authority": {
                "name": "Authority Bias",
                "description": "People trust and follow experts and authority figures",
                "business_application": "Use expert endorsements, credentials, data",
                "example": "Recommended by Forbes, used by IIT professors",
                "how_to_use": [
                    "Display credentials, awards, certifications",
                    "Expert endorsements and quotes",
                    "Media mentions and press coverage",
                    "Data-backed claims with research citations"
                ]
            },
            "framing_effect": {
                "name": "Framing Effect",
                "description": "Same information presented differently leads to different decisions",
                "business_application": "Frame features as gains or avoid losses",
                "example": "95% success rate vs. 5% failure rate",
                "how_to_use": [
                    "Positive framing for gains ('Save ₹5000/month')",
                    "Negative framing for risks ('Losing ₹60,000/year')",
                    "Percentages vs. absolute numbers (choose impactful one)",
                    "Reference points matter ('₹100/day' vs '₹3000/month')"
                ]
            },
            "default_effect": {
                "name": "Default Effect / Status Quo Bias",
                "description": "People tend to stick with default options",
                "business_application": "Set profitable option as default",
                "example": "Annual billing (save 20%) pre-selected",
                "how_to_use": [
                    "Pre-select recommended option",
                    "Auto-renewal as default (with easy opt-out)",
                    "Opt-out newsletter subscription at checkout",
                    "Default to higher-value tier in trials"
                ]
            },
            "endowment_effect": {
                "name": "Endowment Effect",
                "description": "People value things more once they own them",
                "business_application": "Free trials, demo accounts with data",
                "example": "30-day free trial with full features",
                "how_to_use": [
                    "Let users build/create something during trial",
                    "Populate demo account with their data",
                    "Personalized experience from day 1",
                    "Hard to leave once invested time/effort"
                ]
            }
        }

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process behavioral analysis request

        Args:
            query: User query about behavior/psychology
            context: Business context

        Returns:
            Dict with behavioral analysis results
        """
        try:
            # Determine analysis type
            analysis_type = self._determine_analysis_type(query)

            # Extract context
            business_context = self._extract_business_context(query, context)

            # Perform analysis
            if analysis_type == "cognitive_biases":
                analysis = await self._analyze_cognitive_biases(business_context)
            elif analysis_type == "decision_making":
                analysis = await self._analyze_decision_making(business_context)
            elif analysis_type == "nudge_theory":
                analysis = await self._apply_nudge_theory(business_context)
            elif analysis_type == "persona":
                analysis = await self._create_behavioral_persona(business_context)
            elif analysis_type == "choice_architecture":
                analysis = await self._design_choice_architecture(business_context)
            else:
                analysis = await self._comprehensive_behavioral_analysis(business_context)

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
                "confidence": 0.89,
                "sources": self._get_sources(),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in HumanBehaviourAgent: {str(e)}")
            return self._error_response(str(e))

    def _determine_analysis_type(self, query: str) -> str:
        """Determine type of behavioral analysis needed"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["bias", "biases", "cognitive"]):
            return "cognitive_biases"
        elif any(word in query_lower for word in ["decision", "choose", "choice"]):
            return "decision_making"
        elif any(word in query_lower for word in ["nudge", "persuade", "influence"]):
            return "nudge_theory"
        elif any(word in query_lower for word in ["persona", "customer profile", "buyer"]):
            return "persona"
        elif any(word in query_lower for word in ["choice architecture", "pricing page", "design"]):
            return "choice_architecture"
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
                "product": context.get("product", "SaaS product"),
                "target_customer": context.get("target_customer", "Business owners"),
                "industry": context.get("industry", "B2B SaaS"),
                "price_point": context.get("price_point", "Medium"),
                "customer_journey_stage": context.get("stage", "consideration"),
                "current_conversion_rate": context.get("conversion_rate", 2.0),
                "problem": query
            }
        else:
            return {
                "product": "SaaS product",
                "target_customer": "Business owners",
                "industry": "B2B SaaS",
                "price_point": "Medium",
                "customer_journey_stage": "consideration",
                "current_conversion_rate": 2.0,
                "problem": query
            }

    async def _analyze_cognitive_biases(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze which cognitive biases to apply"""

        # Select top biases for the business
        recommended_biases = []

        # Always recommend social proof for B2B
        if "B2B" in context["industry"]:
            recommended_biases.append({
                **self.cognitive_biases["social_proof"],
                "priority": "High",
                "implementation": "Display enterprise customer logos on homepage"
            })
            recommended_biases.append({
                **self.cognitive_biases["authority"],
                "priority": "High",
                "implementation": "Showcase case studies and ROI data"
            })

        # Recommend anchoring for pricing
        recommended_biases.append({
            **self.cognitive_biases["anchoring"],
            "priority": "High",
            "implementation": "Show enterprise plan first, then highlight mid-tier as 'most popular'"
        })

        # Recommend scarcity if selling
        if context["customer_journey_stage"] in ["decision", "purchase"]:
            recommended_biases.append({
                **self.cognitive_biases["scarcity"],
                "priority": "Medium",
                "implementation": "Limited-time discount or bonus for early action"
            })

        # Recommend loss aversion
        recommended_biases.append({
            **self.cognitive_biases["loss_aversion"],
            "priority": "High",
            "implementation": "Frame messaging around cost of inaction"
        })

        return {
            "type": "cognitive_biases",
            "recommended_biases": recommended_biases,
            "total_count": len(recommended_biases)
        }

    async def _analyze_decision_making(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer decision-making process"""

        # Map customer journey
        decision_journey = {
            "awareness": {
                "customer_state": "Unaware of problem or solution",
                "psychology": "Attention is scarce, emotional triggers work",
                "tactics": [
                    "Use curiosity gap in headlines",
                    "Emotional storytelling",
                    "Pattern interrupts",
                    "Relatable pain points"
                ]
            },
            "consideration": {
                "customer_state": "Evaluating options, comparing alternatives",
                "psychology": "Analysis paralysis, need for social proof",
                "tactics": [
                    "Comparison tables (bias in your favor)",
                    "Customer testimonials and reviews",
                    "Free trial to reduce perceived risk",
                    "Expert content (authority bias)"
                ]
            },
            "decision": {
                "customer_state": "Ready to buy but needs final push",
                "psychology": "Loss aversion, fear of regret",
                "tactics": [
                    "Money-back guarantee",
                    "Scarcity (limited time offer)",
                    "Social proof (recent purchases)",
                    "Easy first step (commitment & consistency)"
                ]
            },
            "retention": {
                "customer_state": "Evaluating if they made right choice",
                "psychology": "Cognitive dissonance reduction, endowment effect",
                "tactics": [
                    "Confirmation of good decision (welcome email)",
                    "Quick wins in onboarding",
                    "Build investment (personalization)",
                    "Create habits through triggers"
                ]
            }
        }

        current_stage = context["customer_journey_stage"]
        stage_analysis = decision_journey.get(current_stage, decision_journey["consideration"])

        return {
            "type": "decision_making",
            "current_stage": current_stage,
            "stage_analysis": stage_analysis,
            "full_journey": decision_journey
        }

    async def _apply_nudge_theory(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply nudge theory to influence behavior"""

        nudges = [
            {
                "nudge_name": "Default Nudge",
                "principle": "Pre-select desired option",
                "application": "Set annual billing as default (with clear monthly option)",
                "expected_impact": "30-50% of users stick with annual default"
            },
            {
                "nudge_name": "Social Norm Nudge",
                "principle": "Show what others are doing",
                "application": "87% of businesses like yours choose the Pro plan",
                "expected_impact": "Increases Pro plan adoption by 20%+"
            },
            {
                "nudge_name": "Framing Nudge",
                "principle": "Frame choice to highlight desired behavior",
                "application": "₹100/day (vs ₹3000/month) makes it feel cheaper",
                "expected_impact": "Reduces perceived cost, increases conversion"
            },
            {
                "nudge_name": "Commitment Device",
                "principle": "Get small commitment to lead to bigger one",
                "application": "Start free trial → Add team members → Upgrade to paid",
                "expected_impact": "Each step increases conversion to next"
            },
            {
                "nudge_name": "Fresh Start Effect",
                "principle": "People more motivated at temporal landmarks",
                "application": "New Year, new quarter, Monday - promote at these times",
                "expected_impact": "Higher engagement and conversion"
            },
            {
                "nudge_name": "Progress Tracking",
                "principle": "Showing progress motivates completion",
                "application": "Profile completeness bar (70% complete)",
                "expected_impact": "Users complete setup to reach 100%"
            }
        ]

        return {
            "type": "nudge_theory",
            "nudges": nudges,
            "implementation_priority": "Start with Default and Social Norm nudges"
        }

    async def _create_behavioral_persona(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create customer persona using behavioral psychology"""

        persona = {
            "name": f"{context['target_customer']} Persona",
            "demographics": {
                "role": context['target_customer'],
                "industry": context['industry']
            },
            "psychological_profile": {
                "decision_style": "Analytical with risk-aversion (B2B buyers)",
                "primary_motivations": [
                    "Career advancement / not getting fired",
                    "ROI and measurable results",
                    "Ease of use and quick wins"
                ],
                "fears_and_anxieties": [
                    "Making wrong choice and looking bad",
                    "Wasting company money",
                    "Complex implementation",
                    "Vendor lock-in"
                ],
                "cognitive_biases_susceptible_to": [
                    "Social proof (what peers are using)",
                    "Authority (expert recommendations)",
                    "Loss aversion (cost of inaction)",
                    "Status quo bias (switching costs)"
                ]
            },
            "behavioral_patterns": {
                "information_gathering": "Reads reviews, asks peers, downloads comparison content",
                "decision_timeline": "2-8 weeks for B2B purchases",
                "influencers": "Boss, peers, industry experts",
                "triggers": "Pain point reached critical level, competitor making them look bad"
            },
            "messaging_framework": {
                "emotional_hook": "Don't let [PROBLEM] slow down your team",
                "rational_justification": "Proven ROI of X%, used by [SOCIAL PROOF]",
                "call_to_action": "Start free trial - no credit card required",
                "objection_handling": "Money-back guarantee, migration support, dedicated onboarding"
            }
        }

        return {
            "type": "behavioral_persona",
            "persona": persona
        }

    async def _design_choice_architecture(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Design choice architecture (e.g., pricing page)"""

        choice_design = {
            "principle": "Choice Architecture - how options are presented influences decisions",
            "pricing_page_design": {
                "structure": "3 tiers (Good-Better-Best)",
                "anchor": {
                    "position": "Left or right (extreme pricing)",
                    "purpose": "Makes middle option feel reasonable",
                    "pricing": "Show highest price first, or decoy expensive option"
                },
                "highlight": {
                    "which_tier": "Middle tier",
                    "label": "'Most Popular' or 'Recommended'",
                    "visual": "Different color, badge, slightly larger"
                },
                "biases_at_play": [
                    "Anchoring: Expensive option makes others look cheaper",
                    "Social proof: 'Most popular' guides choice",
                    "Default effect: Pre-select recommended option",
                    "Compromise effect: People avoid extremes, choose middle"
                ],
                "pricing_display": {
                    "annual_vs_monthly": "Show annual as default with 'Save X%'",
                    "price_format": "₹999/month (precise number feels researched)",
                    "strike_through": "Show ₹1499 ~~₹2000~~ for anchor effect"
                }
            },
            "option_reduction": {
                "principle": "Too many choices leads to analysis paralysis",
                "recommendation": "Max 3-4 tiers. Hide advanced options behind 'See all features' link",
                "hicks_law": "Decision time increases logarithmically with options"
            },
            "comparison_table": {
                "principle": "Guide comparison in your favor",
                "tactics": [
                    "Lead with your strengths in feature list",
                    "Use ✓ and ✗ for visual clarity",
                    "Highlight your unique features",
                    "Frame competitor weaknesses as missing features"
                ]
            }
        }

        return {
            "type": "choice_architecture",
            "design": choice_design
        }

    async def _comprehensive_behavioral_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive behavioral analysis"""

        biases = await self._analyze_cognitive_biases(context)
        decision = await self._analyze_decision_making(context)
        nudges = await self._apply_nudge_theory(context)

        return {
            "type": "comprehensive",
            "cognitive_biases": biases,
            "decision_making": decision,
            "nudge_theory": nudges
        }

    async def _generate_recommendations(
        self,
        context: Dict[str, Any],
        analysis: Dict[str, Any],
        analysis_type: str
    ) -> List[Dict[str, Any]]:
        """Generate behavioral recommendations"""

        recommendations = []

        # Universal recommendations
        recommendations.append({
            "title": "Implement Social Proof Everywhere",
            "description": "Add customer logos, testimonials, and user count on homepage and pricing page",
            "priority": "high",
            "expected_impact": "15-30% increase in conversions",
            "effort": "Low"
        })

        recommendations.append({
            "title": "Reduce Friction in Signup",
            "description": "Remove credit card requirement from free trial. Use commitment & consistency bias to build up from there",
            "priority": "high",
            "expected_impact": "50-100% increase in trial signups",
            "effort": "Medium"
        })

        recommendations.append({
            "title": "Add Money-Back Guarantee",
            "description": "Reduces loss aversion. 'Try risk-free for 30 days' dramatically increases conversions",
            "priority": "medium",
            "expected_impact": "10-20% increase in paid conversions",
            "effort": "Low"
        })

        return recommendations

    async def _generate_response(
        self,
        query: str,
        context: Dict[str, Any],
        analysis: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> str:
        """Generate comprehensive response"""

        prompt = f"""You are a behavioral economics expert. Provide actionable advice based on:

Query: {query}

Business Context:
{json.dumps(context, indent=2)}

Analysis:
{json.dumps(analysis, indent=2)[:1500]}

Recommendations:
{json.dumps(recommendations, indent=2)}

Generate a professional, actionable behavioral analysis (400-500 words) that:
1. Explains the psychology behind customer behavior
2. Identifies which cognitive biases to leverage
3. Provides specific, implementable tactics
4. Gives examples of how to apply nudge theory
5. Estimates impact on conversions

Be specific with examples and actionable advice."""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                temperature=0.6,
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

        response = "## Behavioral Analysis\n\n"
        response += f"**Product:** {context['product']}\n"
        response += f"**Target:** {context['target_customer']}\n\n"

        if "recommended_biases" in analysis:
            response += "**Top Cognitive Biases to Apply:**\n"
            for bias in analysis["recommended_biases"][:3]:
                response += f"• **{bias['name']}**: {bias['implementation']}\n"

        response += "\n**Recommendations:**\n"
        for i, rec in enumerate(recommendations, 1):
            response += f"{i}. **{rec['title']}**\n"
            response += f"   {rec['description']}\n"
            response += f"   Expected Impact: {rec['expected_impact']}\n\n"

        return response

    def _get_sources(self) -> List[Dict[str, str]]:
        """Get sources"""
        return [
            {
                "type": "behavioral_economics",
                "source": "Kahneman, Tversky - Prospect Theory; Thaler - Nudge Theory"
            },
            {
                "type": "cognitive_biases",
                "source": "Cialdini - Influence; Ariely - Predictably Irrational"
            }
        ]

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "answer": f"I encountered an error while analyzing behavior: {error}. Please provide details about your product and target customer.",
            "error": error,
            "confidence": 0.0,
            "agent": self.name
        }


# Export
__all__ = ["HumanBehaviourAgent"]
