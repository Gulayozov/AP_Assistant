from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.bot.context import AppContext
from app.bot.formatting import detect_lang
from app.bot.handlers.start import show_language_picker, upsert_from_message
from app.bot.keyboards import handoff_keyboard, main_menu
from app.config import settings
from app.i18n import t
from app.kb import loc

router = Router()


def is_addressed(message: Message, bot_username: str) -> bool:
    if message.chat.type == "private":
        return True
    if (
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.is_bot
    ):
        return True
    text = message.text or message.caption or ""
    return f"@{bot_username}".lower() in text.lower()


@router.message(F.text, ~F.text.startswith("/"))
async def handle_question(message: Message, ctx: AppContext, bot_username: str) -> None:
    if not message.from_user or not message.text:
        return
    if not is_addressed(message, bot_username):
        return

    record = upsert_from_message(ctx, message)
    if not record.get("lang_chosen"):
        await show_language_picker(message)
        return

    detected = detect_lang(message.text, record.get("lang") or "ru")
    if detected != record.get("lang"):
        record = ctx.store.upsert_user(
            {
                "user_id": message.from_user.id,
                "lang": detected,
                "lang_chosen": True,
            }
        )
        await message.answer(
            t(detected, "language_set"),
            reply_markup=main_menu(detected),
        )

    await message.bot.send_chat_action(message.chat.id, "typing")
    await reply_with_ai(message, ctx, message.text.strip(), record)


async def reply_with_ai(message: Message, ctx: AppContext, question: str, record: dict) -> None:
    user = message.from_user
    lang = record.get("lang") or "ru"
    ctx.store.set_last_question(user.id if user else 0, question)
    reply = await ctx.assistant.answer(question, record.get("program_id"), lang)
    if not reply.known:
        ctx.store.log_unanswered(
            {
                "user_id": user.id if user else None,
                "username": user.username if user else None,
                "program_id": record.get("program_id"),
                "question": question,
                "lang": lang,
            }
        )
        await message.answer(reply.text, reply_markup=handoff_keyboard(lang))
        return
    await message.answer(reply.text)


@router.callback_query(F.data == "handoff:yes")
async def handoff_callback(callback: CallbackQuery, ctx: AppContext) -> None:
    if not callback.from_user or not callback.message:
        await callback.answer()
        return
    record = ctx.store.get_user(callback.from_user.id)
    fake = callback.message
    # Reuse the original chat to send the ticket text.
    await send_handoff(fake, ctx, record, from_user=callback.from_user)
    await callback.answer()


async def send_handoff(message: Message, ctx: AppContext, record: dict, from_user=None) -> None:
    user = from_user or message.from_user
    lang = record.get("lang") or "ru"
    program = ctx.kb.get_program(record.get("program_id"))
    program_name = loc(program["name"], lang) if program else "—"
    extra = (program or {}).get("coordinator") or {}
    username = str(extra.get("telegram") or settings.coordinator_username).lstrip("@")
    question = record.get("last_question") or "—"
    payload = (
        f"Program: {program_name}\n"
        f"Cohort: {loc(program.get('cohort'), lang) if program else '—'}\n"
        f"Participant: {user.first_name if user else '—'} "
        f"(@{user.username if user and user.username else 'no_username'})\n"
        f"Question: {question}"
    )
    await message.answer(
        t(
            lang,
            "handoff_done" if question != "—" else "handoff_empty",
            username=username,
            payload=payload,
        )
    )
    ctx.store.log_ticket(
        {
            "user_id": user.id if user else None,
            "username": user.username if user else None,
            "program_id": record.get("program_id"),
            "question": question,
        }
    )
    coordinator_chat = ctx.store.coordinator_chat_id()
    if coordinator_chat:
        notice = (
            "❓ Новый вопрос без ответа\n\n"
            f"{payload}"
        )
        try:
            await message.bot.send_message(coordinator_chat, notice)
            await message.answer(t(lang, "handoff_notified"))
        except Exception:
            pass
