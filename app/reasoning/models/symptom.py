from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Symptom:

    name: str

    confidence: float = 0.0
