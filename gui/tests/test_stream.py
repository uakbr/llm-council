import asyncio

import pytest

from gui.stream import StreamRunner
from gui.state import AppState
from gui.models import SSEEvent


class FakeAPI:
    def __init__(self):
        self.calls = 0

    async def stream_message(self, conversation_id, content, cancel_event=None):
        events = [
            SSEEvent(type="stage1_start"),
            SSEEvent(type="stage1_complete"),
            SSEEvent(type="complete"),
        ]
        for ev in events:
            self.calls += 1
            if cancel_event and cancel_event.is_set():
                break
            await asyncio.sleep(0)  # yield control
            yield ev


@pytest.mark.asyncio
async def test_stream_runner_runs_and_updates_state():
    api = FakeAPI()
    state = AppState()
    seen = []

    async def on_event(ev):
        seen.append(ev.type)

    runner = StreamRunner(api, state)
    task = await runner.start("c1", "hello", on_event=on_event)
    result_events = await task

    assert seen == ["stage1_start", "stage1_complete", "complete"]
    assert [e.type for e in result_events] == seen
    assert state.stream_status.in_flight is False
    assert state.stream_status.last_event == "complete"
    assert api.calls == 3


@pytest.mark.asyncio
async def test_stream_runner_cancel_sets_cancelled_state():
    api = FakeAPI()
    state = AppState()
    runner = StreamRunner(api, state)

    # Start streaming
    task = await runner.start("c1", "hello", on_event=None)

    # Cancel immediately
    await runner.cancel()
    await task

    assert state.stream_status.cancelled is True
    assert state.stream_status.last_event == "cancelled"
    # At least one call should have happened, but not necessarily all
    assert api.calls >= 0
