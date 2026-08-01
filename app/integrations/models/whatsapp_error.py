from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WhatsAppError:

    code: str

    message: str

    details: dict[str, Any] = field(
        default_factory=dict
    )

    retryable: bool = False
