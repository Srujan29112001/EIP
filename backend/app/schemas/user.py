"""
Pydantic schemas for User models
"""
from pydantic import BaseModel, EmailStr, Field, UUID4
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class UserTierEnum(str, Enum):
    """User tier enumeration"""
    ASPIRING = "aspiring"
    MID_LEVEL = "mid"
    TOP_LEVEL = "top"


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: str


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8)
    tier: UserTierEnum = UserTierEnum.ASPIRING


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    name: Optional[str] = None
    tier: Optional[UserTierEnum] = None
    metadata: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: UUID4
    tier: UserTierEnum
    created_at: datetime
    is_active: bool
    is_verified: bool
    metadata: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[str] = None
    email: Optional[str] = None
