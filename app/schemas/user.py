import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    username: str = Field(..., min_length=3, max_length=50, description="User name")
    email: EmailStr = Field(..., description="User email address")

    @field_validator("username")
    def validate_username(cls, v):
        if not re.match(r"^[A-Za-z0-9_-]+$", v):
            raise ValueError(
                "Username may only contain letters, numbers, underscores, and hyphens."
            )
        return v


class UserResponse(BaseModel):
    """Schema for user response"""

    id: str
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
