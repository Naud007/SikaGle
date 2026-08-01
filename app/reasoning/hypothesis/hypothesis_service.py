from app.reasoning.hypothesis.hypothesis_engine import (
    HypothesisEngine,
)
from app.reasoning.models.hypothesis import (
    Hypothesis,
)
from app.reasoning.models.reasoning_context import (
    ReasoningContext,
)


class HypothesisService:

    def __init__(self):

        self.engine = (
            HypothesisEngine()
        )

    def build(
        self,
        context: ReasoningContext,
    ) -> list[Hypothesis]:

        return self.engine.build(
            context
        )
