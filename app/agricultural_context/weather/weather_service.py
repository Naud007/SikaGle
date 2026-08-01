from app.agricultural_context.models.weather import (
    Weather,
)
from app.agricultural_context.weather.weather_provider import (
    WeatherProvider,
)


class WeatherService:

    def __init__(self):

        self.provider = WeatherProvider()

    def get_weather(
        self,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> Weather:

        return self.provider.get_weather(
            latitude=latitude,
            longitude=longitude,
        )
