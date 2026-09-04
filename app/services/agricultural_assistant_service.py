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

    # =========================================================
    # NOMBRE MAXIMUM DE MESSAGES D'HISTORIQUE INCLUS DANS LE
    # PROMPT (au-delà de ce que ContextBuilder récupère déjà,
    # une deuxième limite ici pour garder le prompt raisonnable)
    # =========================================================

    MAX_HISTORY_MESSAGES_IN_PROMPT = 6

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
        # 1. CONTEXTE CONVERSATIONNEL (AVANT de sauvegarder le
        #    nouveau message, pour que l'historique ne contienne
        #    que les messages PRÉCÉDENTS, pas le message actuel)
        #
        # NOTE (correctif, 04/09/2026) :
        #
        # ContextService/ReasoningContextService existaient déjà
        # et étaient appelés, mais leur résultat n'était jamais
        # transmis à knowledge.ask() — SikaGlé traitait chaque
        # message comme isolé, sans mémoire de la conversation
        # en cours. Corrigé ci-dessous : les deux contextes sont
        # maintenant formatés en texte et transmis jusqu'au
        # prompt final.
        # =====================================================

        conversation_context = (
            self.conversation_context.build(
                user_id
            )
        )

        # =====================================================
        # 2. CONTEXTE AGRICOLE / RAISONNEMENT
        # =====================================================

        reasoning_context = (
            self.reasoning_context.analyze(
                user_id=user_id,
                text=message,
            )
        )

        # =====================================================
        # 3. SAUVEGARDE DU MESSAGE UTILISATEUR (après avoir
        #    construit les contextes ci-dessus)
        # =====================================================

        self.conversation.add_message(
            user_id=user_id,
            author="user",
            content=message,
        )

        # =====================================================
        # 4. FORMATAGE DE L'HISTORIQUE EN TEXTE
        # =====================================================

        conversation_history_text = (
            self._format_history(
                conversation_context.history
            )
        )

        # =====================================================
        # 5. FORMATAGE DU RAISONNEMENT EN TEXTE
        # =====================================================

        reasoning_summary_text = (
            self._format_reasoning(
                reasoning_context
            )
        )

        # =====================================================
        # 6. RECHERCHE + GÉNÉRATION RAG
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

        rag_result = self.knowledge.ask(
            question=message,
            top_k=15,
            language=language,
            input_type=input_type,
            weather_context=weather_context,
            conversation_history=(
                conversation_history_text
            ),
            reasoning_summary=(
                reasoning_summary_text
            ),
        )

        # =====================================================
        # 7. RÉCUPÉRATION DE LA RÉPONSE RAG
        # =====================================================

        answer = rag_result.get(
            "answer",
            "",
        )

        # =====================================================
        # 8. FALLBACK
        # =====================================================

        if not answer:

            answer = (
                "Je n'ai pas pu générer une réponse."
            )

        # =====================================================
        # 9. SAUVEGARDE DE LA RÉPONSE
        # =====================================================

        self.conversation.add_message(
            user_id=user_id,
            author="assistant",
            content=answer,
        )

        # =====================================================
        # 10. RETOUR
        # =====================================================

        return answer

    # =========================================================
    # FORMATAGE DE L'HISTORIQUE
    # =========================================================

    def _format_history(
        self,
        history: list,
    ) -> str | None:

        if not history:

            return None

        recent_history = history[
            -self.MAX_HISTORY_MESSAGES_IN_PROMPT:
        ]

        lines = []

        for entry in recent_history:

            author = getattr(
                entry,
                "author",
                "",
            )

            content = getattr(
                entry,
                "content",
                "",
            )

            if not content:

                continue

            speaker_label = (
                "Agriculteur"
                if author == "user"
                else "SikaGlé"
            )

            lines.append(
                f"{speaker_label} : {content}"
            )

        if not lines:

            return None

        return "\n".join(lines)

    # =========================================================
    # FORMATAGE DU RAISONNEMENT
    #
    # NOTE : utilise getattr avec plusieurs noms de champs
    # possibles par prudence, la structure exacte de
    # Intent/Crop/Symptom n'étant pas garantie stable.
    # =========================================================

    def _format_reasoning(
        self,
        reasoning_context,
    ) -> str | None:

        lines = []

        crop = getattr(
            reasoning_context,
            "crop",
            None,
        )

        crop_label = self._extract_label(
            crop
        )

        if crop_label:

            lines.append(
                f"Culture déjà identifiée : {crop_label}"
            )

        symptoms = getattr(
            reasoning_context,
            "symptoms",
            [],
        ) or []

        symptom_labels = [
            self._extract_label(symptom)
            for symptom in symptoms
        ]

        symptom_labels = [
            label
            for label in symptom_labels
            if label
        ]

        if symptom_labels:

            lines.append(
                "Symptômes déjà mentionnés : "
                + ", ".join(symptom_labels)
            )

        intent = getattr(
            reasoning_context,
            "intent",
            None,
        )

        intent_label = self._extract_label(
            intent
        )

        if intent_label:

            lines.append(
                f"Intention déjà détectée : {intent_label}"
            )

        if not lines:

            return None

        return "\n".join(lines)

    @staticmethod
    def _extract_label(
        item,
    ) -> str | None:

        if item is None:

            return None

        for attribute_name in (
            "label",
            "name",
            "value",
            "type",
        ):

            value = getattr(
                item,
                attribute_name,
                None,
            )

            if value:

                return str(value)

        return None