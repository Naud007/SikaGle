from __future__ import annotations

import base64
import io
from pathlib import Path

import requests

from app.core.config import settings


class PlantVillageSimilarityService:
    """
    Recherche les images PlantVillage les plus visuellement
    similaires à une photo envoyée par un agriculteur, en
    comparant leurs embeddings Jina (même modèle que celui
    utilisé lors de l'ingestion PlantVillage — voir
    PlantVillageIngestionWorker).

    NOTE (important) : ce service enrichit l'observation de
    ImageAnalysisService avec un contexte supplémentaire
    ("cas connus similaires"), il ne remplace jamais le
    diagnostic — celui-ci reste entièrement du ressort du
    pipeline RAG existant.
    """

    JINA_API_URL = (
        "https://api.jina.ai/v1/embeddings"
    )

    JINA_MODEL = "jina-embeddings-v5-omni-small"

    # =========================================================
    # SEUIL DE SIMILARITÉ MINIMUM
    #
    # NOTE : en dessous de ce seuil, les résultats sont trop
    # peu similaires pour être utiles — mieux vaut ne rien
    # remonter que de suggérer un cas non pertinent (même
    # logique que MINIMUM_RELEVANCE_SCORE pour le RAG texte).
    # =========================================================

    MINIMUM_SIMILARITY = 0.5

    def __init__(
        self,
        supabase_client,
    ):

        self.supabase = supabase_client

    # =========================================================
    # RECHERCHE
    # =========================================================

    def find_similar_cases(
        self,
        image_path: str | Path,
        mime_type: str = "image/jpeg",
        top_k: int = 3,
    ) -> list[str]:
        """
        Retourne une liste de libellés (ex: "Tomato - Late
        blight") correspondant aux images PlantVillage les
        plus similaires, ou une liste vide en cas d'échec ou
        d'absence de résultat suffisamment similaire.

        Ne lève jamais d'exception : une panne de cet
        enrichissement ne doit jamais empêcher l'analyse
        d'image principale de continuer.
        """

        try:

            embedding = (
                self._generate_embedding(
                    image_path
                )
            )

            response = (
                self.supabase
                .rpc(
                    "search_plantvillage_similar",
                    {
                        "query_embedding":
                            embedding,
                        "result_limit":
                            top_k,
                    },
                )
                .execute()
            )

            rows = response.data or []

            labels = []

            for row in rows:

                similarity = row.get(
                    "similarity",
                    0.0,
                )

                if (
                    similarity
                    < self.MINIMUM_SIMILARITY
                ):

                    continue

                crop = row.get(
                    "crop",
                    "",
                )

                disease = row.get(
                    "disease",
                    "",
                )

                if crop and disease:

                    labels.append(
                        f"{crop} - {disease}"
                    )

                elif crop:

                    labels.append(crop)

            return labels

        except Exception as e:

            print(
                "⚠️ Recherche de similarité "
                f"PlantVillage échouée : {e}"
            )

            return []

    # =========================================================
    # EMBEDDING JINA (même méthode que l'ingestion)
    # =========================================================

    def _generate_embedding(
        self,
        image_path: str | Path,
    ) -> list[float]:

        image_path = Path(image_path)

        image_bytes = (
            image_path.read_bytes()
        )

        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        payload = {
            "model": self.JINA_MODEL,
            "task": "retrieval.query",
            "input": [
                {"image": image_base64}
            ],
        }

        headers = {
            "Authorization": (
                f"Bearer {settings.JINA_API_KEY}"
            ),
            "Content-Type": (
                "application/json"
            ),
        }

        response = requests.post(
            self.JINA_API_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code != 200:

            raise RuntimeError(
                "Erreur Jina : "
                f"{response.status_code} "
                f"{response.text}"
            )

        data = response.json()

        return (
            data["data"][0]["embedding"]
        )