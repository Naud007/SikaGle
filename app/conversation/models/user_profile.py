from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class UserProfile:

    user_id: str

    name: str | None = None

    phone_number: str | None = None

    language: str | None = None

    region: str | None = None

    crops: list[str] = field(
        default_factory=list
    )

    farm_type: str | None = None

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    def touch(
        self,
    ) -> None:

        self.updated_at = datetime.utcnow()
