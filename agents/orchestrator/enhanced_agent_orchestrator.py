"""
Enhanced Agent Orchestrator with Inter-Agent Communication
Manages all 14+ specialized agents with intelligent routing and A2A communication
"""
import os
import sys
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from services.llm_service import LLMService

# Import original agents
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from policy_agent.policy_agent import PolicyAgent
from market_agent.market_agent import MarketAgent
from finance_agent.finance_agent import FinanceAgent
from tax_agent.tax_agent import TaxAgent
from distribution_agent.distribution_agent import DistributionAgent
from investment_agent.investment_agent import InvestmentAgent
from legal_agent.legal_agent import LegalAgent
from news_agent.news_agent import NewsAgent

# Import enhanced agents - Phase 2 (First 12)
from enhanced.business_model_agent import BusinessModelAgent
from enhanced.stock_analysis_agent import StockAnalysisAgent
from enhanced.competitor_intelligence_agent import CompetitorIntelligenceAgent
from enhanced.subsidies_agent import SubsidiesAnalyzerAgent
from enhanced.business_model_recommender_agent import BusinessModelRecommenderAgent
from enhanced.loophole_predictor_agent import LoopholePredictorAgent
from enhanced.hedge_fund_agent import HedgeFundAnalyzerAgent
from enhanced.mutual_fund_agent import MutualFundAnalyzerAgent
from enhanced.industry_expert_agent import IndustryDomainExpertAgent
from enhanced.enhanced_news_agent import EnhancedNewsAgent
from enhanced.macroeconomics_agent import MacroeconomicsAgent
from enhanced.international_markets_agent import InternationalMarketsAgent

# Import enhanced agents - Phase 3 (Final 15 agents)
from enhanced.real_estate_agent import RealEstateAnalysisAgent
from enhanced.marketing_strategy_agent import MarketingStrategyAgent
from enhanced.business_strategy_agent import BusinessStrategyAgent
from enhanced.connecting_dots_agent import ConnectingDotsAgent
from enhanced.hft_analysis_agent import HFTAnalysisAgent
from enhanced.hr_analytics_agent import HRAnalyticsAgent
from enhanced.human_behaviour_agent import HumanBehaviourAgent
from enhanced.human_needs_agent import HumanNeedsAgent
from enhanced.esg_environmental_agent import ESGEnvironmentalAgent
from enhanced.philosophy_ethics_agent import PhilosophyEthicsAgent
from enhanced.money_happiness_agent import MoneyHappinessAgent
from enhanced.ngo_nonprofit_agent import NGONonProfitAgent
from enhanced.philanthropy_impact_agent import PhilanthropyImpactAgent
from enhanced.schemes_monitoring_agent import SchemesMonitoringAgent
from enhanced.regulator_analysis_agent import RegulatorAnalysisAgent


