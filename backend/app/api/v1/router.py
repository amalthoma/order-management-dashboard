from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.api.dependencies import get_db
from app.database.session import check_database_health
from app.core.settings import settings
from app.api.v1.endpoints import auth, orders, dashboard, ws, currency

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)
api_router.include_router(
    ws.router,
    prefix="/ws",
    tags=["Realtime"]
)
api_router.include_router(
    currency.router,
    prefix="/currency",
    tags=["Currency"]
)

@api_router.get("/health", response_model=dict, tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint."""
    is_db_healthy = await check_database_health()
    return {
        "status": "healthy" if is_db_healthy else "degraded",
        "version": settings.VERSION,
        "database": "connected" if is_db_healthy else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
