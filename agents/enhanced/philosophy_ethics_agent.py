"""
Philosophy & Ethics Agent
Ethical framework recommendations, stakeholder capitalism, long-term thinking, purpose-driven business models
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


class PhilosophyEthicsAgent:
    """
    Philosophy & Ethics Agent

    Provides ethical and philosophical guidance for business including:
    - Ethical framework recommendations (utilitarianism, deontology, virtue ethics)
    - Stakeholder capitalism vs shareholder primacy
    - Long-term thinking and intergenerational responsibility
    - Purpose-driven business models
    - Ethical decision-making frameworks
    - Corporate social responsibility (CSR)
    - Values-based leadership
    """

    def __init__(self):
        """Initialize Philosophy Ethics Agent"""
        self.name = "PhilosophyEthicsAgent"
        self.description = "Ethical frameworks and purpose-driven business guidance"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

        # Ethical frameworks
        self.ethical_frameworks = self._initialize_ethical_frameworks()

        # Purpose-driven business models
        self.business_models = ["B Corporation", "Social Enterprise", "Conscious Capitalism", "Stakeholder Capitalism"]

    def _initialize_ethical_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Initialize ethical frameworks"""
        return {
            "utilitarianism": {
                "principle": "Greatest good for the greatest number",
                "philosopher": "Jeremy Bentham, John Stuart Mill",
                "business_application": "Maximize overall stakeholder value and societal benefit",
                "decision_rule": "Choose action that produces most positive outcomes for most people",
                "pros": ["Clear measurement", "Democratic", "Practical"],
                "cons": ["Can justify harming minorities", "Difficult to measure all consequences"],
                "example": "Launching affordable healthcare product that helps millions, even if lower profit margin"
            },
            "deontology": {
                "principle": "Duty and rules-based ethics",
                "philosopher": "Immanuel Kant",
                "business_application": "Follow universal moral rules regardless of consequences",
                "decision_rule": "Act according to principles that could be universal laws",
                "pros": ["Respect for individual rights", "Clear principles", "Predictable"],
                "cons": ["Can be inflexible", "Rules may conflict"],
                "example": "Never lying to customers, even if it means losing a sale"
            },
            "virtue_ethics": {
                "principle": "Character and virtues over rules or consequences",
                "philosopher": "Aristotle",
                "business_application": "Cultivate virtuous character in leaders and organizations",
                "decision_rule": "What would a virtuous person do?",
                "pros": ["Holistic", "Character development", "Context-sensitive"],
                "cons": ["Less concrete guidance", "Whose virtues?"],
                "example": "Building culture of integrity, courage, compassion, and wisdom"
            },
            "care_ethics": {
                "principle": "Relationships and care for others",
                "philosopher": "Carol Gilligan, Nel Noddings",
                "business_application": "Prioritize care for stakeholders and relationships",
                "decision_rule": "Maintain and strengthen caring relationships",
                "pros": ["Emphasizes relationships", "Contextual", "Inclusive"],
                "cons": ["May favor in-groups", "Can conflict with impartiality"],
                "example": "Supporting employees through difficult times, work-life balance policies"
            },
            "rights_based": {
                "principle": "Respect fundamental human rights",
                "philosopher": "John Locke, UN Declaration of Human Rights",
                "business_application": "Ensure business doesn't violate human rights",
                "decision_rule": "Respect rights to life, liberty, property, dignity",
                "pros": ["Protects individuals", "Clear boundaries", "Universal"],
                "cons": ["Rights can conflict", "Cultural variations"],
                "example": "Fair labor practices, data privacy, non-discrimination"
            },
            "justice_ethics": {
                "principle": "Fairness and justice in distribution",
                "philosopher": "John Rawls",
                "business_application": "Fair distribution of benefits and burdens",
                "decision_rule": "Would I accept this if I didn't know my position (veil of ignorance)?",
                "pros": ["Addresses inequality", "Fair procedures", "Protects disadvantaged"],
                "cons": ["What is 'fair' is debatable", "May limit efficiency"],
                "example": "Living wages for all employees, progressive benefit structures"
            }
        }

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process ethics/philosophy request

        Args:
            query: User query about ethics/philosophy
            context: Business context

        Returns:
            Dict with ethical analysis results
        """
        try:
            # Determine analysis type
            analysis_type = self._determine_analysis_type(query)

            # Extract context
            business_context = self._extract_business_context(query, context)

            # Perform analysis
            if analysis_type == "ethical_framework":
                analysis = await self._recommend_ethical_framework(business_context)
            elif analysis_type == "stakeholder_capitalism":
                analysis = await self._stakeholder_capitalism_analysis(business_context)
            elif analysis_type == "long_term_thinking":
                analysis = await self._long_term_thinking_framework(business_context)
            elif analysis_type == "purpose_driven":
                analysis = await self._purpose_driven_model(business_context)
            elif analysis_type == "ethical_dilemma":
                analysis = await self._ethical_dilemma_resolution(business_context)
            else:
                analysis = await self._comprehensive_ethics_analysis(business_context)

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
                "confidence": 0.86,
                "sources": self._get_sources(),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in PhilosophyEthicsAgent: {str(e)}")
            return self._error_response(str(e))

    def _determine_analysis_type(self, query: str) -> str:
        """Determine type of ethics analysis"""
        query_lower = query.lower()

        if any(word in query_lower for word in ["ethical framework", "ethics", "moral"]):
            return "ethical_framework"
        elif any(word in query_lower for word in ["stakeholder", "capitalism", "shareholder"]):
            return "stakeholder_capitalism"
        elif any(word in query_lower for word in ["long-term", "long term", "future", "sustainability"]):
            return "long_term_thinking"
        elif any(word in query_lower for word in ["purpose", "mission", "values", "why"]):
            return "purpose_driven"
        elif any(word in query_lower for word in ["dilemma", "decision", "should i", "right thing"]):
            return "ethical_dilemma"
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
                "company_name": context.get("company_name", "Company"),
                "industry": context.get("industry", "Technology"),
                "stage": context.get("stage", "seed"),
                "current_values": context.get("values", []),
                "stakeholders": context.get("stakeholders", ["customers", "employees", "investors"]),
                "dilemma": context.get("dilemma", query),
                "revenue_model": context.get("revenue_model", "Subscription")
            }
        else:
            return {
                "company_name": "Company",
                "industry": "Technology",
                "stage": "seed",
                "current_values": [],
                "stakeholders": ["customers", "employees", "investors", "society"],
                "dilemma": query,
                "revenue_model": "Subscription"
            }

    async def _recommend_ethical_framework(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend ethical framework for business"""

        # Analyze which framework fits best
        industry = context["industry"]
        stakeholders = context["stakeholders"]

        # Recommend primary and supporting frameworks
        if "society" in stakeholders or industry in ["Healthcare", "Education"]:
            primary = "utilitarianism"
            supporting = ["care_ethics", "rights_based"]
            rationale = "Healthcare/education should maximize societal benefit while respecting rights"
        elif industry == "Finance":
            primary = "deontology"
            supporting = ["rights_based", "justice_ethics"]
            rationale = "Financial services require strict rules, protection of rights, and fairness"
        else:
            primary = "virtue_ethics"
            supporting = ["care_ethics", "utilitarianism"]
            rationale = "Build strong character and care for stakeholders while seeking positive outcomes"

        # Get framework details
        primary_framework = self.ethical_frameworks[primary].copy()
        supporting_frameworks = [self.ethical_frameworks[s] for s in supporting]

        # Practical application guide
        application_guide = {
            "decision_making_process": [
                f"1. Consider {primary_framework['principle']} ({primary})",
                "2. Ask: Does this respect all stakeholder rights?",
                "3. Evaluate: Long-term consequences for all affected",
                "4. Check: Aligns with company values?",
                "5. Test: Would I be comfortable if this was public?"
            ],
            "values_to_embed": [
                "Integrity - Do what's right, not what's easy",
                "Transparency - Honest communication with all stakeholders",
                "Respect - Treat all people with dignity",
                "Responsibility - Own our impact on society and environment",
                "Excellence - Deliver quality and value"
            ]
        }

        return {
            "type": "ethical_framework",
            "primary_framework": {
                "name": primary,
                **primary_framework
            },
            "supporting_frameworks": supporting_frameworks,
            "rationale": rationale,
            "application_guide": application_guide
        }

    async def _stakeholder_capitalism_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze stakeholder capitalism approach"""

        # Stakeholder mapping
        stakeholders = {
            "customers": {
                "value_creation": "Quality products/services that solve real problems",
                "measurement": "Customer satisfaction, NPS, retention rate",
                "balance": "Fair pricing, data privacy, honest marketing"
            },
            "employees": {
                "value_creation": "Meaningful work, fair compensation, growth opportunities",
                "measurement": "Employee satisfaction, retention, diversity",
                "balance": "Living wages, work-life balance, safe working conditions"
            },
            "investors": {
                "value_creation": "Sustainable long-term returns",
                "measurement": "ROI, ESG performance, risk management",
                "balance": "Transparent reporting, ethical growth, patient capital"
            },
            "suppliers": {
                "value_creation": "Fair partnerships, timely payments",
                "measurement": "Supplier satisfaction, payment terms",
                "balance": "Fair prices, ethical sourcing, long-term relationships"
            },
            "community_society": {
                "value_creation": "Jobs, taxes, social impact, environmental stewardship",
                "measurement": "Social impact metrics, carbon footprint, CSR spend",
                "balance": "Give back 1-2% of revenue, volunteer programs, local sourcing"
            },
            "environment": {
                "value_creation": "Minimize harm, regenerate where possible",
                "measurement": "Carbon emissions, waste, resource use",
                "balance": "Net-zero commitment, circular economy practices"
            }
        }

        # Shareholder primacy vs stakeholder capitalism
        comparison = {
            "shareholder_primacy": {
                "focus": "Maximize shareholder value above all",
                "pros": ["Clear metric (stock price)", "Efficient capital allocation"],
                "cons": ["Short-termism", "Ignores externalities", "Can harm other stakeholders"],
                "examples": ["Traditional public companies"]
            },
            "stakeholder_capitalism": {
                "focus": "Balance all stakeholder interests",
                "pros": ["Long-term sustainability", "Resilience", "Social license to operate"],
                "cons": ["Harder to measure success", "Potential conflicts", "Requires strong governance"],
                "examples": ["Patagonia", "Unilever", "B Corps"]
            }
        }

        recommendation = "Stakeholder Capitalism with transparency - balance stakeholder needs while maintaining financial sustainability"

        return {
            "type": "stakeholder_capitalism",
            "stakeholder_map": stakeholders,
            "comparison": comparison,
            "recommendation": recommendation,
            "implementation": [
                "Define specific commitments to each stakeholder group",
                "Measure and report on stakeholder metrics (not just financial)",
                "Create stakeholder advisory council",
                "Link executive compensation to stakeholder KPIs",
                "Publish annual stakeholder impact report"
            ]
        }

    async def _long_term_thinking_framework(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Framework for long-term thinking"""

        long_term_principles = {
            "cathedral_thinking": {
                "concept": "Build for generations, not quarters",
                "origin": "Medieval cathedral builders who worked on projects lasting centuries",
                "application": "Make decisions with 10, 50, 100 year horizon",
                "example": "Amazon's long-term customer obsession over short-term profits"
            },
            "seventh_generation": {
                "concept": "Consider impact on seventh generation",
                "origin": "Iroquois principle of sustainability",
                "application": "Will this decision be good for people 140 years from now?",
                "example": "Patagonia's environmental commitments"
            },
            "lindy_effect": {
                "concept": "Future life expectancy proportional to current age",
                "origin": "Nassim Taleb",
                "application": "Build timeless businesses based on fundamental needs, not trends",
                "example": "Food, shelter, health, education businesses outlast fads"
            },
            "second_order_thinking": {
                "concept": "Consider consequences of consequences",
                "origin": "Systems thinking",
                "application": "What happens next? And then what?",
                "example": "Free product → lock-in → pricing power → customer backlash"
            }
        }

        time_horizons = {
            "quarterly": {
                "focus": "Financial results, immediate execution",
                "metrics": "Revenue, profit, cash flow",
                "risk": "Short-termism, cutting investments"
            },
            "annual": {
                "focus": "Strategic initiatives, team building",
                "metrics": "Market share, customer growth, employee retention",
                "risk": "Still relatively short-term"
            },
            "3_5_years": {
                "focus": "Market position, moats, brand",
                "metrics": "Brand value, competitive advantages, ecosystem",
                "balanced": "Good balance of short and long term"
            },
            "10_plus_years": {
                "focus": "Legacy, impact, sustainability",
                "metrics": "Societal impact, environmental footprint, values",
                "benefit": "True long-term thinking, resilience"
            }
        }

        return {
            "type": "long_term_thinking",
            "principles": long_term_principles,
            "time_horizons": time_horizons,
            "practices": [
                "Set 10-year vision alongside annual goals",
                "Measure long-term metrics (brand, culture, impact)",
                "Resist short-term pressures from investors",
                "Invest in R&D and people development",
                "Build for resilience, not just efficiency",
                "Write 'letters from future self' - what would you want to have done?"
            ]
        }

    async def _purpose_driven_model(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Purpose-driven business model"""

        # Purpose discovery framework
        purpose_framework = {
            "why_you_exist": "Beyond making money, why does your company exist?",
            "problem_you_solve": "What problem in the world are you uniquely positioned to solve?",
            "impact_you_seek": "What change do you want to see in the world?",
            "values_you_embody": "What principles guide how you operate?"
        }

        # Purpose-driven business models
        models = {
            "b_corporation": {
                "description": "Certified benefit corporation - profit and purpose",
                "requirements": "Legal commitment to stakeholders, minimum impact score",
                "benefits": "Credibility, community, legal protection for purpose",
                "examples": ["Patagonia", "Warby Parker", "Bombas"],
                "process": "B Lab certification, score 80+ on B Impact Assessment"
            },
            "social_enterprise": {
                "description": "Business with primary social/environmental mission",
                "requirements": "Social impact as core, reinvestment of majority of profits",
                "benefits": "Grants access, mission-aligned talent, customer loyalty",
                "examples": ["TOMS", "Grameen Bank", "Aravind Eye Care"],
                "models": ["One-for-one", "Bottom of pyramid", "Hybrid nonprofit-for-profit"]
            },
            "conscious_capitalism": {
                "description": "Business based on higher purpose and stakeholder integration",
                "requirements": "Higher purpose, stakeholder orientation, conscious leadership, culture",
                "benefits": "Employee engagement, customer loyalty, long-term performance",
                "examples": ["Whole Foods", "Southwest Airlines", "The Container Store"],
                "principles": ["Higher purpose", "Stakeholder integration", "Conscious leadership", "Conscious culture"]
            }
        }

        # Purpose statement template
        purpose_template = {
            "format": "We exist to [IMPACT] by [HOW] for [WHO]",
            "example": "We exist to make sustainable products accessible to everyone by creating affordable, high-quality alternatives for conscious consumers"
        }

        return {
            "type": "purpose_driven",
            "purpose_framework": purpose_framework,
            "business_models": models,
            "purpose_template": purpose_template,
            "benefits": [
                "Attracts mission-aligned talent (willing to accept 10-20% lower pay)",
                "Customer loyalty and premium pricing (20-30% willing to pay more)",
                "Resilience in downturns (purpose provides direction)",
                "Investor interest (impact investors, long-term capital)",
                "Competitive differentiation"
            ],
            "implementation": [
                "Co-create purpose with team (not top-down)",
                "Embed in hiring, onboarding, performance reviews",
                "Measure and report on purpose metrics",
                "Make hard trade-offs in favor of purpose",
                "Tell purpose stories constantly"
            ]
        }

    async def _ethical_dilemma_resolution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Framework for resolving ethical dilemmas"""

        dilemma = context.get("dilemma", "")

        # Ethical decision-making framework
        decision_framework = {
            "step_1_recognize": {
                "question": "Is this an ethical issue?",
                "test": "Would you be comfortable if this decision was on front page of newspaper?"
            },
            "step_2_gather_facts": {
                "question": "What are all the relevant facts?",
                "considerations": ["Who is affected?", "What are the consequences?", "What are the alternatives?"]
            },
            "step_3_identify_stakeholders": {
                "question": "Who has a stake in this decision?",
                "stakeholders": ["Customers", "Employees", "Investors", "Suppliers", "Community", "Environment"]
            },
            "step_4_evaluate_alternatives": {
                "frameworks_to_apply": [
                    "Utilitarian: Which option creates most good for most people?",
                    "Rights: Which option best respects everyone's rights?",
                    "Justice: Which option is most fair?",
                    "Virtue: What would a person of integrity do?",
                    "Care: Which option best maintains relationships?"
                ]
            },
            "step_5_decide_and_act": {
                "question": "What decision can you live with?",
                "tests": [
                    "Publicity test: Would you be okay if this was public?",
                    "Mirror test: Can you look yourself in the mirror?",
                    "Role model test: Would you want others to do the same?",
                    "Golden rule: Would you want this done to you?"
                ]
            },
            "step_6_reflect": {
                "question": "What did you learn?",
                "actions": ["Debrief with team", "Update policies", "Share lessons"]
            }
        }

        common_dilemmas = [
            {
                "dilemma": "Profitability vs Customer Value",
                "example": "Cutting features to increase margins",
                "resolution": "Long-term: Customer value wins. Short-term profit hurts long-term"
            },
            {
                "dilemma": "Growth vs Sustainability",
                "example": "Scaling fast vs building sustainably",
                "resolution": "Sustainable growth. Unsustainable growth leads to collapse"
            },
            {
                "dilemma": "Transparency vs Competitive Advantage",
                "example": "How much to disclose publicly",
                "resolution": "Default to transparency unless genuine competitive harm"
            }
        ]

        return {
            "type": "ethical_dilemma",
            "decision_framework": decision_framework,
            "common_dilemmas": common_dilemmas
        }

    async def _comprehensive_ethics_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive ethics analysis"""

        framework = await self._recommend_ethical_framework(context)
        stakeholder = await self._stakeholder_capitalism_analysis(context)
        purpose = await self._purpose_driven_model(context)

        return {
            "type": "comprehensive",
            "ethical_framework": framework,
            "stakeholder_capitalism": stakeholder,
            "purpose_driven": purpose
        }

    async def _generate_recommendations(
        self,
        context: Dict[str, Any],
        analysis: Dict[str, Any],
        analysis_type: str
    ) -> List[Dict[str, Any]]:
        """Generate recommendations"""

        recommendations = []

        recommendations.append({
            "title": "Define and Document Core Values",
            "description": "Create 3-5 core values that guide all decisions. Make them specific and actionable, not generic",
            "priority": "high",
            "example": "Instead of 'Integrity', use 'We do what's right even when no one is watching'"
        })

        recommendations.append({
            "title": "Create Ethics Committee",
            "description": "Form a committee to review major ethical decisions and dilemmas",
            "priority": "medium",
            "composition": "Cross-functional team including employees, advisors, external ethicist"
        })

        recommendations.append({
            "title": "Implement Stakeholder Reporting",
            "description": "Report on metrics for all stakeholders, not just financial",
            "priority": "medium",
            "metrics": "Employee satisfaction, customer NPS, social impact, environmental footprint"
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

        prompt = f"""You are a business ethics and philosophy expert. Provide wisdom based on:

Query: {query}

Context:
{json.dumps(context, indent=2)}

Analysis:
{json.dumps(analysis, indent=2)[:1500]}

Recommendations:
{json.dumps(recommendations, indent=2)}

Generate thoughtful guidance (400-500 words) that:
1. Explains relevant ethical frameworks
2. Discusses stakeholder capitalism vs shareholder primacy
3. Provides framework for long-term thinking
4. Guides toward purpose-driven business
5. Offers practical ethical decision-making tools

Be philosophical yet practical."""

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

        response = "## Ethics & Philosophy Guidance\n\n"
        response += f"**Company:** {context['company_name']}\n\n"

        response += "**Recommendations:**\n"
        for i, rec in enumerate(recommendations, 1):
            response += f"{i}. **{rec['title']}**\n"
            response += f"   {rec['description']}\n\n"

        return response

    def _get_sources(self) -> List[Dict[str, str]]:
        """Get sources"""
        return [
            {"type": "philosophy", "source": "Aristotle, Kant, Mill - ethical philosophy"},
            {"type": "business_ethics", "source": "Conscious Capitalism, B Corp, Stakeholder theory"}
        ]

    def _error_response(self, error: str) -> Dict[str, Any]:
        """Error response"""
        return {
            "answer": f"Error in ethics analysis: {error}",
            "error": error,
            "confidence": 0.0,
            "agent": self.name
        }


# Export
__all__ = ["PhilosophyEthicsAgent"]
