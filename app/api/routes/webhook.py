import asyncio
import os
import tempfile
from datetime import date, datetime

from fastapi import APIRouter, Request, Response

from app.integrations.media.media_service import (
    MediaService,
)
from app.integrations.whatsapp.sender import (
    send_whatsapp_message,
)
from app.multimodal.speech.speech_service import (
    SpeechService,
)
from app.services.agricultural_assistant_service import (
    AgriculturalAssistantService,
)


router = APIRouter()


VERIFY_TOKEN = os.getenv(
    "WHATSAPP_VERIFY_TOKEN",
    "sikagle_webhook_2026",
)

print(
    "🔐 WHATSAPP_VERIFY_TOKEN: PRESENT=",
    bool(VERIFY_TOKEN),
    "LENGTH=",
    len(VERIFY_TOKEN),
    "LAST4=",
    VERIFY_TOKEN[-4:] if VERIFY_TOKEN else "",
)

TRIAL_PERIOD_DAYS = 31
TRIAL_DAILY_LIMIT = 15
REGULAR_DAILY_LIMIT = 5


assistant = AgriculturalAssistantService()

media_service = MediaService()

speech_service = SpeechService()


# =========================================================
# VÉRIFICATION DU WEBHOOK WHATSAPP
# =========================================================

@router.get("/webhook")
def verify_webhook(
    request: Request,
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
            status_code=200,
        )

    return Response(
        content="Verification failed",
        status_code=403,
    )


# =========================================================
# RÉCEPTION DES MESSAGES WHATSAPP
# =========================================================

