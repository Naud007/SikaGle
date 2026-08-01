from __future__ import annotations

from pydantic import BaseModel, Field


class UserRequest(BaseModel):

    username: str = Field(
        min_length=3,
    )

    preferred_language: str = "fr"

    phone_number: str | None = None

    email: str | None = None
