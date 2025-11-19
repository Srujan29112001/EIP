"""
Unit tests for Authentication API
"""
import pytest
from fastapi.testclient import TestClient


class TestAuthAPI:
    """Test suite for Authentication endpoints"""

    def test_register_new_user(self, api_client):
        """Test user registration"""
        response = api_client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "name": "New User",
                "password": "SecurePassword123!",
                "tier": "aspiring"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == "newuser@example.com"
        assert "hashed_password" not in data  # Should not expose password

    def test_register_duplicate_email(self, api_client, test_user_data):
        """Test registration with duplicate email"""
        # Register first user
        api_client.post("/api/v1/auth/register", json=test_user_data)

        # Try to register with same email
        response = api_client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, api_client):
        """Test registration with invalid email"""
        response = api_client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "name": "Test",
                "password": "Password123!",
                "tier": "mid"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_login_success(self, api_client, test_user_data, db_session):
        """Test successful login"""
        # First register
        api_client.post("/api/v1/auth/register", json=test_user_data)

        # Then login
        response = api_client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, api_client, test_user_data):
        """Test login with wrong password"""
        # Register user
        api_client.post("/api/v1/auth/register", json=test_user_data)

        # Try login with wrong password
        response = api_client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "WrongPassword123!"
            }
        )

        assert response.status_code == 401

    def test_login_nonexistent_user(self, api_client):
        """Test login with non-existent user"""
        response = api_client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "Password123!"
            }
        )

        assert response.status_code == 401

    def test_get_current_user(self, api_client, auth_headers):
        """Test getting current user info"""
        response = api_client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "name" in data
        assert "tier" in data

    def test_get_current_user_unauthorized(self, api_client):
        """Test getting user info without token"""
        response = api_client.get("/api/v1/auth/me")

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, api_client):
        """Test getting user info with invalid token"""
        response = api_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401
