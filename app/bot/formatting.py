from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import settings
from app.i18n import Lang
from app.kb import loc


def detect_lang(text: str, fallback: Lang = "ru") -> Lang:
    cyr = sum(1 for ch in text.lower() if "а" <= ch <= "я" or ch == "ё")
    lat = sum(1 for ch in text.lower() if "a" <= ch <= "z")
    if cyr > lat:
        return "ru"
    if lat > cyr:
        return "en"
    return fallback


def lang_from_telegram(code: str | None) -> Lang:
    if code and code.lower().startswith("en"):
        return "en"
    return "ru"


def tz() -> ZoneInfo:
    return ZoneInfo(settings.timezone)


def parse_event_dt(date_str: str, time_str: str) -> datetime:
    time_part = time_str.split("–")[0].split("-")[0].strip()
    if re.fullmatch(r"\d{2}:\d{2}", time_part):
        value = f"{date_str} {time_part}"
        return datetime.strptime(value, "%Y-%m-%d %H:%M").replace(tzinfo=tz())
    return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=tz())


def format_event(event: dict, lang: Lang) -> str:
    link = event.get("link") or "—"
    speaker = event.get("speaker") or "—"
    location = event.get("location") or ""
    extra = f"\n{location}" if location else ""
    return (
        f"📅 {loc(event['title'], lang)}\n"
        f"{event['date']} {event['time']} ({settings.timezone})\n"
        f"{loc(event.get('format'), lang)}\n"
        f"{loc(event.get('description'), lang)}\n"
        f"{speaker}\n"
        f"{link}{extra}"
    )


def format_deadline(item: dict, lang: Lang) -> str:
    return (
        f"⏰ {loc(item['title'], lang)}\n"
        f"{item['date']} {item['time']} ({settings.timezone})\n"
        f"{loc(item.get('description'), lang)}\n"
        f"{item.get('link') or '—'}"
    )


def upcoming(items: list[dict], date_key: str = "date", time_key: str = "time") -> list[dict]:
    now = datetime.now(tz())
    future = []
    for item in items:
        try:
            when = parse_event_dt(item[date_key], item.get(time_key) or "00:00")
        except ValueError:
            continue
        if when >= now:
            future.append((when, item))
    future.sort(key=lambda pair: pair[0])
    return [item for _, item in future]
