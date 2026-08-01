from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ApiError:

    code: str

    message: str

    details: dict[str, Any] = field(
        default_factory=dict,
    )
