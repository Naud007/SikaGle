from app.reasoning.models.evidence import (
    Evidence,
)
from app.reasoning.models.hypothesis import (
    Hypothesis,
)
from app.reasoning.models.response_plan import (
    ResponsePlan,
)


class ResponsePlanner:

    def build(
        self,
        hypotheses: list[Hypothesis],
        evidences: list[Evidence],
    ) -> ResponsePlan:

        main = hypotheses[0]

        secondary = hypotheses[1:]

        recommendations = [
            (
                "Recueillir davantage d'informations "
                "avant toute intervention."
            )
        ]

        return ResponsePlan(
            summary=(
                "Analyse terminée."
            ),
            main_hypothesis=main,
            secondary_hypotheses=secondary,
            evidences=evidences,
            recommendations=recommendations,
        )
