from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Weather:

    temperature: float | None = None

    humidity: float | None = None

    rainfall: float | None = None

    wind_speed: float | None = None

    forecast: str | None = None
