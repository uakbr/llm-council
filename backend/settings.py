"""Local settings management for LLM Council.

Stores editable settings (OpenRouter credentials and model choices) in
`data/settings.json` so users can change them at runtime via the API/UI
without touching environment variables. Falls back to environment defaults
from `config.py` when a value has not been saved.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

import httpx
from pydantic import BaseModel, Field, ValidationError, field_validator

from . import config

# Use the parent of the conversation directory (data/) for settings storage
DATA_ROOT = Path(config.DATA_DIR).parent or Path(".")
SETTINGS_FILE = DATA_ROOT / "settings.json"


class Settings(BaseModel):
    """Persisted (or default) settings."""

    openrouter_api_key: Optional[str] = None
    openrouter_api_url: str = config.OPENROUTER_API_URL
    council_models: List[str] = Field(default_factory=lambda: list(config.COUNCIL_MODELS))
    chairman_model: str = config.CHAIRMAN_MODEL

    @field_validator("openrouter_api_url")
    def validate_url(cls, value: str) -> str:
        if not value:
            raise ValueError("openrouter_api_url must not be empty")
        return value


class OpenRouterCredentials(BaseModel):
    """Minimal credentials payload used by the OpenRouter client and tests."""

    api_key: Optional[str]
    api_url: str


def _ensure_data_root() -> None:
    """Make sure the data directory exists."""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)


def redact_api_key(api_key: Optional[str]) -> Optional[str]:
    """Return a masked version of the API key for safe display."""
    if not api_key:
        return None
    if len(api_key) <= 8:
        return "*" * max(len(api_key) - 4, 1) + api_key[-4:]
    return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]


def _load_settings_raw() -> Settings:
    """Load settings from disk or return defaults."""
    _ensure_data_root()
    if not SETTINGS_FILE.exists():
        return Settings()

    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return Settings(**data)
    except (json.JSONDecodeError, ValidationError):
        # Invalid file contents – fall back to defaults
        return Settings()


def save_settings(new_settings: Settings) -> Settings:
    """Persist validated settings to disk."""
    _ensure_data_root()
    with SETTINGS_FILE.open("w", encoding="utf-8") as f:
        json.dump(new_settings.model_dump(), f, indent=2)
    return new_settings


def update_settings(partial: Dict) -> Settings:
    """
    Update settings using a partial dict and persist them.
    Fields omitted remain unchanged/defaulted.
    """
    current = _load_settings_raw()
    updated = current.model_copy(update=partial, deep=True)
    return save_settings(updated)


def load_settings(redact: bool = False) -> Settings | Dict[str, Optional[str]]:
    """
    Load settings for API use.

    Args:
        redact: When True, mask the API key for safe return to clients.
    """
    settings_obj = _load_settings_raw()
    if not redact:
        return settings_obj

    return {
        "openrouter_api_key": redact_api_key(settings_obj.openrouter_api_key),
        "openrouter_api_url": settings_obj.openrouter_api_url,
        "council_models": settings_obj.council_models,
        "chairman_model": settings_obj.chairman_model,
    }


def get_effective_settings() -> Settings:
    """
    Return settings with fallbacks to environment defaults.

    - API key: settings file > environment variable
    - API URL / models: settings file (already defaulted to config)
    """
    settings_obj = _load_settings_raw()
    if not settings_obj.openrouter_api_key:
        settings_obj.openrouter_api_key = config.OPENROUTER_API_KEY

    # Ensure models/URL are never empty
    if not settings_obj.council_models:
        settings_obj.council_models = list(config.COUNCIL_MODELS)
    if not settings_obj.chairman_model:
        settings_obj.chairman_model = config.CHAIRMAN_MODEL
    if not settings_obj.openrouter_api_url:
        settings_obj.openrouter_api_url = config.OPENROUTER_API_URL

    return settings_obj


def get_openrouter_credentials(override: Optional[Dict] = None) -> OpenRouterCredentials:
    """
    Compose OpenRouter credentials with optional overrides (used by the
    test-connection endpoint).
    """
    effective = get_effective_settings()
    override = override or {}
    api_key = override.get("openrouter_api_key") or effective.openrouter_api_key
    api_url = override.get("openrouter_api_url") or effective.openrouter_api_url
    return OpenRouterCredentials(api_key=api_key, api_url=api_url)


async def test_openrouter_connection(creds: OpenRouterCredentials) -> Dict[str, Optional[str]]:
    """
    Perform a lightweight connectivity check against the OpenRouter models
    endpoint using the provided credentials.
    """
    if not creds.api_key:
        return {"ok": False, "error": "Missing OpenRouter API key"}

    # Try to derive a models endpoint from the base URL; default to OpenRouter's
    models_url = creds.api_url.rstrip("/")
    if models_url.endswith("/chat/completions"):
        models_url = models_url.rsplit("/chat/completions", 1)[0]
    models_url = f"{models_url}/models"

    headers = {"Authorization": f"Bearer {creds.api_key}"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(models_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            models = data.get("data") or []
            return {"ok": True, "model_count": len(models)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
