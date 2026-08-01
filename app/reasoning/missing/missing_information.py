from app.reasoning.models.missing_information import (
    MissingInformation,
)
from app.reasoning.models.reasoning_context import (
    ReasoningContext,
)


class MissingInformationDetector:

    def detect(
        self,
        context: ReasoningContext,
    ) -> list[MissingInformation]:

        missing: list[
            MissingInformation
        ] = []

        if context.crop.name == "inconnue":

            missing.append(
                MissingInformation(
                    field="crop",
                    question="Quelle culture est concernée ?",
                )
            )

        if not context.symptoms:

            missing.append(
                MissingInformation(
                    field="symptoms",
                    question="Quels sont les symptômes observés ?",
                )
            )

        if (
            context.memory is None
            or context.memory.location is None
        ):

            missing.append(
                MissingInformation(
                    field="location",
                    question="Dans quelle localité se trouve votre parcelle ?",
                )
            )

        return missing
