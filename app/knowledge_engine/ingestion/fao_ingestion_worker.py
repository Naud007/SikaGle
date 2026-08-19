import os
from pathlib import Path

from supabase import create_client, Client

from app.knowledge_engine.connectors.fao_ods import (
    FAOODSDownloader,
)
from app.knowledge_engine.parsers.fao_ods_parser import (
    FAOODSParser,
)
from app.knowledge_engine.connectors.fao_datasets import (
    FAODatasetsDownloader,
)
from app.knowledge_engine.parsers.fao_dataset_parser import (
    FAODatasetParser,
)
from app.knowledge_engine.storage.rag_ingestion import (
    RAGIngestion,
)


class FAOIngestionWorker:

    PIPELINE_NAME = "fao_agris"

    MAX_DATASET_LIMIT = 5

    def __init__(self):

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

        # =====================================================
        # CLIENT SUPABASE
        # =====================================================

        self.supabase: Client = (
            create_client(
                supabase_url,
                supabase_key,
            )
        )

    # =========================================================
    # ÉTAT
    # =========================================================

    def get_state(self):

        response = (
            self.supabase
            .table(
                "fao_ingestion_state"
            )
            .select("*")
            .eq(
                "pipeline_name",
                self.PIPELINE_NAME,
            )
            .limit(1)
            .execute()
        )

        rows = response.data or []

        if not rows:

            raise RuntimeError(
                "État d'ingestion FAO "
                "introuvable dans Supabase."
            )

        return rows[0]

    # =========================================================
    # SAUVEGARDER L'ÉTAT
    # =========================================================

    def save_state(
        self,
        dataset_offset,
        document_offset,
        documents_processed,
        datasets_completed,
        status,
        last_error=None,
    ):

        (
            self.supabase
            .table(
                "fao_ingestion_state"
            )
            .update({

                "dataset_offset":
                    dataset_offset,

                "document_offset":
                    document_offset,

                "documents_processed":
                    documents_processed,

                "datasets_completed":
                    datasets_completed,

                "status":
                    status,

                "last_error":
                    last_error,

            })
            .eq(
                "pipeline_name",
                self.PIPELINE_NAME,
            )
            .execute()
        )

    # =========================================================
    # TÉLÉCHARGER + PARSER LE CATALOGUE AGRIS
    # =========================================================

    def load_catalog(self):

        downloader = FAOODSDownloader()

        result = downloader.download()

        if not isinstance(
            result,
            dict,
        ):

            raise ValueError(
                "Format retourné par "
                "FAOODSDownloader invalide."
            )

        content = result.get(
            "content"
        )

        if not content:

            raise ValueError(
                "Catalogue AGRIS vide."
            )

        parser = FAOODSParser(
            result
        )

        datasets = parser.parse()

        if not datasets:

            raise ValueError(
                "Aucun dataset trouvé "
                "dans le catalogue AGRIS."
            )

        return {
            "filename":
                result.get(
                    "filename"
                )
                or "AGRIS.ODS.xml",

            "datasets":
                datasets,
        }

    # =========================================================
    # TÉLÉCHARGER UN DATASET
    # =========================================================

    def download_dataset(
        self,
        dataset,
        dataset_index,
    ):

        dataset_url = str(
            dataset.url
        ).strip()

        filename = (
            dataset_url
            .rstrip("/")
            .split("/")[-1]
        )

        if not filename:

            filename = (
                f"dataset_{dataset_index}.xml"
            )

        downloader = (
            FAODatasetsDownloader()
        )

        downloaded = (
            downloader.download(
                url=dataset_url,
                filename=filename,
            )
        )

        if not downloaded:

            raise ValueError(
                "Dataset impossible "
                "à télécharger."
            )

        if isinstance(
            downloaded,
            dict,
        ):

            xml_content = (
                downloaded.get(
                    "content"
                )
            )

            actual_filename = (
                downloaded.get(
                    "filename"
                )
                or filename
            )

        elif isinstance(
            downloaded,
            (str, Path),
        ):

            dataset_path = Path(
                downloaded
            )

            if not dataset_path.exists():

                raise ValueError(
                    "Le fichier dataset "
                    "n'existe pas."
                )

            xml_content = (
                dataset_path.read_bytes()
            )

            actual_filename = (
                dataset_path.name
            )

        else:

            raise ValueError(
                "Format du dataset "
                "téléchargé invalide."
            )

        if not xml_content:

            raise ValueError(
                "Dataset XML vide."
            )

        return {
            "url":
                dataset_url,

            "filename":
                actual_filename,

            "content":
                xml_content,
        }

    # =========================================================
    # PARSER UN DATASET
    # =========================================================

    def parse_dataset(
        self,
        xml_content,
        filename,
        source_url,
    ):

        parser = FAODatasetParser()

        return parser.parse(
            xml_content=xml_content,
            filename=filename,
            source_url=source_url,
        )

    # =========================================================
    # TRAITER UN DATASET
    # =========================================================

    def process_dataset(
        self,
        dataset,
        dataset_index,
        document_offset,
        rag_limit,
    ):

        downloaded = self.download_dataset(
            dataset=dataset,
            dataset_index=dataset_index,
        )

        dataset_url = downloaded["url"]
        filename = downloaded["filename"]
        xml_content = downloaded["content"]

        documents = self.parse_dataset(
            xml_content=xml_content,
            filename=filename,
            source_url=dataset_url,
        )

        documents_count = len(
            documents
        )

        # =====================================================
        # DATASET VIDE
        # =====================================================

        if documents_count == 0:

            return {
                "status":
                    "success",

                "dataset_index":
                    dataset_index,

                "dataset_url":
                    dataset_url,

                "dataset_filename":
                    filename,

                "documents_parsed":
                    0,

                "batch_processed":
                    0,

                "next_offset":
                    0,

                "has_more":
                    False,

                "dataset_completed":
                    True,

                "rag": {},
            }

        # =====================================================
        # INGESTION RAG
        # =====================================================

        ingestion = RAGIngestion()

        rag_result = (
            ingestion.ingest_documents(
                documents=documents,
                limit=rag_limit,
                offset=document_offset,
            )
        )

        inserted = int(
            rag_result.get(
                "inserted",
                0,
            )
            or 0
        )

        updated = int(
            rag_result.get(
                "updated",
                0,
            )
            or 0
        )

        skipped = int(
            rag_result.get(
                "skipped",
                0,
            )
            or 0
        )

        errors = int(
            rag_result.get(
                "errors",
                0,
            )
            or 0
        )

        batch_processed = int(
            rag_result.get(
                "batch_processed",
                0,
            )
            or 0
        )

        next_offset = int(
            rag_result.get(
                "next_offset",
                document_offset,
            )
            or document_offset
        )

        has_more = bool(
            rag_result.get(
                "has_more",
                False,
            )
        )

        return {

            "status":
                "success",

            "dataset_index":
                dataset_index,

            "dataset_url":
                dataset_url,

            "dataset_filename":
                filename,

            "xml_size":
                len(xml_content),

            "documents_parsed":
                documents_count,

            "document_offset":
                document_offset,

            "batch_processed":
                batch_processed,

            "inserted":
                inserted,

            "updated":
                updated,

            "skipped":
                skipped,

            "errors":
                errors,

            "next_offset":
                next_offset,

            "has_more":
                has_more,

            "dataset_completed":
                not has_more,

            "rag":
                rag_result,
        }

    # =========================================================
    # EXÉCUTER UN BATCH
    # =========================================================

    def run_batch(
        self,
        dataset_limit=1,
        rag_limit=20,
    ):

        # =====================================================
        # VALIDATION
        # =====================================================

        if dataset_limit <= 0:

            return {
                "status":
                    "error",

                "message":
                    (
                        "dataset_limit doit être "
                        "supérieur à 0."
                    ),
            }

        if dataset_limit > self.MAX_DATASET_LIMIT:

            return {
                "status":
                    "error",

                "message":
                    (
                        "dataset_limit ne peut pas "
                        f"dépasser {self.MAX_DATASET_LIMIT}."
                    ),
            }

        if rag_limit <= 0:

            return {
                "status":
                    "error",

                "message":
                    (
                        "rag_limit doit être "
                        "supérieur à 0."
                    ),
            }

        # =====================================================
        # ÉTAT
        # =====================================================

        state = self.get_state()

        dataset_offset = int(
            state.get(
                "dataset_offset",
                0,
            )
            or 0
        )

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

        datasets_completed_before = int(
            state.get(
                "datasets_completed",
                0,
            )
            or 0
        )

        # =====================================================
        # CATALOGUE
        # =====================================================

        catalog = self.load_catalog()

        catalog_filename = catalog["filename"]
        datasets = catalog["datasets"]

        total_datasets = len(
            datasets
        )

        # =====================================================
        # FIN
        # =====================================================

        if dataset_offset >= total_datasets:

            self.save_state(
                dataset_offset=dataset_offset,
                document_offset=document_offset,
                documents_processed=(
                    documents_processed_before
                ),
                datasets_completed=(
                    datasets_completed_before
                ),
                status="completed",
                last_error=None,
            )

            return {

                "status":
                    "completed",

                "message":
                    (
                        "Tous les datasets AGRIS "
                        "ont été parcourus."
                    ),

                "catalog_filename":
                    catalog_filename,

                "datasets_found":
                    total_datasets,

                "dataset_offset":
                    dataset_offset,

                "document_offset":
                    document_offset,

                "has_more_datasets":
                    False,
            }

        # =====================================================
        # DATASETS À TRAITER
        # =====================================================

        selected_datasets = datasets[
            dataset_offset:
            dataset_offset + dataset_limit
        ]

        datasets_results = []

        datasets_success = 0
        datasets_errors = 0

        total_documents_parsed = 0

        total_inserted = 0
        total_updated = 0
        total_skipped = 0
        total_errors = 0

        documents_processed_delta = 0
        datasets_completed_delta = 0

        next_dataset_offset = (
            dataset_offset
        )

        next_document_offset = (
            document_offset
        )

        # =====================================================
        # TRAITEMENT
        # =====================================================

        for local_index, dataset in enumerate(
            selected_datasets
        ):

            dataset_index = (
                dataset_offset
                + local_index
            )

            current_document_offset = (
                document_offset
                if local_index == 0
                else 0
            )

            try:

                result = self.process_dataset(
                    dataset=dataset,
                    dataset_index=dataset_index,
                    document_offset=current_document_offset,
                    rag_limit=rag_limit,
                )

                datasets_results.append(
                    result
                )

                datasets_success += 1

                documents_count = int(
                    result.get(
                        "documents_parsed",
                        0,
                    )
                    or 0
                )

                total_documents_parsed += (
                    documents_count
                )

                total_inserted += int(
                    result.get(
                        "inserted",
                        0,
                    )
                    or 0
                )

                total_updated += int(
                    result.get(
                        "updated",
                        0,
                    )
                    or 0
                )

                total_skipped += int(
                    result.get(
                        "skipped",
                        0,
                    )
                    or 0
                )

                total_errors += int(
                    result.get(
                        "errors",
                        0,
                    )
                    or 0
                )

                batch_processed = int(
                    result.get(
                        "batch_processed",
                        0,
                    )
                    or 0
                )

                documents_processed_delta += (
                    batch_processed
                )

                # =============================================
                # DATASET NON TERMINÉ
                # =============================================

                if result.get(
                    "has_more",
                    False,
                ):

                    next_dataset_offset = (
                        dataset_index
                    )

                    next_document_offset = (
                        result.get(
                            "next_offset",
                            current_document_offset,
                        )
                    )

                    break

                # =============================================
                # DATASET TERMINÉ
                # =============================================

                datasets_completed_delta += 1

                next_dataset_offset = (
                    dataset_index + 1
                )

                next_document_offset = 0

            except Exception as exc:

                datasets_errors += 1
                total_errors += 1

                next_dataset_offset = (
                    dataset_index
                )

                next_document_offset = (
                    current_document_offset
                )

                datasets_results.append({

                    "dataset_index":
                        dataset_index,

                    "status":
                        "error",

                    "message":
                        str(exc),
                })

                break

        # =====================================================
        # NOUVEL ÉTAT
        # =====================================================

        new_documents_processed = (
            documents_processed_before
            + documents_processed_delta
        )

        new_datasets_completed = (
            datasets_completed_before
            + datasets_completed_delta
        )

        has_more_datasets = (
            next_dataset_offset
            < total_datasets
        )

        pipeline_status = (
            "idle"
            if has_more_datasets
            else "completed"
        )

        last_error = None

        if datasets_errors > 0:

            pipeline_status = "error"

            if datasets_results:

                last_error = (
                    datasets_results[-1]
                    .get("message")
                )

        # =====================================================
        # SAUVEGARDE
        # =====================================================

        self.save_state(
            dataset_offset=next_dataset_offset,
            document_offset=next_document_offset,
            documents_processed=(
                new_documents_processed
            ),
            datasets_completed=(
                new_datasets_completed
            ),
            status=pipeline_status,
            last_error=last_error,
        )

        # =====================================================
        # ÉTAT FINAL
        # =====================================================

        final_state = self.get_state()

        # =====================================================
        # RÉSULTAT
        # =====================================================

        return {

            "status":
                (
                    "success"
                    if datasets_errors == 0
                    else "error"
                ),

            "catalog_filename":
                catalog_filename,

            "datasets_found":
                total_datasets,

            "start_dataset_offset":
                dataset_offset,

            "start_document_offset":
                document_offset,

            "dataset_limit":
                dataset_limit,

            "rag_limit":
                rag_limit,

            "datasets_processed":
                len(
                    datasets_results
                ),

            "datasets_success":
                datasets_success,

            "datasets_errors":
                datasets_errors,

            "documents_parsed":
                total_documents_parsed,

            "inserted":
                total_inserted,

            "updated":
                total_updated,

            "skipped":
                total_skipped,

            "errors":
                total_errors,

            "next_dataset_offset":
                final_state.get(
                    "dataset_offset"
                ),

            "next_document_offset":
                final_state.get(
                    "document_offset"
                ),

            "documents_processed":
                final_state.get(
                    "documents_processed"
                ),

            "datasets_completed":
                final_state.get(
                    "datasets_completed"
                ),

            "pipeline_status":
                final_state.get(
                    "status"
                ),

            "has_more_datasets":
                (
                    int(
                        final_state.get(
                            "dataset_offset",
                            0,
                        )
                        or 0
                    )
                    < total_datasets
                ),

            "datasets":
                datasets_results,
        }