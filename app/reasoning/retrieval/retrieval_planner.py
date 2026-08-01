from app.reasoning.models.reasoning_context import (
    ReasoningContext,
)
from app.reasoning.models.retrieval_query import (
    RetrievalQuery,
)


class RetrievalPlanner:

    def build(
        self,
        context: ReasoningContext,
    ) -> RetrievalQuery:

        return RetrievalQuery(
            crop=context.crop.name,
            symptoms=[
                symptom.name
                for symptom in context.symptoms
            ],
            intent=context.intent.name,
            location=(
                context.memory.location
                if context.memory
                else None
            ),
            keywords=[
                context.crop.name,
                *[
                    symptom.name
                    for symptom in context.symptoms
                ],
                context.intent.name,
            ],
        )
