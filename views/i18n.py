"""UI strings loaded from YAML locale files (views/locales/*.yml)."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, FrozenSet, Tuple

import yaml

_LOCALES_DIR = Path(__file__).resolve().parent / "locales"

DEFAULT_LANGUAGE = "en"

# Regional flag emoji for each UI language (shown in the combobox list and field)
LANG_FLAGS: Dict[str, str] = {
    "en": "🇬🇧",
    "it": "🇮🇹",
    "de": "🇩🇪",
    "es": "🇪🇸",
    "fr": "🇫🇷",
}

# Native name of each language (shown in the selector)
NATIVE_LANGUAGE_NAMES: Dict[str, str] = {
    "en": "English",
    "it": "Italiano",
    "de": "Deutsch",
    "es": "Español",
    "fr": "Français",
}

SUPPORTED_CODES: Tuple[str, ...] = tuple(NATIVE_LANGUAGE_NAMES.keys())

# code → "English" etc. (for any code that still needs the short label)
CODE_TO_LABEL: Dict[str, str] = dict(NATIVE_LANGUAGE_NAMES)


def language_option_display(code: str) -> str:
    """Combobox value: flag + native name (globe icon remains beside the control)."""
    flag = LANG_FLAGS.get(code, "🏁")
    name = NATIVE_LANGUAGE_NAMES.get(code, code)
    return f"{flag}  {name}"


# Full combobox value → language code
LANG_DISPLAY_TO_CODE: Dict[str, str] = {
    language_option_display(code): code for code in SUPPORTED_CODES
}


def _load_locale_files() -> Dict[str, Dict[str, str]]:
    """Load all *.yml files under views/locales/."""
    strings: Dict[str, Dict[str, str]] = {}
    for code in SUPPORTED_CODES:
        path = _LOCALES_DIR / f"{code}.yml"
        if not path.is_file():
            raise FileNotFoundError(f"Missing locale file: {path}")
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        if raw is None:
            raw = {}
        if not isinstance(raw, dict):
            raise ValueError(f"Locale {code} must be a YAML mapping")
        strings[code] = {str(k): str(v) for k, v in raw.items() if not str(k).startswith("#")}
    return strings


UI_STRINGS: Dict[str, Dict[str, str]] = _load_locale_files()

REFERENCE_KEYS: FrozenSet[str] = frozenset(UI_STRINGS[DEFAULT_LANGUAGE].keys())


def validate_locale_completeness() -> None:
    """Ensure every locale file defines the same keys as English."""
    for code in SUPPORTED_CODES:
        keys = frozenset(UI_STRINGS[code].keys())
        missing = REFERENCE_KEYS - keys
        extra = keys - REFERENCE_KEYS
        if missing or extra:
            raise ValueError(
                f"Locale {code}.yml key mismatch vs en: missing={sorted(missing)!r} extra={sorted(extra)!r}"
            )


validate_locale_completeness()


def get_ui_string(lang: str, key: str) -> str:
    """Return translated string; fall back to English, then to the key itself."""
    table = UI_STRINGS.get(lang) or UI_STRINGS[DEFAULT_LANGUAGE]
    if key not in table:
        table = UI_STRINGS[DEFAULT_LANGUAGE]
    return table.get(key, UI_STRINGS[DEFAULT_LANGUAGE].get(key, key))


def make_translate(lang: str) -> Callable[[str], str]:
    """Build a key -> string function bound to one language."""

    def _t(key: str) -> str:
        return get_ui_string(lang, key)

    return _t
