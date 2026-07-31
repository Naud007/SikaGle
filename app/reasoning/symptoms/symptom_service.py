from app.reasoning.models.symptom import (
    Symptom,
)
from app.reasoning.symptoms.symptom_extractor import (
    SymptomExtractor,
)


class SymptomService:

    def __init__(self):

        self.extractor = SymptomExtractor()

    def extract(
        self,
        text: str,
    ) -> list[Symptom]:

        return self.extractor.extract(
            text
        )
