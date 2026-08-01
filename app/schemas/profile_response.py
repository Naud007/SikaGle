from __future__ import annotations

from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):

    user_id: str

    preferred_language: str

    location: str | None = None

    main_crops: list[str] = Field(
        default_factory=list,
    )

    persona: str | None = None
