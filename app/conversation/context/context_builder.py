from app.conversation.models.context import (
    Context,
)
from app.conversation.memory.memory_service import (
    MemoryService,
)
from app.conversation.history.history_service import (
    HistoryService,
)


class ContextBuilder:

    def __init__(self):

        self.memory_service = MemoryService()

        self.history_service = HistoryService()

    def build(
        self,
        user_id: str,
    ) -> Context:

        memory = self.memory_service.get_or_create(
            user_id
        )

        history = self.history_service.last_messages(
            user_id=user_id,
            limit=10,
        )

        return Context(
            user_id=user_id,
            memory=memory,
            history=history,
        )
