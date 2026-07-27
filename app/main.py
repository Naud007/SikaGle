from datetime import date, datetime
import os
import requests
from pathlib import Path

from fastapi import FastAPI, Request, Response
from supabase import create_client, Client

from app.ai.gemini_client import (
    test_gemini,
    list_gemini_models,
)

from app.ai.embeddings import (
    test_embedding,
)

from app.ai.rag_service import (
    test_rag,
)

from app.knowledge_engine.manager import (
    run,
    test_fao_ods,
    test_fao_parser,
    download_fao_datasets,
    test_fao_dataset_parser,
)

from app.knowledge_engine.storage.rag_ingestion import (
    RAGIngestion,
    test_rag_ingestion,
)
from app.knowledge_engine.ingestion.fao_ingestion_worker import (
    FAOIngestionWorker,
)


# =========================================================
# INITIALISATION FASTAPI
# =========================================================

app = FastAPI(
    title="SikaGlé API",
    version="1.0.0"
)


# =========================================================
# CONFIGURATION DES QUOTAS
# =========================================================

TRIAL_PERIOD_DAYS = 31
TRIAL_DAILY_LIMIT = 15
REGULAR_DAILY_LIMIT = 5


# =========================================================
# VARIABLES D'ENVIRONNEMENT
# =========================================================

VERIFY_TOKEN = os.getenv(
    "WHATSAPP_VERIFY_TOKEN",
    "sikagle_secret_token_2026"
)

WHATSAPP_TOKEN = os.getenv(
    "WHATSAPP_TOKEN",
    ""
)

WHATSAPP_PHONE_ID = os.getenv(
    "WHATSAPP_PHONE_ID",
    ""
)

SUPABASE_URL = os.getenv(
    "SUPABASE_URL",
    ""
)

SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    ""
)


# =========================================================
# INITIALISATION SUPABASE
# =========================================================

supabase: Client | None = None


if SUPABASE_URL and SUPABASE_KEY:

    try:

        supabase = create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

        print(
            "✅ Connexion Supabase initialisée."
        )

    except Exception as e:

        print(
            "❌ Erreur initialisation Supabase:",
            e
        )


# =========================================================
# ENVOI MESSAGE WHATSAPP
# =========================================================

def send_whatsapp_message(
    to_phone: str,
    text_body: str
):

    """
    Envoie un message texte à un utilisateur
    via l'API WhatsApp Cloud de Meta.
    """

    if (
        not WHATSAPP_TOKEN
        or not WHATSAPP_PHONE_ID
    ):

        print(
            "❌ Variables WHATSAPP_TOKEN "
            "ou WHATSAPP_PHONE_ID manquantes."
        )

        return False


    url = (
        f"https://graph.facebook.com/v18.0/"
        f"{WHATSAPP_PHONE_ID}/messages"
    )


    headers = {

        "Authorization":
            f"Bearer {WHATSAPP_TOKEN}",

        "Content-Type":
            "application/json"

    }


    payload = {

        "messaging_product":
            "whatsapp",

        "recipient_type":
            "individual",

        "to":
            to_phone,

        "type":
            "text",

        "text": {

            "body":
                text_body

        }

    }


    try:

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )


        if response.status_code == 200:

            print(
                f"✉️ Message WhatsApp envoyé "
                f"avec succès à {to_phone}"
            )

            return True


        print(
            f"❌ Échec d'envoi WhatsApp "
            f"({response.status_code}):",
            response.text
        )

        return False


    except Exception as e:

        print(
            "❌ Erreur de connexion "
            "lors de l'envoi WhatsApp:",
            str(e)
        )

        return False


# =========================================================
# ROUTE RACINE
# =========================================================

@app.get("/")
def root():

    return {

        "status":
            "online",

        "message":
            "API SikaGlé fonctionnelle"

    }


# =========================================================
# STATUT BASE DE DONNÉES
# =========================================================

@app.get(
    "/db-status"
)
def db_status():

    if not supabase:

        return {

            "database":
                "disconnected",

            "reason":
                "Variables Supabase manquantes"

        }


    try:

        response = (

            supabase

            .table(
                "users"
            )

            .select(
                "id",
                count="exact"
            )

            .limit(
                1
            )

            .execute()

        )


        return {

            "database":
                "connected",

            "status":
                "ok",

            "users_count":
                response.count or 0

        }


    except Exception as e:

        return {

            "database":
                "error",

            "details":
                str(e)

        }


