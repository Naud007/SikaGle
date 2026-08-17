from uuid import uuid4

from app.application.orchestrator.application_orchestrator import (
    ApplicationOrchestrator,
)
from app.conversation.services.conversation_service import (
    ConversationService,
)
from app.schemas.message_request import (
    MessageRequest,
)
from app.schemas.message_response import (
    MessageResponse,
)


class MessageService:

    def __init__(self):

        self.orchestrator = (
            ApplicationOrchestrator()
        )

        self.conversation = (
            ConversationService()
        )

    def send(
        self,
        conversation_id: str,
        request: MessageRequest,
    ) -> MessageResponse:

        conversation = (
            self.conversation.get_or_create(
                conversation_id
            )
        )

        result = self.orchestrator.message(
            user_id=conversation.user_id,
            message=request.message,
            language=request.language,
            channel="api",
        )

        return MessageResponse(
            message_id=str(uuid4()),
            conversation_id=conversation.id,
            response=result.response,
            confidence=result.confidence,
            sources=result.sources,
            metadata=result.metadata,
        )

    def history(
        self,
        conversation_id: str,
    ) -> list[MessageResponse]:

        conversation = (
            self.conversation.get_or_create(
                conversation_id
            )
        )

        return [
            MessageResponse(
                message_id=message.id,
                conversation_id=conversation.id,
                response=message.content,
                confidence=0.0,
                sources=[],
                metadata={
                    "author": message.author,
                    "message_type": message.message_type,
                    "created_at": (
                        message.created_at.isoformat()
                    ),
                },
            )
            for message in conversation.messages
        ]