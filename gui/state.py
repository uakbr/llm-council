"""In-memory state container for the desktop GUI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from . import config
from .models import (
    AssistantMessage,
    Conversation,
    ConversationMetadata,
    SSEEvent,
    Stage1Response,
    Stage2Ranking,
    Stage3Result,
)


@dataclass
class StreamStatus:
    in_flight: bool = False
    current_stage: str | None = None
    last_event: str | None = None
    cancelled: bool = False


@dataclass
class StagePayloads:
    """Latest stage outputs for the selected conversation/stream."""

    stage1: List[Stage1Response] = field(default_factory=list)
    stage2: List[Stage2Ranking] = field(default_factory=list)
    stage3: Stage3Result | None = None
    title: str | None = None
    label_to_model: Dict[str, str] = field(default_factory=dict)
    aggregate_rankings: List[Dict[str, Any]] = field(default_factory=list)


class AppState:
    """
    Lightweight state store with subscription callbacks.
    This avoids tight coupling to Qt; signals can be attached later.
    """

    def __init__(self, backend_url: str | None = None):
        self.backend_url: str = backend_url or config.DEFAULT_BACKEND_URL
        self.conversations: List[ConversationMetadata] = []
        self.current_conversation: Optional[Conversation] = None
        self.stream_status = StreamStatus()
        self.stage_payloads = StagePayloads()
        self._subscribers: List[Callable[[], None]] = []

    # Subscription -------------------------------------------------------
    def subscribe(self, callback: Callable[[], None]) -> None:
        """Register a callback that fires after state changes."""
        self._subscribers.append(callback)

    def _notify(self) -> None:
        for cb in list(self._subscribers):
            cb()

    # Mutators -----------------------------------------------------------
    def set_backend_url(self, url: str) -> None:
        self.backend_url = url
        self._notify()

    def set_conversations(self, items: List[ConversationMetadata]) -> None:
        self.conversations = items
        self._notify()

    def set_current_conversation(self, convo: Optional[Conversation]) -> None:
        self.current_conversation = convo
        if convo:
            self.stage_payloads = self._stage_payloads_from_conversation(convo)
        else:
            self.reset_stage_payloads()
        self._notify()

    def start_stream(self) -> None:
        self.stream_status = StreamStatus(in_flight=True, current_stage="starting")
        self.reset_stage_payloads()
        self._notify()

    def apply_event(self, event: SSEEvent) -> None:
        self.stream_status.in_flight = True
        self.stream_status.current_stage = event.type
        self.stream_status.last_event = event.type
        self._apply_stage_payload(event)
        self._notify()

    def end_stream(self) -> None:
        self.stream_status = StreamStatus(
            in_flight=False, current_stage=None, last_event="complete", cancelled=False
        )
        self._notify()

    def cancel_stream(self) -> None:
        self.stream_status = StreamStatus(
            in_flight=False, current_stage=None, last_event="cancelled", cancelled=True
        )
        self._notify()

    # Stage data helpers ------------------------------------------------
    def reset_stage_payloads(self) -> None:
        self.stage_payloads = StagePayloads(title=self.current_conversation.title if self.current_conversation else None)

    def _apply_stage_payload(self, event: SSEEvent) -> None:
        if event.type == "stage1_complete" and event.data is not None:
            self.stage_payloads.stage1 = [Stage1Response.from_dict(item) for item in event.data or []]
        elif event.type == "stage2_complete":
            self.stage_payloads.stage2 = [Stage2Ranking.from_dict(item) for item in event.data or []]
            meta = event.metadata or {}
            self.stage_payloads.label_to_model = meta.get("label_to_model", {}) or {}
            self.stage_payloads.aggregate_rankings = meta.get("aggregate_rankings", []) or []
        elif event.type == "stage3_complete" and event.data is not None:
            self.stage_payloads.stage3 = Stage3Result.from_dict(event.data or {})
        elif event.type == "title_complete":
            title = (event.data or {}).get("title") if event.data else None
            if title:
                self.stage_payloads.title = title
                self._apply_title_to_state(title)

    def _apply_title_to_state(self, title: str) -> None:
        if self.current_conversation:
            self.current_conversation.title = title
            for meta in self.conversations:
                if meta.id == self.current_conversation.id:
                    meta.title = title
                    break

    def _stage_payloads_from_conversation(self, convo: Conversation) -> StagePayloads:
        payloads = StagePayloads(title=convo.title)
        last_assistant: AssistantMessage | None = None
        for message in reversed(convo.messages):
            if isinstance(message, AssistantMessage):
                last_assistant = message
                break

        if last_assistant:
            payloads.stage1 = list(last_assistant.stage1)
            payloads.stage2 = list(last_assistant.stage2)
            payloads.stage3 = last_assistant.stage3
            if last_assistant.metadata:
                payloads.label_to_model = last_assistant.metadata.get("label_to_model") or {}
                payloads.aggregate_rankings = last_assistant.metadata.get("aggregate_rankings") or []
        return payloads
