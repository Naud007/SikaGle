from typing import Any

from supabase import Client, create_client

from app.core import settings


class SupabaseStore:
    """
    Gestionnaire de la base vectorielle Supabase + pgvector.

    Stockage persistant des documents et de leurs embeddings.
    """

    TABLE_NAME = "knowledge_embeddings"

    def __init__(self):

        supabase_url = settings.SUPABASE_URL
        supabase_key = settings.SUPABASE_KEY

        if not supabase_url:

            raise ValueError(
                "SUPABASE_URL est manquante."
            )

        if not supabase_key:

            raise ValueError(
                "SUPABASE_KEY est manquante."
            )

        self.client: Client = create_client(
            supabase_url,
            supabase_key,
        )

    # =========================================================
    # EXISTENCE
    # =========================================================

    def exists(
        self,
        doc_id: str,
    ) -> bool:

        response = (
            self.client
            .table(self.TABLE_NAME)
            .select("id")
            .eq(
                "document_id",
                doc_id,
            )
            .limit(1)
            .execute()
        )

        return bool(
            response.data
        )

    # =========================================================
    # AJOUT DOCUMENT
    # =========================================================

    def add_document(
        self,
        doc_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
        metadata: dict,
    ) -> None:

        if not chunks:

            raise ValueError(
                "Aucun chunk à enregistrer."
            )

        if len(chunks) != len(
            embeddings
        ):

            raise ValueError(
                "Le nombre de chunks et "
                "d'embeddings ne correspond pas."
            )

        total_chunks = len(
            chunks
        )

        rows = []

        for index, chunk in enumerate(
            chunks
        ):

            rows.append(
                {
                    "document_id":
                        str(doc_id),

                    "chunk_index":
                        index,

                    "chunk_count":
                        total_chunks,

                    "content":
                        str(chunk),

                    "title":
                        self._to_string(
                            metadata.get(
                                "title"
                            )
                        ),

                    "source":
                        self._to_string(
                            metadata.get(
                                "source"
                            )
                        ),

                    "identifier":
                        self._to_string(
                            metadata.get(
                                "identifier"
                            )
                        ),

                    "url":
                        self._to_string(
                            metadata.get(
                                "url"
                            )
                        ),

                    "author":
                        self._to_string(
                            metadata.get(
                                "author"
                            )
                        ),

                    "published_at":
                        self._normalize_date(
                            metadata.get(
                                "published_at"
                            )
                        ),

                    "language":
                        self._to_string(
                            metadata.get(
                                "language"
                            )
                        ),

                    "document_type":
                        self._to_string(
                            metadata.get(
                                "document_type"
                            )
                        ),

                    "publisher":
                        self._to_string(
                            metadata.get(
                                "publisher"
                            )
                        ),

                    "crop":
                        self._to_string(
                            metadata.get(
                                "crop"
                            )
                        ),

                    "culture":
                        self._to_string(
                            metadata.get(
                                "culture"
                            )
                        ),

                    "keywords":
                        self._normalize_keywords(
                            metadata.get(
                                "keywords"
                            )
                            or metadata.get(
                                "mots_cles"
                            )
                        ),

                    "country":
                        self._to_string(
                            metadata.get(
                                "country"
                            )
                        ),

                    "zone_geographique":
                        self._to_string(
                            metadata.get(
                                "zone_geographique"
                            )
                        ),
                }
            )

        (
            self.client
            .table(self.TABLE_NAME)
            .insert(rows)
            .execute()
        )

    # =========================================================
    # RECHERCHE VECTORIELLE
    # =========================================================

    def search(
        self,
        embedding: list[float],
        n_results: int = 5,
    ) -> dict:

        response = self.client.rpc(
            "match_knowledge_embeddings",
            {
                "query_embedding":
                    embedding,

                "match_threshold":
                    0.20,

                "match_count":
                    n_results,
            },
        ).execute()

        documents = []
        metadatas = []
        distances = []

        for row in (
            response.data or []
        ):

            documents.append(
                row.get(
                    "content",
                    "",
                )
            )

            metadatas.append(
                self._build_metadata(
                    row
                )
            )

            similarity = float(
                row.get(
                    "similarity",
                    0.0,
                )
            )

            distances.append(
                max(
                    0.0,
                    1.0 - similarity,
                )
            )

        return {
            "documents": [
                documents
            ],
            "metadatas": [
                metadatas
            ],
            "distances": [
                distances
            ],
        }

    # =========================================================
    # COMPTER
    # =========================================================

    def count(
        self,
    ) -> int:

        response = (
            self.client
            .table(self.TABLE_NAME)
            .select(
                "id",
                count="exact",
            )
            .execute()
        )

        return int(
            response.count or 0
        )

    # =========================================================
    # SUPPRIMER
    # =========================================================

    def delete_document(
        self,
        doc_id: str,
    ) -> None:

        (
            self.client
            .table(self.TABLE_NAME)
            .delete()
            .eq(
                "document_id",
                doc_id,
            )
            .execute()
        )

    # =========================================================
    # RÉCUPÉRER
    # =========================================================

    def get_document(
        self,
        doc_id: str,
    ) -> dict:

        response = (
            self.client
            .table(self.TABLE_NAME)
            .select("*")
            .eq(
                "document_id",
                doc_id,
            )
            .order(
                "chunk_index"
            )
            .execute()
        )

        rows = (
            response.data or []
        )

        return {
            "ids": [
                str(row["id"])
                for row in rows
            ],

            "documents": [
                row.get(
                    "content",
                    "",
                )
                for row in rows
            ],

            "metadatas": [
                self._build_metadata(
                    row
                )
                for row in rows
            ],
        }

    # =========================================================
    # MÉTADONNÉES
    # =========================================================

    @staticmethod
    def _build_metadata(
        row: dict,
    ) -> dict:

        metadata = {
            "document":
                row.get(
                    "document_id"
                ),

            "chunk_index":
                row.get(
                    "chunk_index"
                ),

            "chunk_count":
                row.get(
                    "chunk_count"
                ),

            "title":
                row.get(
                    "title"
                ),

            "source":
                row.get(
                    "source"
                ),

            "identifier":
                row.get(
                    "identifier"
                ),

            "url":
                row.get(
                    "url"
                ),

            "author":
                row.get(
                    "author"
                ),

            "published_at":
                row.get(
                    "published_at"
                ),

            "language":
                row.get(
                    "language"
                ),

            "document_type":
                row.get(
                    "document_type"
                ),

            "publisher":
                row.get(
                    "publisher"
                ),

            "crop":
                row.get(
                    "crop"
                ),

            "culture":
                row.get(
                    "culture"
                ),

            "keywords":
                row.get(
                    "keywords"
                ),

            "country":
                row.get(
                    "country"
                ),

            "zone_geographique":
                row.get(
                    "zone_geographique"
                ),
        }

        return {
            key: value
            for key, value in metadata.items()
            if value is not None
        }

    # =========================================================
    # CONVERSION VALEUR → STRING
    # =========================================================

    @staticmethod
    def _to_string(
        value: Any,
    ):

        if value is None:

            return None

        return str(value)

    # =========================================================
    # NORMALISATION DATE
    # =========================================================

    @staticmethod
    def _normalize_date(
        value: Any,
    ):

        if value is None:

            return None

        if hasattr(
            value,
            "isoformat",
        ):

            return value.isoformat()

        return str(value)

    # =========================================================
    # NORMALISATION MOTS-CLÉS
    # =========================================================

    @staticmethod
    def _normalize_keywords(
        value: Any,
    ):

        if value is None:

            return None

        if isinstance(
            value,
            list,
        ):

            return ", ".join(
                str(item)
                for item in value
            )

        return str(value)