from pathlib import Path

from gui import persistence
from gui import config


def test_settings_round_trip(tmp_path, monkeypatch):
    # Redirect config paths to temp dir
    cfg_dir = tmp_path / ".llm-council"
    monkeypatch.setattr(config, "CONFIG_DIR", cfg_dir)
    monkeypatch.setattr(config, "SETTINGS_FILE", cfg_dir / "config.json")
    monkeypatch.setattr(persistence, "SETTINGS_FILE", cfg_dir / "config.json")

    loaded = persistence.load_settings()
    assert loaded.backend_url == config.DEFAULT_BACKEND_URL

    loaded.backend_url = "http://example.com"
    loaded.api_key = "secret"
    persistence.save_settings(loaded)

    reread = persistence.load_settings()
    assert reread.backend_url == "http://example.com"
    assert reread.api_key == "secret"
    assert (cfg_dir / "config.json").exists()
