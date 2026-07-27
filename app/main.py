from datetime import date, datetime
import os
import requests

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

        downloader = FAOODSDownloader()

        result = downloader.download()

        # =================================================
        # CAS 1 : DICTIONNAIRE
        # =================================================

        if isinstance(result, dict):

            content = result.get("content")

            return {

                "status":
                    "success",

                "returned_type":
                    "dict",

                "keys":
                    list(result.keys()),

                "filename":
                    result.get("filename"),

                "url":
                    result.get("url"),

                "has_content":
                    content is not None,

                "content_type":
                    (
                        type(content).__name__
                        if content is not None
                        else None
                    ),

                "content_size":
                    (
                        len(content)
                        if content is not None
                        else 0
                    ),

                "content_preview":
                    (
                        content[:1000].decode(
                            "utf-8",
                            errors="replace"
                        )
                        if isinstance(content, bytes)
                        else str(content)[:1000]
                        if content is not None
                        else None
                    )

            }

        # =================================================
        # CAS 2 : CHEMIN / AUTRE VALEUR
        # =================================================

        return {

            "status":
                "success",

            "returned_type":
                type(result).__name__,

            "returned_value":
                str(result)

        }

    except Exception as e:

        return {

            "status":
                "error",

            "error_type":
                type(e).__name__,

            "message":
                str(e)

        }

# =========================================================
# TEST PIPELINE FAO → RAG → SUPABASE
# =========================================================

@app.get(
    "/knowledge/fao-rag-pipeline-test"
)
def fao_rag_pipeline_test():

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

    from app.knowledge_engine.storage.rag_ingestion import (
        RAGIngestion
    )

    try:

        # =====================================================
        # 1. TÉLÉCHARGER LE CATALOGUE AGRIS
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

        # =====================================================
        # 2. EXTRAIRE LE CONTENU DU CATALOGUE
        # =====================================================

        if isinstance(
            ods_downloaded,
            dict
        ):

            ods_content = (
                ods_downloaded.get(
                    "content"
                )
            )

        else:

            ods_content = None

        if not ods_content:

            return {
                "status": "error",
                "step": "ods_download",
                "message": (
                    "Le catalogue AGRIS "
                    "ne contient aucun contenu."
                )
            }

        # =====================================================
        # 3. PARSER LE CATALOGUE AGRIS
        # =====================================================

        print(
            "[FAO RAG] "
            "Parsing catalogue AGRIS..."
        )

        ods_parser = (
            FAOODSParser(
                ods_content
            )
        )

        datasets = (
            ods_parser.parse()
        )

        if not datasets:

            return {
                "status": "error",
                "step": "ods_parse",
                "message": (
                    "Aucun dataset trouvé "
                    "dans le catalogue AGRIS."
                )
            }

        # =====================================================
        # 4. PRENDRE LE PREMIER DATASET
        # =====================================================

        dataset = datasets[0]

        dataset_url = str(
            dataset.url
        ).strip()

        filename = (
            dataset_url
            .rstrip("/")
            .split("/")[-1]
        )

        print(
            "[FAO RAG] "
            f"Dataset sélectionné : {filename}"
        )

        # =====================================================
        # 5. TÉLÉCHARGER LE DATASET EN MÉMOIRE
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
                "status": "error",
                "step": "dataset_download",
                "message": (
                    "Format du dataset "
                    "téléchargé invalide."
                )
            }

        xml_content = (
            downloaded.get(
                "content"
            )
        )

        if not xml_content:

            return {
                "status": "error",
                "step": "dataset_content",
                "message": (
                    "Dataset XML vide."
                )
            }

        # =====================================================
        # 6. PARSER LE DATASET
        # =====================================================

        print(
            "[FAO RAG] "
            "Parsing du dataset..."
        )

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
                "status": "error",
                "step": "dataset_parse",
                "message": (
                    "Aucun document extrait "
                    "du dataset."
                )
            }

        print(
            "[FAO RAG] "
            f"{len(documents)} document(s) extraits."
        )

        # =====================================================
        # 7. INGESTION RAG
        # =====================================================

        print(
            "[FAO RAG] "
            "Début ingestion RAG..."
        )

        ingestion = (
            RAGIngestion()
        )

        # Pour le premier test :
        # seulement 3 documents.
        #
        # Cela évite de lancer inutilement
        # beaucoup d'appels Gemini si une erreur
        # Supabase apparaît.

        ingestion_result = (
            ingestion.ingest_documents(
                documents=documents,
                limit=3
            )
        )

        # =====================================================
        # 8. RÉSULTAT
        # =====================================================

        return {
            "status": "success",
            "dataset_url": dataset_url,
            "dataset_filename": filename,
            "documents_parsed": len(
                documents
            ),
            "rag": ingestion_result
        }

    except Exception as e:

        print(
            "[FAO RAG] "
            f"Erreur : {e}"
        )

        return {
            "status": "error",
            "message": str(
                e
            )
        }
