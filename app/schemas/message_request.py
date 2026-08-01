from __future__ import annotations

from pydantic import BaseModel, Field


class MessageRequest(BaseModel):

    message: str = Field(
        min_length=1,
    )

    language: str = "fr"

    attachments: list[str] = Field(
        default_factory=list,
    )
