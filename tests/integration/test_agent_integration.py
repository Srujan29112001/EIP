"""
Integration tests for multi-agent system
"""
import pytest
from agents.orchestrator.agent_orchestrator import AgentOrchestrator


@pytest.mark.integration
class TestAgentIntegration:
    """Test suite for agent integration"""

    @pytest.fixture
    def orchestrator(self):
        """Create agent orchestrator"""
        return AgentOrchestrator()

    @pytest.mark.asyncio
    async def test_multi_agent_coordination(self, orchestrator):
        """Test coordination between multiple agents"""
        query = "I need market analysis and tax optimization advice for my startup"

        response = await orchestrator.process_query(
            query=query,
            context={"user_tier": "mid", "business_sector": "SaaS"}
        )

        assert response is not None
        assert "agents_used" in response
        # Should involve multiple agents
        assert len(response["agents_used"]) >= 2

    @pytest.mark.asyncio
    async def test_agent_rag_integration(self, orchestrator):
        """Test agent integration with RAG system"""
        # Query that requires knowledge retrieval
        query = "What are the specific tax deductions available for SaaS companies?"

        response = await orchestrator.process_query(query)

        assert "answer" in response
        if "sources" in response:
            assert isinstance(response["sources"], list)

    @pytest.mark.asyncio
    async def test_agent_graphrag_integration(self, orchestrator):
        """Test agent integration with GraphRAG"""
        query = "How do recent policy changes affect tech startups?"

        response = await orchestrator.process_query(
            query=query,
            use_graphrag=True
        )

        assert response is not None
        assert "answer" in response

    @pytest.mark.asyncio
    async def test_context_preservation_across_agents(self, orchestrator):
        """Test that context is preserved when multiple agents are used"""
        context = {
            "user_tier": "top",
            "business_sector": "E-commerce",
            "revenue": "$10M"
        }

        query = "Provide market analysis and investment recommendations"

        response = await orchestrator.process_query(query, context)

        assert response is not None
        # Response should consider the context
        assert "answer" in response
