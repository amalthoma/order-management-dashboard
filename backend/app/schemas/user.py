import uuid
from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr, Field, field_validator

class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr
    full_name: str

    @field_validator("email", mode="after")
    @classmethod
    def email_to_lower(cls, v: str) -> str:
        return v.lower()

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: Annotated[
        str,
        Field(
            min_length=8,
            max_length=128,
            description="Password must be at least 8 characters long."
        )
    ]

class UserResponse(UserBase):
    """Schema for returning user data."""
    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
