from uuid import uuid4

from app.application.orchestrator.application_orchestrator import (
    ApplicationOrchestrator,
)

from app.schemas.chat_request import (
    ChatRequest,
)

from app.schemas.chat_response import (
    ChatResponse,
)


class ChatService:
    """
    Service applicatif pour les requêtes /chat.

    Il délègue le traitement réel à
    ApplicationOrchestrator.
    """

    def __init__(self):

        self.orchestrator = (
            ApplicationOrchestrator()
        )

    def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:

        result = self.orchestrator.chat(
            user_id=request.user_id,
            message=request.message,
            language=request.language,
            channel=request.channel,
        )

        return ChatResponse(
            conversation_id=(
                request.conversation_id
                or str(uuid4())
            ),

            message_id=str(uuid4()),

            response=result.response,

            sources=result.sources,

            confidence=result.confidence,

            metadata=result.metadata,
        )