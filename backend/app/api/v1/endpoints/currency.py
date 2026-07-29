from decimal import Decimal
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
    """Retrieve exchange rate."""
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
    """Convert currency amount."""
    currency_service = CurrencyService()
    result = await currency_service.convert_currency(base, target, amount)
    return StandardResponse(
        data=result,
        message="Currency converted successfully"
    )
