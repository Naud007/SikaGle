from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WebhookVerification:

    mode: str

    challenge: str

    verify_token: str

    verified: bool = False
