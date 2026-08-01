from app.reasoning.models.confidence import (
    Confidence,
)
from app.reasoning.models.evidence import (
    Evidence,
)
from app.reasoning.models.hypothesis import (
    Hypothesis,
)


class ConfidenceEstimator:

    def estimate(
        self,
        hypotheses: list[Hypothesis],
        evidences: list[Evidence],
    ) -> Confidence:

        if not hypotheses:

            return Confidence(
                score=0.0,
                level="faible",
                justification="Aucune hypothèse disponible.",
            )

        score = hypotheses[0].confidence

        if evidences:

            evidence_score = (
                sum(
                    evidence.score
                    for evidence in evidences
                )
                / len(evidences)
            )

            score = (
                score + evidence_score
            ) / 2

        if score >= 0.80:

            level = "élevé"

        elif score >= 0.50:

            level = "moyen"

        else:

            level = "faible"

        return Confidence(
            score=round(score, 2),
            level=level,
            justification=(
                "Niveau de confiance calculé à partir "
                "des hypothèses et des preuves."
            ),
        )
