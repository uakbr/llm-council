from gui import models


def test_stage_models_from_dict_roundtrip():
    raw_stage1 = {"model": "m1", "response": "hi"}
    raw_stage2 = {"model": "m2", "ranking": "FINAL RANKING:\n1. Response A", "parsed_ranking": ["Response A"]}
    raw_stage3 = {"model": "chair", "response": "final"}

    s1 = models.Stage1Response.from_dict(raw_stage1)
    s2 = models.Stage2Ranking.from_dict(raw_stage2)
    s3 = models.Stage3Result.from_dict(raw_stage3)

    assert s1.model == "m1" and s1.response == "hi"
    assert s2.parsed_ranking == ["Response A"]
    assert s3.model == "chair" and s3.response == "final"


def test_conversation_from_dict_parses_message_types():
    raw = {
        "id": "abc",
        "created_at": "2024-01-01T00:00:00Z",
        "title": "Test",
        "messages": [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "stage1": [], "stage2": [], "stage3": {"model": "c", "response": "r"}},
        ],
    }
    convo = models.Conversation.from_dict(raw)
    assert convo.id == "abc"
    assert len(convo.messages) == 2
    assert isinstance(convo.messages[0], models.UserMessage)
    assert isinstance(convo.messages[1], models.AssistantMessage)


def test_sse_event_parsing_raw_payload():
    raw = "not-json"
    ev = models.SSEEvent(type="raw", raw=raw)
    assert ev.type == "raw"
    assert ev.raw == raw
