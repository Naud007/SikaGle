from app.reasoning.models.crop import (
    Crop,
)


class CropDetector:

    CROPS = [
        "maïs",
        "riz",
        "manioc",
        "tomate",
        "soja",
        "igname",
        "piment",
        "gombo",
        "coton",
        "ananas",
        "banane",
        "niébé",
        "arachide",
        "sorgho",
    ]

    def detect(
        self,
        text: str,
    ) -> Crop:

        text = text.lower()

        for crop in self.CROPS:

            if crop in text:

                return Crop(
                    name=crop,
                    confidence=0.90,
                )

        return Crop(
            name="inconnue",
            confidence=0.0,
        )
