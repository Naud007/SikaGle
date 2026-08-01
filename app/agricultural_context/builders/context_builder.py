from app.agricultural_context.calendar.crop_calendar_service import (
    CropCalendarService,
)
from app.agricultural_context.location.location_service import (
    LocationService,
)
from app.agricultural_context.models.agricultural_context import (
    AgriculturalContext,
)
from app.agricultural_context.providers.regional_knowledge_provider import (
    RegionalKnowledgeProvider,
)
from app.agricultural_context.regions.agroecological_service import (
    AgroEcologicalService,
)
from app.agricultural_context.season.season_service import (
    SeasonService,
)
from app.agricultural_context.weather.weather_service import (
    WeatherService,
)


class ContextBuilder:

    def __init__(self):

        self.location = LocationService()

        self.weather = WeatherService()

        self.season = SeasonService()

        self.calendar = CropCalendarService()

        self.zone = AgroEcologicalService()

        self.knowledge = (
            RegionalKnowledgeProvider()
        )

    def build(
        self,
        crop: str,
        department: str | None = None,
        commune: str | None = None,
    ) -> AgriculturalContext:

        location = self.location.get_location(
            department=department,
            commune=commune,
        )

        return AgriculturalContext(
            location=location,
            weather=self.weather.get_weather(
                latitude=location.latitude,
                longitude=location.longitude,
            ),
            season=self.season.detect(),
            calendar=self.calendar.get_calendar(
                crop=crop,
            ),
            agroecological_zone=self.zone.get_zone(
                department=department,
            ),
            regional_knowledge=self.knowledge.get(
                department=department,
            ),
        )
