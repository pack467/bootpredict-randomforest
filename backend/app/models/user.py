"""
User Model
==========
Pydantic models for user-related request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserLogin(BaseModel):
    """Schema for login request."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=4, max_length=100, description="Password")


class UserRegister(BaseModel):
    """Schema for registration request."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=4, max_length=100, description="Password")


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: int
    username: str
    role: str
    created_at: Optional[str] = None


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
