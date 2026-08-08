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

    # =========================================================
    # EMBEDDING DOCUMENT UNIQUE
    # =========================================================

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

        if (
            not result.embeddings
            or not result.embeddings[0].values
        ):

            raise ValueError(
                "Aucun embedding document généré."
            )

        return result.embeddings[0].values

    # =========================================================
    # EMBEDDING DOCUMENTS EN BATCH
    # =========================================================

    def generate_document_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:

            return []

        for text in texts:

            if not text or not text.strip():

                raise ValueError(
                    "Un des textes à encoder est vide."
                )

        result = (
            self.client.models.embed_content(

                model=self.model,

                contents=texts,

                config=types.EmbedContentConfig(

                    task_type="RETRIEVAL_DOCUMENT",

                    output_dimensionality=(
                        self.output_dimensionality
                    ),

                ),
            )
        )

        if not result.embeddings:

            raise ValueError(
                "Aucun embedding document généré."
            )

        embeddings = []

        for embedding in result.embeddings:

            if not embedding.values:

                raise ValueError(
                    "Un embedding document est vide."
                )

            embeddings.append(
                embedding.values
            )

        if len(embeddings) != len(texts):

            raise ValueError(
                "Le nombre d'embeddings reçus "
                "ne correspond pas au nombre "
                "de textes envoyés."
            )

        return embeddings

    # =========================================================
    # EMBEDDING REQUÊTE
    # =========================================================

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

        if (
            not result.embeddings
            or not result.embeddings[0].values
        ):

            raise ValueError(
                "Aucun embedding de requête généré."
            )

        return result.embeddings[0].values


# =========================================================
# COMPATIBILITÉ ANCIENNE VERSION
# =========================================================

GeminiEmbedding = GeminiEmbeddingService