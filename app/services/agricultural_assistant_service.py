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


class AgriculturalAssistantService:
    """
    Point d'entrée principal de SikaGlé.

    Ce service orchestre tous les moteurs du système.

    Il ne contient aucune logique agricole.
    Il coordonne uniquement les différents moteurs.
    """

    def __init__(self):

        self.conversation = ConversationService()

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

    def process(
        self,
        user_id: str,
        message: str,
    ) -> str:

        #
        # 1. Sauvegarde du message utilisateur
        #

        self.conversation.add_message(
            user_id=user_id,
            author="user",
            content=message,
        )

        #
        # 2. Construction du contexte conversationnel
        #

        conversation_context = (
            self.conversation_context.build(
                user_id
            )
        )

        #
        # 3. Construction du contexte agricole
        #

        reasoning_context = (
            self.reasoning_context.analyze(
                user_id=user_id,
                text=message,
            )
        )

        #
        # 4. Recherche documentaire
        #

        rag_result = self.knowledge.ask(
            question=message,
            top_k=5,
        )

        #
        # 5. Construction du prompt
        #

        prompt = self.build_prompt(
            conversation_context=conversation_context,
            reasoning_context=reasoning_context,
            rag_result=rag_result,
            user_message=message,
        )

        #
        # 6. Génération Gemini
        #

        answer = self.llm.generate_text(
            prompt
        )

        #
        # 7. Sauvegarde de la réponse
        #

        self.conversation.add_message(
            user_id=user_id,
            author="assistant",
            content=answer,
        )

        return answer

    def build_prompt(
        self,
        conversation_context,
        reasoning_context,
        rag_result,
        user_message: str,
    ) -> str:

        sources = "\n".join(

            f"- {source}"

            for source in rag_result.get(
                "sources",
                [],
            )

        )

        documents = rag_result.get(
            "answer",
            "",
        )

        return f"""
Tu es SikaGlé.

Tu es un conseiller agricole intelligent.

Tu dois :

- raisonner avant de répondre ;
- utiliser les connaissances fournies ;
- ne jamais inventer une information ;
- expliquer simplement ;
- citer les sources si elles existent.

Question de l'utilisateur :

{user_message}

Connaissances retrouvées :

{documents}

Sources :

{sources}

Rédige maintenant la meilleure réponse possible.
"""