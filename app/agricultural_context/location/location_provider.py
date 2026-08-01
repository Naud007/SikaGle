from app.agricultural_context.models.location import (
    Location,
)


class LocationProvider:

    def get_location(
        self,
        country: str = "Bénin",
        department: str | None = None,
        commune: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> Location:

        return Location(
            country=country,
            department=department,
            commune=commune,
            latitude=latitude,
            longitude=longitude,
        )
