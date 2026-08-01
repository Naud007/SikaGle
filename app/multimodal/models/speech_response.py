from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SpeechResponse:

    audio_path: Path

    language: str

    voice: str

    speed: float = 1.0
