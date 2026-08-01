from uuid import uuid4

from app.schemas.chat_request import (
    ChatRequest,
)
from app.schemas.chat_response import (
    ChatResponse,
)


class ChatService:

    def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:

        #
        # Implémentation V1 :
        # Stub prêt à être connecté au
        # Conversation Orchestrator.
        #

        return ChatResponse(
            conversation_id=(
                request.conversation_id
                or str(uuid4())
            ),
            message_id=str(uuid4()),
            response="",
            sources=[],
            confidence=0.0,
            metadata={},
        )
