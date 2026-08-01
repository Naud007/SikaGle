from app.reasoning.models.hypothesis import (
    Hypothesis,
)
from app.reasoning.models.reasoning_context import (
    ReasoningContext,
)


class HypothesisEngine:

    def build(
        self,
        context: ReasoningContext,
    ) -> list[Hypothesis]:

        hypotheses: list[
            Hypothesis
        ] = []

        for symptom in context.symptoms:

            if (
                "jaune"
                in symptom.name
            ):

                hypotheses.append(
                    Hypothesis(
                        name="Carence en azote",
                        confidence=0.80,
                        justification=(
                            "Présence de feuilles jaunes."
                        ),
                    )
                )

            if (
                "tache"
                in symptom.name
            ):

                hypotheses.append(
                    Hypothesis(
                        name="Maladie foliaire",
                        confidence=0.75,
                        justification=(
                            "Présence de taches sur les feuilles."
                        ),
                    )
                )

        if not hypotheses:

            hypotheses.append(
                Hypothesis(
                    name="Hypothèse générale",
                    confidence=0.30,
                    justification=(
                        "Informations insuffisantes."
                    ),
                )
            )

        return hypotheses
