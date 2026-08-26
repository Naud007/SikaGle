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


class AgriculturalAssistantService:
    """
    Point d'entrée principal de SikaGlé.

    Ce service orchestre les différents moteurs du système.

    Il ne contient aucune logique agricole.
    Il coordonne uniquement :

    - la conversation ;
    - le contexte conversationnel ;
    - le contexte de raisonnement ;
    - le moteur de connaissances / RAG.

    La génération Gemini est réalisée à l'intérieur
    du RAG via ResponseGenerator.
    """

    def __init__(self):

        # =====================================================
        # CONVERSATION
        # =====================================================

        self.conversation = ConversationService()

        # =====================================================
        # CONTEXTE CONVERSATIONNEL
        # =====================================================

        self.conversation_context = (
            ContextService()
        )

        # =====================================================
        # CONTEXTE DE RAISONNEMENT
        # =====================================================

        self.reasoning_context = (
            ReasoningContextService()
        )

        # =====================================================
        # MOTEUR DE CONNAISSANCES / RAG
        # =====================================================

        self.knowledge = (
            KnowledgeService()
        )

    # =========================================================
    # TRAITEMENT PRINCIPAL
    # =========================================================

    def process(
        self,
        user_id: str,
        message: str,
        language: str = "fr",
        input_type: str = "text",
    ) -> str:

        # =====================================================
        # 1. SAUVEGARDE DU MESSAGE UTILISATEUR
        # =====================================================

        self.conversation.add_message(
            user_id=user_id,
            author="user",
            content=message,
        )

        # =====================================================
        # 2. CONTEXTE CONVERSATIONNEL
        # =====================================================

        conversation_context = (
            self.conversation_context.build(
                user_id
            )
        )

        # =====================================================
        # 3. CONTEXTE AGRICOLE / RAISONNEMENT
        # =====================================================

        reasoning_context = (
            self.reasoning_context.analyze(
                user_id=user_id,
                text=message,
            )
        )

        # =====================================================
        # 4. RECHERCHE + GÉNÉRATION RAG
        # =====================================================
        #
        # IMPORTANT :
        #
        # Le RAG réalise maintenant tout le parcours :
        #
        # question
        #    ↓
        # HybridRetriever
        #    ↓
        # documents pertinents
        #    ↓
        # ResponseGenerator
        #    ↓
        # Gemini
        #    ↓
        # réponse finale
        #
        # Il ne faut donc PAS appeler Gemini une deuxième fois
        # ici.
        #
        # NOTE (correctif performance) :
        #
        # top_k a été réduit de 20 à 8 : un prompt Gemini
        # construit à partir de 20 passages complets atteignait
        # ~60 000 caractères, ce qui provoquait des temps de
        # génération de 10 à 70 secondes et un risque accru
        # d'erreurs 429 (quota Gemini). Réduire à 8 passages
        # garde largement assez de contexte pertinent (les
        # résultats sont déjà classés par pertinence par
        # SearchEngine.merge()) tout en réduisant fortement
        # la taille du prompt.
        #

        rag_result = self.knowledge.ask(
            question=message,
            top_k=8,
            language=language,
        )

        # =====================================================
        # 5. RÉCUPÉRATION DE LA RÉPONSE RAG
        # =====================================================

        answer = rag_result.get(
            "answer",
            "",
        )

        # =====================================================
        # 6. FALLBACK
        # =====================================================

        if not answer:

            answer = (
                "Je n'ai pas pu générer une réponse."
            )

        # =====================================================
        # 7. SAUVEGARDE DE LA RÉPONSE
        # =====================================================

        self.conversation.add_message(
            user_id=user_id,
            author="assistant",
            content=answer,
        )

        # =====================================================
        # 8. RETOUR
        # =====================================================

        return answer