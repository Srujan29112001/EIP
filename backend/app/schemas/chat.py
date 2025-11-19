"""
Pydantic schemas for Chat/Query models
"""
from pydantic import BaseModel, Field, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat/Query request schema"""
    query: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[UUID4] = None
    context: Optional[Dict[str, Any]] = None
    agent_preference: Optional[str] = None


class Source(BaseModel):
    """Source citation for response"""
    title: str
    content: str
    url: Optional[str] = None
    relevance_score: Optional[float] = None


class ChatResponse(BaseModel):
    """Chat/Query response schema"""
    query_id: UUID4
    session_id: UUID4
    answer: str
    agent_used: str
    sources: List[Source] = []
    confidence_score: Optional[float] = None
    latency_ms: float
    tokens_used: Optional[int] = None
    timestamp: datetime


class ConversationHistory(BaseModel):
    """Conversation history schema"""
    session_id: UUID4
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
