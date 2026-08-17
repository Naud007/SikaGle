from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MessageSource(BaseModel):

    title: str = ""

    url: str = ""


class MessageResponse(BaseModel):

    message_id: str

    conversation_id: str

    response: str

    confidence: float

    sources: list[MessageSource] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )