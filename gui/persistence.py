"""Simple local settings persistence."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Optional

from .config import DEFAULT_BACKEND_URL, SETTINGS_FILE, ensure_dirs


@dataclass
class Settings:
    backend_url: str = DEFAULT_BACKEND_URL
    api_key: Optional[str] = None
    theme: str = "dark"


def load_settings() -> Settings:
    ensure_dirs()
    if not SETTINGS_FILE.exists():
        return Settings()
    try:
        data = json.loads(SETTINGS_FILE.read_text())
        return Settings(
            backend_url=data.get("backend_url", DEFAULT_BACKEND_URL),
            api_key=data.get("api_key"),
            theme=data.get("theme", "dark"),
        )
    except Exception:
        return Settings()


def save_settings(settings: Settings) -> None:
    ensure_dirs()
    SETTINGS_FILE.write_text(json.dumps(asdict(settings), indent=2))
