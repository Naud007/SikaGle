from app.reasoning.models.symptom import (
    Symptom,
)


class SymptomExtractor:

    SYMPTOMS = [
        "feuilles jaunes",
        "jaunissement",
        "taches",
        "flétrissement",
        "pourriture",
        "insectes",
        "chenilles",
        "trous",
        "dessèchement",
        "racines noires",
        "fruits noirs",
        "moisissure",
    ]

    def extract(
        self,
        text: str,
    ) -> list[Symptom]:

        text = text.lower()

        symptoms: list[Symptom] = []

        for symptom in self.SYMPTOMS:

            if symptom in text:

                symptoms.append(
                    Symptom(
                        name=symptom,
                        confidence=0.90,
                    )
                )

        return symptoms
