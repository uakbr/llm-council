"""Typed models used by the desktop GUI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class Stage1Response:
    model: str
    response: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Stage1Response":
        return Stage1Response(
            model=data.get("model", ""),
            response=data.get("response", ""),
        )


@dataclass
class Stage2Ranking:
    model: str
    ranking: str
    parsed_ranking: List[str] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Stage2Ranking":
        return Stage2Ranking(
            model=data.get("model", ""),
            ranking=data.get("ranking", ""),
            parsed_ranking=list(data.get("parsed_ranking", []) or []),
        )


@dataclass
class Stage3Result:
    model: str
    response: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Stage3Result":
        return Stage3Result(
            model=data.get("model", ""),
            response=data.get("response", ""),
        )


@dataclass
class AssistantMessage:
    stage1: List[Stage1Response]
    stage2: List[Stage2Ranking]
    stage3: Stage3Result
    metadata: Dict[str, Any] | None = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AssistantMessage":
        return AssistantMessage(
            stage1=[Stage1Response.from_dict(x) for x in data.get("stage1", [])],
            stage2=[Stage2Ranking.from_dict(x) for x in data.get("stage2", [])],
            stage3=Stage3Result.from_dict(data.get("stage3", {})),
            metadata=data.get("metadata"),
        )


@dataclass
class UserMessage:
    role: str
    content: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "UserMessage":
        return UserMessage(
            role=data.get("role", "user"),
            content=data.get("content", ""),
        )


Message = Union[UserMessage, AssistantMessage]


@dataclass
class ConversationMetadata:
    id: str
    created_at: str
    title: str
    message_count: int

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ConversationMetadata":
        return ConversationMetadata(
            id=data.get("id", ""),
            created_at=data.get("created_at", ""),
            title=data.get("title", "New Conversation"),
            message_count=int(data.get("message_count", 0)),
        )


@dataclass
class Conversation:
    id: str
    created_at: str
    title: str
    messages: List[Message]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Conversation":
        parsed_messages: List[Message] = []
        for item in data.get("messages", []):
            if item.get("role") == "assistant":
                parsed_messages.append(AssistantMessage.from_dict(item))
            else:
                parsed_messages.append(UserMessage.from_dict(item))

        return Conversation(
            id=data.get("id", ""),
            created_at=data.get("created_at", ""),
            title=data.get("title", "New Conversation"),
            messages=parsed_messages,
        )


@dataclass
class AggregateRank:
    model: str
    average_rank: float
    rankings_count: int

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AggregateRank":
        return AggregateRank(
            model=data.get("model", ""),
            average_rank=float(data.get("average_rank", 0.0)),
            rankings_count=int(data.get("rankings_count", 0)),
        )


@dataclass
class SSEEvent:
    """Structured Server-Sent Event payload."""

    type: str
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    raw: str | None = None
