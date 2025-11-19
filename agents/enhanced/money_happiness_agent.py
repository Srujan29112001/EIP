"""
Money & Happiness Agent
Well-being economics, work-life balance, FIRE movement, burnout prevention
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


class MoneyHappinessAgent:
    """
    Money & Happiness Agent

    Analyzes the relationship between wealth and well-being:
    - Well-being economics (Easterlin Paradox, hedonic adaptation)
    - Work-life balance optimization
    - FIRE movement frameworks (Financial Independence Retire Early)
    - Burnout prevention and mental health
    - Optimal income for happiness
    - Money mindset and financial psychology
    - Wealth vs well-being trade-offs
    """

    def __init__(self):
        """Initialize Money Happiness Agent"""
        self.name = "MoneyHappinessAgent"
        self.description = "Money, happiness, and well-being analysis"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

        # Happiness research findings
        self.happiness_principles = self._initialize_happiness_principles()

        # FIRE movement types
        self.fire_types = ["Lean FIRE", "Fat FIRE", "Barista FIRE", "Coast FIRE"]

    def _initialize_happiness_principles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize happiness research findings"""
        return {
            "income_happiness_curve": {
                "finding": "Income increases happiness, but with diminishing returns",
                "research": "Kahneman & Deaton (2010), Killingsworth (2021)",
                "satiation_point_emotional": "₹75 lakh/year (~$90K USD) - India adjusted ₹30-40 lakh",
                "satiation_point_life_evaluation": "No satiation, but slope decreases",
                "implication": "Beyond ₹40 lakh/year, more money = minimal happiness gain",
                "advice": "Don't sacrifice everything for income beyond this point"
            },
            "hedonic_adaptation": {
                "finding": "People adapt to positive and negative changes, returning to baseline happiness",
                "research": "Brickman & Campbell (1971)",
                "examples": ["Lottery winners return to baseline within 6-12 months", "Luxury purchases lose appeal quickly"],
                "implication": "Material purchases provide temporary happiness boost only",
                "advice": "Focus on experiences and growth over material possessions"
            },
            "easterlin_paradox": {
                "finding": "National income growth doesn't increase average happiness beyond basic needs",
                "research": "Richard Easterlin (1974)",
                "reason": "Relative income matters more than absolute (keeping up with Joneses)",
                "implication": "Comparison trap reduces happiness from wealth",
                "advice": "Focus on absolute well-being, not relative status"
            },
            "time_affluence": {
                "finding": "Time affluence (feeling you have enough time) predicts happiness better than money",
                "research": "Whillans et al. (2016)",
                "trade_off": "Would you take ₹10L less for 10 hours/week less work?",
                "implication": "Time is often more valuable than money beyond certain point",
                "advice": "Optimize for time freedom, not just wealth"
            },
            "autonomy_happiness": {
                "finding": "Autonomy (control over work and life) strongly predicts happiness",
                "research": "Self-Determination Theory, Deci & Ryan",
                "entrepreneurship": "Entrepreneurs report higher life satisfaction despite lower income and longer hours",
                "implication": "Control matters more than money for well-being",
                "advice": "Choose autonomy over higher paying but constraining roles"
            },
            "experiences_over_things": {
                "finding": "Experiential purchases (travel, events) provide more lasting happiness than material goods",
                "research": "Van Boven & Gilovich (2003)",
                "reasons": ["Experiences connect us to others", "Memories improve over time", "Less comparison"],
                "implication": "Spending on experiences yields better happiness ROI",
                "advice": "Allocate budget to experiences, relationships, personal growth"
            },
            "prosocial_spending": {
                "finding": "Spending money on others increases happiness more than spending on self",
                "research": "Dunn, Aknin, Norton (2008)",
                "examples": ["Charitable giving", "Gifts to friends/family", "Treating colleagues"],
                "implication": "Generosity = happiness",
                "advice": "Build charitable giving into budget (2-5% of income)"
            }
        }

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process money & happiness analysis request

        Args:
            query: User query about money/happiness
            context: Financial and personal context

        Returns:
            Dict with analysis results
        """
        try:
            # Determine analysis type
            analysis_type = self._determine_analysis_type(query)

            # Extract context
            personal_context = self._extract_personal_context(query, context)

            # Perform analysis
            if analysis_type == "income_happiness":
                analysis = await self._income_happiness_analysis(personal_context)
            elif analysis_type == "work_life_balance":
                analysis = await self._work_life_balance_optimization(personal_context)
            elif analysis_type == "fire":
                analysis = await self._fire_movement_analysis(personal_context)
            elif analysis_type == "burnout":
                analysis = await self._burnout_prevention(personal_context)
            elif analysis_type == "wealth_wellbeing":
                analysis = await self._wealth_wellbeing_tradeoffs(personal_context)
            else:
                analysis = await self._comprehensive_happiness_analysis(personal_context)

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                personal_context,
                analysis,
                analysis_type
            )

            # Create response
            response = await self._generate_response(
                query,
                personal_context,
                analysis,
                recommendations
            )

            return {
                "answer": response,
                "analysis": analysis,
                "recommendations": recommendations,
                "confidence": 0.84,
                "sources": self._get_sources(),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in MoneyHappinessAgent: {str(e)}")
            return self._error_response(str(e))

    def _determine_analysis_type(self, query: str) -> str:
        """Determine analysis type"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["income", "salary", "enough money", "how much"]):
            return "income_happiness"
        elif any(word in query_lower for word in ["work-life", "work life", "balance", "hours"]):
            return "work_life_balance"
        elif any(word in query_lower for word in ["fire", "retire early", "financial independence"]):
            return "fire"
        elif any(word in query_lower for word in ["burnout", "stress", "mental health", "exhausted"]):
            return "burnout"
        elif any(word in query_lower for word in ["wealth", "rich", "success", "trade-off"]):
            return "wealth_wellbeing"
        else:
            return "comprehensive"

    def _extract_personal_context(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract personal context"""

        if context:
            return {
                "annual_income": context.get("income", 2000000),
                "age": context.get("age", 30),
                "work_hours_week": context.get("work_hours", 60),
                "savings_rate": context.get("savings_rate", 0.20),
                "current_savings": context.get("savings", 1000000),
                "monthly_expenses": context.get("expenses", 80000),
                "dependents": context.get("dependents", 0),
                "debt": context.get("debt", 0),
                "career_satisfaction": context.get("career_satisfaction", 7),
                "life_satisfaction": context.get("life_satisfaction", 6),
                "location": context.get("location", "Bangalore")
            }
        else:
            return {
                "annual_income": 2000000,
                "age": 30,
                "work_hours_week": 60,
                "savings_rate": 0.20,
                "current_savings": 1000000,
                "monthly_expenses": 80000,
                "dependents": 0,
                "debt": 0,
                "career_satisfaction": 7,
                "life_satisfaction": 6,
                "location": "Bangalore"
            }

    async def _income_happiness_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze income vs happiness relationship"""

        income = context["annual_income"]

        # Optimal income for happiness (India-adjusted)
        optimal_income_india = 4000000  # ₹40 lakh/year

        # Current position on curve
        if income < 1000000:
            position = "Below baseline - significant happiness gains from more income"
            happiness_impact = "High"
        elif income < 2000000:
            position = "Rising rapidly - income increases still meaningful"
            happiness_impact = "High-Medium"
        elif income < 4000000:
            position = "Approaching optimal - moderate happiness gains"
            happiness_impact = "Medium"
        elif income < 8000000:
            position = "Beyond optimal - diminishing returns on happiness"
            happiness_impact = "Low-Medium"
        else:
            position = "Well beyond optimal - minimal happiness gains from more income"
            happiness_impact = "Low"

        # Calculate if pursuing more income makes sense
        current_satisfaction = context["life_satisfaction"]
        work_hours = context["work_hours_week"]

        advice = []
        if income < optimal_income_india and work_hours < 50:
            advice.append("You're below optimal income and not overworking - reasonable to pursue more income")
        elif income >= optimal_income_india:
            advice.append("You're at/beyond optimal income - focus on time affluence, autonomy, and meaningful work")
        elif work_hours > 60:
            advice.append("Warning: You're working 60+ hours/week - likely trading happiness for money inefficiently")

        return {
            "type": "income_happiness",
            "current_income": income,
            "optimal_income": optimal_income_india,
            "position_on_curve": position,
            "happiness_impact_of_more_money": happiness_impact,
            "advice": advice,
            "research_insight": self.happiness_principles["income_happiness_curve"]
        }

    async def _work_life_balance_optimization(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize work-life balance"""

        work_hours = context["work_hours_week"]
        income = context["annual_income"]
        hourly_rate = income / (work_hours * 52)

        # Assess current balance
        if work_hours <= 40:
            balance_rating = "Excellent"
            risk = "Low burnout risk"
        elif work_hours <= 50:
            balance_rating = "Good"
            risk = "Moderate stress, manageable"
        elif work_hours <= 60:
            balance_rating = "Poor"
            risk = "High stress, burnout risk"
        else:
            balance_rating = "Unsustainable"
            risk = "Very high burnout risk, health impact likely"

        # Time-money trade-offs
        extra_hours_per_week = max(0, work_hours - 40)
        opportunity_cost = {
            "time_lost_per_year": f"{extra_hours_per_week * 52} hours ({extra_hours_per_week * 52 / 24:.0f} days)",
            "activities_sacrificed": ["Family time", "Hobbies", "Exercise", "Friends", "Rest"],
            "hourly_rate": f"₹{hourly_rate:,.0f}/hour",
            "question": f"Is each extra hour worth ₹{hourly_rate:,.0f} to you?"
        }

        # Optimization recommendations
        optimizations = [
            {
                "action": "Reduce work hours to 50/week",
                "time_gained": f"{max(0, work_hours - 50)} hours/week",
                "income_impact": "Potentially 0-10% less (but often no impact if more focused)",
                "happiness_impact": "+2 points on 10-point scale",
                "recommendation": "High priority if working >50 hours"
            },
            {
                "action": "Negotiate remote/flexible work",
                "time_gained": "5-10 hours/week (no commute, flexibility)",
                "income_impact": "None",
                "happiness_impact": "+1 point",
                "recommendation": "Ask for this immediately"
            },
            {
                "action": "Take full vacation days",
                "time_gained": "Additional rest and recovery",
                "income_impact": "None (already entitled)",
                "happiness_impact": "+1-2 points",
                "recommendation": "Use all vacation days, guilt-free"
            }
        ]

        return {
            "type": "work_life_balance",
            "current_hours": work_hours,
            "balance_rating": balance_rating,
            "burnout_risk": risk,
            "opportunity_cost": opportunity_cost,
            "optimizations": optimizations
        }

    async def _fire_movement_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze FIRE (Financial Independence Retire Early) path"""

        income = context["annual_income"]
        expenses = context["monthly_expenses"] * 12
        savings_rate = context["savings_rate"]
        current_savings = context["current_savings"]
        age = context["age"]

        # Calculate FIRE number (25x annual expenses - 4% rule)
        fire_number = expenses * 25

        # Calculate years to FIRE
        annual_savings = income * savings_rate
        if annual_savings > 0:
            # Simplified calculation (ignoring investment returns for now)
            years_to_fire = (fire_number - current_savings) / annual_savings
            years_to_fire = max(0, years_to_fire)
        else:
            years_to_fire = float('inf')

        fire_age = age + years_to_fire

        # FIRE types assessment
        fire_types_analysis = {
            "Lean FIRE": {
                "description": "Retire on minimal expenses (₹25-40K/month)",
                "fire_number": f"₹{300000 * 25:,} - ₹{480000 * 25:,}",
                "feasibility": "Possible in 8-12 years with 50%+ savings rate",
                "lifestyle": "Frugal, simple living, often in lower cost location"
            },
            "Regular FIRE": {
                "description": "Retire on current lifestyle expenses",
                "fire_number": f"₹{fire_number:,}",
                "feasibility": f"~{years_to_fire:.0f} years at current savings rate",
                "lifestyle": "Maintain current standard of living"
            },
            "Fat FIRE": {
                "description": "Retire with high expenses (₹2L+/month)",
                "fire_number": f"₹{2400000 * 25:,}+",
                "feasibility": "15-25 years, requires high income and savings",
                "lifestyle": "Comfortable, travel, no financial constraints"
            },
            "Barista FIRE": {
                "description": "Semi-retire, work part-time for expenses",
                "fire_number": f"₹{fire_number * 0.5:,} (50% of full FIRE)",
                "feasibility": f"~{years_to_fire/2:.0f} years",
                "lifestyle": "Mix of work and freedom, health insurance from employer"
            }
        }

        # Recommendations
        if savings_rate < 0.10:
            recommendation = "Increase savings rate to at least 20% to make FIRE viable"
        elif savings_rate < 0.30:
            recommendation = f"Good progress. FIRE in {years_to_fire:.0f} years. Consider Barista FIRE for earlier freedom."
        else:
            recommendation = f"Excellent savings rate! On track for FIRE in {years_to_fire:.0f} years."

        return {
            "type": "fire",
            "fire_number": fire_number,
            "current_savings": current_savings,
            "progress_to_fire": f"{(current_savings / fire_number * 100):.1f}%",
            "years_to_fire": years_to_fire if years_to_fire != float('inf') else "Not on track",
            "fire_age": int(fire_age) if years_to_fire != float('inf') else "N/A",
            "current_savings_rate": f"{savings_rate * 100:.0f}%",
            "fire_types": fire_types_analysis,
            "recommendation": recommendation
        }

    async def _burnout_prevention(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze burnout risk and prevention"""

        work_hours = context["work_hours_week"]
        career_satisfaction = context["career_satisfaction"]
        life_satisfaction = context["life_satisfaction"]

        # Burnout risk factors
        risk_factors = []
        risk_score = 0

        if work_hours > 60:
            risk_factors.append("Working >60 hours/week")
            risk_score += 3
        elif work_hours > 50:
            risk_factors.append("Working >50 hours/week")
            risk_score += 2

        if career_satisfaction < 6:
            risk_factors.append("Low career satisfaction")
            risk_score += 2

        if life_satisfaction < 6:
            risk_factors.append("Low life satisfaction")
            risk_score += 2

        # Burnout level
        if risk_score >= 6:
            burnout_level = "High Risk - Take action now"
        elif risk_score >= 4:
            burnout_level = "Moderate Risk - Monitor and adjust"
        else:
            burnout_level = "Low Risk - Maintain current balance"

        # Prevention strategies
        prevention_strategies = [
            {
                "strategy": "Set Hard Boundaries",
                "actions": [
                    "No work after 7pm or on weekends (except emergencies)",
                    "Turn off work notifications outside work hours",
                    "Schedule personal time as non-negotiable appointments"
                ],
                "effectiveness": "High"
            },
            {
                "strategy": "Regular Recovery",
                "actions": [
                    "7-8 hours sleep (non-negotiable)",
                    "Exercise 3-4x/week",
                    "Weekly digital detox (no screens for 4+ hours)",
                    "Use all vacation days"
                ],
                "effectiveness": "High"
            },
            {
                "strategy": "Meaning and Autonomy",
                "actions": [
                    "Align work with personal values",
                    "Negotiate for more autonomy in how you work",
                    "Focus on impact, not just hours worked"
                ],
                "effectiveness": "Medium-High"
            },
            {
                "strategy": "Social Support",
                "actions": [
                    "Regular catch-ups with friends/family",
                    "Join communities aligned with interests",
                    "Consider therapy/coaching if needed"
                ],
                "effectiveness": "Medium"
            }
        ]

        return {
            "type": "burnout",
            "burnout_level": burnout_level,
            "risk_score": f"{risk_score}/10",
            "risk_factors": risk_factors,
            "prevention_strategies": prevention_strategies,
            "warning_signs": [
                "Chronic fatigue despite rest",
                "Cynicism about work",
                "Reduced performance",
                "Physical symptoms (headaches, stomach issues)",
                "Emotional exhaustion"
            ]
        }

    async def _wealth_wellbeing_tradeoffs(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze wealth vs well-being trade-offs"""

        income = context["annual_income"]
        work_hours = context["work_hours_week"]
        life_satisfaction = context["life_satisfaction"]

        # Common trade-offs
        tradeoffs = [
            {
                "trade_off": "High Income vs Time Freedom",
                "your_choice": "High income path" if work_hours > 55 else "Balanced/Time freedom",
                "consideration": "After ₹40L/year, time becomes more valuable than money for happiness",
                "recommendation": "Consider 20% pay cut for 20% less hours" if income > 4000000 else "Income still matters at your level"
            },
            {
                "trade_off": "Career Advancement vs Work-Life Balance",
                "your_choice": "Advancement focus" if work_hours > 50 else "Balance focus",
                "consideration": "Promotions increase income but often decrease satisfaction (more responsibility, stress)",
                "recommendation": "Be intentional about which promotions to pursue"
            },
            {
                "trade_off": "Entrepreneurship vs Corporate Stability",
                "consideration": "Entrepreneurs: higher autonomy and satisfaction, but often lower income initially",
                "recommendation": "If autonomy matters more than security, entrepreneurship may increase well-being"
            }
        ]

        # Life satisfaction optimization
        satisfaction_factors = {
            "Strong Predictors of Life Satisfaction": [
                "Autonomy and control over work",
                "Strong relationships and social connections",
                "Physical health and exercise",
                "Meaning and purpose",
                "Financial security (not extreme wealth)"
            ],
            "Weak Predictors": [
                "Income (beyond ₹30-40L/year)",
                "Luxury possessions",
                "Social status",
                "Physical attractiveness"
            ]
        }

        return {
            "type": "wealth_wellbeing",
            "current_satisfaction": life_satisfaction,
            "tradeoffs": tradeoffs,
            "satisfaction_factors": satisfaction_factors,
            "key_insight": "Focus on time affluence, autonomy, relationships, and health over wealth accumulation beyond financial security"
        }

    async def _comprehensive_happiness_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive happiness analysis"""

        income_analysis = await self._income_happiness_analysis(context)
        work_life = await self._work_life_balance_optimization(context)
        fire = await self._fire_movement_analysis(context)

        return {
            "type": "comprehensive",
            "income_happiness": income_analysis,
            "work_life_balance": work_life,
            "fire_analysis": fire
        }

    async def _generate_recommendations(
        self,
        context: Dict[str, Any],
        analysis: Dict[str, Any],
        analysis_type: str
    ) -> List[Dict[str, Any]]:
        """Generate recommendations"""

        recommendations = []

        work_hours = context["work_hours_week"]
        if work_hours > 55:
            recommendations.append({
                "title": "Reduce Work Hours to 50/week",
                "description": "You're working 55+ hours. Research shows diminishing returns beyond 50 hours. Negotiate boundaries.",
                "priority": "critical",
                "impact": "Major improvement in well-being and relationships"
            })

        income = context["annual_income"]
        if income > 4000000:
            recommendations.append({
                "title": "Optimize for Time, Not More Money",
                "description": "You're beyond optimal income for happiness. Focus on time affluence, autonomy, and meaningful work.",
                "priority": "high",
                "impact": "Shift from hedonic treadmill to lasting well-being"
            })

        recommendations.append({
            "title": "Track Time Use for 1 Week",
            "description": "Track how you spend every hour for 1 week. Identify time drains and reallocate to high-value activities.",
            "priority": "medium",
            "impact": "Clarity on where your life is going"
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

        prompt = f"""You are a well-being economist and life satisfaction expert. Provide wisdom based on:

Query: {query}

Context:
{json.dumps(context, indent=2)}

Analysis:
{json.dumps(analysis, indent=2)[:1500]}

Recommendations:
{json.dumps(recommendations, indent=2)}

Generate thoughtful guidance (400-500 words) that:
1. Explains the income-happiness relationship
2. Assesses work-life balance and burnout risk
3. Discusses FIRE concepts if relevant
4. Provides actionable advice for well-being
5. Challenges conventional "more money = better life" thinking

Be evidence-based but compassionate."""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                temperature=0.6,
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

        response = "## Money & Happiness Analysis\n\n"
        response += f"**Income:** ₹{context['annual_income']/100000:.1f}L/year\n"
        response += f"**Work Hours:** {context['work_hours_week']} hours/week\n\n"

        response += "**Recommendations:**\n"
        for i, rec in enumerate(recommendations, 1):
            response += f"{i}. **{rec['title']}**\n"
            response += f"   {rec['description']}\n\n"

        return response

    def _get_sources(self) -> List[Dict[str, str]]:
        """Get sources"""
        return [
            {"type": "research", "source": "Kahneman, Deaton - Income and well-being"},
            {"type": "research", "source": "Easterlin Paradox, Hedonic Adaptation research"}
        ]

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Error response"""
        return {
            "answer": f"Error in happiness analysis: {error}",
            "error": error,
            "confidence": 0.0,
            "agent": self.name
        }


# Export
__all__ = ["MoneyHappinessAgent"]
