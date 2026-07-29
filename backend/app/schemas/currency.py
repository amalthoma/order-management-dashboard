from decimal import Decimal
from pydantic import BaseModel, Field

class CurrencyRateResponse(BaseModel):
    """Schema for returning a single exchange rate."""
    base: str = Field(..., description="Base currency code")
    target: str = Field(..., description="Target currency code")
    rate: Decimal = Field(..., description="Exchange rate")
    last_updated: str = Field(..., description="Last update timestamp from provider")

class CurrencyConvertResponse(BaseModel):
    """Schema for returning a currency conversion result."""
    base: str = Field(..., description="Base currency code")
    target: str = Field(..., description="Target currency code")
    amount: Decimal = Field(..., description="Original amount")
    converted_amount: Decimal = Field(..., description="Converted amount")
    rate: Decimal = Field(..., description="Exchange rate used")
    last_updated: str = Field(..., description="Last update timestamp from provider")
