from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WhatsAppTemplate:

    name: str

    language: str

    body: str

    category: str

    parameters: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
