from gui.state import AppState
from gui.models import SSEEvent


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
