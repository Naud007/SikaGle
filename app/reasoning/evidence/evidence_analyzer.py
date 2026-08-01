from app.reasoning.models.evidence import (
    Evidence,
)


class EvidenceAnalyzer:

    def analyze(
        self,
        results: list[dict],
    ) -> list[Evidence]:

        evidences: list[
            Evidence
        ] = []

        for result in results:

            evidences.append(
                Evidence(
                    source=result.get(
                        "source",
                        "Inconnue",
                    ),
                    excerpt=result.get(
                        "document",
                        "",
                    )[:500],
                    score=result.get(
                        "score",
                        0.0,
                    ),
                )
            )

        evidences.sort(
            key=lambda evidence: evidence.score,
            reverse=True,
        )

        return evidences
