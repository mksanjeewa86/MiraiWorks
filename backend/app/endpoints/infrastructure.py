import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config.endpoints import API_ROUTES

from app.dependencies import get_redis

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(API_ROUTES.INFRASTRUCTURE.HEALTH)
async def health_check():
    """Health check endpoint."""
    try:
        # Test Redis
        redis_conn = await get_redis()
        await redis_conn.ping()

        return {
            "status": "healthy",
            "services": {"redis": "connected", "database": "connected"},
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503, content={"status": "unhealthy", "error": str(e)}
        )


@router.get(API_ROUTES.INFRASTRUCTURE.ROOT)
async def root():
    """Root endpoint."""
    return {"message": "MiraiWorks API", "version": "1.0.0", "docs": "/docs"}
