"""
Translation utility for backend API responses and error messages
Provides internationalization support for English and Japanese
"""

import json
from pathlib import Path
from typing import Dict, Optional


class Translator:
    """Handles loading and retrieving translations for different locales"""

    def __init__(self):
        """Initialize the translator and load all translation files"""
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()

    def _load_translations(self):
        """Load all translation files from the locales directory"""
        locale_dir = Path(__file__).parent / "locales"

        # Create locales directory if it doesn't exist
        locale_dir.mkdir(parents=True, exist_ok=True)

        # Load all JSON files in the locales directory
        for locale_file in locale_dir.glob("*.json"):
            locale = locale_file.stem
            try:
                with open(locale_file, "r", encoding="utf-8") as f:
                    self.translations[locale] = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load translations for {locale}: {e}")
                self.translations[locale] = {}

    def t(self, key: str, locale: str = "en", **kwargs) -> str:
        """
        Translate a key with optional formatting

        Args:
            key: The translation key (e.g., "errors.user_not_found")
            locale: The locale code (e.g., "en", "ja")
            **kwargs: Optional formatting arguments

        Returns:
            Translated string, or the key itself if translation not found

        Examples:
            translator.t("errors.user_not_found", locale="ja")
            translator.t("success.interview_scheduled", locale="en", datetime="2025-01-10 15:30")
        """
        # Get the translation dictionary for the locale, fallback to English
        locale_dict = self.translations.get(locale, self.translations.get("en", {}))

        # Navigate through nested keys (e.g., "errors.user_not_found")
        keys = key.split(".")
        value = locale_dict

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                value = None
                break

        # If no translation found, try to fall back to English
        if value is None and locale != "en":
            en_dict = self.translations.get("en", {})
            value = en_dict
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    value = None
                    break

        # If still no translation, return the key
        if value is None:
            return key

        # Format the string if kwargs provided
        if kwargs and isinstance(value, str):
            try:
                return value.format(**kwargs)
            except (KeyError, ValueError):
                # If formatting fails, return the unformatted string
                return value

        return value if isinstance(value, str) else key

    def get_supported_locales(self) -> list:
        """Get list of supported locale codes"""
        return list(self.translations.keys())

    def reload(self):
        """Reload all translation files (useful for development)"""
        self.translations = {}
        self._load_translations()


# Global translator instance
translator = Translator()


def get_locale_from_header(accept_language: Optional[str]) -> str:
    """
    Extract locale from Accept-Language header

    Args:
        accept_language: The Accept-Language header value

    Returns:
        Locale code (e.g., "en", "ja")
    """
    if not accept_language:
        return "en"

    # Parse Accept-Language header (e.g., "ja-JP,ja;q=0.9,en;q=0.8" -> "ja")
    locale = accept_language.split(",")[0].split("-")[0].strip()

    # Validate locale is supported
    if locale in translator.get_supported_locales():
        return locale

    return "en"  # Default to English
