"""Controller to coordinate API calls and shared state for the GUI."""

from __future__ import annotations

import asyncio
import logging
from typing import List, Optional

from .api import CouncilAPI
from .models import Conversation, ConversationMetadata, SSEEvent
from .state import AppState

logger = logging.getLogger(__name__)


class GUIController:
    """
    Thin orchestration layer between UI and data/API.
    Keeps all side effects (network, state mutation) in one place.
    """

    def __init__(self, api: CouncilAPI, state: AppState):
        self.api = api
        self.state = state

    async def load_conversations(self) -> List[ConversationMetadata]:
        items = await self.api.list_conversations()
        self.state.set_conversations(items)
        return items

    async def select_conversation(self, conversation_id: str) -> Optional[Conversation]:
        convo = await self.api.get_conversation(conversation_id)
        self.state.set_current_conversation(convo)
        return convo

    async def create_conversation(self) -> Conversation:
        convo = await self.api.create_conversation()
        # Prepend new conversation to state list
        new_list = [ConversationMetadata.from_dict(
            {"id": convo.id, "created_at": convo.created_at, "title": convo.title, "message_count": len(convo.messages)}
        )]
        new_list.extend(self.state.conversations)
        self.state.set_conversations(new_list)
        self.state.set_current_conversation(convo)
        return convo

    async def send_and_stream(self, conversation_id: str, content: str) -> List[SSEEvent]:
        """
        Send a message and stream stage events, updating state along the way.
        Returns the list of events received.
        """
        events: List[SSEEvent] = []
        self.state.start_stream()
        try:
            async for event in self.api.stream_message(conversation_id, content):
                events.append(event)
                self.state.apply_event(event)
                if event.type == "complete":
                    break
        except Exception as exc:  # pragma: no cover - safety net
            logger.exception("Streaming failed: %s", exc)
            raise
        finally:
            # Ensure we always leave streaming mode
            self.state.end_stream()
        return events
