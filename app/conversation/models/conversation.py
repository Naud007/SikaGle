from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from app.conversation.models.message import Message


@dataclass
class Conversation:

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

    active: bool = True

    messages: list[Message] = field(
        default_factory=list
    )

    def add_message(
        self,
        message: Message,
    ) -> None:

        self.messages.append(
            message
        )

        self.updated_at = datetime.utcnow()

    def close(
        self,
    ) -> None:

        self.active = False

        self.updated_at = datetime.utcnow()
