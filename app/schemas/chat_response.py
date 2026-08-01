from __future__ import annotations

from pydantic import BaseModel, Field


class ChatResponse(BaseModel):

    conversation_id: str

    message_id: str

    response: str

    sources: list[str] = Field(
        default_factory=list,
    )

    confidence: float

    metadata: dict = Field(
        default_factory=dict,
    )
