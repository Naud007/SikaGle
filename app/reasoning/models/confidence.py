from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Confidence:

    score: float

    level: str

    justification: str
