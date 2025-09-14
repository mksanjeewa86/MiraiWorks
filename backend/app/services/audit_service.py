"""
Audit service stub for testing purposes.
This is a minimal implementation to allow tests to run.
"""

from typing import Any, Dict, Optional


def log_action(
    user_id: Optional[int] = None,
    action: str = "",
    resource_type: str = "",
    resource_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> None:
    """
    Log an audit action.
    This is a stub implementation that does nothing.
    In a real implementation, this would log to database or external system.
    """
    pass