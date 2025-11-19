"""
Business and portfolio database models
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .database import Base


class Business(Base):
    """Business entity model"""
    __tablename__ = "businesses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    revenue_range = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metrics = Column(JSON, default=dict)

    def __repr__(self):
        return f"<Business(id={self.id}, name={self.name}, sector={self.sector})>"


class Portfolio(Base):
    """Investment portfolio model"""
    __tablename__ = "portfolios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    asset_name = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)  # stock, mutual_fund, startup, etc.
    value = Column(Numeric(15, 2), nullable=False)
    quantity = Column(Numeric(15, 4))
    allocation_pct = Column(Numeric(5, 2))
    purchase_date = Column(DateTime)
    purchase_price = Column(Numeric(15, 2))
    current_price = Column(Numeric(15, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default=dict)

    def __repr__(self):
        return f"<Portfolio(id={self.id}, asset={self.asset_name}, value={self.value})>"


class Query(Base):
    """User query history model"""
    __tablename__ = "queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    query_text = Column(String, nullable=False)
    agent_used = Column(String)
    response = Column(String)
    latency_ms = Column(Numeric(10, 2))
    tokens_used = Column(Numeric(10, 0))
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default=dict)

    def __repr__(self):
        return f"<Query(id={self.id}, agent={self.agent_used})>"
