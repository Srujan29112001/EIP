"""
Integration tests for AI agents
Tests complete flow from query → agent → LLM → response
"""
import pytest
import asyncio
from agents.orchestrator.agent_orchestrator import AgentOrchestrator, AgentType
from backend.app.services.llm_service import LLMService
from backend.app.services.rag_service import RAGService
from backend.app.services.graphrag_service import GraphRAGService


class TestAgentIntegration:
    """Integration tests for agent system"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup test environment"""
        self.orchestrator = AgentOrchestrator()
        self.llm_service = LLMService()
        self.rag_service = RAGService()
        self.graphrag_service = GraphRAGService()

        yield

        # Cleanup
        if hasattr(self.rag_service, 'close'):
            await self.rag_service.close()
        if hasattr(self.graphrag_service, 'close'):
            await self.graphrag_service.close()

    @pytest.mark.asyncio
    async def test_policy_query_end_to_end(self):
        """Test policy-related query end-to-end"""
        query = "What are the latest startup tax incentives in India?"

        # Classify query
        agent_types = await self.orchestrator.classify_query(query)
        assert AgentType.POLICY in agent_types or AgentType.TAX in agent_types

        # Execute agents
        response = await self.orchestrator.execute(query)

        # Verify response
        assert response is not None
        assert len(response['answer']) > 0
        assert 'agent_used' in response
        assert response['confidence'] > 0

    @pytest.mark.asyncio
    async def test_market_analysis_query(self):
        """Test market analysis query"""
        query = "What are the growth opportunities in the SaaS market?"

        agent_types = await self.orchestrator.classify_query(query)
        assert AgentType.MARKET in agent_types

        response = await self.orchestrator.execute(query)

        assert response is not None
        assert 'market' in response['answer'].lower() or 'saas' in response['answer'].lower()
        assert isinstance(response['sources'], list)

    @pytest.mark.asyncio
    async def test_multi_agent_coordination(self):
        """Test multi-agent query requiring coordination"""
        query = "I'm starting a SaaS business. What are the tax implications and market opportunities?"

        agent_types = await self.orchestrator.classify_query(query)

        # Should involve multiple agents
        assert len(agent_types) >= 2

        response = await self.orchestrator.execute(query)

        assert response is not None
        assert len(response['answer']) > 100  # Substantial answer
        assert 'agents_used' in response or 'agent_used' in response

    @pytest.mark.asyncio
    async def test_rag_retrieval_integration(self):
        """Test RAG retrieval works with agents"""
        # Add test document to RAG
        test_doc = {
            "content": "Section 80IAC provides tax exemption for eligible startups for 3 consecutive years",
            "metadata": {"source": "Income Tax Act", "section": "80IAC"}
        }

        await self.rag_service.add_documents([test_doc], collection="policies")

        # Query should retrieve this document
        query = "Tax exemption for startups"
        response = await self.orchestrator.execute(query)

        assert response is not None
        # Should mention Section 80IAC or tax exemption
        assert '80iac' in response['answer'].lower() or 'exemption' in response['answer'].lower()

    @pytest.mark.asyncio
    async def test_graphrag_integration(self):
        """Test GraphRAG integration with agents"""
        # Add test nodes to graph
        await self.graphrag_service.add_node(
            "Policy",
            {"title": "Startup India Initiative", "type": "incentive"}
        )

        # Query should use graph
        query = "Tell me about Startup India"
        response = await self.orchestrator.execute(query)

        assert response is not None
        assert len(response['answer']) > 0

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test graceful error handling"""
        # Invalid/malformed query
        query = ""

        response = await self.orchestrator.execute(query)

        # Should handle gracefully
        assert response is not None
        assert 'error' in response or len(response.get('answer', '')) > 0

    @pytest.mark.asyncio
    async def test_llm_fallback(self):
        """Test LLM fallback when RAG/GraphRAG unavailable"""
        # Query without retrievable context
        query = "What is entrepreneurship?"

        response = await self.orchestrator.execute(query)

        # Should still return LLM-generated response
        assert response is not None
        assert len(response['answer']) > 0
        assert 'entrepreneur' in response['answer'].lower()

    @pytest.mark.asyncio
    async def test_response_quality(self):
        """Test response quality metrics"""
        query = "How can I optimize my startup's cash flow?"

        response = await self.orchestrator.execute(query)

        assert response is not None

        # Check response completeness
        assert len(response['answer']) >= 100  # Minimum length for quality answer
        assert response['confidence'] >= 0.3  # Reasonable confidence

        # Check for actionable content
        answer_lower = response['answer'].lower()
        assert any(word in answer_lower for word in ['recommend', 'suggest', 'should', 'can', 'optimize'])

    @pytest.mark.asyncio
    async def test_concurrent_queries(self):
        """Test handling concurrent queries"""
        queries = [
            "Tax deductions for startups",
            "Market size for SaaS",
            "Investment strategies",
            "Legal requirements for incorporation"
        ]

        # Execute concurrently
        tasks = [self.orchestrator.execute(q) for q in queries]
        responses = await asyncio.gather(*tasks)

        # All should succeed
        assert len(responses) == len(queries)
        for response in responses:
            assert response is not None
            assert len(response['answer']) > 0

    @pytest.mark.asyncio
    async def test_agent_memory_persistence(self):
        """Test conversation memory across multiple queries"""
        session_id = "test_session_123"

        # First query
        query1 = "I run a SaaS business"
        response1 = await self.orchestrator.execute(query1, session_id=session_id)

        # Follow-up query
        query2 = "What tax deductions am I eligible for?"
        response2 = await self.orchestrator.execute(query2, session_id=session_id)

        # Second response should consider context from first
        assert response2 is not None
        # Should mention SaaS or tech-related deductions
        assert 'saas' in response2['answer'].lower() or 'software' in response2['answer'].lower() or 'technology' in response2['answer'].lower()


@pytest.mark.slow
class TestAgentPerformance:
    """Performance tests for agents"""

    @pytest.mark.asyncio
    async def test_response_time(self):
        """Test agent response time is acceptable"""
        import time

        orchestrator = AgentOrchestrator()
        query = "What are startup funding options?"

        start = time.time()
        response = await orchestrator.execute(query)
        duration = time.time() - start

        assert response is not None
        # Should respond within 10 seconds
        assert duration < 10.0

    @pytest.mark.asyncio
    async def test_throughput(self):
        """Test system can handle multiple queries"""
        orchestrator = AgentOrchestrator()
        queries = [f"Query {i}" for i in range(10)]

        import time
        start = time.time()

        tasks = [orchestrator.execute(q) for q in queries]
        responses = await asyncio.gather(*tasks)

        duration = time.time() - start

        # Should handle 10 queries in reasonable time
        assert len(responses) == 10
        assert duration < 30.0  # 3 seconds per query on average
