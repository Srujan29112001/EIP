"""
Pytest configuration and fixtures
Shared test utilities and setup
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app.core.config import settings
from backend.app.models.database import engine, Base, SessionLocal
from backend.app.core.security import create_access_token
import redis
from neo4j import GraphDatabase


# ===== Event Loop Fixture =====
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ===== Database Fixtures =====
@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine"""
    # Use test database
    test_db_url = settings.DATABASE_URL.replace("/eip_db", "/eip_test_db")
    engine = create_engine(test_db_url)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a new database session for a test"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ===== Redis Fixtures =====
@pytest.fixture(scope="session")
def redis_client():
    """Create Redis client for testing"""
    client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB + 1,  # Use different DB for testing
        decode_responses=True
    )
    yield client
    # Cleanup
    client.flushdb()
    client.close()


# ===== Neo4j Fixtures =====
@pytest.fixture(scope="session")
def neo4j_driver():
    """Create Neo4j driver for testing"""
    driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )
    yield driver
    # Cleanup test data
    with driver.session() as session:
        session.run("MATCH (n:Test) DETACH DELETE n")
    driver.close()


# ===== Authentication Fixtures =====
@pytest.fixture
def test_user_data():
    """Test user data"""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "TestPassword123!",
        "tier": "mid"
    }


@pytest.fixture
def test_access_token(test_user_data):
    """Create test access token"""
    return create_access_token(
        data={"sub": test_user_data["email"]},
        expires_delta=timedelta(minutes=30)
    )


@pytest.fixture
def auth_headers(test_access_token):
    """Create authentication headers"""
    return {"Authorization": f"Bearer {test_access_token}"}


# ===== API Client Fixtures =====
@pytest.fixture
def api_client():
    """Create test API client"""
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    return client


# ===== Mock Data Fixtures =====
@pytest.fixture
def mock_llm_response():
    """Mock LLM response"""
    return {
        "answer": "This is a test response from the AI agent.",
        "sources": ["source1", "source2"],
        "confidence": 0.95,
        "agent_used": "policy_agent"
    }


@pytest.fixture
def mock_document_data():
    """Mock document data for OCR testing"""
    return {
        "filename": "test_document.pdf",
        "content": b"Mock PDF content",
        "mime_type": "application/pdf"
    }


@pytest.fixture
def mock_market_data():
    """Mock market data"""
    return {
        "symbol": "AAPL",
        "price": 150.25,
        "volume": 1000000,
        "change_percent": 2.5,
        "timestamp": datetime.utcnow().isoformat()
    }


@pytest.fixture
def mock_policy_data():
    """Mock policy data"""
    return {
        "title": "Test Policy Update",
        "content": "This is a test policy content.",
        "category": "taxation",
        "effective_date": "2025-01-01",
        "source": "test_government_agency"
    }


# ===== Agent Fixtures =====
@pytest.fixture
def mock_agent_config():
    """Mock agent configuration"""
    from agents.base_agent import AgentConfig
    return AgentConfig(
        llm_provider="openai",
        llm_model="gpt-4o",
        temperature=0.7,
        max_tokens=4000,
        use_rag=False,  # Disable for faster testing
        use_graphrag=False
    )


# ===== Service Fixtures =====
@pytest.fixture
async def llm_service():
    """Create LLM service instance"""
    from backend.app.services.llm_service import LLMService, LLMProvider

    # Check if API key is available
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not available")

    service = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")
    return service


@pytest.fixture
async def rag_service():
    """Create RAG service instance"""
    from backend.app.services.rag_service import RAGService, VectorStoreType

    service = RAGService(
        vector_store_type=VectorStoreType.CHROMA,
        embedding_model="text-embedding-3-large"
    )
    return service


# ===== Cleanup Fixtures =====
@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test"""
    yield
    # Add any global cleanup here
    pass


# ===== Utility Functions =====
def create_test_user(db_session, user_data=None):
    """Helper function to create a test user"""
    from backend.app.models.user import User
    from backend.app.core.security import get_password_hash

    if user_data is None:
        user_data = {
            "email": f"test_{datetime.utcnow().timestamp()}@example.com",
            "name": "Test User",
            "password": "TestPassword123!",
            "tier": "mid"
        }

    user = User(
        email=user_data["email"],
        name=user_data["name"],
        hashed_password=get_password_hash(user_data["password"]),
        tier=user_data["tier"]
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ===== Markers =====
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "requires_api_keys: marks tests that require API keys"
    )
