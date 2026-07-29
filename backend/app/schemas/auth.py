from pydantic import BaseModel, EmailStr, field_validator

class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str

    @field_validator("email", mode="after")
    @classmethod
    def email_to_lower(cls, v: str) -> str:
        return v.lower()
