"""In-memory state container for the desktop GUI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from . import config
from .models import Conversation, ConversationMetadata, SSEEvent


@dataclass
class StreamStatus:
    in_flight: bool = False
    current_stage: str | None = None
    last_event: str | None = None
    cancelled: bool = False


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
        self._notify()

    def start_stream(self) -> None:
        self.stream_status = StreamStatus(in_flight=True, current_stage="starting")
        self._notify()

    def apply_event(self, event: SSEEvent) -> None:
        self.stream_status.in_flight = True
        self.stream_status.current_stage = event.type
        self.stream_status.last_event = event.type
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
