"""Qt bridge exposing AppState/Controller to QML."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import asdict
from typing import Any, Dict, List

from PySide6.QtCore import QObject, Property, Signal
from qasync import asyncSlot

from .controller import GUIController
from .state import AppState, StagePayloads, StreamStatus
from .stream import StreamRunner
from .models import AssistantMessage, Conversation, ConversationMetadata, UserMessage

logger = logging.getLogger(__name__)


def _meta_to_dict(meta: ConversationMetadata, streaming: bool) -> Dict[str, Any]:
    return {
        "id": meta.id,
        "title": meta.title,
        "message_count": meta.message_count,
        "streaming": streaming,
    }


def _conversation_to_dict(convo: Conversation | None) -> Dict[str, Any] | None:
    if convo is None:
        return None

    def _message_to_dict(msg: AssistantMessage | UserMessage) -> Dict[str, Any]:
        if isinstance(msg, AssistantMessage):
            payload = asdict(msg)
            return {"role": "assistant", **payload}
        return {"role": "user", "content": msg.content}

    return {
        "id": convo.id,
        "title": convo.title,
        "created_at": convo.created_at,
        "messages": [_message_to_dict(m) for m in convo.messages],
    }


def _stream_status_to_dict(status: StreamStatus) -> Dict[str, Any]:
    return {
        "inFlight": status.in_flight,
        "currentStage": status.current_stage,
        "lastEvent": status.last_event,
        "cancelled": status.cancelled,
    }


def _stage_payload_to_dict(payloads: StagePayloads) -> Dict[str, Any]:
    return {
        "stage1": [asdict(item) for item in payloads.stage1],
        "stage2": [asdict(item) for item in payloads.stage2],
        "stage3": asdict(payloads.stage3) if payloads.stage3 else None,
        "title": payloads.title,
        "labelToModel": payloads.label_to_model,
        "aggregateRankings": payloads.aggregate_rankings,
    }


class QmlBridge(QObject):
    """Expose controller/state to QML via signals + properties."""

    conversationsChanged = Signal()
    currentConversationChanged = Signal()
    streamStatusChanged = Signal()
    stageDataChanged = Signal()
    backendUrlChanged = Signal()
    busyChanged = Signal()
    errorOccurred = Signal(str)

    def __init__(self, controller: GUIController, stream_runner: StreamRunner, state: AppState):
        super().__init__()
        self.controller = controller
        self.stream_runner = stream_runner
        self.state = state
        self._busy = False
        self.state.subscribe(self._on_state_change)

    # Property helpers --------------------------------------------------
    def _on_state_change(self) -> None:
        self.conversationsChanged.emit()
        self.currentConversationChanged.emit()
        self.streamStatusChanged.emit()
        self.stageDataChanged.emit()
        self.backendUrlChanged.emit()

    def _get_conversations(self) -> List[Dict[str, Any]]:
        current_id = self.state.current_conversation.id if self.state.current_conversation else None
        streaming = self.state.stream_status.in_flight
        return [
            _meta_to_dict(meta, streaming and meta.id == current_id)
            for meta in self.state.conversations
        ]

    conversations = Property(list, fget=_get_conversations, notify=conversationsChanged)

    def _get_current_conversation(self) -> Dict[str, Any] | None:
        return _conversation_to_dict(self.state.current_conversation)

    currentConversation = Property("QVariant", fget=_get_current_conversation, notify=currentConversationChanged)

    def _get_stream_status(self) -> Dict[str, Any]:
        return _stream_status_to_dict(self.state.stream_status)

    streamStatus = Property("QVariant", fget=_get_stream_status, notify=streamStatusChanged)

    def _get_stage_data(self) -> Dict[str, Any]:
        return _stage_payload_to_dict(self.state.stage_payloads)

    stageData = Property("QVariant", fget=_get_stage_data, notify=stageDataChanged)

    def _get_backend_url(self) -> str:
        return self.state.backend_url

    backendUrl = Property(str, fget=_get_backend_url, notify=backendUrlChanged)

    def _get_busy(self) -> bool:
        return self._busy

    busy = Property(bool, fget=_get_busy, notify=busyChanged)

    def _set_busy(self, value: bool) -> None:
        if self._busy != value:
            self._busy = value
            self.busyChanged.emit()

    def _wrap_errors(self, coro, *, rethrow: bool = False):
        async def _wrapper():
            try:
                self._set_busy(True)
                return await coro
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("GUI bridge error: %s", exc)
                self.errorOccurred.emit(str(exc))
                if rethrow:
                    raise
                return None
            finally:
                self._set_busy(False)

        return _wrapper()

    # Slots exposed to QML ---------------------------------------------
    @asyncSlot(result=bool)
    async def loadConversations(self) -> bool:
        await self._wrap_errors(self.controller.load_conversations())
        if not self.state.current_conversation and self.state.conversations:
            await self._wrap_errors(
                self.controller.select_conversation(self.state.conversations[0].id)
            )
        return True

    @asyncSlot(result=str)
    async def newConversation(self) -> str:
        convo = await self._wrap_errors(self.controller.create_conversation(), rethrow=True)
        return convo.id if convo else ""

    @asyncSlot(str, result=bool)
    async def selectConversation(self, conversation_id: str) -> bool:
        await self._wrap_errors(self.controller.select_conversation(conversation_id))
        return True

    @asyncSlot(str, result=bool)
    async def sendMessage(self, content: str) -> bool:
        if not content or not content.strip():
            return False
        # Ensure a conversation exists
        if not self.state.current_conversation:
            await self.newConversation()
        convo_id = self.state.current_conversation.id if self.state.current_conversation else None
        if not convo_id:
            return False

        task = await self._wrap_errors(
            self.stream_runner.start(convo_id, content),
            rethrow=True,
        )
        if isinstance(task, asyncio.Task):
            task.add_done_callback(self._log_task_error)
        return True

    @asyncSlot(result=bool)
    async def cancelStream(self) -> bool:
        await self._wrap_errors(self.stream_runner.cancel())
        return True

    # Utilities ---------------------------------------------------------
    @staticmethod
    def _log_task_error(task: asyncio.Task) -> None:  # pragma: no cover - callback guard
        if task.cancelled():
            return
        exc = task.exception()
        if exc:
            logger.error("Stream task error: %s", exc)