# =========================================================
# TEST GEMINI
# =========================================================

@app.get(
    "/ai/gemini-test"
)
def gemini_test():

    return test_gemini()


# =========================================================
# LISTE DES MODÈLES GEMINI
# =========================================================

@app.get(
    "/ai/models"
)
def gemini_models():

    return list_gemini_models()


# =========================================================
# TEST EMBEDDING GEMINI
# =========================================================

@app.get(
    "/ai/embedding-test"
)
def embedding_test():

    return test_embedding()


# =========================================================
# TEST RAG
# =========================================================

@app.get(
    "/ai/rag-test"
)
def rag_test():

    return test_rag()


# =========================================================
# KNOWLEDGE ENGINE
# =========================================================

@app.get(
    "/knowledge/test"
)
def test_knowledge_engine():

    try:

        run()

        return {

            "status":
                "success",

            "message":
                "Knowledge Engine exécuté"

        }

    except Exception as e:

        return {

            "status":
                "error",

            "message":
                str(e)

        }


# =========================================================
# DEBUG RETOUR FAO ODS DOWNLOADER
# =========================================================

@app.get(
    "/knowledge/fao-ods-structure"
)
def fao_ods_structure():

    from app.knowledge_engine.connectors.fao_ods import (
        FAOODSDownloader
    )


    try:

        downloader = (
            FAOODSDownloader()
        )

        result = (
            downloader.download()
        )


        # =====================================================
        # CAS DICTIONNAIRE
        # =====================================================

        if isinstance(
            result,
            dict
        ):

            content = (
                result.get(
                    "content"
                )
            )


            return {

                "status":
                    "success",

                "returned_type":
                    "dict",

                "keys":
                    list(
                        result.keys()
                    ),

                "filename":
                    result.get(
                        "filename"
                    ),

                "url":
                    result.get(
                        "url"
                    ),

                "has_content":
                    content is not None,

                "content_type":
                    (
                        type(
                            content
                        ).__name__

                        if content is not None

                        else None
                    ),

                "content_size":
                    (
                        len(
                            content
                        )

                        if content is not None

                        else 0
                    ),

                "content_preview":
                    (
                        content[:1000].decode(
                            "utf-8",
                            errors="replace"
                        )

                        if isinstance(
                            content,
                            bytes
                        )

                        else str(
                            content
                        )[:1000]

                        if content is not None

                        else None
                    )

            }


        return {

            "status":
                "success",

            "returned_type":
                type(
                    result
                ).__name__,

            "returned_value":
                str(
                    result
                )

        }


    except Exception as e:

        return {

            "status":
                "error",

            "error_type":
                type(
                    e
                ).__name__,

            "message":
                str(
                    e
                )

        }


# =========================================================
# TEST FAO ODS
# =========================================================

@app.get(
    "/knowledge/fao-ods-test"
)
def fao_ods_test():

    return test_fao_ods()


# =========================================================
# TEST PARSER CATALOGUE FAO AGRIS
# =========================================================

@app.get(
    "/knowledge/fao-parser-test"
)
def fao_parser_test():

    return test_fao_parser()


# =========================================================
# TÉLÉCHARGEMENT DATASETS FAO
# =========================================================

@app.get(
    "/knowledge/fao-datasets-test"
)
def fao_datasets_test(
    limit: int = 10
):

    try:

        return download_fao_datasets(
            limit=limit
        )

    except Exception as e:

        return {

            "status":
                "error",

            "message":
                str(e)

        }


# =========================================================
# TEST PIPELINE SIMPLE
# FAO -> PARSER -> RAG -> SUPABASE
# =========================================================

