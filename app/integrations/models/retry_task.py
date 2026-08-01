from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RetryTask:

    task_id: str

    operation: str

    payload: dict[str, Any]

    attempts: int = 0

    max_attempts: int = 3

    next_retry_at: datetime | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
