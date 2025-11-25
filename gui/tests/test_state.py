from gui.state import AppState
from gui.models import Conversation, ConversationMetadata, SSEEvent


def test_state_subscriptions_and_stream_flags():
    calls = []

    def cb():
        calls.append("called")

    state = AppState()
    state.subscribe(cb)
    state.start_stream()
    assert state.stream_status.in_flight is True
    assert state.stream_status.current_stage == "starting"
    assert len(calls) == 1

    state.apply_event(SSEEvent(type="stage1_start"))
    assert state.stream_status.current_stage == "stage1_start"
    assert calls[-1] == "called"

    state.end_stream()
    assert state.stream_status.in_flight is False
    assert state.stream_status.last_event == "complete"
    assert calls[-1] == "called"

    state.cancel_stream()
    assert state.stream_status.cancelled is True
    assert state.stream_status.last_event == "cancelled"


def test_stage_payloads_update_and_title_propagation():
    state = AppState()
    meta = ConversationMetadata.from_dict(
        {"id": "c1", "created_at": "2024-01-01T00:00:00Z", "title": "Old", "message_count": 0}
    )
    convo = Conversation.from_dict(
        {"id": "c1", "created_at": "2024-01-01T00:00:00Z", "title": "Old", "messages": []}
    )
    state.set_conversations([meta])
    state.set_current_conversation(convo)

    state.start_stream()
    state.apply_event(SSEEvent(type="stage1_complete", data=[{"model": "m1", "response": "r1"}]))
    assert len(state.stage_payloads.stage1) == 1

    state.apply_event(
        SSEEvent(
            type="stage2_complete",
            data=[{"model": "m2", "ranking": "A>B", "parsed_ranking": ["A", "B"]}],
            metadata={"label_to_model": {"A": "m2"}, "aggregate_rankings": [{"model": "m2", "average_rank": 1.0, "rankings_count": 1}]},
        )
    )
    assert state.stage_payloads.label_to_model["A"] == "m2"
    assert state.stage_payloads.aggregate_rankings[0]["average_rank"] == 1.0

    state.apply_event(SSEEvent(type="stage3_complete", data={"model": "chair", "response": "final"}))
    assert state.stage_payloads.stage3.response == "final"

    state.apply_event(SSEEvent(type="title_complete", data={"title": "New Title"}))
    assert state.stage_payloads.title == "New Title"
    assert state.current_conversation.title == "New Title"
    assert state.conversations[0].title == "New Title"
    state.fail_stream("boom")
    assert state.stream_status.error == "boom"
    assert state.stream_status.last_event == "error"


def test_backend_url_and_reset_state_on_none_conversation():
    state = AppState()
    state.set_backend_url("http://example.com")
    assert state.backend_url == "http://example.com"
    state.set_api_key("token")
    assert state.api_key == "token"

    state.set_current_conversation(None)
    assert state.stage_payloads.title is None

    state.apply_event(SSEEvent(type="error", data={"message": "oops"}))
    assert state.stream_status.error == "oops"
    assert state.stream_status.last_event == "error"


def test_stage_payloads_hydrate_from_conversation():
    state = AppState()
    convo = Conversation.from_dict(
        {
            "id": "c2",
            "created_at": "2024-01-01T00:00:00Z",
            "title": "Existing",
            "messages": [
                {"role": "user", "content": "hello"},
                {
                    "role": "assistant",
                    "stage1": [{"model": "m1", "response": "stage1"}],
                    "stage2": [{"model": "m2", "ranking": "A>B"}],
                    "stage3": {"model": "chair", "response": "done"},
                    "metadata": {"aggregate_rankings": [{"model": "m2", "average_rank": 1.5, "rankings_count": 2}]},
                },
            ],
        }
    )
    state.set_current_conversation(convo)
    assert len(state.stage_payloads.stage1) == 1
    assert len(state.stage_payloads.stage2) == 1
    assert state.stage_payloads.stage3.response == "done"
    assert state.stage_payloads.aggregate_rankings[0]["rankings_count"] == 2
