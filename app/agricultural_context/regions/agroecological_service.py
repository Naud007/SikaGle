from app.agricultural_context.models.agroecological_zone import (
    AgroEcologicalZone,
)


class AgroEcologicalService:

    ZONES = {
        "Atlantique": AgroEcologicalZone(
            name="Zone côtière",
            climate="Subéquatorial",
            characteristics=[
                "Humidité élevée",
                "Deux saisons des pluies",
            ],
        ),
        "Borgou": AgroEcologicalZone(
            name="Zone soudanienne",
            climate="Soudanien",
            characteristics=[
                "Saison sèche marquée",
                "Cultures céréalières",
            ],
        ),
    }

    def get_zone(
        self,
        department: str | None,
    ) -> AgroEcologicalZone:

        if department in self.ZONES:

            return self.ZONES[
                department
            ]

        return AgroEcologicalZone(
            name="Zone inconnue",
            climate="Inconnu",
            characteristics=[],
        )