@app.get(
    "/knowledge/fao-rag-pipeline-test"
)
def fao_rag_pipeline_test(
    rag_limit: int = 3
):

    from app.knowledge_engine.connectors.fao_ods import (
        FAOODSDownloader
    )

    from app.knowledge_engine.parsers.fao_ods_parser import (
        FAOODSParser
    )

    from app.knowledge_engine.connectors.fao_datasets import (
        FAODatasetsDownloader
    )

    from app.knowledge_engine.parsers.fao_dataset_parser import (
        FAODatasetParser
    )


    try:

        # =====================================================
        # VALIDATION
        # =====================================================

        if rag_limit <= 0:

            return {

                "status":
                    "error",

                "message":
                    "rag_limit doit être supérieur à 0."

            }


        # =====================================================
        # 1. CATALOGUE AGRIS
        # =====================================================

        print(
            "[FAO RAG] "
            "Téléchargement catalogue AGRIS..."
        )


        ods_downloader = (
            FAOODSDownloader()
        )


        ods_downloaded = (
            ods_downloader.download()
        )


        if not isinstance(
            ods_downloaded,
            dict
        ):

            return {

                "status":
                    "error",

                "step":
                    "ods_download",

                "message":
                    "Format catalogue AGRIS invalide."

            }


        ods_content = (
            ods_downloaded.get(
                "content"
            )
        )


        if not ods_content:

            return {

                "status":
                    "error",

                "step":
                    "ods_download",

                "message":
                    "Catalogue AGRIS vide."

            }


        # =====================================================
        # 2. PARSER CATALOGUE
        # =====================================================

        ods_parser = (
            FAOODSParser(
                ods_downloaded
            )
        )


        datasets = (
            ods_parser.parse()
        )


        if not datasets:

            return {

                "status":
                    "error",

                "step":
                    "ods_parse",

                "message":
                    "Aucun dataset trouvé."

            }


        # =====================================================
        # 3. PREMIER DATASET
        # =====================================================

        dataset = (
            datasets[0]
        )


        dataset_url = str(
            dataset.url
        ).strip()


        filename = (
            dataset_url
            .rstrip("/")
            .split("/")
            [-1]
        )


        # =====================================================
        # 4. TÉLÉCHARGER DATASET
        # =====================================================

        dataset_downloader = (
            FAODatasetsDownloader()
        )


        downloaded = (
            dataset_downloader.download(
                url=dataset_url,
                filename=filename
            )
        )


        if not isinstance(
            downloaded,
            dict
        ):

            return {

                "status":
                    "error",

                "step":
                    "dataset_download",

                "message":
                    "Format dataset invalide."

            }


        xml_content = (
            downloaded.get(
                "content"
            )
        )


        if not xml_content:

            return {

                "status":
                    "error",

                "step":
                    "dataset_content",

                "message":
                    "Dataset XML vide."

            }


        # =====================================================
        # 5. PARSER DATASET
        # =====================================================

        dataset_parser = (
            FAODatasetParser()
        )


        documents = (
            dataset_parser.parse(
                xml_content=xml_content,
                filename=filename,
                source_url=dataset_url
            )
        )


        if not documents:

            return {

                "status":
                    "error",

                "step":
                    "dataset_parse",

                "message":
                    "Aucun document extrait."

            }


        # =====================================================
        # 6. INGESTION DIRECTE
        # =====================================================

        ingestion = (
            RAGIngestion()
        )


        ingestion_result = (
            ingestion.ingest_documents(
                documents=documents,
                limit=rag_limit,
                offset=0
            )
        )


        # =====================================================
        # RÉSULTAT
        # =====================================================

        return {

            "status":
                "success",

            "dataset_url":
                dataset_url,

            "dataset_filename":
                filename,

            "documents_parsed":
                len(
                    documents
                ),

            "rag":
                ingestion_result

        }


    except Exception as e:

        print(
            "[FAO RAG] "
            f"Erreur : {e}"
        )


        return {

            "status":
                "error",

            "message":
                str(
                    e
                )

        }


