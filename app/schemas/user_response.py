from __future__ import annotations

from pydantic import BaseModel


class UserResponse(BaseModel):

    user_id: str

    username: str

    preferred_language: str

    phone_number: str | None = None

    email: str | None = None
