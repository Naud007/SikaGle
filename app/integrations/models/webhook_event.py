from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WebhookEvent:

    event_type: str

    payload: dict[str, Any]

    timestamp: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
