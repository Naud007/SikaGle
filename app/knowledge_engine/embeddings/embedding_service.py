from google import genai
from google.genai import types

from app.core import settings


class GeminiEmbeddingService:
    """
    Service de génération d'embeddings avec Gemini.
    """

    def __init__(
        self,
        model=None,
        output_dimensionality=None,
    ):

        api_key = settings.GEMINI_API_KEY

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY n'est pas configurée."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = (
            model
            or settings.GEMINI_EMBEDDING_MODEL
        )

        self.output_dimensionality = (
            output_dimensionality
            or settings.EMBEDDING_DIMENSION
        )

    def generate_document_embedding(
        self,
        text: str,
    ):

        if not text or not text.strip():

            raise ValueError(
                "Le texte à encoder est vide."
            )

        result = (
            self.client.models.embed_content(
                model=self.model,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=(
                        self.output_dimensionality
                    ),
                ),
            )
        )

        return result.embeddings[0].values

    def generate_query_embedding(
        self,
        text: str,
    ):

        if not text or not text.strip():

            raise ValueError(
                "La requête à encoder est vide."
            )

        result = (
            self.client.models.embed_content(
                model=self.model,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_QUERY",
                    output_dimensionality=(
                        self.output_dimensionality
                    ),
                ),
            )
        )

        return result.embeddings[0].values
