from google import genai

from app.core import settings
from app.knowledge_engine.rag.prompt_builder import (
    PromptBuilder,
)


class ResponseGenerator:
    """
    Génère une réponse avec Gemini
    à partir des passages récupérés
    dans la base vectorielle.
    """

    def __init__(self):

        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY n'est pas configurée."
            )

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = (
            settings.GEMINI_GENERATION_MODEL
        )

        self.prompt_builder = PromptBuilder()

    def generate(
        self,
        question: str,
        contexts: list[str],
    ) -> str:

        prompt = self.prompt_builder.build(
            question=question,
            contexts=contexts,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        # Récupération explicite uniquement des
        # parties textuelles de la réponse Gemini.
        text_parts = []

        try:
            candidates = response.candidates or []

            for candidate in candidates:

                content = getattr(
                    candidate,
                    "content",
                    None,
                )

                if content is None:
                    continue

                parts = getattr(
                    content,
                    "parts",
                    [],
                )

                for part in parts:

                    text = getattr(
                        part,
                        "text",
                        None,
                    )

                    if text:
                        text_parts.append(
                            text
                        )

        except Exception:
            text_parts = []

        if text_parts:

            return "\n".join(
                text_parts
            ).strip()

        # Fallback standard
        if response.text:

            return response.text.strip()

        return (
            "Je n'ai pas pu générer une réponse."
        )