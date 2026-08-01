from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CropCalendar:

    crop: str

    sowing_date: str | None = None

    stage: str | None = None
