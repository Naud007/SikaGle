import requests

from app.core import settings


class JinaEmbeddingService:
    """
    Service de génération d'embeddings avec Jina.

    Jina est utilisé uniquement pour les embeddings.
    Gemini reste utilisé pour la génération des réponses.

    Documents :
        retrieval.passage

    Requêtes :
        retrieval.query
    """

    API_URL = "https://api.jina.ai/v1/embeddings"

    MAX_BATCH_SIZE = 50

    def __init__(
        self,
        model=None,
        output_dimensionality=None,
    ):

        api_key = settings.JINA_API_KEY

        if not api_key:
            raise ValueError(
                "JINA_API_KEY n'est pas configurée."
            )

        self.api_key = api_key

        self.model = (
            model
            or settings.JINA_EMBEDDING_MODEL
        )

        self.output_dimensionality = (
            output_dimensionality
            or settings.JINA_EMBEDDING_DIMENSION
        )

    # =========================================================
    # APPEL JINA
    # =========================================================

    def _embed(
        self,
        texts: list[str],
        task: str,
    ) -> list[list[float]]:
        """
        Génère les embeddings Jina.
        """

        if not texts:

            raise ValueError(
                "Aucun texte à encoder."
            )

        if len(texts) > self.MAX_BATCH_SIZE:

            raise ValueError(
                f"Maximum de "
                f"{self.MAX_BATCH_SIZE} textes "
                f"par requête."
            )

        response = requests.post(
            self.API_URL,
            headers={
                "Authorization": (
                    f"Bearer {self.api_key}"
                ),
                "Content-Type": (
                    "application/json"
                ),
            },
            json={
                "model": self.model,
                "input": texts,
                "task": task,
                "dimensions": (
                    self.output_dimensionality
                ),
            },
            timeout=120,
        )

        if not response.ok:

            raise RuntimeError(
                "Erreur Jina Embeddings : "
                f"{response.status_code} "
                f"{response.text}"
            )

        data = response.json()

        embeddings = data.get(
            "data",
            [],
        )

        if not embeddings:

            raise ValueError(
                "Jina n'a retourné aucun embedding."
            )

        embeddings = sorted(
            embeddings,
            key=lambda item: item["index"],
        )

        vectors = [
            item["embedding"]
            for item in embeddings
        ]

        for vector in vectors:

            if not vector:

                raise ValueError(
                    "Jina a retourné un "
                    "embedding vide."
                )

            if len(vector) != (
                self.output_dimensionality
            ):

                raise ValueError(
                    "Dimension incorrecte : "
                    f"{len(vector)} "
                    "au lieu de "
                    f"{self.output_dimensionality}."
                )

        return vectors

    # =========================================================
    # DOCUMENT UNIQUE
    # =========================================================

    def generate_document_embedding(
        self,
        text: str,
    ) -> list[float]:

        if not text or not text.strip():

            raise ValueError(
                "Le texte à encoder est vide."
            )

        embeddings = self._embed(
            texts=[text.strip()],
            task="retrieval.passage",
        )

        return embeddings[0]

    # =========================================================
    # DOCUMENTS EN BATCH
    # =========================================================

    def generate_document_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Génère les embeddings de plusieurs documents.

        Les textes sont automatiquement découpés
        en lots de 50 maximum.
        """

        if not texts:

            raise ValueError(
                "La liste des textes "
                "à encoder est vide."
            )

        cleaned_texts = []

        for text in texts:

            if not text or not text.strip():

                raise ValueError(
                    "Un des textes à encoder "
                    "est vide."
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

            batch_embeddings = self._embed(
                texts=batch,
                task="retrieval.passage",
            )

            embeddings.extend(
                batch_embeddings
            )

        if len(embeddings) != len(
            cleaned_texts
        ):

            raise ValueError(
                "Le nombre d'embeddings "
                "ne correspond pas au nombre "
                "de textes."
            )

        return embeddings

    # =========================================================
    # REQUÊTE
    # =========================================================

    def generate_query_embedding(
        self,
        text: str,
    ) -> list[float]:

        if not text or not text.strip():

            raise ValueError(
                "La requête à encoder est vide."
            )

        embeddings = self._embed(
            texts=[text.strip()],
            task="retrieval.query",
        )

        return embeddings[0]


# =============================================================
# COMPATIBILITÉ
# =============================================================

GeminiEmbeddingService = JinaEmbeddingService
GeminiEmbedding = JinaEmbeddingService