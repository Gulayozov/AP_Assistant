from __future__ import annotations

from pathlib import Path

NO_ANSWER_TOKEN = "[NO_ANSWER]"
_PROMPT_PATH = Path(__file__).with_name("prompt.md")


def load_system_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def build_prompt(
    question: str,
    context: str,
    language: str,
    program_name: str = "—",
    cohort: str = "—",
) -> str:
    lang_name = "Russian" if language == "ru" else "English"
    system = (
        load_system_prompt()
        .replace("{no_answer_token}", NO_ANSWER_TOKEN)
        .replace("{language}", lang_name)
        .replace("{program_name}", program_name)
        .replace("{cohort}", cohort)
    )
    return (
        system
        + "\n\n## CONTEXT\n\n"
        + (context or "(empty)")
        + "\n\n## USER QUESTION\n\n"
        + question
    )
