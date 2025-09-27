"""
Audit service stub for testing purposes.
This is a minimal implementation to allow tests to run.
"""

from typing import Any


def log_action(
    user_id: int | None = None,
    action: str = "",
    resource_type: str = "",
    resource_id: int | None = None,
    details: dict[str, Any] | None = None,
    **kwargs,
) -> None:
    """
    Log an audit action.
    This is a stub implementation that does nothing.
    In a real implementation, this would log to database or external system.
    """
    pass
