"""Tests for YAML locales and i18n helpers."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from views import i18n


class TestI18n:
    """Locale files and string lookup."""

    def test_all_locales_match_english_keys(self):
        """Every *.yml must define the same keys as en.yml."""
        ref = frozenset(i18n.UI_STRINGS[i18n.DEFAULT_LANGUAGE].keys())
        for code in i18n.SUPPORTED_CODES:
            assert frozenset(i18n.UI_STRINGS[code].keys()) == ref

    def test_get_ui_string_fallback(self):
        """Unknown key falls back sensibly."""
        assert i18n.get_ui_string("en", "___missing___") == "___missing___"

    def test_language_option_display_roundtrip(self):
        """Combobox display strings map back to codes."""
        for code in i18n.SUPPORTED_CODES:
            disp = i18n.language_option_display(code)
            assert i18n.LANG_DISPLAY_TO_CODE[disp] == code
