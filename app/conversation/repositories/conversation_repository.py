from app.conversation.models.conversation import (
    Conversation,
)


class ConversationRepository:

    def __init__(self):

        self._conversations: dict[
            str,
            Conversation,
        ] = {}

    def save(
        self,
        conversation: Conversation,
    ) -> None:

        self._conversations[
            conversation.user_id
        ] = conversation

    def get(
        self,
        user_id: str,
    ) -> Conversation | None:

        return self._conversations.get(
            user_id
        )

    def exists(
        self,
        user_id: str,
    ) -> bool:

        return user_id in self._conversations

    def delete(
        self,
        user_id: str,
    ) -> None:

        self._conversations.pop(
            user_id,
            None,
        )

    def all(
        self,
    ) -> list[Conversation]:

        return list(
            self._conversations.values()
        )
