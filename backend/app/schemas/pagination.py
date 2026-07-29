from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class PaginationMeta(BaseModel):
    """Metadata for paginated responses."""
    page: int
    page_size: int
    total_records: int
    total_pages: int

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic wrapper for paginated lists of items."""
    items: list[T]
    pagination: PaginationMeta
