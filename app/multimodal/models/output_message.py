from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class OutputMessage:

    modality: str

    content: str | None = None

    audio_path: Path | None = None

    language: str = "fr"
