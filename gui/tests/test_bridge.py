import asyncio

import pytest
from PySide6.QtCore import QCoreApplication
from PySide6.QtTest import QSignalSpy

from gui.bridge import QmlBridge
from gui.models import Conversation, ConversationMetadata, SSEEvent
from gui.state import AppState


@pytest.fixture(scope="module")
def qt_app():
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


class FakeController:
    def __init__(self, state: AppState):
        self.state = state
        self.created = 0

    async def load_conversations(self):
        items = [
            ConversationMetadata.from_dict(
                {
                    "id": "c1",
                    "created_at": "2024-01-01T00:00:00Z",
                    "title": "First",
                    "message_count": 0,
                }
            )
        ]
        self.state.set_conversations(items)
        return items

    async def create_conversation(self):
        self.created += 1
        convo = Conversation.from_dict(
            {
                "id": f"new-{self.created}",
                "created_at": "2024-01-02T00:00:00Z",
                "title": "New Conversation",
                "messages": [],
            }
        )
        self.state.set_conversations([
            ConversationMetadata.from_dict(
                {
                    "id": convo.id,
                    "created_at": convo.created_at,
                    "title": convo.title,
                    "message_count": 0,
                }
            )
        ] + self.state.conversations)
        self.state.set_current_conversation(convo)
        return convo

    async def select_conversation(self, convo_id: str):
        convo = Conversation.from_dict(
            {
                "id": convo_id,
                "created_at": "2024-01-03T00:00:00Z",
                "title": "Selected",
                "messages": [
                    {
                        "role": "assistant",
                        "stage1": [{"model": "m1", "response": "one"}],
                        "stage2": [{"model": "m2", "ranking": "A>B"}],
                        "stage3": {"model": "chair", "response": "final"},
                    }
                ],
            }
        )
        self.state.set_current_conversation(convo)
        return convo


class FakeStreamRunner:
    def __init__(self, state: AppState):
        self.state = state
        self.started = False
        self.cancelled = False

    async def start(self, conversation_id: str, content: str):
        self.started = True

        async def _run():
            self.state.start_stream()
            self.state.apply_event(SSEEvent(type="stage1_complete", data=[{"model": "m1", "response": content}]))
            self.state.end_stream()
            return []

        return asyncio.create_task(_run())

    async def cancel(self):
        self.cancelled = True
        self.state.cancel_stream()


@pytest.mark.asyncio
async def test_bridge_loads_and_exposes_conversations(qt_app):
    state = AppState()
    bridge = QmlBridge(FakeController(state), FakeStreamRunner(state), state)

    spy = QSignalSpy(bridge.conversationsChanged)
    await bridge.loadConversations()
    await asyncio.sleep(0)

    assert spy.count() >= 1
    assert len(bridge.conversations) == 1
    assert bridge.conversations[0]["title"] == "First"


@pytest.mark.asyncio
async def test_bridge_send_message_runs_stream_and_updates_stage(qt_app):
    state = AppState()
    controller = FakeController(state)
    bridge = QmlBridge(controller, FakeStreamRunner(state), state)

    await bridge.newConversation()
    await bridge.sendMessage("hello")
    await asyncio.sleep(0.05)

    assert state.stage_payloads.stage1[0].response == "hello"
    assert state.stream_status.in_flight is False


@pytest.mark.asyncio
async def test_bridge_select_conversation_hydrates_stage_data(qt_app):
    state = AppState()
    controller = FakeController(state)
    bridge = QmlBridge(controller, FakeStreamRunner(state), state)

    await bridge.loadConversations()
    await bridge.selectConversation("c2")

    assert bridge.stageData["stage1"][0]["response"] == "one"
    assert bridge.stageData["stage3"]["response"] == "final"
