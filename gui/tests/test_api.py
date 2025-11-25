import asyncio
import json
from typing import Optional
import asyncio

import httpx
import pytest

from gui.api import CouncilAPI
from gui.models import SSEEvent


def _mock_transport(with_long_stream: bool = False):
    convo = {
        "id": "c1",
        "created_at": "2024-01-01T00:00:00Z",
        "title": "New Conversation",
        "messages": [],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/":
            return httpx.Response(200, json={"status": "ok"})

        if path == "/api/conversations" and request.method == "GET":
            return httpx.Response(200, json=[{**convo, "message_count": 0}])

        if path == "/api/conversations" and request.method == "POST":
            return httpx.Response(200, json=convo)

        if path == f"/api/conversations/{convo['id']}" and request.method == "GET":
            return httpx.Response(200, json=convo)

        if path.endswith("/message") and request.method == "POST":
            return httpx.Response(
                200,
                json={
                    "stage1": [{"model": "m1", "response": "hi"}],
                    "stage2": [],
                    "stage3": {"model": "chair", "response": "final"},
                    "metadata": {},
                },
            )

        if path.endswith("/message/stream") and request.method == "POST":
            if with_long_stream:
                body = (
                    'data: {"type": "stage1_start"}\n\n'
                    'data: {"type": "stage1_complete"}\n\n'
                    'data: {"type": "stage2_start"}\n\n'
                    'data: {"type": "stage2_complete"}\n\n'
                    'data: {"type": "complete"}\n\n'
                )
            else:
                body = (
                    'data: {"type": "stage1_start"}\n\n'
                    'data: {"type": "stage1_complete", "data": {"ok": true}}\n\n'
                    'data: {"type": "complete"}\n\n'
                )
            return httpx.Response(200, text=body)

        return httpx.Response(404, json={"detail": "not found"})

    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_rest_calls_and_stream_events():
    transport = _mock_transport()
    async with httpx.AsyncClient(transport=transport) as client:
        api = CouncilAPI(base_url="http://test", client=client)

        health = await api.health()
        assert health["status"] == "ok"

        convos = await api.list_conversations()
        assert len(convos) == 1

        created = await api.create_conversation()
        assert created.id == "c1"

        fetched = await api.get_conversation("c1")
        assert fetched.id == "c1"

        non_stream = await api.send_message("c1", "hello")
        assert non_stream["stage3"]["model"] == "chair"

        events = []
        async for ev in api.stream_message("c1", "hello"):
            events.append(ev.type)

        assert events == ["stage1_start", "stage1_complete", "complete"]


def test_parse_event_handles_invalid_json():
    ev = CouncilAPI._parse_event("not-json")
    assert isinstance(ev, SSEEvent)
    assert ev.type == "raw"


@pytest.mark.asyncio
async def test_stream_message_honors_cancel_event():
    transport = _mock_transport(with_long_stream=True)
    async with httpx.AsyncClient(transport=transport) as client:
        api = CouncilAPI(base_url="http://test", client=client)
        cancel = asyncio.Event()
        events = []
        async for ev in api.stream_message("c1", "hello", cancel_event=cancel):
            events.append(ev.type)
            cancel.set()  # cancel after first event
        # Only the first event should be received because cancel stops the loop
        assert events == ["stage1_start"]
