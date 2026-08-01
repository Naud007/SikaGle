from datetime import datetime

from app.agricultural_context.models.season import (
    Season,
)
from app.agricultural_context.season.season_detector import (
    SeasonDetector,
)


class SeasonService:

    def __init__(self):

        self.detector = SeasonDetector()

    def detect(
        self,
        date: datetime | None = None,
    ) -> Season:

        return self.detector.detect(
            date=date,
        )
