from app.reasoning.models.intent import (
    Intent,
)


class IntentDetector:

    KEYWORDS = {
        "diagnostic": [
            "maladie",
            "symptôme",
            "jaune",
            "tache",
            "attaque",
            "parasite",
            "insecte",
            "pourriture",
        ],
        "traitement": [
            "traiter",
            "traitement",
            "soigner",
            "pulvériser",
        ],
        "prévention": [
            "prévenir",
            "éviter",
            "protéger",
        ],
        "fertilisation": [
            "engrais",
            "fertiliser",
            "azote",
            "npk",
        ],
        "irrigation": [
            "arroser",
            "eau",
            "irrigation",
        ],
        "calendrier": [
            "quand",
            "semer",
            "planter",
            "récolter",
        ],
    }

    def detect(
        self,
        text: str,
    ) -> Intent:

        text = text.lower()

        for intent, keywords in self.KEYWORDS.items():

            if any(
                keyword in text
                for keyword in keywords
            ):
                return Intent(
                    name=intent,
                    confidence=0.80,
                )

        return Intent(
            name="information",
            confidence=0.50,
        )
