from app.reasoning.models.missing_information import (
    MissingInformation,
)


class QuestionBuilder:

    def build(
        self,
        missing: list[MissingInformation],
    ) -> list[str]:

        return [
            item.question
            for item in missing
        ]
