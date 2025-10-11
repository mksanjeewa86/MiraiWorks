"""
i18n package for backend internationalization
Provides translation utilities for API responses and error messages
"""

from .translate import translator, get_locale_from_header

__all__ = ["translator", "get_locale_from_header"]
