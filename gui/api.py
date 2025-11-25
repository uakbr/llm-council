"""Async client for the LLM Council backend."""

from __future__ import annotations

import json
import asyncio
from typing import AsyncGenerator, Dict, List, Optional

import httpx

from .config import DEFAULT_BACKEND_URL
from .models import (
    Conversation,
    ConversationMetadata,
    SSEEvent,
)


class CouncilAPI:
    """Convenience wrapper around the FastAPI endpoints."""

    def __init__(
        self,
        base_url: str = DEFAULT_BACKEND_URL,
        api_key: str | None = None,
        client: Optional[httpx.AsyncClient] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._owns_client = client is None
        timeout = httpx.Timeout(connect=10.0, read=320.0, write=30.0, pool=10.0)
        self._client = client or httpx.AsyncClient(timeout=timeout)

    # Lifecycle ----------------------------------------------------------
    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> "CouncilAPI":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    # Helpers ------------------------------------------------------------
    def _headers(self) -> Dict[str, str]:
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    # REST calls ---------------------------------------------------------
    async def health(self) -> Dict:
        resp = await self._client.get(f"{self.base_url}/", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    async def list_conversations(self) -> List[ConversationMetadata]:
        resp = await self._client.get(f"{self.base_url}/api/conversations", headers=self._headers())
        resp.raise_for_status()
        return [ConversationMetadata.from_dict(item) for item in resp.json()]

    async def create_conversation(self) -> Conversation:
        resp = await self._client.post(f"{self.base_url}/api/conversations", json={}, headers=self._headers())
        resp.raise_for_status()
        return Conversation.from_dict(resp.json())

    async def get_conversation(self, conversation_id: str) -> Conversation:
        resp = await self._client.get(
            f"{self.base_url}/api/conversations/{conversation_id}",
            headers=self._headers(),
        )
        resp.raise_for_status()
        return Conversation.from_dict(resp.json())

    async def send_message(self, conversation_id: str, content: str) -> Dict:
        resp = await self._client.post(
            f"{self.base_url}/api/conversations/{conversation_id}/message",
            json={"content": content},
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    # Streaming ----------------------------------------------------------
    async def stream_message(
        self,
        conversation_id: str,
        content: str,
        cancel_event: asyncio.Event | None = None,
    ) -> AsyncGenerator[SSEEvent, None]:
        """
        Stream council stages via SSE.

        Yields:
            SSEEvent objects as they arrive.
        """
        url = f"{self.base_url}/api/conversations/{conversation_id}/message/stream"
        async with self._client.stream(
            "POST",
            url,
            json={"content": content},
            headers={"Accept": "text/event-stream", **self._headers()},
        ) as resp:
            resp.raise_for_status()
            buffer = ""
            async for line in resp.aiter_lines():
                if cancel_event and cancel_event.is_set():
                    break
                if line is None:
                    continue
                if line.startswith("data:"):
                    buffer += line[len("data:") :].strip()
                elif line == "":
                    if buffer:
                        event = self._parse_event(buffer)
                        if event:
                            yield event
                        buffer = ""
                else:
                    continue
            if buffer and not (cancel_event and cancel_event.is_set()):
                event = self._parse_event(buffer)
                if event:
                    yield event

    @staticmethod
    def _parse_event(raw_payload: str) -> Optional[SSEEvent]:
        """Parse a single SSE data block into an SSEEvent."""
        try:
            payload = json.loads(raw_payload)
        except json.JSONDecodeError:
            return SSEEvent(type="raw", raw=raw_payload)

        return SSEEvent(
            type=payload.get("type", "message"),
            data=payload.get("data"),
            metadata=payload.get("metadata"),
            raw=raw_payload,
        )
