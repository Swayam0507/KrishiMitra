# ─── AgriFlow AI — Auth Schemas ───────────────────────────────────────────────
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

VALID_ROLES = {"Farmer", "Manager", "Admin"}


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, description="Minimum 6 characters")
    role: str = Field(default="Farmer")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Rajesh Patel",
                "email": "rajesh@farm.com",
                "password": "securepass123",
                "role": "Farmer",
            }
        }
    }


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    createdAt: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
