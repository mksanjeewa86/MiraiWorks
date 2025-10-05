"""Datetime utility functions for timezone-aware datetime handling."""

from datetime import UTC, datetime


def get_utc_now() -> datetime:
    """
    Get current UTC time for SQLAlchemy default.

    This function provides a timezone-aware UTC datetime that can be used
    as a callable default in SQLAlchemy column definitions.

    Returns:
        datetime: Current UTC time with timezone information

    Example:
        created_at = Column(DateTime, default=get_utc_now, nullable=False)
    """
    return datetime.now(UTC)