@app.get("/knowledge/fao-dataset-pipeline-test")
def fao_dataset_pipeline_test(
    dataset_limit: int = 1,
    rag_limit: int = 3
):

    from app.knowledge_engine.connectors.fao_ods import (
        FAOODSDownloader
    )

    from app.knowledge_engine.parsers.fao_ods_parser import (
        FAOODSParser
    )

    from app.knowledge_engine.connectors.fao_datasets import (
        FAODatasetsDownloader
    )

    from app.knowledge_engine.parsers.fao_dataset_parser import (
        FAODatasetParser
    )

    try:

        # =====================================================
        # 1. VALIDATION
        # =====================================================

        if dataset_limit <= 0:

            return {
                "status": "error",
                "message": (
                    "dataset_limit doit être supérieur à 0."
                )
            }

        if dataset_limit > 5:

            return {
                "status": "error",
                "message": (
                    "dataset_limit ne peut pas dépasser 5."
                )
            }

        if rag_limit <= 0:

            return {
                "status": "error",
                "message": (
                    "rag_limit doit être supérieur à 0."
                )
            }

        # =====================================================
        # 2. LIRE LA PROGRESSION DEPUIS SUPABASE
        # =====================================================

        worker = FAOIngestionWorker()

        state = worker.get_state()

        dataset_offset = int(
            state.get(
                "dataset_offset"
            )
            or 0
        )

        document_offset = int(
            state.get(
                "document_offset"
            )
            or 0
        )

        documents_processed_before = int(
            state.get(
                "documents_processed"
            )
            or 0
        )

        datasets_completed_before = int(
            state.get(
                "datasets_completed"
            )
            or 0
        )

        print(
            "[FAO PIPELINE] "
            f"Reprise automatique : "
            f"dataset_offset={dataset_offset}, "
            f"document_offset={document_offset}"
        )

        # =====================================================
        # 3. TÉLÉCHARGER LE CATALOGUE AGRIS
        # =====================================================

        ods_downloader = (
            FAOODSDownloader()
        )

        ods_result = (
            ods_downloader.download()
        )

        if not isinstance(
            ods_result,
            dict
        ):

            return {
                "status": "error",
                "step": "catalog_download",
                "message": (
                    "Format retourné par "
                    "FAOODSDownloader invalide."
                )
            }

        catalog_content = (
            ods_result.get(
                "content"
            )
        )

        catalog_filename = (
            ods_result.get(
                "filename"
            )
            or "AGRIS.ODS.xml"
        )

        if not catalog_content:

            return {
                "status": "error",
                "step": "catalog_download",
                "message": (
                    "Catalogue AGRIS vide."
                )
            }

        # =====================================================
        # 4. PARSER LE CATALOGUE
        # =====================================================

        ods_parser = (
            FAOODSParser(
                ods_result
            )
        )

        datasets = (
            ods_parser.parse()
        )

        if not datasets:

            return {
                "status": "error",
                "step": "catalog_parse",
                "message": (
                    "Aucun dataset trouvé "
                    "dans le catalogue AGRIS."
                )
            }

        total_datasets = len(
            datasets
        )

        # =====================================================
        # 5. VÉRIFIER SI TOUT EST TERMINÉ
        # =====================================================

        if dataset_offset >= total_datasets:

            (
                worker.supabase
                .table(
                    "fao_ingestion_state"
                )
                .update({
                    "status":
                        "completed",
                    "last_error":
                        None
                })
                .eq(
                    "pipeline_name",
                    worker.PIPELINE_NAME
                )
                .execute()
            )

            return {
                "status":
                    "completed",

                "message":
                    (
                        "Tous les datasets AGRIS "
                        "ont été parcourus."
                    ),

                "datasets_found":
                    total_datasets,

                "dataset_offset":
                    dataset_offset,

                "document_offset":
                    document_offset,

                "has_more_datasets":
                    False
            }

        # =====================================================
        # 6. DATASETS À TRAITER
        # =====================================================

        selected_datasets = datasets[
            dataset_offset:
            dataset_offset + dataset_limit
        ]

        dataset_downloader = (
            FAODatasetsDownloader()
        )

        dataset_parser = (
            FAODatasetParser()
        )

        rag_ingestion = (
            RAGIngestion()
        )

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
        # 7. TRAITER LES DATASETS
        # =====================================================

        for local_index, dataset in enumerate(
            selected_datasets
        ):

            dataset_index = (
                dataset_offset
                + local_index
            )

            try:

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

                # =============================================
                # TÉLÉCHARGER DATASET
                # =============================================

                downloaded = (
                    dataset_downloader.download(
                        url=dataset_url,
                        filename=filename
                    )
                )

                if not downloaded:

                    raise ValueError(
                        "Dataset impossible "
                        "à télécharger."
                    )

                # =============================================
                # RÉCUPÉRER XML
                # =============================================

                if isinstance(
                    downloaded,
                    dict
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
                    (str, Path)
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
                        dataset_path
                        .read_bytes()
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

                # =============================================
                # PARSER DATASET
                # =============================================

                documents = (
                    dataset_parser.parse(
                        xml_content=
                            xml_content,
                        filename=
                            actual_filename,
                        source_url=
                            dataset_url
                    )
                )

                documents_count = len(
                    documents
                )

                total_documents_parsed += (
                    documents_count
                )

                # =============================================
                # DATASET VIDE
                # =============================================

                if documents_count == 0:

                    datasets_success += 1
                    datasets_completed_delta += 1

                    next_dataset_offset = (
                        dataset_index + 1
                    )

                    next_document_offset = 0

                    datasets_results.append({
                        "dataset_index":
                            dataset_index,

                        "status":
                            "success",

                        "dataset_url":
                            dataset_url,

                        "dataset_filename":
                            actual_filename,

                        "documents_parsed":
                            0,

                        "message":
                            "Dataset sans document."
                    })

                    continue

                # =============================================
                # OFFSET DU DOCUMENT
                # =============================================

                if local_index == 0:

                    current_document_offset = (
                        document_offset
                    )

                else:

                    current_document_offset = 0

                # =============================================
                # INGESTION RAG
                # =============================================

                rag_result = (
                    rag_ingestion
                    .ingest_documents(
                        documents=documents,
                        limit=rag_limit,
                        offset=current_document_offset
                    )
                )

                inserted = int(
                    rag_result.get(
                        "inserted",
                        0
                    )
                    or 0
                )

                updated = int(
                    rag_result.get(
                        "updated",
                        0
                    )
                    or 0
                )

                skipped = int(
                    rag_result.get(
                        "skipped",
                        0
                    )
                    or 0
                )

                errors = int(
                    rag_result.get(
                        "errors",
                        0
                    )
                    or 0
                )

                batch_processed = int(
                    rag_result.get(
                        "batch_processed",
                        0
                    )
                    or 0
                )

                rag_next_offset = int(
                    rag_result.get(
                        "next_offset",
                        current_document_offset
                    )
                    or current_document_offset
                )

                has_more_documents = bool(
                    rag_result.get(
                        "has_more",
                        False
                    )
                )

                total_inserted += inserted
                total_updated += updated
                total_skipped += skipped
                total_errors += errors

                documents_processed_delta += (
                    batch_processed
                )

                datasets_success += 1

                datasets_results.append({
                    "dataset_index":
                        dataset_index,

                    "status":
                        "success",

                    "dataset_url":
                        dataset_url,

                    "dataset_filename":
                        actual_filename,

                    "xml_size":
                        len(
                            xml_content
                        ),

                    "documents_parsed":
                        documents_count,

                    "document_offset":
                        current_document_offset,

                    "rag":
                        rag_result
                })

                # =============================================
                # DATASET PAS ENCORE TERMINÉ
                # =============================================

                if has_more_documents:

                    next_dataset_offset = (
                        dataset_index
                    )

                    next_document_offset = (
                        rag_next_offset
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

            except Exception as e:

                datasets_errors += 1
                total_errors += 1

                next_dataset_offset = (
                    dataset_index
                )

                if local_index == 0:

                    next_document_offset = (
                        document_offset
                    )

                else:

                    next_document_offset = 0

                datasets_results.append({
                    "dataset_index":
                        dataset_index,

                    "status":
                        "error",

                    "message":
                        str(e)
                })

                break

        # =====================================================
        # 8. CALCULER LA NOUVELLE PROGRESSION
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
                    .get(
                        "message"
                    )
                )

        # =====================================================
        # 9. SAUVEGARDER LA PROGRESSION DANS SUPABASE
        # =====================================================

        (
            worker.supabase
            .table(
                "fao_ingestion_state"
            )
            .update({

                "dataset_offset":
                    next_dataset_offset,

                "document_offset":
                    next_document_offset,

                "documents_processed":
                    new_documents_processed,

                "datasets_completed":
                    new_datasets_completed,

                "status":
                    pipeline_status,

                "last_error":
                    last_error

            })
            .eq(
                "pipeline_name",
                worker.PIPELINE_NAME
            )
            .execute()
        )

        # =====================================================
        # 10. RELIRE L'ÉTAT SAUVEGARDÉ
        # =====================================================

        final_state = (
            worker.get_state()
        )

        # =====================================================
        # 11. RÉSULTAT
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
                            "dataset_offset"
                        )
                        or 0
                    )
                    < total_datasets
                ),

            "datasets":
                datasets_results
        }

    except Exception as e:

        return {
            "status":
                "error",

            "message":
                str(e)
        }
