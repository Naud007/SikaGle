from datetime import datetime

from app.agricultural_context.models.season import (
    Season,
)


class SeasonDetector:

    def detect(
        self,
        date: datetime | None = None,
    ) -> Season:

        date = date or datetime.utcnow()

        month = date.month

        if month in (
            4,
            5,
            6,
            7,
            8,
            9,
            10,
        ):

            return Season(
                name="Saison des pluies",
                period="Humide",
            )

        return Season(
            name="Saison sèche",
            period="Sèche",
        )
