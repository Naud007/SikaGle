from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Translation:

    source_language: str

    target_language: str

    original_text: str

    translated_text: str

    confidence: float
