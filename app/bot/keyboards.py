from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.i18n import Lang, t


def main_menu(lang: Lang) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "my_program")), KeyboardButton(text=t(lang, "calendar"))],
            [KeyboardButton(text=t(lang, "next_meeting")), KeyboardButton(text=t(lang, "deadlines"))],
            [KeyboardButton(text=t(lang, "materials")), KeyboardButton(text=t(lang, "speakers"))],
            [KeyboardButton(text=t(lang, "consultations")), KeyboardButton(text=t(lang, "faq"))],
            [KeyboardButton(text=t(lang, "ask_question")), KeyboardButton(text=t(lang, "contact_coordinator"))],
            [KeyboardButton(text=t(lang, "change_program")), KeyboardButton(text=t(lang, "change_language"))],
        ],
        resize_keyboard=True,
    )


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="English", callback_data="lang:en"),
            ]
        ]
    )


def programs_keyboard(items: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=f"prog:{program_id}")]
            for program_id, label in items
        ]
    )


def handoff_keyboard(lang: Lang) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "handoff_offer"), callback_data="handoff:yes")]
        ]
    )
