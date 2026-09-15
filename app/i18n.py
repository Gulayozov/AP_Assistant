from __future__ import annotations

from typing import Literal

Lang = Literal["ru", "en"]

TEXTS: dict[str, dict[str, str]] = {
    "ru": {
        "start": (
            "Здравствуйте! Я {bot_name} — цифровой координатор программ "
            "Accelerate Prosperity.\n\n"
            "Сейчас доступ открыт без кода участника. "
            "Выберите программу, чтобы получать календарь, материалы и ответы "
            "по вашей программе."
        ),
        "choose_language": "Выберите язык / Choose a language:",
        "language_set": "Язык: русский. Дальше буду отвечать на русском.",
        "change_language": "Язык / Language",
        "choose_program": "Выберите программу:",
        "program_selected": "Программа выбрана: {name} ({cohort}).",
        "menu_hint": "Можно пользоваться меню или просто написать вопрос.",
        "ask_prompt": "Напишите вопрос о программе — отвечу по утверждённой базе знаний.",
        "no_program": "Сначала выберите программу в меню «Сменить программу».",
        "no_answer": (
            "У меня нет подтверждённой информации по этому вопросу.\n\n"
            "Я могу передать ваш вопрос координатору."
        ),
        "handoff_offer": "Передать вопрос координатору",
        "handoff_done": (
            "Вопрос зафиксирован. Напишите координатору: @{username}\n\n"
            "Текст обращения:\n{payload}"
        ),
        "handoff_empty": (
            "Координатор: @{username}\n"
            "Напишите ему напрямую, если вопрос нельзя решить в боте."
        ),
        "handoff_notified": "Координатор получил уведомление в этом боте.",
        "ai_unavailable": "ИИ сейчас недоступен. Попробуйте позже или напишите координатору.",
        "faq": "FAQ",
        "empty_faq": "Для этой программы пока нет опубликованных FAQ.",
        "my_program": "Моя программа",
        "calendar": "Календарь",
        "next_meeting": "Следующая встреча",
        "materials": "Материалы",
        "deadlines": "Дедлайны",
        "speakers": "Спикеры",
        "consultations": "Консультации",
        "ask_question": "Задать вопрос",
        "contact_coordinator": "Связаться с координатором",
        "change_program": "Сменить программу",
        "empty_calendar": "В календаре пока нет опубликованных встреч.",
        "empty_next": "Ближайшая встреча пока не опубликована.",
        "empty_materials": "В библиотеке пока нет опубликованных материалов.",
        "empty_deadlines": "Опубликованных дедлайнов пока нет.",
        "empty_speakers": "Информация о спикерах пока не опубликована.",
        "empty_consultations": "Расписание консультаций пока не опубликовано.",
        "reminder_event": (
            "🔔 Напоминание\n\n"
            "{when} начинается {title}.\n\n"
            "Время: {time}\n"
            "Спикер: {speaker}\n"
            "Формат: {format}\n"
            "Ссылка: {link}"
        ),
        "reminder_deadline": (
            "⏰ Напоминание о дедлайне\n\n"
            "{title}\n"
            "Срок: {when}\n"
            "{description}\n"
            "Форма: {link}"
        ),
        "in_24h": "Через 24 часа",
        "in_2h": "Через 2 часа",
        "in_15m": "Через 15 минут",
        "today": "Сегодня",
        "unknown_speaker": "не указан",
        "unknown_link": "ссылка не указана",
    },
    "en": {
        "start": (
            "Hello! I am {bot_name} — a digital coordinator for "
            "Accelerate Prosperity programs.\n\n"
            "Access is currently open without a participant code. "
            "Choose a program to get its calendar, materials, and Q&A."
        ),
        "choose_language": "Choose a language / Выберите язык:",
        "language_set": "Language: English. I will continue in English.",
        "change_language": "Language / Язык",
        "choose_program": "Choose a program:",
        "program_selected": "Program selected: {name} ({cohort}).",
        "menu_hint": "Use the menu or just type a question.",
        "ask_prompt": "Type a question about the program. I will answer from the approved knowledge base only.",
        "no_program": "Please choose a program first via “Change program”.",
        "no_answer": (
            "I do not have confirmed information on this question.\n\n"
            "I can pass your question to the coordinator."
        ),
        "handoff_offer": "Pass the question to the coordinator",
        "handoff_done": (
            "The question has been logged. Message the coordinator: @{username}\n\n"
            "Ticket text:\n{payload}"
        ),
        "handoff_empty": (
            "Coordinator: @{username}\n"
            "Write to them directly if the bot cannot help."
        ),
        "handoff_notified": "The coordinator received a notification in this bot.",
        "ai_unavailable": "The AI is unavailable right now. Try again later or message the coordinator.",
        "faq": "FAQ",
        "empty_faq": "No published FAQ for this program yet.",
        "my_program": "My program",
        "calendar": "Calendar",
        "next_meeting": "Next meeting",
        "materials": "Materials",
        "deadlines": "Deadlines",
        "speakers": "Speakers",
        "consultations": "Consultations",
        "ask_question": "Ask a question",
        "contact_coordinator": "Contact coordinator",
        "change_program": "Change program",
        "empty_calendar": "No published meetings in the calendar yet.",
        "empty_next": "The next meeting has not been published yet.",
        "empty_materials": "No published materials in the library yet.",
        "empty_deadlines": "No published deadlines yet.",
        "empty_speakers": "Speaker information has not been published yet.",
        "empty_consultations": "Consultation slots have not been published yet.",
        "reminder_event": (
            "🔔 Reminder\n\n"
            "{when} {title} starts.\n\n"
            "Time: {time}\n"
            "Speaker: {speaker}\n"
            "Format: {format}\n"
            "Link: {link}"
        ),
        "reminder_deadline": (
            "⏰ Deadline reminder\n\n"
            "{title}\n"
            "Due: {when}\n"
            "{description}\n"
            "Form: {link}"
        ),
        "in_24h": "In 24 hours",
        "in_2h": "In 2 hours",
        "in_15m": "In 15 minutes",
        "today": "Today",
        "unknown_speaker": "not specified",
        "unknown_link": "no link published",
    },
}


def t(lang: Lang, key: str, **kwargs: object) -> str:
    table = TEXTS.get(lang) or TEXTS["ru"]
    text = table.get(key) or TEXTS["ru"][key]
    return text.format(**kwargs) if kwargs else text
