from __future__ import annotations

from dataclasses import dataclass, field

from app.conversation.models.memory import Memory
from app.conversation.models.message import Message


@dataclass
class Context:

    user_id: str

    memory: Memory

    history: list[Message] = field(
        default_factory=list
    )

    profile: dict = field(
        default_factory=dict
    )

    weather: dict = field(
        default_factory=dict
    )
