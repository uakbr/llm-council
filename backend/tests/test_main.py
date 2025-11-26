import json
import tempfile
from importlib import reload
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from backend import config, main, settings, storage


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Isolate settings file
    temp_settings = tmp_path / "settings.json"
    monkeypatch.setattr(settings, "SETTINGS_FILE", temp_settings)
    settings.save_settings(
        settings.Settings(
            openrouter_api_key="sk-test",
            openrouter_api_url="https://example.com/api/v1/chat/completions",
            council_models=["m1", "m2"],
            chairman_model="chair",
        )
    )

    # Isolate storage directory
    data_dir = tmp_path / "conversations"
    data_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(storage, "DATA_DIR", str(data_dir))
    monkeypatch.setattr(config, "DATA_DIR", str(data_dir))
    reload(storage)

    return TestClient(main.app)


@pytest.fixture(autouse=True)
def stub_council(monkeypatch):
    async def fake_run_full_council(user_query: str):
        return (
            [{"model": "m1", "response": "r1"}],
            [{"model": "m1", "ranking": "FINAL RANKING:\n1. Response A", "parsed_ranking": ["Response A"]}],
            {"model": "chair", "response": "final"},
            {"label_to_model": {"Response A": "m1"}, "aggregate_rankings": [{"model": "m1", "average_rank": 1.0, "rankings_count": 1}]},
        )

    async def fake_title(content: str):
        return "Test Title"

    async def fake_stage1(content: str, council_models=None):
        return [{"model": "m1", "response": "r1"}]

    async def fake_stage2(content: str, stage1_results, council_models=None):
        return [{"model": "m1", "ranking": "FINAL RANKING:\n1. Response A", "parsed_ranking": ["Response A"]}], {"Response A": "m1"}

    async def fake_stage3(content: str, stage1_results, stage2_results, chairman_model=None):
        return {"model": chairman_model or "chair", "response": "final"}

    monkeypatch.setattr(main, "run_full_council", fake_run_full_council)
    monkeypatch.setattr(main, "generate_conversation_title", fake_title)
    monkeypatch.setattr(main, "stage1_collect_responses", fake_stage1)
    monkeypatch.setattr(main, "stage2_collect_rankings", fake_stage2)
    monkeypatch.setattr(main, "stage3_synthesize_final", fake_stage3)
    return


def test_root_health(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_settings_endpoints_update_and_redact(client):
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert data["openrouter_api_key"] is not None

    resp = client.post(
        "/api/settings",
        json={
            "openrouter_api_key": "sk-new",
            "openrouter_api_url": "https://override.com/chat/completions",
            "council_models": ["mx"],
            "chairman_model": "boss",
        },
    )
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["openrouter_api_key"].endswith("new")
    assert updated["chairman_model"] == "boss"


def test_send_message_flow(client):
    conv = client.post("/api/conversations", json={}).json()
    conv_id = conv["id"]

    resp = client.post(f"/api/conversations/{conv_id}/message", json={"content": "Hello"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["stage1"][0]["response"] == "r1"
    assert body["stage3"]["response"] == "final"


def test_send_message_stream_emits_events(client):
    conv = client.post("/api/conversations", json={}).json()
    conv_id = conv["id"]

    with client.stream("POST", f"/api/conversations/{conv_id}/message/stream", json={"content": "Hi"}) as resp:
        assert resp.status_code == 200
        content = resp.iter_lines()
        events = [line for line in content if line]

    assert any("stage1_start" in e for e in events)
    assert any("stage3_complete" in e for e in events)


def test_send_message_requires_api_key(client, monkeypatch):
    class NoKey(SimpleNamespace):
        openrouter_api_key = None

    monkeypatch.setattr(main.settings, "get_effective_settings", lambda: NoKey)

    conv = client.post("/api/conversations", json={}).json()
    conv_id = conv["id"]

    resp = client.post(f"/api/conversations/{conv_id}/message", json={"content": "Hello"})
    assert resp.status_code == 400
    assert "API key" in resp.json()["detail"]
