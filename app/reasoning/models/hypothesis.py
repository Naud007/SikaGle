from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Hypothesis:

    name: str

    confidence: float

    justification: str
