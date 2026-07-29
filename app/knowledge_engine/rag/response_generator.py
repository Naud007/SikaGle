from google import genai

from app.core import settings


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

    def generate(
        self,
        question: str,
        contexts: list[str],
    ) -> str:

        context = "\n\n".join(contexts)

        prompt = f"""
Tu es SikaGlé, un assistant agricole spécialisé.

Tu réponds uniquement en utilisant les informations présentes
dans le contexte fourni.

Si la réponse ne se trouve pas dans le contexte,
dis clairement que tu ne disposes pas de suffisamment
d'informations.

Réponds en français avec un langage simple,
clair et pédagogique.

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
