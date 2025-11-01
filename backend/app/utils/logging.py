"""
Structured logging configuration using structlog.
"""

import logging
import sys
from typing import Any

import structlog
from structlog.typing import FilteringBoundLogger


def configure_structlog(
    log_level: str = "INFO", json_logs: bool = False, show_locals: bool = False
) -> None:
    """
    Configure structured logging with structlog.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output JSON formatted logs
        show_locals: Whether to include local variables in error logs
    """

    # Configure timestamper
    timestamper = structlog.processors.TimeStamper(fmt="ISO")

    # Shared processors for both structlog and stdlib
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if show_locals:
        shared_processors.append(structlog.processors.format_exc_info)

    if json_logs:
        # JSON formatted logs for production
        structlog.configure(
            processors=shared_processors
            + [
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Console formatted logs for development
        structlog.configure(
            processors=shared_processors
            + [
                structlog.dev.ConsoleRenderer(
                    colors=True, exception_formatter=structlog.dev.rich_traceback
                )
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    # Configure stdlib logging
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(colors=False)
        if not json_logs
        else structlog.processors.JSONRenderer(),
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Quiet down some noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> FilteringBoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def bind_request_context(**kwargs: Any) -> None:
    """
    Bind request context variables to structlog context.

    Args:
        **kwargs: Context variables to bind
    """
    for key, value in kwargs.items():
        structlog.contextvars.bind_contextvars(**{key: value})


def clear_request_context() -> None:
    """Clear request context variables."""
    structlog.contextvars.clear_contextvars()


# Convenience functions for common logging patterns
def log_api_request(
    logger: FilteringBoundLogger,
    method: str,
    path: str,
    user_id: int | None = None,
    ip: str | None = None,
) -> None:
    """Log API request with common fields."""
    logger.info("API request", method=method, path=path, user_id=user_id, ip=ip)


def log_api_response(
    logger: FilteringBoundLogger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float | None = None,
) -> None:
    """Log API response with common fields."""
    logger.info(
        "API response",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
    )


def log_db_query(
    logger: FilteringBoundLogger,
    query: str,
    duration_ms: float | None = None,
    rows_affected: int | None = None,
) -> None:
    """Log database query with performance info."""
    logger.debug(
        "Database query",
        query=query,
        duration_ms=duration_ms,
        rows_affected=rows_affected,
    )


def log_error(
    logger: FilteringBoundLogger, error: Exception, context: str | None = None, **kwargs: Any
) -> None:
    """Log error with context."""
    logger.error(
        f"Error: {context or str(error)}",
        error_type=type(error).__name__,
        error_message=str(error),
        **kwargs,
    )
