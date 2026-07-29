import logging
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException, status
from app.integrations.currency_client import CurrencyClient
from app.schemas.currency import CurrencyRateResponse, CurrencyConvertResponse

logger = logging.getLogger(__name__)

class CurrencyService:
    """Service layer for currency exchange and conversion operations."""
    
    def __init__(self):
        self.client = CurrencyClient()
        
    async def get_exchange_rate(self, base: str, target: str) -> CurrencyRateResponse:
        """
        Retrieves the exchange rate between two currencies.
        
        Args:
            base (str): Base currency code.
            target (str): Target currency code.
            
        Returns:
            CurrencyRateResponse: The exchange rate data.
            
        Raises:
            HTTPException: If the target currency is not found in the rates.
        """
        base = base.upper()
        target = target.upper()
        
        if len(base) != 3 or len(target) != 3:
            logger.warning(f"Invalid currency code length: base={base}, target={target}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Currency codes must be exactly 3 characters long."
            )
        
        logger.info(f"Currency rate requested: {base} to {target}")
        
        data = await self.client.get_latest_rates(base)
        
        rates = data.get("rates", {})
        if target not in rates:
            logger.warning(f"Target currency {target} not found for base {base}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported target currency: {target}"
            )
            
        rate = Decimal(str(rates[target]))
        last_updated = data.get("time_last_update_utc", "Unknown")
        
        return CurrencyRateResponse(
            base=base,
            target=target,
            rate=rate,
            last_updated=last_updated
        )
        
    async def convert_currency(self, base: str, target: str, amount: Decimal) -> CurrencyConvertResponse:
        """
        Converts an amount from a base currency to a target currency.
        
        Args:
            base (str): Base currency code.
            target (str): Target currency code.
            amount (Decimal): Amount to convert.
            
        Returns:
            CurrencyConvertResponse: The conversion result.
            
        Raises:
            HTTPException: If the amount is invalid.
        """
        if amount <= 0:
            logger.warning(f"Invalid conversion amount: {amount}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than zero."
            )
            
        logger.info(f"Currency conversion requested: {amount} {base.upper()} to {target.upper()}")
        
        rate_response = await self.get_exchange_rate(base, target)
        
        # Calculate and round to 2 decimal places
        converted_amount = (amount * rate_response.rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        return CurrencyConvertResponse(
            base=rate_response.base,
            target=rate_response.target,
            amount=amount,
            converted_amount=converted_amount,
            rate=rate_response.rate,
            last_updated=rate_response.last_updated
        )
