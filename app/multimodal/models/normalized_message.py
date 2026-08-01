from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class NormalizedMessage:

    message_id: str

    conversation_id: str

    user_id: str

    channel: str

    modality: str

    detected_language: str

    normalized_text: str

    original_content: str

    attachments: list[Any] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    timestamp: datetime | None = None
