"""
Unit tests for Policy Agent
"""
import pytest
import asyncio
from agents.policy_agent.policy_agent import PolicyAgent
from agents.base_agent import AgentConfig


class TestPolicyAgent:
    """Test suite for Policy Agent"""

    @pytest.fixture
    def agent(self, mock_agent_config):
        """Create Policy Agent instance"""
        return PolicyAgent(config=mock_agent_config)

    def test_agent_initialization(self, agent):
        """Test that agent initializes correctly"""
        assert agent is not None
        assert agent.name == "PolicyAgent"
        assert agent.description is not None

    def test_get_system_prompt(self, agent):
        """Test system prompt generation"""
        prompt = agent.get_system_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "policy" in prompt.lower()

    @pytest.mark.asyncio
    async def test_process_query_basic(self, agent):
        """Test basic query processing"""
        query = "What are the latest tax policies for startups?"
        context = {"user_tier": "mid"}

        response = await agent.process(query, context)

        assert isinstance(response, dict)
        assert "answer" in response
        assert "sources" in response
        assert isinstance(response["answer"], str)
        assert len(response["answer"]) > 0

    @pytest.mark.asyncio
    async def test_process_query_with_context(self, agent):
        """Test query processing with user context"""
        query = "How does the new policy affect my business?"
        context = {
            "user_tier": "mid",
            "business_sector": "SaaS",
            "revenue_range": "$1M-5M"
        }

        response = await agent.process(query, context)

        assert response is not None
        assert "answer" in response

    @pytest.mark.asyncio
    async def test_process_empty_query(self, agent):
        """Test handling of empty query"""
        query = ""

        with pytest.raises(ValueError):
            await agent.process(query)

    @pytest.mark.asyncio
    async def test_agent_fallback_response(self, agent):
        """Test fallback response when LLM unavailable"""
        # Agent should return fallback when API key missing
        query = "Test policy query"
        response = await agent.process(query)

        assert response is not None
        assert "answer" in response
        # Fallback response should indicate limitation
        assert any(word in response["answer"].lower()
                  for word in ["fallback", "demo", "example"])
