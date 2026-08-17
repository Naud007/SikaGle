from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PipelineResult:
    """
    Résultat standard du pipeline SikaGlé.
    """

    response: str

    sources: list[str] = field(default_factory=list)

    confidence: float = 0.0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class ConversationPipeline:
    """
    Pipeline principal de traitement d'une question SikaGlé.

    Responsabilités :

    1. Construire le contexte conversationnel
    2. Analyser le contexte agricole
    3. Rechercher les connaissances
    4. Construire le prompt
    5. Générer la réponse avec Gemini

    Ce pipeline ne gère pas HTTP.
    """

    def __init__(
        self,
        conversation_service,
        conversation_context_service,
        reasoning_context_service,
        knowledge_service,
        llm,
    ):

        self.conversation = (
            conversation_service
        )

        self.conversation_context = (
            conversation_context_service
        )

        self.reasoning_context = (
            reasoning_context_service
        )

        self.knowledge = (
            knowledge_service
        )

        self.llm = llm

    # =========================================================
    # EXECUTION
    # =========================================================

    def run(
        self,
        user_id: str,
        message: str,
        language: str = "fr",
        channel: str = "api",
    ) -> PipelineResult:

        # -----------------------------------------------------
        # 1. Sauvegarder le message utilisateur
        # -----------------------------------------------------

        self.conversation.add_message(
            user_id=user_id,
            author="user",
            content=message,
        )

        # -----------------------------------------------------
        # 2. Construire le contexte conversationnel
        # -----------------------------------------------------

        conversation_context = (
            self.conversation_context.build(
                user_id
            )
        )

        # -----------------------------------------------------
        # 3. Analyser le contexte agricole
        # -----------------------------------------------------

        reasoning_context = (
            self.reasoning_context.analyze(
                user_id=user_id,
                text=message,
            )
        )

        # -----------------------------------------------------
        # 4. Recherche RAG
        # -----------------------------------------------------

        rag_result = self.knowledge.ask(
            question=message,
            top_k=5,
        )

        # -----------------------------------------------------
        # 5. Construire le prompt
        # -----------------------------------------------------

        prompt = self._build_prompt(
            user_message=message,
            language=language,
            channel=channel,
            conversation_context=conversation_context,
            reasoning_context=reasoning_context,
            rag_result=rag_result,
        )

        # -----------------------------------------------------
        # 6. Générer avec Gemini
        # -----------------------------------------------------

        answer = self.llm.generate_text(
            prompt
        )

        # -----------------------------------------------------
        # 7. Récupérer les sources
        # -----------------------------------------------------

        sources = rag_result.get(
            "sources",
            [],
        )

        # -----------------------------------------------------
        # 8. Estimation initiale de confiance
        # -----------------------------------------------------

        confidence = self._extract_confidence(
            reasoning_context
        )

        # -----------------------------------------------------
        # 9. Sauvegarder la réponse
        # -----------------------------------------------------

        self.conversation.add_message(
            user_id=user_id,
            author="assistant",
            content=answer,
        )

        return PipelineResult(
            response=answer,
            sources=sources,
            confidence=confidence,
            metadata={
                "channel": channel,
                "language": language,
                "chunks_used": rag_result.get(
                    "chunks_used",
                    0,
                ),
                "rag_success": rag_result.get(
                    "success",
                    False,
                ),
            },
        )

    # =========================================================
    # PROMPT
    # =========================================================

    def _build_prompt(
        self,
        user_message: str,
        language: str,
        channel: str,
        conversation_context,
        reasoning_context,
        rag_result: dict,
    ) -> str:

        documents = rag_result.get(
            "answer",
            "",
        )

        sources = rag_result.get(
            "sources",
            [],
        )

        formatted_sources = "\n".join(
            f"- {source}"
            for source in sources
        )

        return f"""
Tu es SikaGlé, un conseiller agricole intelligent
destiné principalement aux agriculteurs d'Afrique de l'Ouest.

Tu dois fournir une réponse agricole utile,
compréhensible, prudente et fondée sur les connaissances
disponibles.

RÈGLES IMPORTANTES :

- Ne jamais inventer une information.
- Utiliser les connaissances retrouvées.
- Tenir compte du contexte de l'agriculteur.
- Si les informations sont insuffisantes, le signaler.
- Ne pas donner une recommandation dangereuse lorsque
  les informations nécessaires sont absentes.
- Donner clairement une recommandation lorsque les
  éléments disponibles permettent de le faire.
- Expliquer brièvement pourquoi.
- Mentionner les précautions importantes.
- Citer les sources disponibles.
- Ne pas présenter une hypothèse comme un fait.
- Si les sources sont contradictoires, le signaler.

LANGUE DEMANDÉE :

{language}

CANAL :

{channel}

QUESTION DE L'AGRICULTEUR :

{user_message}

CONTEXTE CONVERSATIONNEL :

{conversation_context}

CONTEXTE AGRICOLE / RAISONNEMENT :

{reasoning_context}

CONNAISSANCES AGRICOLES RETROUVÉES :

{documents}

SOURCES :

{formatted_sources}

STRUCTURE DE RÉPONSE SOUHAITÉE :

1. Réponse / recommandation
2. Pourquoi
3. Précautions ou prochaines étapes si nécessaire
4. Sources

Réponds maintenant à l'agriculteur.
"""

    # =========================================================
    # CONFIDENCE
    # =========================================================

    def _extract_confidence(
        self,
        reasoning_context,
    ) -> float:

        if reasoning_context is None:
            return 0.0

        # Objet avec attribut confidence
        confidence = getattr(
            reasoning_context,
            "confidence",
            None,
        )

        if confidence is not None:

            try:

                value = float(
                    confidence
                )

                return max(
                    0.0,
                    min(
                        1.0,
                        value,
                    ),
                )

            except (
                TypeError,
                ValueError,
            ):
                pass

        # Objet/dict contenant confidence
        if isinstance(
            reasoning_context,
            dict,
        ):

            confidence = reasoning_context.get(
                "confidence"
            )

            if confidence is not None:

                try:

                    value = float(
                        confidence
                    )

                    return max(
                        0.0,
                        min(
                            1.0,
                            value,
                        ),
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    pass

        return 0.0