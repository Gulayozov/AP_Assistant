from __future__ import annotations

from typing import Any

from app.i18n import Lang


def loc(value: Any, lang: Lang) -> str:
    if isinstance(value, dict):
        return str(value.get(lang) or value.get("ru") or value.get("en") or "")
    return "" if value is None else str(value)
