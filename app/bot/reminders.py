from __future__ import annotations

import logging
from datetime import datetime, timedelta

from aiogram import Bot

from app.bot.context import AppContext
from app.bot.formatting import parse_event_dt, tz
from app.i18n import t
from app.kb import loc

logger = logging.getLogger(__name__)

OFFSETS = {
    "24h": timedelta(hours=24),
    "2h": timedelta(hours=2),
    "15m": timedelta(minutes=15),
    "3d": timedelta(days=3),
    "today": timedelta(hours=0),
}


async def send_due_reminders(bot: Bot, ctx: AppContext) -> None:
    now = datetime.now(tz())
    users = ctx.store.list_users()
    for program in ctx.kb.programs:
        for event in program.get("calendar") or []:
            await _maybe_send_event(bot, ctx, users, program, event, now)
        for deadline in program.get("deadlines") or []:
            await _maybe_send_deadline(bot, ctx, users, program, deadline, now)


async def _maybe_send_event(bot, ctx, users, program, event, now) -> None:
    try:
        when = parse_event_dt(event["date"], event.get("time") or "00:00")
    except ValueError:
        return
    if when <= now:
        return
    for code in event.get("reminders") or []:
        offset = OFFSETS.get(code)
        if offset is None:
            continue
        reminder_at = when - offset
        if reminder_at > now:
            continue
        for user in users:
            if user.get("program_id") != program["id"]:
                continue
            chat_id = user.get("chat_id")
            if not chat_id:
                continue
            key = f"event:{program['id']}:{event['id']}:{user['user_id']}:{code}"
            if ctx.store.reminder_was_sent(key):
                continue
            lang = user.get("lang") or "ru"
            when_label = {
                "24h": t(lang, "in_24h"),
                "2h": t(lang, "in_2h"),
                "15m": t(lang, "in_15m"),
            }.get(code, t(lang, "in_24h"))
            text = t(
                lang,
                "reminder_event",
                when=when_label,
                title=loc(event["title"], lang),
                time=f"{event['date']} {event['time']}",
                speaker=event.get("speaker") or t(lang, "unknown_speaker"),
                format=loc(event.get("format"), lang),
                link=event.get("link") or t(lang, "unknown_link"),
            )
            try:
                await bot.send_message(chat_id, text)
                ctx.store.mark_reminder_sent(key)
            except Exception:
                logger.exception("Failed to send event reminder to %s", chat_id)


async def _maybe_send_deadline(bot, ctx, users, program, deadline, now) -> None:
    try:
        when = parse_event_dt(deadline["date"], deadline.get("time") or "23:59")
    except ValueError:
        return
    if when <= now:
        return
    for code in deadline.get("reminders") or []:
        offset = OFFSETS.get(code)
        if offset is None:
            continue
        reminder_at = when - offset
        if reminder_at > now:
            continue
        for user in users:
            if user.get("program_id") != program["id"]:
                continue
            chat_id = user.get("chat_id")
            if not chat_id:
                continue
            key = f"deadline:{program['id']}:{deadline['id']}:{user['user_id']}:{code}"
            if ctx.store.reminder_was_sent(key):
                continue
            lang = user.get("lang") or "ru"
            text = t(
                lang,
                "reminder_deadline",
                title=loc(deadline["title"], lang),
                when=f"{deadline['date']} {deadline['time']}",
                description=loc(deadline.get("description"), lang),
                link=deadline.get("link") or t(lang, "unknown_link"),
            )
            try:
                await bot.send_message(chat_id, text)
                ctx.store.mark_reminder_sent(key)
            except Exception:
                logger.exception("Failed to send deadline reminder to %s", chat_id)
