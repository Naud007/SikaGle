from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import uuid4


@dataclass
class Session:

    user_id: str

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    expires_at: datetime = field(
        default_factory=lambda: (
            datetime.utcnow()
            + timedelta(hours=24)
        )
    )

    active: bool = True

    def touch(
        self,
    ) -> None:

        self.updated_at = datetime.utcnow()

    def expire(
        self,
    ) -> None:

        self.active = False

    @property
    def expired(
        self,
    ) -> bool:

        return (
            datetime.utcnow()
            >= self.expires_at
        )
