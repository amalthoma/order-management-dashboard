import os

base_dir = r"C:\Users\Amal Thomas\.gemini\antigravity\scratch\order_management"

files = {
    "backend/app/integrations/__init__.py": '"""External API Integrations."""\n',
    "backend/app/integrations/currency_client.py": """import logging
import httpx
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class CurrencyClient:
    \"\"\"Client for interacting with the external Currency Exchange API.\"\"\"
    
    BASE_URL = "https://open.er-api.com/v6/latest/{base}"
    
    async def get_latest_rates(self, base: str) -> dict:
        \"\"\"
        Fetches the latest currency exchange rates for a given base currency.
        
        Args:
            base (str): The base currency code.
            
        Returns:
            dict: The JSON response containing the rates.
            
        Raises:
            HTTPException: If the external API fails (502 Bad Gateway).
        \"\"\"
        url = self.BASE_URL.format(base=base.upper())
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException as e:
            logger.error(f"Currency API timeout for base {base}: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Currency exchange service timeout."
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Currency API HTTP error for base {base}: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Currency exchange service returned an error."
            )
        except httpx.RequestError as e:
            logger.error(f"Currency API request error for base {base}: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to connect to currency exchange service."
            )
        except Exception as e:
            logger.error(f"Unexpected error calling Currency API: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="An unexpected error occurred while fetching exchange rates."
            )
""",
    "backend/app/schemas/currency.py": """from decimal import Decimal
from pydantic import BaseModel, Field

class CurrencyRateResponse(BaseModel):
    \"\"\"Schema for returning a single exchange rate.\"\"\"
    base: str = Field(..., description="Base currency code")
    target: str = Field(..., description="Target currency code")
    rate: Decimal = Field(..., description="Exchange rate")
    last_updated: str = Field(..., description="Last update timestamp from provider")

class CurrencyConvertResponse(BaseModel):
    \"\"\"Schema for returning a currency conversion result.\"\"\"
    base: str = Field(..., description="Base currency code")
    target: str = Field(..., description="Target currency code")
    amount: Decimal = Field(..., description="Original amount")
    converted_amount: Decimal = Field(..., description="Converted amount")
    rate: Decimal = Field(..., description="Exchange rate used")
    last_updated: str = Field(..., description="Last update timestamp from provider")
""",
    "backend/app/services/currency_service.py": """import logging
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException, status
from app.integrations.currency_client import CurrencyClient
from app.schemas.currency import CurrencyRateResponse, CurrencyConvertResponse

logger = logging.getLogger(__name__)

class CurrencyService:
    \"\"\"Service layer for currency exchange and conversion operations.\"\"\"
    
    def __init__(self):
        self.client = CurrencyClient()
        
    async def get_exchange_rate(self, base: str, target: str) -> CurrencyRateResponse:
        \"\"\"
        Retrieves the exchange rate between two currencies.
        
        Args:
            base (str): Base currency code.
            target (str): Target currency code.
            
        Returns:
            CurrencyRateResponse: The exchange rate data.
            
        Raises:
            HTTPException: If the target currency is not found in the rates.
        \"\"\"
        base = base.upper()
        target = target.upper()
        
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
        \"\"\"
        Converts an amount from a base currency to a target currency.
        
        Args:
            base (str): Base currency code.
            target (str): Target currency code.
            amount (Decimal): Amount to convert.
            
        Returns:
            CurrencyConvertResponse: The conversion result.
            
        Raises:
            HTTPException: If the amount is invalid.
        \"\"\"
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
""",
    "backend/app/api/v1/endpoints/currency.py": """from decimal import Decimal
from fastapi import APIRouter, Depends, Query, status
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.currency_service import CurrencyService
from app.schemas.currency import CurrencyRateResponse, CurrencyConvertResponse
from app.utils.responses import StandardResponse

router = APIRouter()

@router.get(
    "/rate",
    response_model=StandardResponse[CurrencyRateResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Exchange Rate",
    description="Retrieve the current exchange rate from a base currency to a target currency."
)
async def get_rate(
    base: str = Query(..., description="Base currency code (e.g., USD)"),
    target: str = Query(..., description="Target currency code (e.g., INR)"),
    current_user: User = Depends(get_current_user)
):
    \"\"\"Retrieve exchange rate.\"\"\"
    currency_service = CurrencyService()
    result = await currency_service.get_exchange_rate(base, target)
    return StandardResponse(
        data=result,
        message="Exchange rate retrieved successfully"
    )

@router.get(
    "/convert",
    response_model=StandardResponse[CurrencyConvertResponse],
    status_code=status.HTTP_200_OK,
    summary="Convert Currency",
    description="Convert a specific amount from a base currency to a target currency using current exchange rates."
)
async def convert_currency(
    base: str = Query(..., description="Base currency code (e.g., USD)"),
    target: str = Query(..., description="Target currency code (e.g., INR)"),
    amount: Decimal = Query(..., gt=0, description="Amount to convert"),
    current_user: User = Depends(get_current_user)
):
    \"\"\"Convert currency amount.\"\"\"
    currency_service = CurrencyService()
    result = await currency_service.convert_currency(base, target, amount)
    return StandardResponse(
        data=result,
        message="Currency converted successfully"
    )
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path.replace('/', os.sep))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Currency modules successfully generated.")
