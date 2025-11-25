"""Streaming runner to bridge API SSE to state/UI with cancellation."""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, List, Optional

from .api import CouncilAPI
from .models import SSEEvent
from .state import AppState

EventCallback = Callable[[SSEEvent], Awaitable[None]] | Callable[[SSEEvent], None]


class StreamRunner:
    def __init__(self, api: CouncilAPI, state: AppState):
        self.api = api
        self.state = state
        self._task: Optional[asyncio.Task] = None
        self._cancel_event: Optional[asyncio.Event] = None

    async def start(
        self,
        conversation_id: str,
        content: str,
        on_event: EventCallback | None = None,
    ) -> asyncio.Task:
        """Start streaming; cancels previous stream if running."""
        await self.cancel()
        self._cancel_event = asyncio.Event()

        async def runner():
            self.state.start_stream()
            events: List[SSEEvent] = []
            try:
                async for event in self.api.stream_message(
                    conversation_id, content, cancel_event=self._cancel_event
                ):
                    events.append(event)
                    if on_event:
                        res = on_event(event)
                        if asyncio.iscoroutine(res):
                            await res
                    self.state.apply_event(event)
                    if event.type == "complete":
                        break
            finally:
                if self._cancel_event and self._cancel_event.is_set():
                    self.state.cancel_stream()
                else:
                    self.state.end_stream()
            return events

        self._task = asyncio.create_task(runner())
        return self._task

    async def cancel(self) -> None:
        """Signal cancellation and wait for current task to settle."""
        if self._cancel_event and not self._cancel_event.is_set():
            self._cancel_event.set()
        if self._task:
            try:
                await self._task
            except asyncio.CancelledError:
                # Surface cancelled state to observers
                self.state.cancel_stream()
        self._task = None
        self._cancel_event = None
