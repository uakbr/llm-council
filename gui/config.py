"""Configuration helpers for the desktop GUI."""

from pathlib import Path

APP_NAME = "LLM Council GUI"
DEFAULT_BACKEND_URL = "http://localhost:8001"

CONFIG_DIR = Path.home() / ".llm-council"
SETTINGS_FILE = CONFIG_DIR / "config.json"
LOG_FILE = CONFIG_DIR / "gui.log"


def ensure_dirs() -> None:
    """Create config directory if missing."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
