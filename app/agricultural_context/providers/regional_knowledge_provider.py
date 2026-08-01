from app.agricultural_context.models.regional_knowledge import (
    RegionalKnowledge,
)


class RegionalKnowledgeProvider:

    KNOWLEDGE = {
        "Atlantique": RegionalKnowledge(
            department="Atlantique",
            common_crops=[
                "maïs",
                "tomate",
                "manioc",
            ],
            common_diseases=[
                "Rouille",
                "Mildiou",
            ],
            common_pests=[
                "Chenilles",
                "Pucerons",
            ],
            recommendations=[
                "Surveiller régulièrement les parcelles.",
                "Utiliser des semences certifiées.",
            ],
        ),
        "Borgou": RegionalKnowledge(
            department="Borgou",
            common_crops=[
                "maïs",
                "coton",
                "soja",
            ],
            common_diseases=[
                "Charbon",
            ],
            common_pests=[
                "Foreurs de tiges",
            ],
            recommendations=[
                "Respecter le calendrier cultural.",
            ],
        ),
    }

    def get(
        self,
        department: str | None,
    ) -> RegionalKnowledge:

        if department in self.KNOWLEDGE:

            return self.KNOWLEDGE[
                department
            ]

        return RegionalKnowledge(
            department=department or "Inconnu",
        )
