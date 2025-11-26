import tempfile
from importlib import reload
from pathlib import Path

import pytest

from backend import config, settings


def with_temp_settings_file():
    """Swap settings storage to a temp file for isolation."""
    temp_dir = tempfile.TemporaryDirectory()
    new_file = Path(temp_dir.name) / "settings.json"
    original_file = settings.SETTINGS_FILE
    settings.SETTINGS_FILE = new_file
    return temp_dir, original_file


def restore_settings_file(temp_dir, original_file):
    temp_dir.cleanup()
    settings.SETTINGS_FILE = original_file
    reload(settings)


def test_save_and_load_settings_roundtrip():
    temp_dir, original_file = with_temp_settings_file()
    try:
        original = settings.Settings(
            openrouter_api_key="abc123",
            openrouter_api_url="https://example.com/api",
            council_models=["m1", "m2"],
            chairman_model="chair",
        )
        settings.save_settings(original)

        loaded = settings.load_settings()
        assert isinstance(loaded, settings.Settings)
        assert loaded.openrouter_api_key == "abc123"
        assert loaded.council_models == ["m1", "m2"]
        assert loaded.chairman_model == "chair"
    finally:
        restore_settings_file(temp_dir, original_file)


def test_get_effective_settings_falls_back_to_env():
    temp_dir, original_file = with_temp_settings_file()
    original_env_key = config.OPENROUTER_API_KEY
    try:
        config.OPENROUTER_API_KEY = "env-key"
        effective = settings.get_effective_settings()
        assert effective.openrouter_api_key == "env-key"
    finally:
        config.OPENROUTER_API_KEY = original_env_key
        restore_settings_file(temp_dir, original_file)


@pytest.mark.asyncio
async def test_test_connection_handles_missing_key():
    creds = settings.OpenRouterCredentials(api_key=None, api_url="https://openrouter.ai/api/v1/chat/completions")
    result = await settings.test_openrouter_connection(creds)
    assert result["ok"] is False
    assert "Missing" in result["error"]


@pytest.mark.asyncio
async def test_test_connection_success_with_fake_client(monkeypatch):
    class FakeResponse:
        def __init__(self):
            self._data = {"data": ["m1", "m2", "m3"]}

        def raise_for_status(self):
            return None

        def json(self):
            return self._data

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.calls = []

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, headers=None):
            self.calls.append((url, headers))
            return FakeResponse()

    monkeypatch.setattr(settings.httpx, "AsyncClient", FakeClient)

    creds = settings.OpenRouterCredentials(api_key="key-123", api_url="https://example.com/chat/completions")
    result = await settings.test_openrouter_connection(creds)
    assert result["ok"] is True
    assert result["model_count"] == 3
