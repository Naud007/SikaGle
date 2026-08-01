from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Evidence:

    source: str

    excerpt: str

    score: float
