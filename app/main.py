from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent

from app.ai.assistant import Assistant
from app.bot.context import AppContext
from app.bot.handlers import menu, qa, start
from app.bot.reminders import send_due_reminders
from app.config import settings
from app.kb.loader import KnowledgeBase
from app.storage import JsonStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def reminder_loop(bot: Bot, ctx: AppContext) -> None:
    while True:
        try:
            await send_due_reminders(bot, ctx)
        except Exception:
            logger.exception("Reminder loop failed")
        await asyncio.sleep(60)


async def main() -> None:
    if not settings.telegram_token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is missing in .env")

    kb = KnowledgeBase.load()
    ctx = AppContext(
        settings=settings,
        kb=kb,
        store=JsonStore(),
        assistant=Assistant(kb),
    )

    bot = Bot(token=settings.telegram_token)
    me = await bot.get_me()
    dp = Dispatcher()
    dp["ctx"] = ctx
    dp["bot_username"] = me.username or "accelerateprosperitybot"
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(qa.router)

    @dp.error()
    async def on_error(event: ErrorEvent) -> None:
        logger.exception("Unhandled update error: %s", event.exception)

    logger.info("Starting %s as @%s", settings.bot_name, me.username)
    if not settings.gemini_enabled:
        logger.info("GEMINI_API_KEY is empty — using knowledge-base excerpts as fallback")

    loop_task = asyncio.create_task(reminder_loop(bot, ctx))
    try:
        await dp.start_polling(bot)
    finally:
        loop_task.cancel()
        await bot.session.close()
