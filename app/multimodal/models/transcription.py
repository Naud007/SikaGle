from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Transcription:

    text: str

    language: str

    confidence: float