# =========================================================
# ROUTE RACINE
# =========================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "message": "API SikaGlé fonctionnelle"
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
            "database": "disconnected",
            "reason": "Variables Supabase manquantes"
        }

    try:

        response = (
            supabase
            .table("users")
            .select(
                "id",
                count="exact"
            )
            .limit(1)
            .execute()
        )

        return {
            "database": "connected",
            "status": "ok",
            "users_count": response.count or 0
        }

    except Exception as e:

        return {
            "database": "error",
            "details": str(e)
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
            "status": "success",
            "message": "Knowledge Engine exécuté"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
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
# TÉLÉCHARGEMENT DES DATASETS FAO
# =========================================================

@app.get(
    "/knowledge/fao-datasets-test"
)
def fao_datasets_test(
    limit: int = 10
):

    """
    Télécharge les datasets FAO découverts
    dans le catalogue AGRIS.

    Cette route n'est plus une route de debug.
    """

    try:

        return download_fao_datasets(
            limit=limit
        )

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


# =========================================================
# PIPELINE FAO COMPLET EN MÉMOIRE
# =========================================================

# =========================================================
# PIPELINE COMPLET FAO AGRIS -> PARSER -> RAG -> SUPABASE
# =========================================================

@app.get(
    "/knowledge/fao-dataset-pipeline-test"
)
def fao_dataset_pipeline_test(
    dataset_limit: int = 2,
    dataset_offset: int = 0,
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

    from app.knowledge_engine.storage.document_store import (
        DocumentStore
    )

    from app.knowledge_engine.storage.rag_ingestion import (
        RAGIngestion
    )

    try:

        # =====================================================
        # 1. VALIDATION DES PARAMÈTRES
        # =====================================================

        if dataset_limit <= 0:

            return {
                "status": "error",
                "message": (
                    "dataset_limit doit être "
                    "supérieur à 0."
                )
            }

        if dataset_limit > 5:

            return {
                "status": "error",
                "message": (
                    "Pour le moment, dataset_limit "
                    "ne peut pas dépasser 5."
                )
            }

        if dataset_offset < 0:

            return {
                "status": "error",
                "message": (
                    "dataset_offset ne peut pas "
                    "être négatif."
                )
            }

        if rag_limit <= 0:

            return {
                "status": "error",
                "message": (
                    "rag_limit doit être "
                    "supérieur à 0."
                )
            }


        # =====================================================
        # 2. TÉLÉCHARGER LE CATALOGUE AGRIS
        # =====================================================

        print("=" * 60)

        print(
            "[FAO MULTI PIPELINE] "
            "Téléchargement catalogue AGRIS..."
        )

        print("=" * 60)

        ods_downloader = (
            FAOODSDownloader()
        )

        ods_result = (
            ods_downloader.download()
        )


        # =====================================================
        # 3. EXTRAIRE LE CONTENU DU CATALOGUE
        # =====================================================

        if isinstance(
            ods_result,
            dict
        ):

            ods_content = (
                ods_result.get(
                    "content"
                )
            )

            catalog_filename = (
                ods_result.get(
                    "filename"
                )
                or
                "AGRIS.ODS.xml"
            )

        else:

            return {
                "status": "error",
                "step": "catalog_download",
                "message": (
                    "Format retourné par "
                    "FAOODSDownloader invalide."
                ),
                "returned_type": (
                    type(
                        ods_result
                    ).__name__
                )
            }


        if not ods_content:

            return {
                "status": "error",
                "step": "catalog_download",
                "message": (
                    "Le catalogue AGRIS "
                    "est vide."
                )
            }


        # =====================================================
        # 4. PARSER LE CATALOGUE AGRIS
        # =====================================================

        print(
            "[FAO MULTI PIPELINE] "
            "Parsing catalogue..."
        )

        ods_parser = (
            FAOODSParser(
                ods_result
            )
        )

        datasets = (
            ods_parser.parse()
        )

        total_datasets = len(
            datasets
        )


        print(
            "[FAO MULTI PIPELINE] "
            f"{total_datasets} dataset(s) "
            "disponible(s)."
        )


        if total_datasets == 0:

            return {
                "status": "error",
                "step": "catalog_parse",
                "message": (
                    "Aucun dataset AGRIS trouvé."
                )
            }


        # =====================================================
        # 5. VÉRIFIER L'OFFSET
        # =====================================================

        if dataset_offset >= total_datasets:

            return {
                "status": "success",
                "message": (
                    "Tous les datasets AGRIS "
                    "ont été parcourus."
                ),
                "datasets_found": (
                    total_datasets
                ),
                "dataset_offset": (
                    dataset_offset
                ),
                "dataset_limit": (
                    dataset_limit
                ),
                "datasets_processed": 0,
                "next_dataset_offset": (
                    dataset_offset
                ),
                "has_more_datasets": False
            }


        # =====================================================
        # 6. SÉLECTIONNER LE LOT DE DATASETS
        # =====================================================

        selected_datasets = (

            datasets[

                dataset_offset:

                dataset_offset
                + dataset_limit

            ]

        )


        print(
            "[FAO MULTI PIPELINE] "
            f"Traitement datasets "
            f"{dataset_offset} → "
            f"{dataset_offset + len(selected_datasets) - 1}"
        )


        # =====================================================
        # 7. SERVICES
        # =====================================================

        dataset_downloader = (
            FAODatasetsDownloader()
        )

        dataset_parser = (
            FAODatasetParser()
        )

        document_store = (
            DocumentStore()
        )


        # =====================================================
        # 8. COMPTEURS
        # =====================================================

        datasets_processed = 0
        datasets_success = 0
        datasets_errors = 0

        total_documents_parsed = 0
        total_documents_stored = 0

        dataset_results = []


        # =====================================================
        # 9. TRAITER CHAQUE DATASET
        # =====================================================

        for local_index, dataset in enumerate(
            selected_datasets
        ):

            absolute_index = (
                dataset_offset
                + local_index
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

            if not filename:

                filename = (
                    f"dataset_{absolute_index}.xml"
                )


            print("=" * 60)

            print(
                "[FAO MULTI PIPELINE] "
                f"Dataset #{absolute_index}"
            )

            print(
                "[FAO MULTI PIPELINE] "
                f"URL : {dataset_url}"
            )

            print("=" * 60)


            datasets_processed += 1


            try:

                # =============================================
                # 9.1 TÉLÉCHARGEMENT
                # =============================================

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

                    raise ValueError(
                        "Format retourné par "
                        "FAODatasetsDownloader invalide : "
                        f"{type(downloaded).__name__}"
                    )


                xml_content = (
                    downloaded.get(
                        "content"
                    )
                )


                if not xml_content:

                    raise ValueError(
                        "Dataset XML vide."
                    )


                # =============================================
                # 9.2 PARSING
                # =============================================

                documents = (
                    dataset_parser.parse(
                        xml_content=xml_content,
                        filename=filename,
                        source_url=dataset_url
                    )
                )


                parsed_count = len(
                    documents
                )


                total_documents_parsed += (
                    parsed_count
                )


                # =============================================
                # 9.3 STOCKAGE TEMPORAIRE
                # =============================================

                store_result = (
                    document_store.add_documents(
                        documents
                    )
                )


                stored_count = (
                    store_result.get(
                        "added",
                        0
                    )
                )


                total_documents_stored += (
                    stored_count
                )


                datasets_success += 1


                # =============================================
                # 9.4 RÉSULTAT DATASET
                # =============================================

                dataset_results.append({

                    "dataset_index":
                        absolute_index,

                    "status":
                        "success",

                    "dataset_url":
                        dataset_url,

                    "dataset_filename":
                        filename,

                    "xml_size":
                        len(
                            xml_content
                        ),

                    "documents_parsed":
                        parsed_count,

                    "documents_added_to_store":
                        stored_count

                })


            except Exception as dataset_error:

                datasets_errors += 1


                print(
                    "[FAO MULTI PIPELINE] "
                    f"Erreur dataset "
                    f"#{absolute_index} : "
                    f"{dataset_error}"
                )


                dataset_results.append({

                    "dataset_index":
                        absolute_index,

                    "status":
                        "error",

                    "dataset_url":
                        dataset_url,

                    "dataset_filename":
                        filename,

                    "message":
                        str(
                            dataset_error
                        )

                })


        # =====================================================
        # 10. INGESTION RAG
        # =====================================================

        print("=" * 60)

        print(
            "[FAO MULTI PIPELINE] "
            "Ingestion RAG..."
        )

        print("=" * 60)


        rag = (
            RAGIngestion()
        )


        rag_result = (
            rag.ingest(
                limit=rag_limit,
                offset=0
            )
        )


        # =====================================================
        # 11. PROCHAIN OFFSET DATASET
        # =====================================================

        next_dataset_offset = (
            dataset_offset
            + len(
                selected_datasets
            )
        )


        has_more_datasets = (
            next_dataset_offset
            < total_datasets
        )


        # =====================================================
        # 12. RÉSULTAT FINAL
        # =====================================================

        return {

            "status":
                "success",

            "catalog_filename":
                catalog_filename,

            "datasets_found":
                total_datasets,

            "dataset_offset":
                dataset_offset,

            "dataset_limit":
                dataset_limit,

            "datasets_processed":
                datasets_processed,

            "datasets_success":
                datasets_success,

            "datasets_errors":
                datasets_errors,

            "documents_parsed":
                total_documents_parsed,

            "documents_added_to_store":
                total_documents_stored,

            "rag_limit":
                rag_limit,

            "rag":
                rag_result,

            "next_dataset_offset":
                next_dataset_offset,

            "has_more_datasets":
                has_more_datasets,

            "datasets":
                dataset_results

        }


    except Exception as e:

        print(
            "[FAO MULTI PIPELINE] "
            f"Erreur générale : {e}"
        )

        return {

            "status":
                "error",

            "message":
                str(
                    e
                )

        }

# =========================================================
# TEST PARSER DES DATASETS FAO
# =========================================================

@app.get(
    "/knowledge/fao-dataset-parser-test"
)
def fao_dataset_parser_test(
    limit: int = 10
):

    """
    Teste le parser de plusieurs datasets FAO
    et leur sauvegarde dans DocumentStore.
    """

    try:

        return test_fao_dataset_parser(
            limit=limit
        )

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
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
# INGESTION RAG PAR BATCH
# =========================================================

@app.get(
    "/knowledge/rag-ingest"
)
def rag_ingest(
    limit: int = 100,
    offset: int = 0
):

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
            "status": "error",
            "message": str(e)
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
            content=str(challenge),
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

                msg = messages[0]

                sender_phone = msg.get(
                    "from"
                )

                msg_id = msg.get(
                    "id"
                )

                msg_type = msg.get(
                    "type",
                    "text"
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
                # EXTRACTION DU CONTENU
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
                # DATE DU JOUR
                # =================================================

                today_date = date.today()

                today_str = (
                    today_date.isoformat()
                )

                # =================================================
                # RECHERCHE UTILISATEUR
                # =================================================

                user_res = (
                    supabase
                    .table("users")
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
                        if days_old <= TRIAL_PERIOD_DAYS
                        else REGULAR_DAILY_LIMIT
                    )

                    # ---------------------------------------------
                    # RESET QUOTIDIEN
                    # ---------------------------------------------

                    if (
                        last_active != today_str
                        or user_credits is None
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
                        .table("users")
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
                # VÉRIFICATION DU QUOTA
                # =================================================

                if user_credits <= 0:

                    print(
                        f"⚠️ Utilisateur "
                        f"{user_id} "
                        "a épuisé ses crédits "
                        "du jour."
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
                # DÉCRÉMENTER LES CRÉDITS
                # =================================================

                remaining_credits = (
                    user_credits - 1
                )

                (
                    supabase
                    .table("users")
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
                # ENREGISTRER LE MESSAGE
                # =================================================

                (
                    supabase
                    .table("messages")
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
        "status": "success"
    }
