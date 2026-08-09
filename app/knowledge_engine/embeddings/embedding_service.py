from time import sleep, monotonic

from google import genai
from google.genai import types

from app.core import settings


class GeminiEmbeddingService:
    """
    Service de génération d'embeddings avec Gemini.
    """

    MAX_BATCH_SIZE = 100
    MIN_REQUEST_INTERVAL = 1.1

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

        self._last_request_time = 0.0

    # =========================================================
    # LIMITATION DU RYTHME
    # =========================================================

    def _wait_before_request(self):

        elapsed = (
            monotonic()
            - self._last_request_time
        )

        remaining = (
            self.MIN_REQUEST_INTERVAL
            - elapsed
        )

        if remaining > 0:
            sleep(remaining)

        self._last_request_time = monotonic()

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

        self._wait_before_request()

        result = (
            self.client.models.embed_content(
                model=self.model,
                contents=text.strip(),
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
    # EMBEDDINGS DOCUMENTS EN BATCH
    # =========================================================

    def generate_document_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:

            raise ValueError(
                "La liste des textes à encoder est vide."
            )

        cleaned_texts = []

        for text in texts:

            if not text or not text.strip():

                raise ValueError(
                    "Un des textes à encoder est vide."
                )

            cleaned_texts.append(
                text.strip()
            )

        embeddings = []

        for start in range(
            0,
            len(cleaned_texts),
            self.MAX_BATCH_SIZE,
        ):

            batch = cleaned_texts[
                start:
                start + self.MAX_BATCH_SIZE
            ]

            self._wait_before_request()

            result = (
                self.client.models.embed_content(
                    model=self.model,
                    contents=batch,
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

            for embedding in result.embeddings:

                if not embedding.values:

                    raise ValueError(
                        "Un embedding vide a été généré."
                    )

                embeddings.append(
                    embedding.values
                )

        if len(embeddings) != len(
            cleaned_texts
        ):

            raise ValueError(
                "Le nombre d'embeddings générés "
                "ne correspond pas au nombre de textes."
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

        self._wait_before_request()

        result = (
            self.client.models.embed_content(
                model=self.model,
                contents=text.strip(),
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
# TEST EMBEDDING
# =========================================================

def test_embedding():

    try:

        embedding_service = (
            GeminiEmbeddingService()
        )

        vector = (
            embedding_service
            .generate_document_embedding(
                "Comment cultiver le maïs au Bénin ?"
            )
        )

        return {
            "status": "success",
            "model": embedding_service.model,
            "dimension": len(vector),
            "expected_dimension": (
                embedding_service
                .output_dimensionality
            ),
            "preview": vector[:5],
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e),
        }


# =========================================================
# COMPATIBILITÉ ANCIENNE VERSION
# =========================================================

GeminiEmbedding = GeminiEmbeddingService