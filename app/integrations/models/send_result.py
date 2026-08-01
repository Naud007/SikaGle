from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SendResult:

    message_id: str

    status: str

    success: bool
