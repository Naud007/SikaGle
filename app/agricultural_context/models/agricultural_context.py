from __future__ import annotations

from dataclasses import dataclass

from app.agricultural_context.models.agroecological_zone import (
    AgroEcologicalZone,
)
from app.agricultural_context.models.crop_calendar import (
    CropCalendar,
)
from app.agricultural_context.models.location import (
    Location,
)
from app.agricultural_context.models.regional_knowledge import (
    RegionalKnowledge,
)
from app.agricultural_context.models.season import (
    Season,
)
from app.agricultural_context.models.weather import (
    Weather,
)


@dataclass
class AgriculturalContext:

    location: Location

    weather: Weather

    season: Season

    calendar: CropCalendar

    agroecological_zone: AgroEcologicalZone

    regional_knowledge: RegionalKnowledge
