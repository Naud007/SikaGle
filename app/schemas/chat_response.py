from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.schemas.message_response import MessageSource


class ChatResponse(BaseModel):

    conversation_id: str

    message_id: str

    response: str

    sources: list[MessageSource] = Field(
        default_factory=list,
    )

    confidence: float

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )