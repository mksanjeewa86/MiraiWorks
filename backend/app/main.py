import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.dependencies import get_redis
from app.middleware import RequestContextMiddleware, StructuredLoggingMiddleware
from app.routers import include_routers
from app.utils.logging import configure_structlog, get_logger

# Configure structured logging
log_level = os.getenv("LOG_LEVEL", "INFO")
json_logs = os.getenv("JSON_LOGS", "false").lower() == "true"
configure_structlog(log_level=log_level, json_logs=json_logs)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting MiraiWorks API", component="startup")

    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized", component="database")

        # Test Redis connection - TEMPORARILY DISABLED FOR DOCKER ISSUES
        # redis_conn = await get_redis()
        # await redis_conn.ping()
        # logger.info("Redis connection established", component="redis")

        # TODO: Initialize other services (MinIO, ClamAV check, etc.)

        logger.info("MiraiWorks API started successfully", component="startup")
        yield

    except Exception as e:
        logger.error("Failed to start application", error=str(e), component="startup")
        raise

    # Shutdown
    logger.info("Shutting down MiraiWorks API", component="shutdown")


# Create FastAPI app
app = FastAPI(
    title="MiraiWorks API",
    description="HR & Recruitment Management Platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middleware (order matters - first added is executed last)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:5173",
    ],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Add structured logging middleware
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(RequestContextMiddleware)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(
        "Unhandled error",
        method=request.method,
        url=str(request.url),
        error_type=type(exc).__name__,
        error_message=str(exc),
        component="exception_handler",
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "internal_error"},
    )


# Include routers
include_routers(app)
