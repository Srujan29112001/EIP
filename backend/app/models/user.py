"""
User database models
"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from .database import Base


class UserTier(str, enum.Enum):
    """User tier enumeration"""
    ASPIRING = "aspiring"
    MID_LEVEL = "mid"
    TOP_LEVEL = "top"


class User(Base):
    """User model for authentication and profile"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    tier = Column(SQLEnum(UserTier), default=UserTier.ASPIRING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(String, default=True)
    is_verified = Column(String, default=False)
    metadata = Column(JSON, default=dict)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, tier={self.tier})>"
