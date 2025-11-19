"""
Agent Orchestrator
Routes queries to appropriate specialized agents and coordinates responses
"""
from typing import Dict, List, Any, Optional
from enum import Enum
import asyncio
from dataclasses import dataclass


class AgentType(str, Enum):
    """Available agent types"""
    POLICY = "policy"
    MARKET = "market"
    FINANCE = "finance"
    TAX = "tax"
    DISTRIBUTION = "distribution"
    INVESTMENT = "investment"
    LEGAL = "legal"
    NEWS = "news"


@dataclass
class AgentResponse:
    """Standard response format from agents"""
    agent_type: AgentType
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    metadata: Dict[str, Any]


class AgentOrchestrator:
    """
    Main orchestrator for multi-agent system
    Uses LangChain and DSPy for agent coordination
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the orchestrator

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.agents = {}
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all specialized agents"""
        # Import all agent classes
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))

        try:
            from ..policy_agent.policy_agent import PolicyAgent
            from ..market_agent.market_agent import MarketAgent
            from ..finance_agent.finance_agent import FinanceAgent
            from ..tax_agent.tax_agent import TaxAgent
            from ..distribution_agent.distribution_agent import DistributionAgent
            from ..investment_agent.investment_agent import InvestmentAgent
            from ..legal_agent.legal_agent import LegalAgent
            from ..news_agent.news_agent import NewsAgent

            # Initialize each agent
            self.agents[AgentType.POLICY] = PolicyAgent()
            self.agents[AgentType.MARKET] = MarketAgent()
            self.agents[AgentType.FINANCE] = FinanceAgent()
            self.agents[AgentType.TAX] = TaxAgent()
            self.agents[AgentType.DISTRIBUTION] = DistributionAgent()
            self.agents[AgentType.INVESTMENT] = InvestmentAgent()
            self.agents[AgentType.LEGAL] = LegalAgent()
            self.agents[AgentType.NEWS] = NewsAgent()

            print(f"✓ Successfully initialized {len(self.agents)} specialized agents")
        except Exception as e:
            print(f"⚠ Warning: Could not initialize all agents: {e}")
            # Fallback: register None for each type
            for agent_type in AgentType:
                if agent_type not in self.agents:
                    self.agents[agent_type] = None

    async def classify_query(self, query: str) -> List[AgentType]:
        """
        Classify user query and determine which agents should handle it
        Uses LLM for intelligent classification with fallback to keyword matching

        Args:
            query: User query string

        Returns:
            List of agent types that should process the query
        """
        try:
            # Try LLM-based classification first
            return await self._llm_classify_query(query)
        except Exception as e:
            print(f"⚠ LLM classification failed: {e}. Using keyword fallback.")
            return self._keyword_classify_query(query)

    async def _llm_classify_query(self, query: str) -> List[AgentType]:
        """Use LLM to intelligently classify query"""
        from ..base_agent import AgentConfig
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
        from services.llm_service import LLMService, LLMProvider

        llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

        classification_prompt = f"""Classify this business query to determine which specialized agents should handle it.

Available Agents:
- POLICY: Government policies, regulations, compliance, laws
- MARKET: Market analysis, competitors, industry trends, customer insights
- FINANCE: Financial analysis, budgeting, revenue, profit, cash flow
- TAX: Tax optimization, deductions, filing, exemptions
- DISTRIBUTION: Marketing, customer acquisition, sales channels, distribution strategy
- INVESTMENT: Investment analysis, funding, valuation, M&A, due diligence
- LEGAL: Legal matters, contracts, agreements, lawsuits
- NEWS: Latest news, recent updates, current events

User Query: "{query}"

Return ONLY a comma-separated list of agent types (e.g., "MARKET,FINANCE" or "POLICY,LEGAL").
If multiple agents are relevant, list all. If unsure, default to MARKET.
"""

        response = await llm.generate(
            prompt=classification_prompt,
            temperature=0.3,
            max_tokens=50
        )

        # Parse response
        agent_names = [name.strip().upper() for name in response.strip().split(',')]
        selected_agents = []

        for name in agent_names:
            try:
                agent_type = AgentType(name.lower())
                selected_agents.append(agent_type)
            except ValueError:
                continue

        # Ensure at least one agent
        if not selected_agents:
            selected_agents = [AgentType.MARKET]

        return selected_agents

    def _keyword_classify_query(self, query: str) -> List[AgentType]:
        """Fallback keyword-based classification"""
        query_lower = query.lower()
        selected_agents = []

        # Policy-related keywords
        if any(word in query_lower for word in ["policy", "regulation", "compliance", "government", "law"]):
            selected_agents.append(AgentType.POLICY)

        # Market-related keywords
        if any(word in query_lower for word in ["market", "competitor", "industry", "trend", "customer"]):
            selected_agents.append(AgentType.MARKET)

        # Finance-related keywords
        if any(word in query_lower for word in ["finance", "budget", "revenue", "profit", "cash flow"]):
            selected_agents.append(AgentType.FINANCE)

        # Tax-related keywords
        if any(word in query_lower for word in ["tax", "deduction", "filing", "exemption"]):
            selected_agents.append(AgentType.TAX)

        # Distribution-related keywords
        if any(word in query_lower for word in ["distribution", "marketing", "customer acquisition", "sales channel"]):
            selected_agents.append(AgentType.DISTRIBUTION)

        # Investment-related keywords
        if any(word in query_lower for word in ["investment", "investor", "funding", "valuation", "acquisition", "m&a"]):
            selected_agents.append(AgentType.INVESTMENT)

        # Legal-related keywords
        if any(word in query_lower for word in ["legal", "contract", "agreement", "lawsuit"]):
            selected_agents.append(AgentType.LEGAL)

        # News-related keywords
        if any(word in query_lower for word in ["news", "update", "recent", "latest"]):
            selected_agents.append(AgentType.NEWS)

        # Default to market agent if no specific match
        if not selected_agents:
            selected_agents.append(AgentType.MARKET)

        return selected_agents

    async def process_query(
        self,
        query: str,
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process user query through appropriate agents

        Args:
            query: User query string
            user_context: Optional user context (tier, business info, etc.)

        Returns:
            Synthesized response from agents
        """
        # Classify query
        selected_agents = await self.classify_query(query)

        # Execute agents in parallel
        agent_responses = await self._execute_agents(query, selected_agents, user_context)

        # Synthesize responses
        final_response = await self._synthesize_responses(query, agent_responses)

        return final_response

    async def _execute_agents(
        self,
        query: str,
        agents: List[AgentType],
        context: Optional[Dict] = None
    ) -> List[AgentResponse]:
        """
        Execute multiple agents in parallel

        Args:
            query: User query
            agents: List of agents to execute
            context: User context

        Returns:
            List of agent responses
        """
        tasks = []
        for agent_type in agents:
            task = self._execute_single_agent(query, agent_type, context)
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return responses

    async def _execute_single_agent(
        self,
        query: str,
        agent_type: AgentType,
        context: Optional[Dict] = None
    ) -> AgentResponse:
        """
        Execute a single agent with actual implementation

        Args:
            query: User query
            agent_type: Type of agent to execute
            context: User context

        Returns:
            Agent response
        """
        import time
        start_time = time.time()

        try:
            # Get the agent instance
            agent = self.agents.get(agent_type)

            if agent is None:
                # Agent not initialized - return fallback
                return AgentResponse(
                    agent_type=agent_type,
                    answer=f"The {agent_type.value} agent is currently unavailable. Please try again later.",
                    sources=[],
                    confidence=0.0,
                    metadata={"error": "Agent not initialized"}
                )

            # Execute the agent
            response = await agent.process(query, context)

            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Format as AgentResponse
            return AgentResponse(
                agent_type=agent_type,
                answer=response.get("answer", ""),
                sources=response.get("sources", []),
                confidence=response.get("confidence", 0.8),
                metadata={
                    "execution_time_ms": execution_time_ms,
                    **response.get("metadata", {})
                }
            )

        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            print(f"Error executing {agent_type.value} agent: {e}")

            return AgentResponse(
                agent_type=agent_type,
                answer=f"An error occurred while processing your request with the {agent_type.value} agent. Please try again.",
                sources=[],
                confidence=0.0,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "error": str(e)
                }
            )

    async def _synthesize_responses(
        self,
        query: str,
        responses: List[AgentResponse]
    ) -> Dict[str, Any]:
        """
        Synthesize multiple agent responses into a coherent answer using LLM

        Args:
            query: Original user query
            responses: List of agent responses

        Returns:
            Synthesized response
        """
        # If only one response, return it directly
        if len(responses) == 1:
            response = responses[0]
            return {
                "answer": response.answer,
                "primary_agent": response.agent_type.value,
                "agents_consulted": [response.agent_type.value],
                "sources": response.sources,
                "confidence": response.confidence,
            }

        # Try LLM synthesis for multiple responses
        try:
            return await self._llm_synthesize_responses(query, responses)
        except Exception as e:
            print(f"⚠ LLM synthesis failed: {e}. Using fallback.")
            return self._fallback_synthesize_responses(query, responses)

    async def _llm_synthesize_responses(
        self,
        query: str,
        responses: List[AgentResponse]
    ) -> Dict[str, Any]:
        """Use LLM to intelligently synthesize multiple agent responses"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
        from services.llm_service import LLMService, LLMProvider

        llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

        # Build synthesis prompt
        agent_insights = []
        for response in responses:
            agent_insights.append(f"""
**{response.agent_type.value.upper()} AGENT:**
{response.answer}
""")

        synthesis_prompt = f"""You are synthesizing insights from multiple specialized business advisory agents.

Original Question: "{query}"

Insights from Different Agents:
{"".join(agent_insights)}

Your task: Synthesize these insights into a single, coherent, comprehensive answer that:
1. Addresses the original question directly
2. Combines complementary insights from different agents
3. Highlights any conflicting viewpoints (if any)
4. Provides actionable recommendations
5. Maintains a professional, helpful tone

Synthesized Answer:"""

        synthesized_answer = await llm.generate(
            prompt=synthesis_prompt,
            temperature=0.7,
            max_tokens=2000
        )

        # Combine sources from all agents
        all_sources = []
        for response in responses:
            all_sources.extend(response.sources)

        # Remove duplicates and take top sources
        unique_sources = []
        seen_urls = set()
        for source in all_sources:
            url = source.get('url', '')
            if url and url not in seen_urls:
                unique_sources.append(source)
                seen_urls.add(url)
            elif not url:
                unique_sources.append(source)

        # Calculate average confidence
        avg_confidence = sum(r.confidence for r in responses) / len(responses)

        return {
            "answer": synthesized_answer,
            "primary_agent": max(responses, key=lambda r: r.confidence).agent_type.value,
            "agents_consulted": [r.agent_type.value for r in responses],
            "sources": unique_sources[:10],  # Top 10 unique sources
            "confidence": avg_confidence,
            "synthesis_method": "llm"
        }

    def _fallback_synthesize_responses(
        self,
        query: str,
        responses: List[AgentResponse]
    ) -> Dict[str, Any]:
        """Fallback synthesis without LLM"""
        # Pick primary agent (highest confidence)
        primary_response = max(responses, key=lambda r: r.confidence)

        # Combine all answers
        combined_answer = f"**Primary Insight ({primary_response.agent_type.value}):**\n{primary_response.answer}\n\n"

        # Add other insights
        other_responses = [r for r in responses if r.agent_type != primary_response.agent_type]
        if other_responses:
            combined_answer += "**Additional Insights:**\n\n"
            for response in other_responses:
                combined_answer += f"**From {response.agent_type.value}:** {response.answer[:200]}...\n\n"

        # Combine sources from all agents
        all_sources = []
        for response in responses:
            all_sources.extend(response.sources)

        # Create synthesized response
        return {
            "answer": combined_answer,
            "primary_agent": primary_response.agent_type.value,
            "agents_consulted": [r.agent_type.value for r in responses],
            "sources": all_sources[:10],
            "confidence": primary_response.confidence,
            "synthesis_method": "fallback"
        }
