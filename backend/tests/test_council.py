import pytest

from backend import council


@pytest.mark.asyncio
async def test_stage1_collect_responses_filters_none(monkeypatch):
    async def fake_query(models, messages, timeout=120.0):
        return {"m1": {"content": "ok"}, "m2": None}

    monkeypatch.setattr(council, "query_models_parallel", fake_query)
    results = await council.stage1_collect_responses("hi", ["m1", "m2"])
    assert results == [{"model": "m1", "response": "ok"}]


@pytest.mark.asyncio
async def test_stage2_collect_rankings_parses(monkeypatch):
    async def fake_query(models, messages, timeout=120.0):
        # Ranking prompt includes "FINAL RANKING:" so we can ignore messages content
        return {models[0]: {"content": "Analysis\nFINAL RANKING:\n1. Response A\n2. Response B"}}

    monkeypatch.setattr(council, "query_models_parallel", fake_query)

    stage1_results = [
        {"model": "alpha", "response": "A"},
        {"model": "beta", "response": "B"},
    ]
    rankings, label_map = await council.stage2_collect_rankings("hi", stage1_results, ["judge"])

    assert label_map["Response A"] == "alpha"
    assert rankings[0]["parsed_ranking"] == ["Response A", "Response B"]


@pytest.mark.asyncio
async def test_stage3_synthesize_final_fallback(monkeypatch):
    async def fake_query_model(model, messages, timeout=120.0, client=None):
        return None

    monkeypatch.setattr(council, "query_model", fake_query_model)

    result = await council.stage3_synthesize_final("q", [], [], "chair")
    assert result["model"] == "chair"
    assert "Unable" in result["response"]


@pytest.mark.asyncio
async def test_run_full_council_happy_path(monkeypatch):
    async def fake_query_models(models, messages, timeout=120.0):
        if "FINAL RANKING:" in messages[0]["content"]:
            return {models[0]: {"content": "Rank\nFINAL RANKING:\n1. Response A\n2. Response B"}}
        return {model: {"content": f"resp-{model}"} for model in models}

    async def fake_query_model(model, messages, timeout=120.0, client=None):
        return {"content": "final-answer"}

    monkeypatch.setattr(council, "query_models_parallel", fake_query_models)
    monkeypatch.setattr(council, "query_model", fake_query_model)

    stage1, stage2, stage3, metadata = await council.run_full_council("question")

    assert len(stage1) == len(council.get_effective_settings().council_models)
    assert stage2[0]["parsed_ranking"] == ["Response A", "Response B"]
    assert stage3["response"] == "final-answer"
    assert metadata["aggregate_rankings"][0]["model"] in council.get_effective_settings().council_models


@pytest.mark.asyncio
async def test_run_full_council_handles_no_stage1(monkeypatch):
    async def empty_stage1(user_query, council_models=None):
        return []

    monkeypatch.setattr(council, "stage1_collect_responses", empty_stage1)

    stage1, stage2, stage3, metadata = await council.run_full_council("question")

    assert stage1 == []
    assert stage2 == []
    assert stage3["model"] == "error"