# =========================================================
# TEST PARSER DATASETS FAO
# =========================================================

@app.get(
    "/knowledge/fao-dataset-parser-test"
)
def fao_dataset_parser_test(
    limit: int = 10
):

    try:

        return test_fao_dataset_parser(
            limit=limit
        )

    except Exception as e:

        return {

            "status":
                "error",

            "message":
                str(e)

        }


# =========================================================
# TEST RAG INGESTION
# =========================================================

@app.get(
    "/knowledge/rag-ingestion-test"
)
def rag_ingestion_test():

    return test_rag_ingestion()


# =========================================================
# INGESTION RAG LEGACY
# =========================================================

@app.get(
    "/knowledge/rag-ingest"
)
def rag_ingest(
    limit: int = 100,
    offset: int = 0
):

    """
    Route conservée temporairement pour compatibilité.

    Le nouveau pipeline FAO utilise directement
    ingest_documents().
    """

    try:

        ingestion = (
            RAGIngestion()
        )


        return ingestion.ingest(
            limit=limit,
            offset=offset
        )


    except Exception as e:

        return {

            "status":
                "error",

            "message":
                str(e)

        }


# =========================================================
# WEBHOOK META
# VÉRIFICATION
# =========================================================

@app.get(
    "/webhook"
)
def verify_webhook(
    request: Request
):

    mode = request.query_params.get(
        "hub.mode"
    )

    token = request.query_params.get(
        "hub.verify_token"
    )

    challenge = request.query_params.get(
        "hub.challenge"
    )


    if (
        mode == "subscribe"
        and token == VERIFY_TOKEN
    ):

        print(
            "WEBHOOK_VERIFIED"
        )


        return Response(
            content=str(
                challenge
            ),
            media_type="text/plain",
            status_code=200
        )


    return Response(
        content="Verification failed",
        status_code=403
    )


