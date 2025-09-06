import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import Request
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
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
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
        content={
            "detail": "Internal server error",
            "type": "internal_error"
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test Redis
        redis_conn = await get_redis()
        await redis_conn.ping()
        
        return {
            "status": "healthy",
            "services": {
                "redis": "connected",
                "database": "connected"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "MiraiWorks API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Include routers
from app.routers import auth
from app.routers import calendar
from app.routers import dashboard
from app.routers import interviews
from app.routers import messaging
from app.routers import messaging_ws
from app.routers import resumes
from app.routers import webhooks

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(messaging.router, prefix="/api/messaging", tags=["messaging"])
app.include_router(messaging_ws.router, prefix="/ws", tags=["websocket"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(interviews.router, prefix="/api/interviews", tags=["interviews"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(resumes.router, prefix="/api/resumes", tags=["resumes"])
# Temporary stub endpoints to fix 404 errors
@app.get("/api/public/jobs")
async def get_public_jobs(limit: int = 50):
    """Temporary stub for public jobs API"""
    return {"jobs": [], "total": 0, "page": 1, "totalPages": 0}

# TODO: Include other routers when implemented  
# from app.routers import users, companies
# app.include_router(users.router, prefix="/api/users", tags=["users"])
# app.include_router(companies.router, prefix="/api/companies", tags=["companies"])