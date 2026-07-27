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

@app.get(
    "/knowledge/fao-dataset-pipeline-test"
)
def fao_dataset_pipeline_test():

    """
    Teste le pipeline :

    catalogue AGRIS
        -> découverte dataset
        -> téléchargement
        -> contenu XML
        -> parsing des notices.

    Le dataset peut être traité directement en mémoire.
    """

    from pathlib import Path

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
        # 1. TÉLÉCHARGER LE CATALOGUE AGRIS
        # =====================================================

        print(
            "[PIPELINE TEST] "
            "Téléchargement catalogue AGRIS..."
        )

        ods_downloader = (
            FAOODSDownloader()
        )

        ods_path = (
            ods_downloader.download()
        )

        if not ods_path:

            return {
                "status": "error",
                "step": "ods_download",
                "message":
                    "Téléchargement AGRIS impossible."
            }

        # =====================================================
        # 2. PARSER LE CATALOGUE
        # =====================================================

        print(
            "[PIPELINE TEST] "
            "Parsing catalogue AGRIS..."
        )

        ods_parser = (
            FAOODSParser(
                ods_path
            )
        )

        datasets = (
            ods_parser.parse()
        )

        if not datasets:

            return {
                "status": "error",
                "step": "ods_parse",
                "message":
                    "Aucun dataset trouvé "
                    "dans le catalogue AGRIS."
            }

        print(
            "[PIPELINE TEST] "
            f"{len(datasets)} dataset(s) trouvé(s)."
        )

        # =====================================================
        # 3. PRENDRE LE PREMIER DATASET
        # =====================================================

        dataset = (
            datasets[0]
        )

        dataset_url = str(
            dataset.url
        ).strip()

        if not dataset_url:

            return {
                "status": "error",
                "step": "dataset_url",
                "message":
                    "Le premier dataset ne possède "
                    "pas d'URL."
            }

        filename = (
            dataset_url
            .rstrip("/")
            .split("/")[-1]
        )

        if not filename:

            filename = "dataset.xml"

        print(
            "[PIPELINE TEST] "
            "Dataset sélectionné :",
            dataset_url
        )

        # =====================================================
        # 4. TÉLÉCHARGER LE DATASET
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

        if not downloaded:

            return {
                "status": "error",
                "step": "dataset_download",
                "message":
                    "Dataset impossible à télécharger."
            }

        # =====================================================
        # 5. EXTRAIRE LE XML
        # =====================================================

        xml_content = None

        # -----------------------------------------------------
        # DOWNLOADER RETOURNANT UN DICTIONNAIRE
        # -----------------------------------------------------

        if isinstance(
            downloaded,
            dict
        ):

            xml_content = (
                downloaded.get(
                    "content"
                )
            )

        # -----------------------------------------------------
        # DOWNLOADER RETOURNANT UN CHEMIN
        # -----------------------------------------------------

        elif isinstance(
            downloaded,
            (
                str,
                Path
            )
        ):

            dataset_path = Path(
                downloaded
            )

            if not dataset_path.exists():

                return {
                    "status": "error",
                    "step": "dataset_file",
                    "message":
                        "Le fichier dataset "
                        "n'existe pas.",
                    "path":
                        str(dataset_path)
                }

            xml_content = (
                dataset_path.read_bytes()
            )

        # -----------------------------------------------------
        # FORMAT INCONNU
        # -----------------------------------------------------

        else:

            return {
                "status": "error",
                "step": "dataset_content",
                "message":
                    "Format retourné par "
                    "FAODatasetsDownloader non supporté.",
                "returned_type":
                    type(downloaded).__name__
            }

        # =====================================================
        # 6. VÉRIFIER LE CONTENU
        # =====================================================

        if not xml_content:

            return {
                "status": "error",
                "step": "dataset_content",
                "message":
                    "Le dataset téléchargé "
                    "ne contient aucun XML."
            }

        print(
            "[PIPELINE TEST] "
            f"XML chargé : "
            f"{len(xml_content)} octets"
        )

        # =====================================================
        # 7. PARSER LE DATASET
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

        # =====================================================
        # 8. RÉSULTAT
        # =====================================================

        return {
            "status":
                "success",

            "dataset_url":
                dataset_url,

            "dataset_filename":
                filename,

            "xml_size":
                len(xml_content),

            "documents_parsed":
                len(documents),

            "documents_preview": [
                {
                    "title":
                        getattr(
                            document,
                            "title",
                            None
                        ),

                    "url":
                        str(
                            getattr(
                                document,
                                "url",
                                ""
                            )
                        ),

                    "description":
                        getattr(
                            document,
                            "description",
                            None
                        )
                }

                for document in documents[:3]
            ]
        }

    except Exception as e:

        print(
            "[PIPELINE TEST] "
            f"Erreur : {e}"
        )

        return {
            "status": "error",
            "message": str(e)
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
