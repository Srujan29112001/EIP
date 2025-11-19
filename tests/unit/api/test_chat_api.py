"""
Unit tests for Chat API
"""
import pytest


class TestChatAPI:
    """Test suite for Chat endpoints"""

    def test_send_chat_message(self, api_client, auth_headers):
        """Test sending a chat message"""
        response = api_client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={
                "query": "What are the latest tax policies?",
                "session_id": "test-session-123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "agent_used" in data
        assert isinstance(data["answer"], str)

    def test_send_chat_message_unauthorized(self, api_client):
        """Test sending message without authentication"""
        response = api_client.post(
            "/api/v1/chat",
            json={"query": "Test query"}
        )

        assert response.status_code == 401

    def test_send_empty_query(self, api_client, auth_headers):
        """Test sending empty query"""
        response = api_client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"query": ""}
        )

        assert response.status_code == 422  # Validation error

    def test_agent_routing_policy_query(self, api_client, auth_headers):
        """Test that policy queries route to policy agent"""
        response = api_client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={
                "query": "What are the new tax policies for startups?",
                "session_id": "test-123"
            }
        )

        data = response.json()
        assert "agent_used" in data
        # Should route to tax or policy agent
        assert any(agent in data["agent_used"].lower()
                  for agent in ["tax", "policy"])

    def test_agent_routing_market_query(self, api_client, auth_headers):
        """Test that market queries route to market agent"""
        response = api_client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={
                "query": "What is the market opportunity for EV in India?",
                "session_id": "test-123"
            }
        )

        data = response.json()
        assert "market" in data["agent_used"].lower()

    def test_conversation_history(self, api_client, auth_headers):
        """Test conversation history persistence"""
        session_id = "test-session-456"

        # Send first message
        api_client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"query": "Tell me about tax policies", "session_id": session_id}
        )

        # Send follow-up
        response = api_client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"query": "Tell me more about that", "session_id": session_id}
        )

        # Should have context from previous message
        assert response.status_code == 200

    def test_rate_limiting(self, api_client, auth_headers):
        """Test API rate limiting"""
        # Send many requests quickly
        responses = []
        for i in range(150):  # More than rate limit (100/min)
            response = api_client.post(
                "/api/v1/chat",
                headers=auth_headers,
                json={"query": f"Test query {i}", "session_id": f"test-{i}"}
            )
            responses.append(response.status_code)

        # At least one should be rate limited
        assert 429 in responses  # Too Many Requests
