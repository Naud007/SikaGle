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
        weather_context: str | None = None,
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
        # NOTE (correctif bug du 29/08/2026) :
        #
        # input_type était reçu en paramètre de process() mais
        # n'était jamais transmis à self.knowledge.ask() : les
        # règles de formatage spécifiques à l'audio (pas de
        # Markdown, phrases naturelles) dans prompt_builder.py
        # ne se déclenchaient donc jamais, même pour une
        # question posée en vocal. Corrigé ci-dessous.
        #
        # NOTE (météo, 29/08/2026) :
        #
        # weather_context est un contexte optionnel, préparé en
        # amont par webhook.py à partir du profil de
        # l'agriculteur (coordonnées géocodées). Il est transmis
        # tel quel jusqu'au prompt final ; c'est Gemini qui
        # décide si la météo est pertinente pour la question
        # posée.
        #

        rag_result = self.knowledge.ask(
            question=message,
            top_k=15,
            language=language,
            input_type=input_type,
            weather_context=weather_context,
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