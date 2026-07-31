from app.conversation.memory.memory_service import (
    MemoryService,
)
from app.conversation.models.memory import (
    Memory,
)


class MemoryManager:

    def __init__(self):

        self.service = MemoryService()

    def get(
        self,
        user_id: str,
    ) -> Memory:

        return self.service.get_or_create(
            user_id,
        )

    def update(
        self,
        user_id: str,
        **kwargs,
    ) -> Memory:

        return self.service.update(
            user_id,
            **kwargs,
        )
