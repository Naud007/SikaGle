from __future__ import annotations

from dataclasses import dataclass, field

from app.conversation.models.memory import Memory
from app.conversation.models.message import Message
from app.reasoning.models.crop import Crop
from app.reasoning.models.intent import Intent
from app.reasoning.models.symptom import Symptom


@dataclass
class ReasoningContext:

    user_id: str

    intent: Intent

    crop: Crop

    symptoms: list[Symptom] = field(
        default_factory=list
    )

    memory: Memory | None = None

    history: list[Message] = field(
        default_factory=list
    )

    weather: dict = field(
        default_factory=dict
    )
