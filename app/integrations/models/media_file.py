from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class MediaFile:

    media_id: str

    media_type: str

    file_path: Path

    mime_type: str

    downloaded: bool = False
