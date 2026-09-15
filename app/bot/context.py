from __future__ import annotations

from dataclasses import dataclass

from app.ai.assistant import Assistant
from app.config import Settings
from app.kb.loader import KnowledgeBase
from app.storage import JsonStore


@dataclass
class AppContext:
    settings: Settings
    kb: KnowledgeBase
    store: JsonStore
    assistant: Assistant
