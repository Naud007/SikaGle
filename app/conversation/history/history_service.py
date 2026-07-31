from app.conversation.models.message import (
    Message,
)
from app.conversation.services.conversation_service import (
    ConversationService,
)


class HistoryService:

    def __init__(self):

        self.service = ConversationService()

    def history(
        self,
        user_id: str,
    ) -> list[Message]:

        conversation = self.service.get_or_create(
            user_id
        )

        return conversation.messages

    def last_messages(
        self,
        user_id: str,
        limit: int = 10,
    ) -> list[Message]:

        history = self.history(
            user_id
        )

        return history[-limit:]
