from __future__ import annotations

from app.conversation.services.conversation_service import (
    ConversationService,
)
from app.conversation.context.context_service import (
    ContextService,
)
from app.reasoning.context.context_service import (
    ContextService as ReasoningContextService,
)
from app.services.knowledge_service import (
    KnowledgeService,
)
from app.ai.gemini_client import (
    GeminiClient,
)

from app.application.orchestrator.pipeline import (
    ConversationPipeline,
)


class ApplicationOrchestrator:
    """
    Orchestrateur principal de l'application SikaGlé.

    Il coordonne les différents moteurs sans contenir
    lui-même la logique agricole.

    Flux :

    Request
        ↓
    Pipeline
        ↓
    Conversation
        ↓
    Context
        ↓
    Reasoning
        ↓
    Knowledge / RAG
        ↓
    Gemini
        ↓
    Response
    """

    def __init__(self):

        self.conversation = (
            ConversationService()
        )

        self.conversation_context = (
            ContextService()
        )

        self.reasoning_context = (
            ReasoningContextService()
        )

        self.knowledge = (
            KnowledgeService()
        )

        self.llm = GeminiClient()

        self.pipeline = ConversationPipeline(
            conversation_service=self.conversation,
            conversation_context_service=(
                self.conversation_context
            ),
            reasoning_context_service=(
                self.reasoning_context
            ),
            knowledge_service=self.knowledge,
            llm=self.llm,
        )

    # =========================================================
    # CHAT
    # =========================================================

    def chat(
        self,
        user_id: str,
        message: str,
        language: str = "fr",
        channel: str = "api",
    ):

        return self.pipeline.run(
            user_id=user_id,
            message=message,
            language=language,
            channel=channel,
        )

    # =========================================================
    # MESSAGE
    # =========================================================

    def message(
        self,
        user_id: str,
        message: str,
        language: str = "fr",
        channel: str = "api",
    ):

        return self.pipeline.run(
            user_id=user_id,
            message=message,
            language=language,
            channel=channel,
        )