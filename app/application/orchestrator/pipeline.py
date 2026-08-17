from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.schemas.message_response import MessageSource


@dataclass
class PipelineResult:
    """
    Résultat standard du pipeline SikaGlé.
    """

    response: str

    sources: list[MessageSource] = field(
        default_factory=list
    )

    confidence: float = 0.0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class ConversationPipeline:
    """
    Pipeline principal de traitement d'une question SikaGlé.

    Flux :

    utilisateur
        ↓
    conversation
        ↓
    contexte
        ↓
    raisonnement
        ↓
    RAG
        ↓
    Gemini
        ↓
    réponse
    """

    def __init__(
        self,
        conversation_service,
        conversation_context_service,
        reasoning_context_service,
        knowledge_service,
        llm,
    ):
        self.conversation = conversation_service
        self.conversation_context = (
            conversation_context_service
        )
        self.reasoning_context = (
            reasoning_context_service
        )
        self.knowledge = knowledge_service
        self.llm = llm

    def run(
        self,
        user_id: str,
        message: str,
        language: str = "fr",
        channel: str = "api",
    ) -> PipelineResult:

        # 1. Message utilisateur
        self.conversation.add_message(
            user_id=user_id,
            author="user",
            content=message,
        )

        # 2. Contexte conversationnel
        conversation_context = (
            self.conversation_context.build(
                user_id
            )
        )

        # 3. Contexte agricole
        reasoning_context = (
            self.reasoning_context.analyze(
                user_id=user_id,
                text=message,
            )
        )

        # 4. RAG
        rag_result = self.knowledge.ask(
            question=message,
            top_k=5,
        )

        # 5. Prompt
        prompt = self._build_prompt(
            user_message=message,
            language=language,
            channel=channel,
            conversation_context=conversation_context,
            reasoning_context=reasoning_context,
            rag_result=rag_result,
        )

        # 6. Gemini
        answer = self.llm.generate_text(prompt)

        # 7. Sources
        sources = self._normalize_sources(
            rag_result.get("sources", [])
        )

        # 8. Confiance
        confidence = self._extract_confidence(
            reasoning_context
        )

        # 9. Sauvegarde réponse
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
    # SOURCES
    # =========================================================

    def _normalize_sources(
        self,
        sources,
    ) -> list[MessageSource]:

        if not sources:
            return []

        normalized: list[MessageSource] = []

        for source in sources:

            if isinstance(
                source,
                MessageSource,
            ):
                normalized.append(source)
                continue

            if isinstance(source, str):
                normalized.append(
                    MessageSource(
                        title=source,
                        url="",
                    )
                )
                continue

            if isinstance(source, dict):
                normalized.append(
                    MessageSource(
                        title=str(
                            source.get(
                                "title",
                                source.get(
                                    "name",
                                    "",
                                ),
                            )
                        ),
                        url=str(
                            source.get(
                                "url",
                                "",
                            )
                        ),
                    )
                )

        return normalized

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

        confidence = getattr(
            reasoning_context,
            "confidence",
            None,
        )

        if confidence is not None:
            try:
                value = float(confidence)

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

        if isinstance(
            reasoning_context,
            dict,
        ):

            confidence = reasoning_context.get(
                "confidence"
            )

            if confidence is not None:
                try:
                    value = float(confidence)

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