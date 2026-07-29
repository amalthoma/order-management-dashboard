from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user
from app.services.dashboard_service import DashboardService
from app.models.user import User
from app.utils.responses import StandardResponse
from app.schemas.dashboard import DashboardFullResponse

router = APIRouter()

@router.get(
    "/",
    response_model=StandardResponse[DashboardFullResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Full Dashboard"
)
async def get_dashboard(
    limit: int = Query(default=10, ge=1, le=100, description="Limit for recent orders"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve the complete dashboard payload in a single request."""
    dashboard_service = DashboardService(db)
    result = await dashboard_service.get_full_dashboard(recent_orders_limit=limit)
    return StandardResponse(
        data=result,
        message="Dashboard retrieved successfully"
    )
