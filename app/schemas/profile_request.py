from __future__ import annotations

from pydantic import BaseModel, Field


class ProfileRequest(BaseModel):

    preferred_language: str = "fr"

    location: str | None = None

    main_crops: list[str] = Field(
        default_factory=list,
    )

    persona: str | None = None
