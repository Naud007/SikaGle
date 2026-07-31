from app.conversation.models.memory import Memory
from app.conversation.repositories.memory_repository import (
    MemoryRepository,
)


class MemoryService:

    def __init__(self):

        self.repository = MemoryRepository()

    def get_or_create(
        self,
        user_id: str,
    ) -> Memory:

        memory = self.repository.get(
            user_id
        )

        if memory is None:

            memory = Memory(
                user_id=user_id,
            )

            self.repository.save(
                memory,
            )

        return memory

    def update(
        self,
        user_id: str,
        **kwargs,
    ) -> Memory:

        memory = self.get_or_create(
            user_id,
        )

        for key, value in kwargs.items():

            if hasattr(memory, key):

                setattr(
                    memory,
                    key,
                    value,
                )

        memory.touch()

        self.repository.save(
            memory,
        )

        return memory
