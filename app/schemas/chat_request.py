from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):

    conversation_id: str | None = None

    user_id: str

    message: str = Field(
        min_length=1,
    )

    channel: str = "api"

    language: str = "fr"

    attachments: list[str] = Field(
        default_factory=list,
    )
