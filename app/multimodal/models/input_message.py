from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class InputMessage:

    content: str

    modality: str

    channel: str

    timestamp: datetime

    user_id: str | None = None

    conversation_id: str | None = None
