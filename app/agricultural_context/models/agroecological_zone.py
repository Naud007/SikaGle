from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AgroEcologicalZone:

    name: str

    climate: str

    characteristics: list[str]
