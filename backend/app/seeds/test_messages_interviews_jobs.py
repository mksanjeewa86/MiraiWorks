"""
Placeholder for sample messages, interviews, and jobs data.
This file was missing and needed for imports to work.
"""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


async def seed_sample_data(db: AsyncSession, auth_result: dict[str, Any]) -> dict[str, int]:
    """
    Placeholder function for seeding sample messages, interviews, and jobs data.

    Args:
        db: Database session
        auth_result: Result from auth data seeding containing user IDs

    Returns:
        Dictionary with counts of created records
    """
    # TODO: Implement actual sample data seeding
    return {
        "messages": 0,
        "interviews": 0,
        "positions": 0,
    }