class EnhancedAgentOrchestrator:
    """
    Enhanced Agent Orchestrator with Inter-Agent Communication (A2A)

    Features:
    - Manages 14+ specialized agents
    - Intelligent query classification and routing
    - Multi-agent coordination for complex queries
    - Inter-agent communication and data sharing
    - Response synthesis from multiple agents
    - Context management across conversation
    """

    def __init__(self):
        """Initialize Enhanced Agent Orchestrator"""
        self.llm_service = LLMService()

        # Initialize ALL agents (Original 8 + Enhanced 27 = 35 TOTAL)
        print("Initializing Enhanced Agent Orchestrator with 35 agents...")

        # Original 8 agents
        self.policy_agent = PolicyAgent()
        self.market_agent = MarketAgent()
        self.finance_agent = FinanceAgent()
        self.tax_agent = TaxAgent()
        self.distribution_agent = DistributionAgent()
        self.investment_agent = InvestmentAgent()
        self.legal_agent = LegalAgent()
        self.news_agent = NewsAgent()

        # Enhanced agents (Phase 2) - First 12 agents
        self.business_model_agent = BusinessModelAgent()
        self.stock_analysis_agent = StockAnalysisAgent()
        self.competitor_agent = CompetitorIntelligenceAgent()
        self.subsidies_agent = SubsidiesAnalyzerAgent()
        self.business_model_recommender = BusinessModelRecommenderAgent()
        self.loophole_predictor = LoopholePredictorAgent()
        self.hedge_fund_analyzer = HedgeFundAnalyzerAgent()
        self.mutual_fund_analyzer = MutualFundAnalyzerAgent()
        self.industry_expert = IndustryDomainExpertAgent()
        self.enhanced_news_agent = EnhancedNewsAgent()
        self.macroeconomics_agent = MacroeconomicsAgent()
        self.international_markets_agent = InternationalMarketsAgent()

        # Enhanced agents (Phase 3) - Final 15 agents
        self.real_estate_agent = RealEstateAnalysisAgent()
        self.marketing_strategy_agent = MarketingStrategyAgent()
        self.business_strategy_agent = BusinessStrategyAgent()
        self.connecting_dots_agent = ConnectingDotsAgent()
        self.hft_analysis_agent = HFTAnalysisAgent()
        self.hr_analytics_agent = HRAnalyticsAgent()
        self.human_behaviour_agent = HumanBehaviourAgent()
        self.human_needs_agent = HumanNeedsAgent()
        self.esg_environmental_agent = ESGEnvironmentalAgent()
        self.philosophy_ethics_agent = PhilosophyEthicsAgent()
        self.money_happiness_agent = MoneyHappinessAgent()
        self.ngo_nonprofit_agent = NGONonProfitAgent()
        self.philanthropy_impact_agent = PhilanthropyImpactAgent()
        self.schemes_monitoring_agent = SchemesMonitoringAgent()
        self.regulator_analysis_agent = RegulatorAnalysisAgent()

        # Agent registry (ALL 35 AGENTS)
        self.agents = {
            # Core 8 agents
            "policy": self.policy_agent,
            "market": self.market_agent,
            "finance": self.finance_agent,
            "tax": self.tax_agent,
            "distribution": self.distribution_agent,
            "investment": self.investment_agent,
            "legal": self.legal_agent,
            "news": self.news_agent,
            # Phase 2 enhanced agents (12)
            "business_model": self.business_model_agent,
            "business_model_recommender": self.business_model_recommender,
            "stock_analysis": self.stock_analysis_agent,
            "competitor": self.competitor_agent,
            "subsidies": self.subsidies_agent,
            "loophole_predictor": self.loophole_predictor,
            "hedge_fund": self.hedge_fund_analyzer,
            "mutual_fund": self.mutual_fund_analyzer,
            "industry_expert": self.industry_expert,
            "enhanced_news": self.enhanced_news_agent,
            "macroeconomics": self.macroeconomics_agent,
            "international_markets": self.international_markets_agent,
            # Phase 3 enhanced agents (15)
            "real_estate": self.real_estate_agent,
            "marketing_strategy": self.marketing_strategy_agent,
            "business_strategy": self.business_strategy_agent,
            "connecting_dots": self.connecting_dots_agent,
            "hft_analysis": self.hft_analysis_agent,
            "hr_analytics": self.hr_analytics_agent,
            "human_behaviour": self.human_behaviour_agent,
            "human_needs": self.human_needs_agent,
            "esg_environmental": self.esg_environmental_agent,
            "philosophy_ethics": self.philosophy_ethics_agent,
            "money_happiness": self.money_happiness_agent,
            "ngo_nonprofit": self.ngo_nonprofit_agent,
            "philanthropy_impact": self.philanthropy_impact_agent,
            "schemes_monitoring": self.schemes_monitoring_agent,
            "regulator_analysis": self.regulator_analysis_agent
        }

        # Agent routing keywords (ALL 35 AGENTS)
        self.routing_keywords = {
            # Core 8 agents
            "policy": ["policy", "regulation", "compliance", "government rule", "law change"],
            "market": ["market", "industry trend", "market size", "competitor landscape", "market opportunity"],
            "finance": ["financial", "budget", "cash flow", "profit", "revenue", "financial analysis"],
            "tax": ["tax", "deduction", "tax optimization", "gst", "income tax", "tax filing"],
            "distribution": ["distribution", "channel", "go-to-market", "customer acquisition", "gtm"],
            "investment": ["investment", "valuation", "due diligence", "funding", "investor"],
            "legal": ["contract", "legal", "agreement", "terms", "nda", "legal review"],
            "news": ["news", "latest", "update", "announcement", "current events"],
            # Phase 2 enhanced agents (12)
            "business_model": ["business model", "canvas", "value proposition", "revenue stream", "analyze model"],
            "business_model_recommender": ["recommend model", "suggest model", "which model", "best model", "model for"],
            "stock_analysis": ["stock", "share", "equity", "ticker", "invest in stock", "buy stock"],
            "competitor": ["competitor", "competition", "rival", "competitive landscape", "who competes"],
            "subsidies": ["subsidy", "grant", "scheme", "funding program", "government support", "incentive"],
            "loophole_predictor": ["loophole", "tax optimization", "legal optimization", "deduction", "tax credit", "tax strategy"],
            "hedge_fund": ["hedge fund", "alternative investment", "fund manager", "hedge", "alpha", "absolute return"],
            "mutual_fund": ["mutual fund", "index fund", "etf", "vanguard", "fidelity", "portfolio", "fund recommendation"],
            "industry_expert": ["industry", "sector", "domain", "market analysis", "industry trends", "competitive dynamics"],
            "enhanced_news": ["news", "headlines", "market news", "latest news", "breaking", "trending", "updates"],
            "macroeconomics": ["macro", "macroeconomic", "gdp", "inflation", "interest rate", "economy", "fiscal policy", "monetary policy", "recession", "economic growth"],
            "international_markets": ["international", "global market", "foreign market", "overseas", "export", "import", "cross-border", "international trade", "emerging market"],
            # Phase 3 enhanced agents (15)
            "real_estate": ["real estate", "property", "rental", "reit", "cap rate", "commercial real estate", "residential property", "property investment"],
            "marketing_strategy": ["marketing", "brand", "advertising", "campaign", "customer acquisition", "seo", "content marketing", "digital marketing"],
            "business_strategy": ["strategy", "strategic planning", "competitive strategy", "growth strategy", "expansion", "pivot", "business planning"],
            "connecting_dots": ["connect", "correlation", "pattern", "insight", "trend analysis", "hidden connection", "market intelligence"],
            "hft_analysis": ["high frequency", "hft", "algorithmic trading", "quant", "trading strategy", "market microstructure"],
            "hr_analytics": ["hr", "human resources", "salary", "compensation", "hiring", "recruitment", "employee", "workforce"],
            "human_behaviour": ["behavior", "psychology", "consumer behavior", "decision making", "behavioral economics"],
            "human_needs": ["needs", "maslow", "basic needs", "hierarchy", "motivation", "well-being"],
            "esg_environmental": ["esg", "environmental", "sustainability", "climate", "carbon", "green", "sustainable"],
            "philosophy_ethics": ["philosophy", "ethics", "moral", "values", "principles", "philosophical"],
            "money_happiness": ["money", "happiness", "well-being", "life satisfaction", "wealth", "quality of life"],
            "ngo_nonprofit": ["ngo", "nonprofit", "charity", "social sector", "foundation", "non-profit"],
            "philanthropy_impact": ["philanthropy", "donation", "giving", "social impact", "charitable", "impact investing"],
            "schemes_monitoring": ["scheme", "government scheme", "program", "initiative", "welfare"],
            "regulator_analysis": ["regulator", "regulatory body", "sec", "sebi", "rbi", "fda", "compliance authority"]
        }

        # Inter-agent communication context (A2A protocol)
        self.agent_context_sharing = {
            "business_model": ["market", "finance", "competitor", "industry_expert"],
            "stock_analysis": ["enhanced_news", "market", "finance", "hedge_fund"],
            "competitor": ["market", "business_model", "finance", "industry_expert"],
            "investment": ["finance", "market", "legal", "competitor", "hedge_fund", "mutual_fund"],
            "subsidies": ["policy", "tax", "finance", "loophole_predictor", "schemes_monitoring"],
            "loophole_predictor": ["tax", "legal", "policy"],
            "hedge_fund": ["stock_analysis", "enhanced_news", "market", "macroeconomics", "hft_analysis"],
            "mutual_fund": ["stock_analysis", "finance", "market"],
            "industry_expert": ["market", "competitor", "enhanced_news"],
            "enhanced_news": ["market", "stock_analysis", "competitor", "connecting_dots"],
            "macroeconomics": ["market", "finance", "policy", "international_markets"],
            "international_markets": ["market", "macroeconomics", "competitor", "policy"],
            "real_estate": ["finance", "market", "investment"],
            "marketing_strategy": ["market", "competitor", "business_strategy"],
            "business_strategy": ["market", "finance", "competitor", "marketing_strategy"],
            "connecting_dots": ["enhanced_news", "market", "competitor"],
            "hft_analysis": ["stock_analysis", "market", "hedge_fund"],
            "hr_analytics": ["finance", "human_behaviour"],
            "human_behaviour": ["market", "human_needs"],
            "human_needs": ["philosophy_ethics", "money_happiness"],
            "esg_environmental": ["policy", "philosophy_ethics"],
            "philosophy_ethics": ["human_needs", "money_happiness"],
            "money_happiness": ["finance", "human_needs"],
            "ngo_nonprofit": ["philanthropy_impact", "esg_environmental"],
            "philanthropy_impact": ["ngo_nonprofit", "finance"],
            "schemes_monitoring": ["subsidies", "policy", "regulator_analysis"],
            "regulator_analysis": ["policy", "legal", "schemes_monitoring"]
        }

        print(f"✓ Initialized {len(self.agents)} specialized agents")

    async def process_query(
        self,
        query: str,
        user_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user query with intelligent routing and multi-agent coordination

        Args:
            query: User's question or request
            user_context: User profile and context
            session_id: Session ID for conversation tracking

        Returns:
            Dict with answer, agent(s) used, sources, and metadata
        """
        start_time = datetime.now()

        try:
            # Step 1: Classify query and determine agent(s)
            agent_selection = await self._classify_and_route(query, user_context)

            primary_agent_name = agent_selection["primary_agent"]
            secondary_agents = agent_selection.get("secondary_agents", [])
            requires_multi_agent = agent_selection.get("multi_agent", False)

            print(f"Routing: Primary={primary_agent_name}, Secondary={secondary_agents}, Multi={requires_multi_agent}")

            # Step 2: Execute agent(s) with inter-agent communication
            if requires_multi_agent and secondary_agents:
                result = await self._execute_multi_agent(
                    query,
                    primary_agent_name,
                    secondary_agents,
                    user_context
                )
            else:
                result = await self._execute_single_agent(
                    query,
                    primary_agent_name,
                    user_context
                )

            # Step 3: Add execution metadata
            execution_time = (datetime.now() - start_time).total_seconds()
            result["execution_time_seconds"] = round(execution_time, 2)
            result["session_id"] = session_id
            result["timestamp"] = datetime.now().isoformat()

            return result

        except Exception as e:
            print(f"Error in EnhancedAgentOrchestrator: {e}")
            return {
                "answer": f"I apologize, but I encountered an error processing your request: {str(e)}",
                "primary_agent": "error_handler",
                "secondary_agents": [],
                "confidence": 0.5,
                "sources": [],
                "execution_time_seconds": (datetime.now() - start_time).total_seconds()
            }

    async def _classify_and_route(
        self,
        query: str,
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Classify query and determine which agent(s) to use

        Uses hybrid approach:
        1. LLM-based classification (primary)
        2. Keyword matching (fallback)
        """

        # Try LLM classification first
        try:
            classification_prompt = f"""Classify this user query and determine which AI agents should handle it.

User Query: "{query}"

Available Agents (35 total):
**Core Agents (8):**
1. policy - Government policies, regulations, compliance
2. market - Market analysis, industry trends, opportunities
3. finance - Financial analysis, budgeting, cash flow
4. tax - Tax optimization, deductions, filing
5. distribution - Distribution channels, go-to-market strategy
6. investment - Investment analysis, valuation, due diligence
7. legal - Contract review, legal compliance
8. news - Latest news, updates, current events

**Enhanced Agents - Phase 2 (12):**
9. business_model - Analyze existing business models (canvas analysis)
10. business_model_recommender - Recommend business models for ideas
11. stock_analysis - Stock market analysis, investment recommendations
12. competitor - Competitor intelligence, competitive analysis
13. subsidies - Government subsidies, grants, funding schemes
14. loophole_predictor - Tax and legal optimization strategies
15. hedge_fund - Hedge fund analysis, alternative investments
16. mutual_fund - Mutual fund comparison and recommendations
17. industry_expert - Deep industry knowledge across 50+ sectors
18. enhanced_news - Real-time news aggregation with sentiment analysis
19. macroeconomics - Macroeconomic analysis, GDP, inflation, monetary policy
20. international_markets - Global markets, international trade, emerging markets

**Enhanced Agents - Phase 3 (15):**
21. real_estate - Real estate investment analysis, REITs, property valuation
22. marketing_strategy - Marketing campaigns, brand strategy, customer acquisition
23. business_strategy - Strategic planning, growth strategy, competitive positioning
24. connecting_dots - Connect patterns in news, hidden insights, market intelligence
25. hft_analysis - High-frequency trading, algorithmic trading analysis
26. hr_analytics - HR, salary budgeting, compensation, workforce planning
27. human_behaviour - Consumer psychology, behavioral economics
28. human_needs - Human needs analysis, motivation, well-being
29. esg_environmental - ESG, sustainability, environmental impact
30. philosophy_ethics - Philosophy, ethics, moral principles
31. money_happiness - Relationship between money and happiness
32. ngo_nonprofit - NGO operations, nonprofit management
33. philanthropy_impact - Philanthropy, social impact, charitable giving
34. schemes_monitoring - Government schemes, welfare programs
35. regulator_analysis - Regulatory bodies, compliance authorities

Return JSON:
{{
    "primary_agent": "agent_name",
    "secondary_agents": ["agent1", "agent2"],  // if query needs multiple agents
    "multi_agent": true/false,  // true if requires coordination
    "confidence": 0.8,
    "reasoning": "why this routing"
}}

Choose the most relevant agent(s). For complex queries, use multi-agent approach.
"""

            response = await self.llm_service.generate(
                prompt=classification_prompt,
                model="gpt-4o",
                temperature=0.2,
                max_tokens=300
            )

            # Parse JSON response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                classification = json.loads(response[json_start:json_end])

                # Validate agent names
                if classification["primary_agent"] in self.agents:
                    return classification

        except Exception as e:
            print(f"LLM classification failed, using keyword matching: {e}")

        # Fallback to keyword matching
        return self._keyword_based_routing(query)

    def _keyword_based_routing(self, query: str) -> Dict[str, Any]:
        """Fallback keyword-based routing"""
        query_lower = query.lower()

        agent_scores = {}
        for agent_name, keywords in self.routing_keywords.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                agent_scores[agent_name] = score

        if not agent_scores:
            # Default to market agent for general business questions
            return {
                "primary_agent": "market",
                "secondary_agents": [],
                "multi_agent": False,
                "confidence": 0.5,
                "reasoning": "Default routing - no specific keywords matched"
            }

        # Sort by score
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)

        primary = sorted_agents[0][0]
        secondary = [agent for agent, _ in sorted_agents[1:3]] if len(sorted_agents) > 1 else []

        return {
            "primary_agent": primary,
            "secondary_agents": secondary,
            "multi_agent": len(secondary) > 0 and sorted_agents[0][1] == sorted_agents[1][1],
            "confidence": 0.7,
            "reasoning": f"Keyword matching - matched {sorted_agents[0][1]} keywords"
        }

    async def _execute_single_agent(
        self,
        query: str,
        agent_name: str,
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute single agent"""
        agent = self.agents.get(agent_name)

        if not agent:
            return {
                "answer": f"Agent '{agent_name}' not found.",
                "primary_agent": agent_name,
                "confidence": 0.0,
                "sources": []
            }

        result = await agent.process(query, user_context)

        return {
            "answer": result.get("answer", ""),
            "primary_agent": agent_name,
            "secondary_agents": [],
            "confidence": result.get("confidence", 0.7),
            "sources": result.get("sources", []),
            "agent_data": result  # Full agent response for detailed access
        }

    async def _execute_multi_agent(
        self,
        query: str,
        primary_agent_name: str,
        secondary_agent_names: List[str],
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute multiple agents with inter-agent communication

        This is the A2A (Agent-to-Agent) protocol implementation
        """
        print(f"Executing multi-agent: primary={primary_agent_name}, secondary={secondary_agent_names}")

        # Execute all agents in parallel
        tasks = []

        # Primary agent
        primary_agent = self.agents.get(primary_agent_name)
        if primary_agent:
            tasks.append(("primary", primary_agent.process(query, user_context)))

        # Secondary agents
        for agent_name in secondary_agent_names:
            agent = self.agents.get(agent_name)
            if agent:
                tasks.append((agent_name, agent.process(query, user_context)))

        # Execute all agents concurrently
        results = {}
        for agent_type, task in tasks:
            try:
                results[agent_type] = await task
            except Exception as e:
                print(f"Error executing {agent_type} agent: {e}")
                results[agent_type] = {
                    "answer": f"Error from {agent_type}: {str(e)}",
                    "confidence": 0.3,
                    "sources": []
                }

        # Synthesize responses from all agents
        synthesized_response = await self._synthesize_multi_agent_responses(
            query,
            primary_agent_name,
            results
        )

        return synthesized_response

    async def _synthesize_multi_agent_responses(
        self,
        query: str,
        primary_agent_name: str,
        agent_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesize responses from multiple agents into coherent answer"""

        # Collect all agent responses
        responses_text = []
        all_sources = []
        all_confidence = []

        primary_response = agent_results.get("primary", {})
        responses_text.append(f"**Primary Analysis ({primary_agent_name}):**\n{primary_response.get('answer', '')}")
        all_sources.extend(primary_response.get('sources', []))
        all_confidence.append(primary_response.get('confidence', 0.7))

        # Add secondary agent responses
        for agent_name, result in agent_results.items():
            if agent_name != "primary":
                responses_text.append(f"\n**Additional Insights ({agent_name}):**\n{result.get('answer', '')}")
                all_sources.extend(result.get('sources', []))
                all_confidence.append(result.get('confidence', 0.7))

        # Use LLM to synthesize into coherent response
        synthesis_prompt = f"""Synthesize these AI agent responses into a coherent, comprehensive answer.

User Query: "{query}"

Agent Responses:
{chr(10).join(responses_text)}

Create a unified response that:
1. Addresses the user's query directly
2. Integrates insights from all agents
3. Removes redundancy
4. Maintains logical flow
5. Highlights key takeaways

Provide a cohesive answer (not just concatenation).
"""

        try:
            synthesized = await self.llm_service.generate(
                prompt=synthesis_prompt,
                model="gpt-4o",
                temperature=0.3,
                max_tokens=2000
            )

            return {
                "answer": synthesized,
                "primary_agent": primary_agent_name,
                "secondary_agents": [name for name in agent_results.keys() if name != "primary"],
                "confidence": sum(all_confidence) / len(all_confidence) if all_confidence else 0.7,
                "sources": all_sources[:10],  # Top 10 sources
                "multi_agent": True,
                "agent_results": agent_results  # Keep individual results for reference
            }

        except Exception as e:
            print(f"Synthesis failed: {e}")
            # Fallback: return primary response with secondary appended
            combined_answer = "\n\n".join(responses_text)

            return {
                "answer": combined_answer,
                "primary_agent": primary_agent_name,
                "secondary_agents": [name for name in agent_results.keys() if name != "primary"],
                "confidence": sum(all_confidence) / len(all_confidence) if all_confidence else 0.7,
                "sources": all_sources[:10],
                "multi_agent": True
            }

    async def enable_agent_collaboration(
        self,
        requesting_agent: str,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enable inter-agent communication

        This allows agents to call each other for specialized information.
        Example: BusinessModelAgent can call MarketAgent for market data
        """
        allowed_collaborators = self.agent_context_sharing.get(requesting_agent, [])

        if not allowed_collaborators:
            return {"error": "Agent not configured for collaboration"}

        # Execute collaborating agents
        results = {}
        for agent_name in allowed_collaborators:
            agent = self.agents.get(agent_name)
            if agent:
                try:
                    result = await agent.process(query, context)
                    results[agent_name] = result
                except Exception as e:
                    print(f"Collaboration error with {agent_name}: {e}")

        return results


# Standalone test
async def main():
    """Test the Enhanced Agent Orchestrator"""
    orchestrator = EnhancedAgentOrchestrator()

    # Test 1: Single agent query
    print("\n" + "="*80)
    print("TEST 1: Single Agent Query (Subsidies)")
    print("="*80)
    result1 = await orchestrator.process_query(
        "What government subsidies are available for my tech startup in India?",
        user_context={"industry": "Technology", "country": "India"}
    )
    print(f"Primary Agent: {result1['primary_agent']}")
    print(f"Answer:\n{result1['answer'][:500]}...")

    # Test 2: Multi-agent query
    print("\n" + "="*80)
    print("TEST 2: Multi-Agent Query (Business Model + Market + Finance)")
    print("="*80)
    result2 = await orchestrator.process_query(
        "I want to build a SaaS platform for HR. Analyze the market, recommend a business model, and estimate financial projections.",
        user_context={"industry": "SaaS", "stage": "idea"}
    )
    print(f"Primary Agent: {result2['primary_agent']}")
    print(f"Secondary Agents: {result2.get('secondary_agents', [])}")
    print(f"Multi-Agent: {result2.get('multi_agent', False)}")
    print(f"Answer:\n{result2['answer'][:500]}...")

    # Test 3: Stock analysis
    print("\n" + "="*80)
    print("TEST 3: Stock Analysis")
    print("="*80)
    result3 = await orchestrator.process_query(
        "Should I invest in Apple and Microsoft stocks?",
        user_context={"risk_tolerance": "Moderate"}
    )
    print(f"Primary Agent: {result3['primary_agent']}")
    print(f"Answer:\n{result3['answer'][:500]}...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
