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

        if response.text:

            return response.text.strip()

        return (
            "Je n'ai pas pu générer une réponse."
        )
