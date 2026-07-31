from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Memory:

    user_id: str

    crop: str | None = None

    symptoms: list[str] = field(
        default_factory=list
    )

    language: str | None = None

    location: str | None = None

    preferences: dict = field(
        default_factory=dict
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    def touch(
        self,
    ) -> None:

        self.updated_at = datetime.utcnow()
