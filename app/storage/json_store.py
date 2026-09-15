from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import settings


class JsonStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or settings.data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.users_path = self.data_dir / "users.json"
        self.meta_path = self.data_dir / "meta.json"
        self.unanswered_path = self.data_dir / "unanswered.jsonl"
        self.reminders_path = self.data_dir / "sent_reminders.json"
        self.tickets_path = self.data_dir / "tickets.jsonl"

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _append_jsonl(self, path: Path, payload: dict) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def upsert_user(self, user: dict) -> dict:
        users = self._read_json(self.users_path, {})
        user_id = str(user["user_id"])
        current = users.get(user_id, {})
        current.update(user)
        current["updated_at"] = _now()
        current.setdefault("created_at", current["updated_at"])
        users[user_id] = current
        self._write_json(self.users_path, users)
        return current

    def get_user(self, user_id: int) -> dict:
        users = self._read_json(self.users_path, {})
        return users.get(str(user_id), {})

    def list_users(self) -> list[dict]:
        users = self._read_json(self.users_path, {})
        return list(users.values())

    def set_program(self, user_id: int, program_id: str) -> dict:
        user = self.get_user(user_id) or {"user_id": user_id}
        user["program_id"] = program_id
        return self.upsert_user(user)

    def set_last_question(self, user_id: int, question: str) -> None:
        user = self.get_user(user_id) or {"user_id": user_id}
        user["last_question"] = question
        self.upsert_user(user)

    def remember_coordinator(self, chat_id: int, username: str | None) -> None:
        if not username or not settings.coordinator_username:
            return
        if username.lstrip("@").lower() != settings.coordinator_username.lower():
            return
        meta = self._read_json(self.meta_path, {})
        meta["coordinator_chat_id"] = chat_id
        meta["coordinator_username"] = username
        self._write_json(self.meta_path, meta)

    def coordinator_chat_id(self) -> int | None:
        meta = self._read_json(self.meta_path, {})
        value = meta.get("coordinator_chat_id")
        return int(value) if value else None

    def log_unanswered(self, payload: dict) -> None:
        payload = {**payload, "created_at": _now()}
        self._append_jsonl(self.unanswered_path, payload)

    def log_ticket(self, payload: dict) -> None:
        payload = {**payload, "created_at": _now()}
        self._append_jsonl(self.tickets_path, payload)

    def reminder_was_sent(self, key: str) -> bool:
        sent = self._read_json(self.reminders_path, {})
        return bool(sent.get(key))

    def mark_reminder_sent(self, key: str) -> None:
        sent = self._read_json(self.reminders_path, {})
        sent[key] = _now()
        self._write_json(self.reminders_path, sent)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
