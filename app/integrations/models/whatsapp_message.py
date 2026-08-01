from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WhatsAppMessage:

    message_id: str

    from_number: str

    message_type: str

    content: str

    timestamp: str

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
