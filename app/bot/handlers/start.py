from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app.bot.context import AppContext
from app.bot.keyboards import language_keyboard, main_menu, programs_keyboard
from app.i18n import Lang, t
from app.kb import loc

router = Router()


def upsert_from_message(ctx: AppContext, message: Message) -> dict:
    user = message.from_user
    stored = ctx.store.get_user(user.id) if user else {}
    lang = stored.get("lang") or "ru"
    record = ctx.store.upsert_user(
        {
            "user_id": user.id,
            "chat_id": message.chat.id,
            "username": user.username,
            "first_name": user.first_name,
            "lang": lang,
            "lang_chosen": bool(stored.get("lang_chosen")),
        }
    )
    ctx.store.remember_coordinator(message.chat.id, user.username)
    return record


async def show_language_picker(message: Message) -> None:
    await message.answer(
        "Выберите язык / Choose a language:",
        reply_markup=language_keyboard(),
    )


async def after_language_ready(message: Message, ctx: AppContext, lang: Lang) -> None:
    await message.answer(
        t(lang, "start", bot_name=ctx.settings.bot_name),
        reply_markup=main_menu(lang),
    )
    await message.answer(
        t(lang, "choose_program"),
        reply_markup=programs_keyboard(ctx.kb.list_programs(lang)),
    )


@router.message(CommandStart())
async def start(message: Message, ctx: AppContext) -> None:
    upsert_from_message(ctx, message)
    await show_language_picker(message)


@router.callback_query(F.data.startswith("lang:"))
async def choose_language(callback: CallbackQuery, ctx: AppContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang: Lang = "en" if callback.data.endswith(":en") else "ru"
    ctx.store.upsert_user(
        {
            "user_id": callback.from_user.id,
            "chat_id": callback.message.chat.id,
            "username": callback.from_user.username,
            "first_name": callback.from_user.first_name,
            "lang": lang,
            "lang_chosen": True,
        }
    )
    await callback.message.answer(t(lang, "language_set"), reply_markup=main_menu(lang))
    existing = ctx.store.get_user(callback.from_user.id)
    if existing.get("program_id"):
        await callback.message.answer(t(lang, "menu_hint"), reply_markup=main_menu(lang))
    else:
        await after_language_ready(callback.message, ctx, lang)
    await callback.answer()


@router.callback_query(F.data.startswith("prog:"))
async def choose_program(callback: CallbackQuery, ctx: AppContext) -> None:
    if not callback.from_user or not callback.message:
        return
    program_id = callback.data.split(":", 1)[1]
    program = ctx.kb.get_program(program_id)
    if not program:
        await callback.answer()
        return
    existing = ctx.store.get_user(callback.from_user.id)
    lang = existing.get("lang") or "ru"
    ctx.store.upsert_user(
        {
            "user_id": callback.from_user.id,
            "chat_id": callback.message.chat.id,
            "username": callback.from_user.username,
            "first_name": callback.from_user.first_name,
            "lang": lang,
            "lang_chosen": bool(existing.get("lang_chosen")),
        }
    )
    record = ctx.store.set_program(callback.from_user.id, program_id)
    lang = record.get("lang") or "ru"
    name = loc(program["name"], lang)
    await callback.message.answer(
        t(lang, "program_selected", name=name, cohort=loc(program.get("cohort"), lang))
        + "\n"
        + t(lang, "menu_hint"),
        reply_markup=main_menu(lang),
    )
    await callback.answer(name)
