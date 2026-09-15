from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


class Settings:
    telegram_token: str = _env("TELEGRAM_BOT_TOKEN")
    gemini_api_key: str = _env("GEMINI_API_KEY")
    gemini_model: str = _env("GEMINI_MODEL", "gemini-3.6-flash")
    coordinator_username: str = _env("COORDINATOR_USERNAME").lstrip("@")
    bot_name: str = _env("BOT_NAME", "Accelerate Prosperity Assistant")
    timezone: str = _env("TIMEZONE", "Asia/Dushanbe")
    data_dir: Path = ROOT_DIR / "data" / "runtime"
    kb_dir: Path = ROOT_DIR / "app" / "kb"

    @property
    def gemini_enabled(self) -> bool:
        return bool(self.gemini_api_key)


settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
