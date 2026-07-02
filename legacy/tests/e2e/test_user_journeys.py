"""
End-to-end tests for user journeys
Tests the three main scenarios from the specification
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.e2e
class TestUserJourneys:
    """End-to-end tests for complete user journeys"""

    @pytest.mark.slow
    def test_aspiring_entrepreneur_journey(self, api_client):
        """
        Test Scenario 1: Aspiring Entrepreneur - Market Validation
        User: Sarah wants to start a sustainable fashion brand
        """
        # Step 1: Register
        response = api_client.post(
            "/api/v1/auth/register",
            json={
                "email": "sarah@example.com",
                "name": "Sarah",
                "password": "Password123!",
                "tier": "aspiring"
            }
        )
        assert response.status_code == 201

        # Step 2: Login
        login_response = api_client.post(
            "/api/v1/auth/login",
            json={"email": "sarah@example.com", "password": "Password123!"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Ask for market validation
        chat_response = api_client.post(
            "/api/v1/chat",
            headers=headers,
            json={
                "query": "I want to start a sustainable fashion brand targeting Gen Z in India. Is this viable?",
                "session_id": "sarah-session-1"
            }
        )

        assert chat_response.status_code == 200
        data = chat_response.json()
        assert "answer" in data
        assert "market" in data["agent_used"].lower()

        # Step 4: Follow-up question about distribution
        dist_response = api_client.post(
            "/api/v1/chat",
            headers=headers,
            json={
                "query": "How should I reach my customers?",
                "session_id": "sarah-session-1"
            }
        )

        assert dist_response.status_code == 200
        dist_data = dist_response.json()
        # Should suggest distribution strategies
        assert len(dist_data["answer"]) > 100

    @pytest.mark.slow
    def test_mid_level_entrepreneur_journey(self, api_client):
        """
        Test Scenario 2: Mid-Level Entrepreneur - Tax Optimization
        User: Raj runs a SaaS company with $2M revenue
        """
        # Step 1: Register
        api_client.post(
            "/api/v1/auth/register",
            json={
                "email": "raj@example.com",
                "name": "Raj",
                "password": "Password123!",
                "tier": "mid"
            }
        )

        # Step 2: Login
        login_response = api_client.post(
            "/api/v1/auth/login",
            json={"email": "raj@example.com", "password": "Password123!"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Upload P&L document (simulated)
        # Note: Document upload endpoint would be used here
        # For now, we test the chat interface

        # Step 4: Ask for tax optimization
        tax_response = api_client.post(
            "/api/v1/chat",
            headers=headers,
            json={
                "query": "My company made $2M revenue in FY24. How can I minimize tax liability legally?",
                "session_id": "raj-session-1"
            }
        )

        assert tax_response.status_code == 200
        data = tax_response.json()
        assert "tax" in data["agent_used"].lower()
        # Should provide tax optimization advice
        assert any(word in data["answer"].lower()
                  for word in ["deduction", "tax", "exemption"])

    @pytest.mark.slow
    def test_top_level_entrepreneur_journey(self, api_client):
        """
        Test Scenario 3: Top-Level Entrepreneur - M&A Advisory
        User: Priya considering acquisition of logistics company
        """
        # Step 1: Register
        api_client.post(
            "/api/v1/auth/register",
            json={
                "email": "priya@example.com",
                "name": "Priya",
                "password": "Password123!",
                "tier": "top"
            }
        )

        # Step 2: Login
        login_response = api_client.post(
            "/api/v1/auth/login",
            json={"email": "priya@example.com", "password": "Password123!"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Ask for M&A advice
        ma_response = api_client.post(
            "/api/v1/chat",
            headers=headers,
            json={
                "query": "I'm considering acquiring a logistics company valued at ₹150 Cr. What should I consider?",
                "session_id": "priya-session-1"
            }
        )

        assert ma_response.status_code == 200
        data = ma_response.json()
        assert "investment" in data["agent_used"].lower()
        # Should provide M&A advisory
        assert any(word in data["answer"].lower()
                  for word in ["valuation", "due diligence", "risk"])

        # Step 4: Follow-up on legal aspects
        legal_response = api_client.post(
            "/api/v1/chat",
            headers=headers,
            json={
                "query": "What legal aspects should I review?",
                "session_id": "priya-session-1"
            }
        )

        assert legal_response.status_code == 200
        # Should involve legal agent or provide legal advice
        assert len(legal_response.json()["answer"]) > 100

    @pytest.mark.slow
    def test_multi_session_interaction(self, api_client):
        """Test that users can have multiple independent sessions"""
        # Register and login
        api_client.post(
            "/api/v1/auth/register",
            json={
                "email": "multi@example.com",
                "name": "Multi",
                "password": "Password123!",
                "tier": "mid"
            }
        )

        login_response = api_client.post(
            "/api/v1/auth/login",
            json={"email": "multi@example.com", "password": "Password123!"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Session 1: Tax discussion
        api_client.post(
            "/api/v1/chat",
            headers=headers,
            json={"query": "Tax optimization advice", "session_id": "session-1"}
        )

        # Session 2: Market discussion (different topic)
        market_response = api_client.post(
            "/api/v1/chat",
            headers=headers,
            json={"query": "Market analysis for SaaS", "session_id": "session-2"}
        )

        # Sessions should be independent
        assert market_response.status_code == 200
