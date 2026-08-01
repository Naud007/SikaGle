from app.reasoning.context.context_analyzer import (
    ContextAnalyzer,
)
from app.reasoning.models.reasoning_context import (
    ReasoningContext,
)


class ContextService:

    def __init__(self):

        self.analyzer = ContextAnalyzer()

    def analyze(
        self,
        user_id: str,
        text: str,
    ) -> ReasoningContext:

        return self.analyzer.analyze(
            user_id=user_id,
            text=text,
        )
