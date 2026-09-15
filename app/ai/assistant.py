from __future__ import annotations

from dataclasses import dataclass

from app.ai.gemini import GeminiClient, is_model_no_answer
from app.ai.prompts import build_prompt
from app.ai.retrieve import retrieve
from app.i18n import Lang, t
from app.kb import loc
from app.kb.loader import KnowledgeBase


@dataclass
class AssistantReply:
    text: str
    known: bool
    used_fallback: bool = False


class Assistant:
    def __init__(self, kb: KnowledgeBase) -> None:
        self.kb = kb
        self.gemini = GeminiClient()

    async def answer(self, question: str, program_id: str | None, lang: Lang) -> AssistantReply:
        program_ctx = self.kb.program_context(program_id)
        found = retrieve(question, self.kb.chunks, program_id)
        blocks = [program_ctx] if program_ctx else []
        seen = {program_ctx} if program_ctx else set()
        for chunk in found:
            if chunk.program_id:
                continue
            if chunk.text not in seen:
                blocks.append(chunk.text)
                seen.add(chunk.text)
        context = "\n\n---\n\n".join(block for block in blocks if block)

        program = self.kb.get_program(program_id)
        prompt = build_prompt(
            question,
            context,
            lang,
            program_name=loc(program["name"], lang) if program else "—",
            cohort=loc(program.get("cohort"), lang) if program else "—",
        )

        generated = await self.gemini.generate(prompt)
        if generated and not is_model_no_answer(generated):
            return AssistantReply(text=generated, known=True)
        if generated and is_model_no_answer(generated):
            return AssistantReply(text=t(lang, "no_answer"), known=False)
        if not self.gemini.enabled:
            return AssistantReply(text=t(lang, "ai_unavailable"), known=False)
        return AssistantReply(text=t(lang, "no_answer"), known=False)