@router.post("/webhook")
async def receive_webhook(
    request: Request,
):

    from app.main import supabase

    data = await request.json()

    print(
        "Notification WhatsApp reçue :",
        data,
    )

    try:

        entries = data.get(
            "entry",
            [],
        )

        for entry in entries:

            changes = entry.get(
                "changes",
                [],
            )

            for change in changes:

                value = change.get(
                    "value",
                    {},
                )

                messages = value.get(
                    "messages",
                    [],
                )

                contacts = value.get(
                    "contacts",
                    [],
                )

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

                # =================================================
                # PROTECTION CONTRE LES DOUBLONS WHATSAPP
                # =================================================

                if msg_id:

                    existing_message = (
                        supabase
                        .table("messages")
                        .select("id")
                        .eq(
                            "whatsapp_message_id",
                            msg_id,
                        )
                        .limit(1)
                        .execute()
                    )

                    if existing_message.data:

                        print(
                            "ℹ️ Message WhatsApp déjà traité : "
                            f"{msg_id}"
                        )

                        continue

                msg_type = msg.get(
                    "type",
                    "text",
                )

                sender_name = (
                    contacts[0]
                    .get(
                        "profile",
                        {},
                    )
                    .get(
                        "name"
                    )
                    if contacts
                    else "Inconnu"
                )

                content = ""

                media_id = None

                # =================================================
                # MESSAGE TEXTE
                # =================================================

                if msg_type == "text":

                    content = (
                        msg
                        .get(
                            "text",
                            {},
                        )
                        .get(
                            "body",
                            "",
                        )
                    )

                # =================================================
                # MESSAGE AUDIO / VOCAL
                # =================================================

                elif msg_type in [
                    "audio",
                    "voice",
                ]:

                    media_id = (
                        msg
                        .get(
                            msg_type,
                            {},
                        )
                        .get(
                            "id",
                            "",
                        )
                    )

                # =================================================
                # IMAGE / DOCUMENT
                # =================================================

                elif msg_type in [
                    "image",
                    "document",
                ]:

                    content = (
                        f"[{msg_type.upper()}] "
                        "ID: "
                        + str(
                            msg
                            .get(
                                msg_type,
                                {},
                            )
                            .get(
                                "id",
                                "",
                            )
                        )
                    )

                # =================================================
                # DATE / QUOTA UTILISATEUR
                # =================================================

                today_date = date.today()

                today_str = (
                    today_date.isoformat()
                )

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
                        sender_phone,
                    )
                    .execute()
                )

                if user_res.data:

                    user = user_res.data[0]

                    user_id = user["id"]

                    user_credits = user.get(
                        "credits"
                    )

                    last_active = user.get(
                        "last_active_date"
                    )

                    created_at_str = user.get(
                        "created_at"
                    )

                    if created_at_str:

                        created_at_dt = (
                            datetime
                            .fromisoformat(
                                created_at_str.replace(
                                    "Z",
                                    "+00:00",
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

                    if (
                        last_active != today_str
                        or user_credits is None
                    ):

                        user_credits = daily_limit

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
                                today_str,
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
                # QUOTA ÉPUISÉ
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
                        alert_msg,
                    )

                    continue

                # =================================================
                # DÉCRÉMENT DU CRÉDIT
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
                            today_str,
                    })
                    .eq(
                        "id",
                        user_id,
                    )
                    .execute()
                )

                # =================================================
                # TRAITEMENT AUDIO
                # =================================================

                if (
                    msg_type in [
                        "audio",
                        "voice",
                    ]
                    and media_id
                ):

                    try:

                        with tempfile.TemporaryDirectory() as temp_dir:

                            audio_path = os.path.join(
                                temp_dir,
                                f"{media_id}.ogg",
                            )

                            media_file = (
                                media_service.download(
                                    media_id=media_id,
                                    destination=audio_path,
                                    media_type="audio",
                                    mime_type=(
                                        msg
                                        .get(
                                            msg_type,
                                            {},
                                        )
                                        .get(
                                            "mime_type",
                                            "audio/ogg",
                                        )
                                    ),
                                )
                            )

                            if not media_file.downloaded:

                                raise RuntimeError(
                                    "Le fichier audio WhatsApp "
                                    "n'a pas été téléchargé."
                                )

                            transcription = (
                                speech_service.transcribe(
                                    media_file.file_path
                                )
                            )

                            content = (
                                transcription.text
                            )

                            print(
                                "🎙️ Audio transcrit :",
                                content,
                            )

                    except Exception as e:

                        print(
                            f"❌ Erreur traitement audio : {e}"
                        )

                        send_whatsapp_message(
                            sender_phone,
                            "Je n'ai pas pu comprendre "
                            "votre message vocal. "
                            "Veuillez réessayer.",
                        )

                        continue

                # =================================================
                # ENREGISTREMENT DU MESSAGE
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
                            content,
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

                # =================================================
                # ASSISTANT AGRICOLE
                #
                # NOTE (correctif fiabilité) :
                #
                # assistant.process() effectue des appels réseau
                # bloquants (Jina, Supabase, Gemini) qui peuvent
                # prendre plusieurs dizaines de secondes. Comme
                # cette route est "async def", un appel bloquant
                # direct gèlerait tout l'event loop FastAPI,
                # empêchant même la route /health de répondre à
                # temps — ce qui amène Render à croire le service
                # mort et à le redémarrer en pleine génération de
                # réponse. On délègue donc ce traitement à un fil
                # d'exécution séparé via asyncio.to_thread, pour
                # que /health continue de répondre pendant que
                # Gemini travaille. Aucune logique métier ne change.
                # =================================================

                try:

                    print(
                        "🧪 DEBUG WHATSAPP → ASSISTANT :",
                        repr(content),
                    )

                    answer = await asyncio.to_thread(
                        assistant.process,
                        user_id=str(
                            user_id
                        ),
                        message=content,
                    )

                except Exception as e:

                    print(
                        f"Erreur Assistant : {e}"
                    )

                    answer = (
                        "Je rencontre actuellement "
                        "une difficulté technique. "
                        "Veuillez réessayer dans "
                        "quelques instants."
                    )

                # =================================================
                # RÉPONSE WHATSAPP
                # =================================================

                send_whatsapp_message(
                    sender_phone,
                    answer,
                )

    except Exception as e:

        print(
            "❌ Erreur lors du traitement "
            "du message :",
            str(e),
        )

    return {
        "status": "success",
    }