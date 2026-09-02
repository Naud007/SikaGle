import base64
import io
import os
import time

import requests
from datasets import load_dataset
from supabase import create_client, Client


class PlantVillageIngestionWorker:
    """
    Ingère le dataset PlantVillage (54305 images de plantes
    malades/saines, licence CC0) dans Supabase, avec des
    embeddings d'images générés par Jina, pour permettre une
    recherche par similarité depuis ImageAnalysisService.

    Conçu pour tourner en LOCAL (pas sur Render), le volume
    étant trop important pour le plan Render gratuit (leçon
    apprise avec les crashs mémoire FAO).

    Supporte la reprise (image_offset), pour pouvoir changer
    de clé Jina en cours de route sans jamais retraiter une
    image déjà en base.
    """

    DATASET_NAME = (
        "BrandonFors/Plant-Diseases-PlantVillage-Dataset"
    )

    JINA_API_URL = (
        "https://api.jina.ai/v1/embeddings"
    )

    JINA_MODEL = "jina-embeddings-v5-omni-small"

    MAX_RETRIES = 3

    def __init__(
        self,
        jina_api_key: str,
    ):

        if not jina_api_key:

            raise ValueError(
                "jina_api_key est requis."
            )

        self.jina_api_key = jina_api_key

        supabase_url = os.getenv(
            "SUPABASE_URL"
        )

        supabase_key = os.getenv(
            "SUPABASE_KEY"
        )

        if not supabase_url or not supabase_key:

            raise ValueError(
                "SUPABASE_URL et SUPABASE_KEY "
                "doivent être configurées "
                "(variables d'environnement)."
            )

        self.supabase: Client = (
            create_client(
                supabase_url,
                supabase_key,
            )
        )

        self._dataset = None

    # =========================================================
    # DATASET (chargé une seule fois, en cache mémoire local)
    # =========================================================

    def _get_dataset(self):

        if self._dataset is None:

            print(
                "[PLANTVILLAGE] Chargement du "
                "dataset (une seule fois)..."
            )

            self._dataset = load_dataset(
                self.DATASET_NAME,
                split="train",
            )

            print(
                "[PLANTVILLAGE] Dataset chargé : "
                f"{len(self._dataset)} images."
            )

        return self._dataset

    # =========================================================
    # ÉTAT
    # =========================================================

    def get_state(self) -> dict:

        response = (
            self.supabase
            .table(
                "plantvillage_ingestion_state"
            )
            .select("*")
            .limit(1)
            .execute()
        )

        rows = response.data or []

        if not rows:

            raise RuntimeError(
                "État PlantVillage introuvable "
                "(la table devrait avoir été "
                "initialisée avec une ligne)."
            )

        return rows[0]

    def save_state(
        self,
        image_offset: int,
        images_processed: int,
        total_images: int,
        status: str,
        last_error: str | None = None,
    ) -> None:

        state = self.get_state()

        (
            self.supabase
            .table(
                "plantvillage_ingestion_state"
            )
            .update({
                "image_offset":
                    image_offset,
                "images_processed":
                    images_processed,
                "total_images":
                    total_images,
                "status":
                    status,
                "last_error":
                    last_error,
            })
            .eq(
                "id",
                state["id"],
            )
            .execute()
        )

    # =========================================================
    # EMBEDDING JINA (une image)
    # =========================================================

    def _generate_embedding(
        self,
        image,
    ) -> list[float]:

        buffer = io.BytesIO()

        image.convert("RGB").save(
            buffer,
            format="JPEG",
        )

        image_base64 = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

        payload = {
            "model": self.JINA_MODEL,
            "task": "retrieval.passage",
            "input": [
                {"image": image_base64}
            ],
        }

        headers = {
            "Authorization": (
                f"Bearer {self.jina_api_key}"
            ),
            "Content-Type": (
                "application/json"
            ),
        }

        delay = 2.0

        for attempt in range(
            self.MAX_RETRIES + 1
        ):

            response = requests.post(
                self.JINA_API_URL,
                headers=headers,
                json=payload,
                timeout=60,
            )

            if response.status_code == 200:

                data = response.json()

                return (
                    data["data"][0]
                    ["embedding"]
                )

            if response.status_code == 429:

                if attempt >= self.MAX_RETRIES:

                    raise RuntimeError(
                        "Limite de débit Jina "
                        "atteinte après plusieurs "
                        "tentatives."
                    )

                print(
                    "[JINA] Rate limit, "
                    f"attente {delay:.0f}s..."
                )

                time.sleep(delay)

                delay *= 2

                continue

            raise RuntimeError(
                "Erreur Jina : "
                f"{response.status_code} "
                f"{response.text}"
            )

        raise RuntimeError(
            "Échec inattendu de génération "
            "d'embedding."
        )

    # =========================================================
    # EXÉCUTER UN BATCH
    # =========================================================

    def run_batch(
        self,
        batch_size: int = 50,
    ) -> dict:

        dataset = self._get_dataset()

        total_images = len(dataset)

        state = self.get_state()

        image_offset = int(
            state.get(
                "image_offset",
                0,
            )
            or 0
        )

        images_processed_before = int(
            state.get(
                "images_processed",
                0,
            )
            or 0
        )

        if image_offset >= total_images:

            self.save_state(
                image_offset=image_offset,
                images_processed=(
                    images_processed_before
                ),
                total_images=total_images,
                status="completed",
                last_error=None,
            )

            return {
                "status": "completed",
                "message": (
                    "Toutes les images "
                    "PlantVillage ont été "
                    "traitées."
                ),
                "total_images": total_images,
            }

        label_feature = dataset.features[
            "label"
        ]

        end_index = min(
            image_offset + batch_size,
            total_images,
        )

        inserted = 0

        errors = 0

        for index in range(
            image_offset,
            end_index,
        ):

            try:

                example = dataset[index]

                image = example["image"]

                label_id = example["label"]

                label_raw = (
                    label_feature.int2str(
                        label_id
                    )
                )

                if "___" in label_raw:

                    crop, disease = (
                        label_raw.split(
                            "___",
                            1,
                        )
                    )

                else:

                    crop = label_raw

                    disease = ""

                embedding = (
                    self._generate_embedding(
                        image
                    )
                )

                (
                    self.supabase
                    .table(
                        "plantvillage_embeddings"
                    )
                    .upsert(
                        {
                            "dataset_index":
                                index,
                            "crop":
                                crop,
                            "disease":
                                disease,
                            "label_raw":
                                label_raw,
                            "embedding":
                                embedding,
                        },
                        on_conflict=(
                            "dataset_index"
                        ),
                    )
                    .execute()
                )

                inserted += 1

                if (index + 1) % 10 == 0:

                    print(
                        f"[PLANTVILLAGE] "
                        f"{index + 1}/"
                        f"{total_images} traitées "
                        f"({label_raw})"
                    )

            except Exception as e:

                errors += 1

                print(
                    "[PLANTVILLAGE] Erreur "
                    f"image {index} : {e}"
                )

        new_offset = end_index

        new_images_processed = (
            images_processed_before
            + inserted
        )

        has_more = (
            new_offset < total_images
        )

        self.save_state(
            image_offset=new_offset,
            images_processed=(
                new_images_processed
            ),
            total_images=total_images,
            status=(
                "idle"
                if has_more
                else "completed"
            ),
            last_error=None,
        )

        return {
            "status": "success",
            "batch_offset": image_offset,
            "batch_processed": (
                end_index - image_offset
            ),
            "inserted": inserted,
            "errors": errors,
            "next_image_offset": new_offset,
            "images_processed": (
                new_images_processed
            ),
            "total_images": total_images,
            "has_more": has_more,
        }