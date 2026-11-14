"""
Application DTOs: Authentication & User Profile
"""
from typing import Optional
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    full_name: str
    phone: Optional[str] = None
    shipping_address: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    full_name: str
    role: str


class UserProfileResponse(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str
    shipping_address: Optional[str] = None
    loyalty_points: int = 0
