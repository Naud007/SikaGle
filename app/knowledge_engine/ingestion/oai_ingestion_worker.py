import json
import os
from datetime import datetime, timezone

from supabase import create_client, Client

from app.knowledge_engine.connectors.dataverse_license_checker import (
    DataverseLicenseChecker,
)
from app.knowledge_engine.connectors.registry import registry
from app.knowledge_engine.storage.rag_ingestion import (
    RAGIngestion,
)
from app.schemas.document import DocumentMetadata


class OAIIngestionWorker:
    """
    Worker d'ingestion GÉNÉRIQUE pour toute source documentaire
    accessible via un connecteur du registry (registry.get(...))
    dont discover() retourne list[DocumentMetadata] — pensé pour
    les sources OAI-PMH (AfricaRice, IRRI, Bioversity, CIFOR)
    mais pas limité à OAI-PMH en soi.
    """

    CACHE_BUCKET = "oai-cache"

    # =========================================================
    # SOURCES NÉCESSITANT UNE VÉRIFICATION DE LICENCE
    # PAR DOCUMENT (31/08/2026)
    #
    # AfricaRice n'y figure PAS : son dépôt entier est en CC0
    # (vérifié une fois pour toutes), donc inutile de faire un
    # appel réseau supplémentaire par document.
    #
    # IRRI, Bioversity/CIAT, CIFOR (et toute future source
    # Harvard Dataverse dont la licence n'est pas garantie en
    # bloc) doivent être ajoutées ici pour activer le filtrage.
    # =========================================================

    SOURCES_REQUIRING_LICENSE_CHECK = {
        "irri",
        "bioversity",
        "cifor",
    }

    def __init__(
        self,
        source: str,
    ):

        self.source = source

        self.license_checker = (
            DataverseLicenseChecker()
            if source
            in self.SOURCES_REQUIRING_LICENSE_CHECK
            else None
        )

        # =====================================================
        # CONFIGURATION SUPABASE
        # =====================================================

        supabase_url = os.getenv(
            "SUPABASE_URL"
        )

        supabase_key = os.getenv(
            "SUPABASE_KEY"
        )

        if not supabase_url:

            raise ValueError(
                "SUPABASE_URL manquante."
            )

        if not supabase_key:

            raise ValueError(
                "SUPABASE_KEY manquante."
            )

        self.supabase: Client = (
            create_client(
                supabase_url,
                supabase_key,
            )
        )

    # =========================================================
    # ÉTAT
    # =========================================================

    def get_state(self) -> dict:

        response = (
            self.supabase
            .table(
                "oai_ingestion_state"
            )
            .select("*")
            .eq(
                "source",
                self.source,
            )
            .limit(1)
            .execute()
        )

        rows = response.data or []

        if not rows:

            insert_response = (
                self.supabase
                .table(
                    "oai_ingestion_state"
                )
                .insert({
                    "source":
                        self.source,
                    "status":
                        "idle",
                })
                .execute()
            )

            return insert_response.data[0]

        return rows[0]

    def save_state(
        self,
        document_offset: int,
        documents_processed: int,
        total_documents: int | None,
        status: str,
        last_error: str | None = None,
        cache_updated: bool = False,
    ) -> None:

        update_payload = {

            "document_offset":
                document_offset,

            "documents_processed":
                documents_processed,

            "status":
                status,

            "last_error":
                last_error,
        }

        if total_documents is not None:

            update_payload[
                "total_documents"
            ] = total_documents

        if cache_updated:

            update_payload[
                "cache_updated_at"
            ] = (
                datetime
                .now(timezone.utc)
                .isoformat()
            )

        (
            self.supabase
            .table(
                "oai_ingestion_state"
            )
            .update(update_payload)
            .eq(
                "source",
                self.source,
            )
            .execute()
        )

    # =========================================================
    # CACHE (Supabase Storage)
    # =========================================================

    def _cache_path(self) -> str:

        return f"{self.source}.json"

    def _write_cache(
        self,
        documents: list[DocumentMetadata],
    ) -> None:

        payload = json.dumps(
            [
                document.model_dump(
                    mode="json"
                )
                for document in documents
            ]
        ).encode("utf-8")

        try:

            (
                self.supabase
                .storage
                .from_(
                    self.CACHE_BUCKET
                )
                .remove(
                    [self._cache_path()]
                )
            )

        except Exception:

            pass

        (
            self.supabase
            .storage
            .from_(
                self.CACHE_BUCKET
            )
            .upload(
                self._cache_path(),
                payload,
            )
        )

    def _read_cache(
        self,
    ) -> list[dict] | None:

        try:

            raw = (
                self.supabase
                .storage
                .from_(
                    self.CACHE_BUCKET
                )
                .download(
                    self._cache_path()
                )
            )

            return json.loads(
                raw.decode("utf-8")
            )

        except Exception as e:

            print(
                "[OAI CACHE] Lecture "
                f"impossible ({self.source}) : {e}"
            )

            return None

    def _clear_cache(self) -> None:

        try:

            (
                self.supabase
                .storage
                .from_(
                    self.CACHE_BUCKET
                )
                .remove(
                    [self._cache_path()]
                )
            )

        except Exception:

            pass

    # =========================================================
    # EXÉCUTER UN BATCH
    # =========================================================

    def run_batch(
        self,
        rag_limit: int = 20,
    ) -> dict:

        if rag_limit <= 0:

            return {
                "status": "error",
                "message": (
                    "rag_limit doit être "
                    "supérieur à 0."
                ),
            }

        state = self.get_state()

        document_offset = int(
            state.get(
                "document_offset",
                0,
            )
            or 0
        )

        documents_processed_before = int(
            state.get(
                "documents_processed",
                0,
            )
            or 0
        )

        total_documents = state.get(
            "total_documents"
        )

        # =====================================================
        # DÉCOUVERTE (une seule fois, mise en cache ensuite)
        # =====================================================

        cached_documents = None

        if (
            document_offset == 0
            or total_documents is None
        ):

            print(
                f"[OAI INGESTION] Découverte de "
                f"la source '{self.source}' "
                "(première fois ou reprise à zéro)..."
            )

            connector = registry.get(
                self.source
            )

            documents = connector.discover()

            total_documents = len(
                documents
            )

            self._write_cache(
                documents
            )

            cached_documents = [
                document.model_dump(
                    mode="json"
                )
                for document in documents
            ]

            print(
                f"[OAI INGESTION] {total_documents} "
                f"documents découverts pour "
                f"'{self.source}', mis en cache."
            )

        else:

            cached_documents = (
                self._read_cache()
            )

            if cached_documents is None:

                connector = registry.get(
                    self.source
                )

                documents = connector.discover()

                total_documents = len(
                    documents
                )

                self._write_cache(
                    documents
                )

                cached_documents = [
                    document.model_dump(
                        mode="json"
                    )
                    for document in documents
                ]

        # =====================================================
        # FIN
        # =====================================================

        if document_offset >= total_documents:

            self._clear_cache()

            self.save_state(
                document_offset=document_offset,
                documents_processed=(
                    documents_processed_before
                ),
                total_documents=total_documents,
                status="completed",
                last_error=None,
            )

            return {
                "status": "completed",
                "message": (
                    f"Tous les documents de "
                    f"'{self.source}' ont été "
                    "parcourus."
                ),
                "source": self.source,
                "total_documents": total_documents,
            }

        # =====================================================
        # BATCH
        # =====================================================

        batch = cached_documents[
            document_offset:
            document_offset + rag_limit
        ]

        # =====================================================
        # CORRECTIF (bug offset, 31/08/2026) :
        #
        # Retient le nombre de documents EXAMINÉS (avant
        # filtrage licence), car c'est ce nombre qui doit faire
        # avancer l'offset — sinon, un lot entièrement filtré
        # (licence non permissive) bloquait l'ingestion
        # indéfiniment sur le même lot, en boucle infinie
        # (observé en test réel : offset figé à 78 sur IRRI
        # pendant plusieurs dizaines de cycles).
        # =====================================================

        examined_count = len(
            batch
        )

        # =====================================================
        # FILTRAGE PAR LICENCE (si nécessaire pour cette source)
        # =====================================================

        licensed_out_count = 0

        if self.license_checker:

            filtered_batch = []

            for document in batch:

                identifier = document.get(
                    "identifier"
                )

                is_permissive = (
                    self.license_checker
                    .is_license_permissive(
                        identifier
                    )
                )

                if is_permissive:

                    filtered_batch.append(
                        document
                    )

                else:

                    licensed_out_count += 1

                    print(
                        "[LICENSE FILTER] Document "
                        "exclu (licence non permissive "
                        f"ou inconnue) : {identifier}"
                    )

            batch = filtered_batch

        # =====================================================
        # INGESTION RAG (seulement s'il reste des documents
        # après filtrage — sinon RAGIngestion planterait sur
        # une liste vide)
        # =====================================================

        if batch:

            ingestion = RAGIngestion()

            rag_result = (
                ingestion.ingest_documents(
                    documents=batch,
                    limit=rag_limit,
                    offset=0,
                )
            )

        else:

            rag_result = {
                "inserted": 0,
                "updated": 0,
                "filtered_out": 0,
                "skipped": 0,
                "errors": 0,
                "batch_processed": 0,
            }

        next_offset = (
            document_offset
            + examined_count
        )

        has_more = (
            next_offset
            < total_documents
        )

        pipeline_status = (
            "idle"
            if has_more
            else "completed"
        )

        new_documents_processed = (
            documents_processed_before
            + examined_count
        )

        if not has_more:

            self._clear_cache()

        self.save_state(
            document_offset=next_offset,
            documents_processed=(
                new_documents_processed
            ),
            total_documents=total_documents,
            status=pipeline_status,
            last_error=None,
        )

        return {
            "status": "success",
            "source": self.source,
            "total_documents": total_documents,
            "batch_offset": document_offset,
            "batch_processed": examined_count,
            "inserted": rag_result.get(
                "inserted", 0
            ),
            "updated": rag_result.get(
                "updated", 0
            ),
            "filtered_out": rag_result.get(
                "filtered_out", 0
            ),
            "licensed_out": licensed_out_count,
            "skipped": rag_result.get(
                "skipped", 0
            ),
            "errors": rag_result.get(
                "errors", 0
            ),
            "next_document_offset": next_offset,
            "documents_processed": (
                new_documents_processed
            ),
            "has_more": has_more,
        }