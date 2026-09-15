from aiogram import Router
from aiogram.filters import Filter
from aiogram.types import Message

from app.bot.context import AppContext
from app.bot.formatting import format_deadline, format_event, upcoming
from app.bot.handlers.start import show_language_picker, upsert_from_message
from app.bot.keyboards import programs_keyboard
from app.i18n import TEXTS, t
from app.kb import loc

router = Router()

MENU_KEYS = (
    "my_program",
    "calendar",
    "next_meeting",
    "materials",
    "deadlines",
    "speakers",
    "consultations",
    "faq",
    "ask_question",
    "contact_coordinator",
    "change_program",
    "change_language",
)


def menu_key(text: str) -> str | None:
    for table in TEXTS.values():
        for key in MENU_KEYS:
            if text == table.get(key):
                return key
    return None


class MainMenuFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        return bool(message.text) and menu_key(message.text) is not None


@router.message(MainMenuFilter())
async def handle_menu(message: Message, ctx: AppContext) -> None:
    record = upsert_from_message(ctx, message)
    if not record.get("lang_chosen"):
        await show_language_picker(message)
        return

    lang = record.get("lang") or "ru"
    key = menu_key(message.text or "")

    if key == "change_language":
        await show_language_picker(message)
        return
    if key == "change_program":
        await message.answer(
            t(lang, "choose_program"),
            reply_markup=programs_keyboard(ctx.kb.list_programs(lang)),
        )
        return
    if key == "ask_question":
        await message.answer(t(lang, "ask_prompt"))
        return
    if key == "contact_coordinator":
        from app.bot.handlers.qa import send_handoff

        await send_handoff(message, ctx, record)
        return

    if not message.from_user:
        return
    program = ctx.kb.get_program(record.get("program_id"))
    if not program:
        await message.answer(t(lang, "no_program"))
        return

    if key == "faq":
        await message.answer(render_faq(program, lang))
        return

    await message.answer(render_section(program, key, lang))


def render_faq(program: dict, lang: str) -> str:
    items = program.get("faq") or []
    if not items:
        return t(lang, "empty_faq")
    blocks = [f"FAQ · {loc(program['name'], lang)}"]
    for item in items:
        blocks.append(f"Q: {loc(item['q'], lang)}\nA: {loc(item['a'], lang)}")
    return "\n\n".join(blocks)


def render_section(program: dict, key: str, lang: str) -> str:
    if key == "my_program":
        return "\n".join(
            [
                loc(program["name"], lang),
                loc(program.get("cohort"), lang),
                loc(program["current_stage"], lang),
                "",
                loc(program["description"], lang),
                "",
                loc(program["structure"], lang),
            ]
        )
    if key == "calendar":
        events = program.get("calendar") or []
        if not events:
            return t(lang, "empty_calendar")
        return "\n\n".join(format_event(event, lang) for event in events)
    if key == "next_meeting":
        events = upcoming(program.get("calendar") or [])
        if not events:
            return t(lang, "empty_next")
        return format_event(events[0], lang)
    if key == "deadlines":
        items = program.get("deadlines") or []
        if not items:
            return t(lang, "empty_deadlines")
        return "\n\n".join(format_deadline(item, lang) for item in items)
    if key == "speakers":
        speakers = program.get("speakers") or []
        note = loc(program.get("speakers_note"), lang)
        if not speakers:
            return "\n\n".join(part for part in [note, t(lang, "empty_speakers")] if part)
        lines = [note] if note else []
        for speaker in speakers:
            lines.append(
                f"{speaker['name']}\n{loc(speaker['role'], lang)}\n{loc(speaker['topic'], lang)}"
            )
        return "\n\n".join(lines)
    if key == "consultations":
        slots = program.get("consultations") or []
        note = loc(program.get("consultation_note"), lang)
        if not slots:
            return "\n\n".join(part for part in [note, t(lang, "empty_consultations")] if part)
        lines = [note] if note else []
        for slot in slots:
            lines.append(
                f"{loc(slot['title'], lang)}\n{slot['date']} {slot['time']}\n"
                f"{loc(slot.get('format'), lang)}\n{slot.get('link') or '—'}"
            )
        return "\n\n".join(lines)
    if key == "materials":
        categories = program.get("materials") or []
        if not categories:
            return t(lang, "empty_materials")
        blocks = []
        for category in categories:
            lines = [loc(category["category"], lang)]
            for item in category.get("items") or []:
                lines.append(f"• {loc(item['title'], lang)}\n  {item.get('url')}")
            blocks.append("\n".join(lines))
        return "\n\n".join(blocks)
    return t(lang, "menu_hint")
