from app.agricultural_context.location.location_provider import (
    LocationProvider,
)
from app.agricultural_context.models.location import (
    Location,
)


class LocationService:

    def __init__(self):

        self.provider = LocationProvider()

    def get_location(
        self,
        country: str = "Bénin",
        department: str | None = None,
        commune: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> Location:

        return self.provider.get_location(
            country=country,
            department=department,
            commune=commune,
            latitude=latitude,
            longitude=longitude,
        )
