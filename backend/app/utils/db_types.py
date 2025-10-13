"""Database type definitions for MySQL"""

from sqlalchemy import Text

try:
    from sqlalchemy.dialects.mysql import LONGTEXT
except ImportError:
    # Fallback to Text if MySQL dialect not available
    LONGTEXT = Text


# Export the type
__all__ = ["LONGTEXT"]
