from __future__ import annotations

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):

    message_id: str

    conversation_id: str

    response: str

    confidence: float

    sources: list[str] = Field(
        default_factory=list,
    )

    metadata: dict = Field(
        default_factory=dict,
    )
