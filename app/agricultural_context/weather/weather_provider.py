from app.agricultural_context.models.weather import (
    Weather,
)


class WeatherProvider:

    def get_weather(
        self,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> Weather:

        return Weather(
            temperature=None,
            humidity=None,
            rainfall=None,
            wind_speed=None,
            forecast=None,
        )
