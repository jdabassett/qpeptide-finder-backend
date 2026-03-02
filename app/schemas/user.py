from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    username: str = Field(..., min_length=3, max_length=50, description="User name")
    email: EmailStr | None = Field(default=None, description="User email address")

    @model_validator(mode="after")
    def require_email(self):
        if not self.email or (isinstance(self.email, str) and not self.email.strip()):
            raise ValueError(
                "Failed to login because user email address wasn't provided. Please try a different login type."
            )
        return self


class UserResponse(BaseModel):
    """Schema for user response"""

    id: str
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
