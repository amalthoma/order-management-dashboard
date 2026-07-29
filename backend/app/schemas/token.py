from pydantic import BaseModel

class Token(BaseModel):
    """Schema for access token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenPayload(BaseModel):
    """Schema for token payload."""
    sub: str | None = None
