from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Crop:

    name: str

    confidence: float = 0.0
