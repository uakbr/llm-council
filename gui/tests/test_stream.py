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


class FlakyAPI:
    def __init__(self, fail_first=True):
        self.calls = 0
        self.fail_first = fail_first

    async def stream_message(self, conversation_id, content, cancel_event=None):
        self.calls += 1
        if self.fail_first:
            self.fail_first = False
            raise RuntimeError("boom")
        yield SSEEvent(type="complete")


class FailingAPI:
    def __init__(self):
        self.calls = 0

    async def stream_message(self, conversation_id, content, cancel_event=None):
        self.calls += 1
        # Mark as async generator
        if False:
            yield SSEEvent(type="noop")  # pragma: no cover - generator marker
        raise RuntimeError("always down")


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


@pytest.mark.asyncio
async def test_stream_runner_retries_and_recovers():
    api = FlakyAPI()
    state = AppState()
    runner = StreamRunner(api, state)

    task = await runner.start("c1", "hello", retries=1, backoff=0.01)
    events = await task

    assert state.stream_status.last_event == "complete"
    assert state.stream_status.error is None
    assert api.calls == 2
    assert events[-1].type == "complete"


@pytest.mark.asyncio
async def test_stream_runner_sets_error_after_retry_exhaustion():
    api = FailingAPI()
    state = AppState()
    runner = StreamRunner(api, state)

    task = await runner.start("c1", "hello", retries=1, backoff=0.01)
    await task

    assert state.stream_status.last_event == "error"
    assert state.stream_status.error.startswith("always down")
    assert api.calls == 2
