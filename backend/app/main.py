import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.dependencies import get_redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting MiraiWorks API...")

    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")

        # Test Redis connection
        redis_conn = await get_redis()
        await redis_conn.ping()
        logger.info("Redis connection established")

        # TODO: Initialize other services (MinIO, ClamAV check, etc.)

        logger.info("MiraiWorks API started successfully")
        yield

    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

    # Shutdown
    logger.info("Shutting down MiraiWorks API...")


# Create FastAPI app
app = FastAPI(
    title="MiraiWorks API",
    description="HR & Recruitment Management Platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled error on {request.method} {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "internal_error"},
    )


# Include routers
from app.routers import include_routers

include_routers(app)
