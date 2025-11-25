import pytest

from gui.controller import GUIController
from gui.state import AppState
from gui.models import ConversationMetadata, Conversation, SSEEvent


class FakeAPI:
    def __init__(self):
        self.stream_called = False

    async def list_conversations(self):
        return [
            ConversationMetadata.from_dict(
                {
                    "id": "c1",
                    "created_at": "2024-01-01T00:00:00Z",
                    "title": "One",
                    "message_count": 0,
                }
            )
        ]

    async def get_conversation(self, convo_id):
        return Conversation.from_dict(
            {
                "id": convo_id,
                "created_at": "2024-01-01T00:00:00Z",
                "title": "One",
                "messages": [],
            }
        )

    async def create_conversation(self):
        return Conversation.from_dict(
            {
                "id": "new",
                "created_at": "2024-01-02T00:00:00Z",
                "title": "New Conversation",
                "messages": [],
            }
        )

    async def stream_message(self, conversation_id, content):
        self.stream_called = True
        events = [
            SSEEvent(type="stage1_start"),
            SSEEvent(type="stage1_complete"),
            SSEEvent(type="complete"),
        ]
        for ev in events:
            yield ev


@pytest.mark.asyncio
async def test_controller_loads_and_sets_state():
    api = FakeAPI()
    state = AppState()
    controller = GUIController(api, state)

    items = await controller.load_conversations()
    assert len(items) == 1
    assert state.conversations[0].id == "c1"

    convo = await controller.select_conversation("c1")
    assert state.current_conversation.id == "c1"
    assert convo.id == "c1"


@pytest.mark.asyncio
async def test_controller_create_conversation_prepends_and_sets_current():
    api = FakeAPI()
    state = AppState()
    controller = GUIController(api, state)

    await controller.load_conversations()
    created = await controller.create_conversation()

    assert created.id == "new"
    assert state.current_conversation.id == "new"
    assert state.conversations[0].id == "new"
    assert state.conversations[1].id == "c1"


@pytest.mark.asyncio
async def test_controller_stream_updates_state_and_terminates():
    api = FakeAPI()
    state = AppState()
    controller = GUIController(api, state)

    events = await controller.send_and_stream("c1", "hello")
    assert api.stream_called is True
    assert [e.type for e in events] == ["stage1_start", "stage1_complete", "complete"]
    assert state.stream_status.in_flight is False
    assert state.stream_status.last_event == "complete"
