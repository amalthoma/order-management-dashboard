from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    """Standard API response format."""
    success: bool = True
    data: Optional[T] = None
    message: str = "Success"
    error: Optional[Any] = None
