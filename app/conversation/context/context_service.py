from app.conversation.context.context_builder import (
    ContextBuilder,
)
from app.conversation.models.context import (
    Context,
)


class ContextService:

    def __init__(self):

        self.builder = ContextBuilder()

    def build(
        self,
        user_id: str,
    ) -> Context:

        return self.builder.build(
            user_id
        )
