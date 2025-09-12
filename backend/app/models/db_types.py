"""Database type compatibility layer"""

import os
from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator, String

# Check if we're using SQLite for testing
using_sqlite = "sqlite" in os.getenv("TEST_DATABASE_URL", "")

if using_sqlite:
    # For SQLite, use Text instead of LONGTEXT
    LONGTEXT = Text
else:
    # For MySQL, use proper LONGTEXT
    try:
        from sqlalchemy.dialects.mysql import LONGTEXT
    except ImportError:
        # Fallback to Text if MySQL dialect not available
        LONGTEXT = Text

class CompatLONGTEXT(TypeDecorator):
    """A type that works with both MySQL LONGTEXT and SQLite TEXT"""
    impl = Text
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'mysql':
            try:
                from sqlalchemy.dialects.mysql import LONGTEXT
                return dialect.type_descriptor(LONGTEXT())
            except ImportError:
                return dialect.type_descriptor(Text())
        else:
            return dialect.type_descriptor(Text())

# Export the compatible type
__all__ = ['LONGTEXT', 'CompatLONGTEXT']