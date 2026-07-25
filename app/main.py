from fastapi import FastAPI, Request, Response
from supabase import create_client, Client
from datetime import date, datetime
import os
import requests
from pathlib import Path

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

supabase: Client = None


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
            headers=headers
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
# DEBUG FICHIERS XML FAO
# =========================================================

@app.get(
    "/knowledge/fao-xml-debug"
)
def fao_xml_debug():

    """
    Route temporaire de diagnostic.

    Permet de vérifier les fichiers XML FAO
    présents sur le serveur Render.

    Cette route sera supprimée après le diagnostic.
    """

    datasets_path = Path(
        "/app/knowledge/raw/fao/datasets"
    )

    print(
        "[FAO XML DEBUG] "
        f"Recherche dans : {datasets_path}"
    )

    # ---------------------------------------------------------
    # VÉRIFIER SI LE DOSSIER EXISTE
    # ---------------------------------------------------------

    if not datasets_path.exists():

        return {

            "status":
                "error",

            "message":
                "Le dossier des datasets FAO "
                "n'existe pas.",

            "path":
                str(
                    datasets_path
                )

        }


    # ---------------------------------------------------------
    # RECHERCHER LES FICHIERS XML
    # ---------------------------------------------------------

    xml_files = sorted(

        datasets_path.rglob(
            "*.xml"
        )

    )


    print(

        "[FAO XML DEBUG] "

        f"{len(xml_files)} fichier(s) XML trouvé(s)."

    )


    # ---------------------------------------------------------
    # AUCUN FICHIER
    # ---------------------------------------------------------

    if not xml_files:

        return {

            "status":
                "success",

            "message":
                "Aucun fichier XML trouvé.",

            "path":
                str(
                    datasets_path
                ),

            "files_count":
                0,

            "files":
                []

        }


    # ---------------------------------------------------------
    # INFORMATIONS SUR LES FICHIERS
    # ---------------------------------------------------------

    files = []


    for xml_file in xml_files[:20]:

        try:

            stat = (
                xml_file.stat()
            )

            files.append({

                "name":
                    xml_file.name,

                "path":
                    str(
                        xml_file
                    ),

                "size_bytes":
                    stat.st_size

            })

        except Exception as e:

            files.append({

                "name":
                    xml_file.name,

                "path":
                    str(
                        xml_file
                    ),

                "error":
                    str(
                        e
                    )

            })


    # ---------------------------------------------------------
    # LIRE LE PREMIER FICHIER XML
    # ---------------------------------------------------------

    first_file = (
        xml_files[0]
    )

    preview = ""


    try:

        with open(

            first_file,

            "r",

            encoding="utf-8",

            errors="replace"

        ) as file:

            preview = file.read(
                20000
            )


    except Exception as e:

        preview = (

            "Erreur lecture fichier XML : "

            + str(
                e
            )

        )


    # ---------------------------------------------------------
    # RÉSULTAT
    # ---------------------------------------------------------

    return {

        "status":
            "success",

        "path":
            str(
                datasets_path
            ),

        "files_count":
            len(
                xml_files
            ),

        "files":
            files,

        "first_file":
            str(
                first_file
            ),

        "first_file_preview":
            preview

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

        ingestion = RAGIngestion()

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
# TEST RAG
# =========================================================

@app.get(
    "/ai/rag-test"
)
def rag_test():

    return test_rag()


# =========================================================
# LISTE DES MODÈLES GEMINI
# =========================================================

@app.get(
    "/ai/models"
)
def gemini_models():

    return list_gemini_models()


# =========================================================
# TEST GEMINI
# =========================================================

@app.get(
    "/ai/gemini-test"
)
def gemini_test():

    return test_gemini()


# =========================================================
# TEST EMBEDDING GEMINI
# =========================================================

@app.get(
    "/ai/embedding-test"
)
def embedding_test():

    return test_embedding()


# =========================================================
# ROUTES KNOWLEDGE ENGINE
# =========================================================

@app.get(
    "/knowledge/test"
)
def test_knowledge_engine():

    """
    Lance tous les connecteurs enregistrés.
    """

    run()

    return {

        "status":
            "Knowledge Engine exécuté"

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
# TEST PARSER FAO AGRIS
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
def fao_datasets_test():

    return download_fao_datasets(
        limit=10
    )


# =========================================================
# TEST PARSER DES DATASETS FAO
# =========================================================

@app.get(
    "/knowledge/fao-dataset-parser-test"
)
def fao_dataset_parser_test():

    return test_fao_dataset_parser(
        limit=10
    )


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
                "count",
                count="exact"
            )

            .execute()

        )


        return {

            "database":
                "connected",

            "status":
                "ok",

            "users_count":
                response.count

        }


    except Exception as e:

        return {

            "database":
                "error",

            "details":
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

            content=
                str(challenge),

            media_type=
                "text/plain",

            status_code=
                200

        )


    return Response(

        content=
            "Verification failed",

        status_code=
            403

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

                    else

                    "Inconnu"

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
                        f"ID: "

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

                    today_date

                    .isoformat()

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


                    # ---------------------------------------------
                    # CALCUL ANCIENNETÉ
                    # ---------------------------------------------

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


                    # ---------------------------------------------
                    # LIMITE QUOTIDIENNE
                    # ---------------------------------------------

                    daily_limit = (

                        TRIAL_DAILY_LIMIT

                        if days_old
                        <= TRIAL_PERIOD_DAYS

                        else

                        REGULAR_DAILY_LIMIT

                    )


                    # ---------------------------------------------
                    # RESET QUOTIDIEN
                    # ---------------------------------------------

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

                        new_user

                        .data[0]["id"]

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
                        f"a épuisé ses crédits "
                        f"du jour."

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
                # ENREGISTRER LE MESSAGE
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

                    f"✅ Message enregistré. "

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
