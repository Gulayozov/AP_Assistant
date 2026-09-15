from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from app.config import settings
from app.i18n import Lang
from app.kb import loc


@dataclass
class Chunk:
    source: str
    title: str
    text: str
    program_id: str | None = None
    access: str = "public"


class KnowledgeBase:
    def __init__(self, chunks: list[Chunk], programs: list[dict]) -> None:
        self.chunks = chunks
        self.programs = programs
        self.programs_by_id = {p["id"]: p for p in programs}

    @classmethod
    def load(cls, kb_dir: Path | None = None) -> KnowledgeBase:
        kb_dir = kb_dir or settings.kb_dir
        public = (kb_dir / "knowledge.md").read_text(encoding="utf-8")
        payload = json.loads((kb_dir / "programs.json").read_text(encoding="utf-8"))
        programs = payload["programs"]
        chunks = _split_markdown(public, source="knowledge.md", access="public")
        for program in programs:
            chunks.extend(_program_chunks(program))
            guide = kb_dir / f"{program['id']}.md"
            if guide.exists():
                chunks.extend(
                    _split_markdown(
                        guide.read_text(encoding="utf-8"),
                        source=guide.name,
                        access="program",
                        program_id=program["id"],
                    )
                )
        return cls(chunks, programs)

    def get_program(self, program_id: str | None) -> dict | None:
        if not program_id:
            return None
        return self.programs_by_id.get(program_id)

    def program_context(self, program_id: str | None) -> str:
        program = self.get_program(program_id)
        if not program:
            return ""
        coordinator = program.get("coordinator") or {}
        profile = (
            "SELECTED PROGRAM RECORD\n"
            f"Name: {loc(program['name'], 'ru')} / {loc(program['name'], 'en')}\n"
            f"Cohort: {loc(program.get('cohort'), 'ru')} / {loc(program.get('cohort'), 'en')}\n"
            f"Stage: {loc(program['current_stage'], 'ru')} / {loc(program['current_stage'], 'en')}\n"
            f"Description: {loc(program['description'], 'ru')} / {loc(program['description'], 'en')}\n"
            f"Structure: {loc(program['structure'], 'ru')} / {loc(program['structure'], 'en')}\n"
            f"Speakers note: {loc(program.get('speakers_note'), 'ru')} / {loc(program.get('speakers_note'), 'en')}\n"
            f"Consultations note: {loc(program.get('consultation_note'), 'ru')} / {loc(program.get('consultation_note'), 'en')}\n"
            f"Coordinator Telegram: @{str(coordinator.get('telegram') or '').lstrip('@')}\n"
            f"Coordinator WhatsApp: {coordinator.get('whatsapp') or '—'}\n"
            f"Guide: {program.get('guide_url') or '—'}\n"
            f"Application form: {program.get('application_url') or '—'}"
        )
        extra = [chunk.text for chunk in self.chunks if chunk.program_id == program_id]
        return "\n\n---\n\n".join([profile, *extra])

    def list_programs(self, lang: Lang) -> list[tuple[str, str]]:
        items = []
        for program in self.programs:
            label = f"{loc(program['name'], lang)} · {loc(program.get('cohort'), lang)}"
            items.append((program["id"], label))
        return items


def _split_markdown(text: str, source: str, access: str, program_id: str | None = None) -> list[Chunk]:
    chunks: list[Chunk] = []
    parts = re.split(r"(?m)^## ", text)
    for index, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
        if index == 0 and not text.lstrip().startswith("##"):
            continue
        lines = part.splitlines()
        title = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        if not body:
            continue
        chunks.append(
            Chunk(
                source=source,
                title=title,
                text=f"{title}\n{body}",
                program_id=program_id,
                access=access,
            )
        )
    return chunks


def _program_chunks(program: dict) -> list[Chunk]:
    pid = program["id"]
    name_ru = loc(program["name"], "ru")
    name_en = loc(program["name"], "en")
    header = f"{name_ru} / {name_en} ({loc(program.get('cohort'), 'ru')} / {loc(program.get('cohort'), 'en')})"
    blocks = [
        ("description", f"{header}\n{loc(program['description'], 'ru')}\n{loc(program['description'], 'en')}"),
        ("stage", f"{header} current stage\n{loc(program['current_stage'], 'ru')}\n{loc(program['current_stage'], 'en')}"),
        ("structure", f"{header} structure\n{loc(program['structure'], 'ru')}\n{loc(program['structure'], 'en')}"),
    ]
    if loc(program.get("speakers_note"), "ru") or loc(program.get("speakers_note"), "en"):
        blocks.append((
            "speakers_note",
            f"{header} speakers note\n{loc(program.get('speakers_note'), 'ru')}\n{loc(program.get('speakers_note'), 'en')}",
        ))
    if loc(program.get("consultation_note"), "ru") or loc(program.get("consultation_note"), "en"):
        blocks.append((
            "consultation_note",
            f"{header} consultations note\n{loc(program.get('consultation_note'), 'ru')}\n{loc(program.get('consultation_note'), 'en')}",
        ))
    for event in program.get("calendar") or []:
        blocks.append((
            f"event:{event['id']}",
            (
                f"{header} calendar event\n"
                f"{loc(event['title'], 'ru')} / {loc(event['title'], 'en')}\n"
                f"{event['date']} {event['time']}\n"
                f"{loc(event.get('format'), 'ru')} {loc(event.get('description'), 'ru')}\n"
                f"speaker: {event.get('speaker') or '-'}\n"
                f"link: {event.get('link') or '-'}\n"
                f"location: {event.get('location') or '-'}"
            ),
        ))
    for item in program.get("deadlines") or []:
        blocks.append((
            f"deadline:{item['id']}",
            (
                f"{header} deadline\n"
                f"{loc(item['title'], 'ru')} / {loc(item['title'], 'en')}\n"
                f"{item['date']} {item['time']}\n"
                f"{loc(item.get('description'), 'ru')}\n"
                f"form: {item.get('link') or '-'}"
            ),
        ))
    if program.get("speakers"):
        lines = [f"{header} speakers"]
        for speaker in program["speakers"]:
            lines.append(
                f"{speaker['name']} — {loc(speaker['role'], 'ru')} / {loc(speaker['topic'], 'ru')}"
            )
        blocks.append(("speakers", "\n".join(lines)))
    for slot in program.get("consultations") or []:
        blocks.append((
            f"consult:{slot['id']}",
            (
                f"{header} consultation\n"
                f"{loc(slot['title'], 'ru')}\n"
                f"{slot['date']} {slot['time']} {loc(slot.get('format'), 'ru')}\n"
                f"link: {slot.get('link') or '-'}"
            ),
        ))
    for category in program.get("materials") or []:
        lines = [f"{header} materials {loc(category['category'], 'ru')}"]
        for item in category.get("items") or []:
            lines.append(f"{loc(item['title'], 'ru')}: {item.get('url')}")
        blocks.append((f"materials:{loc(category['category'], 'en')}", "\n".join(lines)))
    for idx, faq in enumerate(program.get("faq") or []):
        blocks.append((
            f"faq:{idx}",
            f"{header} FAQ\nQ: {loc(faq['q'], 'ru')} / {loc(faq['q'], 'en')}\nA: {loc(faq['a'], 'ru')} / {loc(faq['a'], 'en')}",
        ))

    return [
        Chunk(source=f"program:{pid}", title=title, text=text, program_id=pid, access="program")
        for title, text in blocks
    ]
