"""
i18n package for backend internationalization
Provides translation utilities for API responses and error messages
"""

from app.i18n.translate import get_locale_from_header, translator

__all__ = ["translator", "get_locale_from_header"]
