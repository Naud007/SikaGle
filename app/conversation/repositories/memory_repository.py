from app.conversation.models.memory import Memory


class MemoryRepository:

    def __init__(self):

        self._memories: dict[
            str,
            Memory,
        ] = {}

    def save(
        self,
        memory: Memory,
    ) -> None:

        self._memories[
            memory.user_id
        ] = memory

    def get(
        self,
        user_id: str,
    ) -> Memory | None:

        return self._memories.get(
            user_id
        )

    def exists(
        self,
        user_id: str,
    ) -> bool:

        return user_id in self._memories

    def delete(
        self,
        user_id: str,
    ) -> None:

        self._memories.pop(
            user_id,
            None,
        )
