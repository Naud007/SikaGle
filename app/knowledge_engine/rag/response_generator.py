from google import genai

from app.core.config import settings


class ResponseGenerator:
    """
    Génère une réponse en utilisant Gemini
    à partir des passages retrouvés.
    """

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = "gemini-2.5-flash"

    def generate(
        self,
        question: str,
        contexts: list[str],
    ) -> str:

        context = "\n\n".join(contexts)

        prompt = f"""
Tu es SikaGlé, un assistant agricole spécialisé.

Réponds UNIQUEMENT à partir du contexte ci-dessous.

Si le contexte ne contient pas la réponse,
dis clairement que l'information n'est pas disponible.

======================
CONTEXTE
======================

{context}

======================
QUESTION
======================

{question}

======================
RÉPONSE
======================
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text
