from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.settings import settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import setup_exception_handlers
from app.middleware.cors import setup_cors
from app.middleware.logging import RequestResponseLoggingMiddleware
from app.api.v1.router import api_router
from app.database.session import engine

setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")
    await engine.dispose()

def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        lifespan=lifespan,
    )
    
    setup_cors(app)
    app.add_middleware(RequestResponseLoggingMiddleware)
    setup_exception_handlers(app)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    
    return app

app = create_app()
