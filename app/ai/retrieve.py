from __future__ import annotations

import re

from app.kb.loader import Chunk

_COMMON = {
    "accelerate",
    "prosperity",
    "акселерейт",
    "просперити",
    "программа",
    "program",
    "assistant",
}

_STOP = {
    "и", "в", "во", "на", "с", "со", "по", "для", "от", "до", "из", "к", "о", "об",
    "это", "как", "что", "или", "а", "но", "же", "ли", "не", "да",     "the", "a", "an",
    "and", "or", "of", "to", "in", "on", "for", "is", "are", "be", "with", "at",
    "что", "такое", "какой", "какая", "какие", "где", "когда", "сколько", "как",
    "who", "what", "when", "where", "how", "which",
}


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zа-яё0-9$%]+", text.lower())
    return {w for w in words if w not in _STOP and len(w) > 1}


def retrieve(
    question: str,
    chunks: list[Chunk],
    program_id: str | None,
    limit: int = 5,
) -> list[Chunk]:
    query = tokenize(question)
    if not query:
        return []

    scored: list[tuple[float, Chunk]] = []
    for chunk in chunks:
        if chunk.access == "program" and chunk.program_id != program_id:
            continue
        if chunk.access == "internal":
            continue
        words = tokenize(chunk.text)
        overlap = query & words
        specific_query = query - _COMMON
        specific_overlap = overlap - _COMMON
        if len(overlap) < 2:
            continue
        if specific_query and not specific_overlap:
            continue
        score = 0.0
        for token in overlap:
            score += 0.25 if token in _COMMON else 1.0
        score /= max(len(query), 1)
        if chunk.program_id and chunk.program_id == program_id and specific_overlap:
            score += 0.05
        scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    top = [chunk for score, chunk in scored if score >= 0.18][:limit]
    return top
