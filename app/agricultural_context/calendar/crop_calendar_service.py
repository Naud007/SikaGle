from app.agricultural_context.models.crop_calendar import (
    CropCalendar,
)


class CropCalendarService:

    DEFAULT_STAGES = {
        "maïs": "Croissance",
        "riz": "Tallage",
        "manioc": "Développement végétatif",
        "tomate": "Floraison",
        "soja": "Croissance",
    }

    def get_calendar(
        self,
        crop: str,
        sowing_date: str | None = None,
    ) -> CropCalendar:

        stage = self.DEFAULT_STAGES.get(
            crop.lower(),
            "Inconnu",
        )

        return CropCalendar(
            crop=crop,
            sowing_date=sowing_date,
            stage=stage,
        )
