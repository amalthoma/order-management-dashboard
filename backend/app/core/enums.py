from enum import Enum

class OrderStatus(str, Enum):
    """Enumeration for order statuses."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
