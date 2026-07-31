from app.conversation.models.conversation import (
    Conversation,
)
from app.conversation.models.message import (
    Message,
)
from app.conversation.repositories.conversation_repository import (
    ConversationRepository,
)


class ConversationService:

    def __init__(self):

        self.repository = ConversationRepository()

    def get_or_create(
        self,
        user_id: str,
    ) -> Conversation:

        conversation = self.repository.get(
            user_id
        )

        if conversation is None:

            conversation = Conversation(
                user_id=user_id,
            )

            self.repository.save(
                conversation
            )

        return conversation

    def add_message(
        self,
        user_id: str,
        author: str,
        content: str,
        message_type: str = "text",
    ) -> Message:

        conversation = self.get_or_create(
            user_id
        )

        message = Message(
            conversation_id=conversation.id,
            author=author,
            content=content,
            message_type=message_type,
        )

        conversation.add_message(
            message
        )

        self.repository.save(
            conversation
        )

        return message