# =========================================================
# WEBHOOK META
# RÉCEPTION DES MESSAGES WHATSAPP
# =========================================================

@app.post(
    "/webhook"
)
async def receive_webhook(
    request: Request
):

    data = await request.json()


    print(
        "Notification WhatsApp reçue :",
        data
    )


    try:

        entries = data.get(
            "entry",
            []
        )


        for entry in entries:

            changes = entry.get(
                "changes",
                []
            )


            for change in changes:

                value = change.get(
                    "value",
                    {}
                )


                messages = value.get(
                    "messages",
                    []
                )


                contacts = value.get(
                    "contacts",
                    []
                )


                # =================================================
                # VÉRIFIER MESSAGE ET SUPABASE
                # =================================================

                if (
                    not messages
                    or not supabase
                ):

                    continue


                msg = (
                    messages[0]
                )


                sender_phone = (
                    msg.get(
                        "from"
                    )
                )


                msg_id = (
                    msg.get(
                        "id"
                    )
                )


                msg_type = (
                    msg.get(
                        "type",
                        "text"
                    )
                )


                sender_name = (

                    contacts[0]

                    .get(
                        "profile",
                        {}
                    )

                    .get(
                        "name"
                    )

                    if contacts

                    else "Inconnu"

                )


                # =================================================
                # EXTRACTION CONTENU
                # =================================================

                content = ""


                if msg_type == "text":

                    content = (

                        msg

                        .get(
                            "text",
                            {}
                        )

                        .get(
                            "body",
                            ""
                        )

                    )


                elif msg_type in [

                    "image",
                    "audio",
                    "voice",
                    "document"

                ]:

                    content = (

                        f"[{msg_type.upper()}] "
                        "ID: "

                        + str(

                            msg

                            .get(
                                msg_type,
                                {}
                            )

                            .get(
                                "id",
                                ""
                            )

                        )

                    )


                # =================================================
                # DATE
                # =================================================

                today_date = (
                    date.today()
                )


                today_str = (
                    today_date.isoformat()
                )


                # =================================================
                # RECHERCHE UTILISATEUR
                # =================================================

                user_res = (

                    supabase

                    .table(
                        "users"
                    )

                    .select(
                        "id, "
                        "credits, "
                        "last_active_date, "
                        "created_at"
                    )

                    .eq(
                        "phone_number",
                        sender_phone
                    )

                    .execute()

                )


                # =================================================
                # UTILISATEUR EXISTANT
                # =================================================

                if user_res.data:

                    user = (
                        user_res.data[0]
                    )


                    user_id = (
                        user["id"]
                    )


                    user_credits = (
                        user.get(
                            "credits"
                        )
                    )


                    last_active = (
                        user.get(
                            "last_active_date"
                        )
                    )


                    created_at_str = (
                        user.get(
                            "created_at"
                        )
                    )


                    if created_at_str:

                        created_at_dt = (

                            datetime

                            .fromisoformat(

                                created_at_str

                                .replace(
                                    "Z",
                                    "+00:00"
                                )

                            )

                            .date()

                        )


                        days_old = (

                            today_date
                            - created_at_dt

                        ).days


                    else:

                        days_old = 0


                    daily_limit = (

                        TRIAL_DAILY_LIMIT

                        if days_old
                        <= TRIAL_PERIOD_DAYS

                        else REGULAR_DAILY_LIMIT

                    )


                    if (

                        last_active
                        != today_str

                        or user_credits
                        is None

                    ):

                        user_credits = (
                            daily_limit
                        )


                # =================================================
                # NOUVEL UTILISATEUR
                # =================================================

                else:

                    days_old = 0


                    daily_limit = (
                        TRIAL_DAILY_LIMIT
                    )


                    new_user = (

                        supabase

                        .table(
                            "users"
                        )

                        .insert({

                            "phone_number":
                                sender_phone,

                            "full_name":
                                sender_name,

                            "credits":
                                daily_limit,

                            "last_active_date":
                                today_str

                        })

                        .execute()

                    )


                    user_id = (
                        new_user.data[0]["id"]
                    )


                    user_credits = (
                        daily_limit
                    )


                # =================================================
                # QUOTA
                # =================================================

                if user_credits <= 0:

                    print(
                        f"⚠️ Utilisateur "
                        f"{user_id} "
                        "a épuisé ses crédits."
                    )


                    if (
                        days_old
                        <= TRIAL_PERIOD_DAYS
                    ):

                        alert_msg = (

                            "⚠️ *Quota quotidien atteint*\n\n"

                            f"Vous avez utilisé vos "
                            f"{TRIAL_DAILY_LIMIT} "
                            "messages gratuits "
                            "pour aujourd'hui.\n\n"

                            "👉 Vos crédits seront "
                            "réinitialisés demain matin. "
                            "À demain sur SikaGlé !"

                        )


                    else:

                        alert_msg = (

                            "⚠️ *Limite quotidienne atteinte*\n\n"

                            f"Vous avez atteint votre "
                            f"limite de "
                            f"{REGULAR_DAILY_LIMIT} "
                            "messages par jour.\n\n"

                            "👉 Pour un accès illimité "
                            "et continuer sans interruption, "
                            "abonnez-vous à SikaGlé !"

                        )


                    send_whatsapp_message(
                        sender_phone,
                        alert_msg
                    )


                    continue


                # =================================================
                # DÉCRÉMENTER CRÉDITS
                # =================================================

                remaining_credits = (
                    user_credits - 1
                )


                (

                    supabase

                    .table(
                        "users"
                    )

                    .update({

                        "credits":
                            remaining_credits,

                        "last_active_date":
                            today_str

                    })

                    .eq(
                        "id",
                        user_id
                    )

                    .execute()

                )


                # =================================================
                # ENREGISTRER MESSAGE
                # =================================================

                (

                    supabase

                    .table(
                        "messages"
                    )

                    .insert({

                        "user_id":
                            user_id,

                        "whatsapp_message_id":
                            msg_id,

                        "message_type":
                            msg_type,

                        "content":
                            content

                    })

                    .execute()

                )


                print(

                    "✅ Message enregistré. "

                    f"Crédits restants pour "
                    f"l'utilisateur {user_id} : "

                    f"{remaining_credits}/"
                    f"{daily_limit}"

                )


    except Exception as e:

        print(
            "❌ Erreur lors du traitement "
            "du message :",
            str(e)
        )


    return {

        "status":
            "success"

    }
