from __future__ import annotations

import logging

import aiohttp

from app.ai.prompts import NO_ANSWER_TOKEN
from app.config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def generate(self, prompt: str) -> str | None:
        if not self.enabled:
            return None
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024,
            },
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    params={"key": self.api_key},
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=45),
                ) as response:
                    data = await response.json()
                    if response.status >= 400:
                        logger.warning("Gemini error %s: %s", response.status, data)
                        return None
        except Exception:
            logger.exception("Gemini request failed")
            return None

        text = _extract_text(data)
        if not text:
            logger.warning("Unexpected Gemini payload: %s", data)
            return None
        return text


def _extract_text(data: dict) -> str | None:
    try:
        parts = data["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError, TypeError):
        return None
    chunks: list[str] = []
    for part in parts:
        if not isinstance(part, dict):
            continue
        if part.get("thought"):
            continue
        text = part.get("text")
        if text:
            chunks.append(text.strip())
    combined = "\n".join(chunk for chunk in chunks if chunk).strip()
    return combined or None


def is_model_no_answer(text: str | None) -> bool:
    if not text:
        return True
    return text.strip().startswith(NO_ANSWER_TOKEN)
