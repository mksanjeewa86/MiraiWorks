"""
Logging middleware for structured request/response logging.
"""

import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logging import bind_request_context, clear_request_context, get_logger

logger = get_logger(__name__)


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request/response logging."""

    def __init__(self, app, exclude_paths: list[str] | None = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Generate request ID
        request_id = str(uuid.uuid4())

        # Get client IP
        client_ip = request.headers.get(
            "x-forwarded-for", request.client.host if request.client else "unknown"
        )

        # Bind request context
        bind_request_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
        )

        # Add request ID to request state for other middleware/handlers to use
        request.state.request_id = request_id

        start_time = time.time()

        # Log incoming request
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            user_agent=request.headers.get("user-agent"),
            client_ip=client_ip,
            component="request",
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000, 2)

            # Log response
            logger.info(
                "Request completed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                component="response",
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)

            # Log error
            logger.error(
                "Request failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
                error_type=type(e).__name__,
                error_message=str(e),
                component="request_error",
            )

            # Re-raise the exception
            raise

        finally:
            # Clear request context
            clear_request_context()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to add user context to logs when available."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            # Try to extract user info from JWT token if available
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                try:
                    # This would require importing and using your JWT decode function
                    # For now, just bind that we have an authenticated request
                    bind_request_context(authenticated=True)
                except Exception:
                    # Invalid token, ignore
                    bind_request_context(authenticated=False)
            else:
                bind_request_context(authenticated=False)

            return await call_next(request)
        except Exception as e:
            # Log error and re-raise
            logger.error(
                "Request context middleware error",
                error_type=type(e).__name__,
                error_message=str(e),
                component="middleware_error",
            )
            raise
