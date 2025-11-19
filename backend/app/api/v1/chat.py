"""
Chat/Query API routes
Main endpoint for AI agent interactions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
import time
import uuid

from ...models import get_db, get_redis, Query
from ...schemas.chat import ChatRequest, ChatResponse, Source
from ...core.security import get_current_user
from ...core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Process user query through AI agent system

    Args:
        request: Chat request with query
        current_user: Authenticated user
        db: Database session
        redis: Redis client

    Returns:
        AI-generated response with sources
    """
    start_time = time.time()
    user_id = current_user.get("sub")

    # Generate or use existing session ID
    session_id = request.session_id or uuid.uuid4()

    logger.info(f"Processing query for user {user_id}: {request.query[:100]}")

    # TODO: Implement agent orchestration
    # For now, return a mock response
    response_text = f"This is a mock response to: {request.query}. Agent system will be implemented next."
    agent_used = "mock_agent"

    # Calculate latency
    latency_ms = (time.time() - start_time) * 1000

    # Store query in database
    query_record = Query(
        user_id=user_id,
        session_id=session_id,
        query_text=request.query,
        agent_used=agent_used,
        response=response_text,
        latency_ms=latency_ms,
    )
    db.add(query_record)
    db.commit()
    db.refresh(query_record)

    # Store in Redis for session management
    session_key = f"session:{session_id}"
    redis.lpush(session_key, f"user: {request.query}")
    redis.lpush(session_key, f"assistant: {response_text}")
    redis.expire(session_key, 3600)  # 1 hour TTL

    # Prepare response
    response = ChatResponse(
        query_id=query_record.id,
        session_id=session_id,
        answer=response_text,
        agent_used=agent_used,
        sources=[
            Source(
                title="Mock Source",
                content="This is a mock source citation",
                url="https://example.com",
                relevance_score=0.95
            )
        ],
        latency_ms=latency_ms,
        tokens_used=100,
        timestamp=query_record.created_at
    )

    logger.info(f"Query processed in {latency_ms:.2f}ms")

    return response


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    current_user: Dict = Depends(get_current_user),
    redis = Depends(get_redis)
):
    """
    Retrieve chat history for a session

    Args:
        session_id: Session identifier
        current_user: Authenticated user
        redis: Redis client

    Returns:
        List of messages in the session
    """
    session_key = f"session:{session_id}"
    messages = redis.lrange(session_key, 0, -1)

    return {
        "session_id": session_id,
        "messages": [msg for msg in reversed(messages)]
    }


@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    current_user: Dict = Depends(get_current_user),
    redis = Depends(get_redis)
):
    """
    Clear chat history for a session

    Args:
        session_id: Session identifier
        current_user: Authenticated user
        redis: Redis client
    """
    session_key = f"session:{session_id}"
    redis.delete(session_key)

    return {"message": "Chat history cleared successfully"}
