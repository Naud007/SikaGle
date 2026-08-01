from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DetectedLanguage:

    code: str

    name: str

    confidence: float
