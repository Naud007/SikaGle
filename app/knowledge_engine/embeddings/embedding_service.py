import time

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

    # Jina accepte davantage de textes, mais pour SikaGlé
    # nous privilégions la stabilité et la maîtrise
    # de la limite de tokens par minute.
    MAX_BATCH_SIZE = 5

    # Nombre maximal de nouvelles tentatives après un 429.
    MAX_RETRIES = 5

    # Délai initial entre deux requêtes.
    INITIAL_DELAY_SECONDS = 2.0

    # Délai minimum entre deux appels Jina.
    #
    # NOTE (correctif performance) :
    #
    # Ce délai n'est utile que lors de l'indexation de documents
    # en lot (retrieval.passage), pour respecter le quota Jina
    # sur plusieurs appels consécutifs. Il est désormais appliqué
    # uniquement pour ce cas, et plus pour les requêtes agricoles
    # ponctuelles (retrieval.query), qui n'ont pas besoin de cette
    # protection puisqu'il n'y a qu'un seul appel à la fois.
    #
    REQUEST_DELAY_SECONDS = 2.0

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

        Protection contre :
        - les lots trop importants ;
        - les erreurs 429 de limitation de débit ;
        - les réponses invalides.
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

        payload = {
            "model": self.model,
            "input": texts,
            "task": task,
            "dimensions": (
                self.output_dimensionality
            ),
        }

        headers = {
            "Authorization": (
                f"Bearer {self.api_key}"
            ),
            "Content-Type": (
                "application/json"
            ),
        }

        delay = self.INITIAL_DELAY_SECONDS

        for attempt in range(
            self.MAX_RETRIES + 1
        ):

            try:

                response = requests.post(
                    self.API_URL,
                    headers=headers,
                    json=payload,
                    timeout=120,
                )

                # =========================================
                # RATE LIMIT JINA
                # =========================================

                if response.status_code == 429:

                    if attempt >= self.MAX_RETRIES:

                        raise RuntimeError(
                            "Erreur Jina Embeddings : "
                            "limite de débit atteinte "
                            "après plusieurs tentatives. "
                            f"{response.text}"
                        )

                    print(
                        "[JINA] Rate limit 429. "
                        f"Nouvelle tentative dans "
                        f"{delay:.1f}s..."
                    )

                    time.sleep(
                        delay
                    )

                    delay *= 2

                    continue

                # =========================================
                # AUTRES ERREURS HTTP
                # =========================================

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
                        "Jina n'a retourné "
                        "aucun embedding."
                    )

                embeddings = sorted(
                    embeddings,
                    key=lambda item: item["index"],
                )

                vectors = [
                    item["embedding"]
                    for item in embeddings
                ]

                # =========================================
                # VALIDATION
                # =========================================

                for vector in vectors:

                    if not vector:

                        raise ValueError(
                            "Jina a retourné "
                            "un embedding vide."
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

                # =========================================
                # PETITE PAUSE ENTRE LES REQUÊTES
                #
                # NOTE (correctif performance) :
                #
                # Uniquement nécessaire pour les appels en
                # lot lors de l'indexation (retrieval.passage).
                # Une requête agricole ponctuelle
                # (retrieval.query) n'a pas besoin d'attendre.
                # =========================================

                if task == "retrieval.passage":

                    time.sleep(
                        self.REQUEST_DELAY_SECONDS
                    )

                return vectors

            except requests.RequestException as exc:

                if attempt >= self.MAX_RETRIES:

                    raise RuntimeError(
                        "Erreur réseau Jina après "
                        "plusieurs tentatives : "
                        f"{exc}"
                    ) from exc

                print(
                    "[JINA] Erreur réseau. "
                    f"Nouvelle tentative dans "
                    f"{delay:.1f}s..."
                )

                time.sleep(
                    delay
                )

                delay *= 2

        raise RuntimeError(
            "Échec inattendu du service Jina."
        )

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
            texts=[
                text.strip()
            ],
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
        en lots de 5 maximum afin de limiter
        le risque de dépassement du quota Jina.
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

            print(
                "[JINA] Embedding batch : "
                f"{start + 1}-"
                f"{start + len(batch)} / "
                f"{len(cleaned_texts)}"
            )

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
            texts=[
                text.strip()
            ],
            task="retrieval.query",
        )

        return embeddings[0]


# =============================================================
# COMPATIBILITÉ
# =============================================================

GeminiEmbeddingService = JinaEmbeddingService

GeminiEmbedding = JinaEmbeddingService