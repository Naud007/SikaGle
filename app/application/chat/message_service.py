from uuid import uuid4

from app.schemas.message_request import (
    MessageRequest,
)
from app.schemas.message_response import (
    MessageResponse,
)


class MessageService:

    def send(
        self,
        conversation_id: str,
        request: MessageRequest,
    ) -> MessageResponse:

        #
        # Implémentation V1 :
        # Stub prêt à être connecté
        # au Conversation Orchestrator.
        #

        return MessageResponse(
            message_id=str(uuid4()),
            conversation_id=conversation_id,
            response="",
            confidence=0.0,
            sources=[],
            metadata={},
        )

    def history(
        self,
        conversation_id: str,
    ) -> list[MessageResponse]:

        return []
