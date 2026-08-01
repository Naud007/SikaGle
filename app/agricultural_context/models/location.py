from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Location:

    country: str

    department: str | None = None

    commune: str | None = None

    latitude: float | None = None

    longitude: float | None = None
