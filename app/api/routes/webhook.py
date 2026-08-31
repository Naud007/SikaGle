import asyncio
import os
import re
import tempfile
from datetime import date, datetime
from pathlib import Path

from fastapi import APIRouter, Request, Response

from app.integrations.media.media_service import (
    MediaService,
)
from app.integrations.whatsapp.sender import (
    send_typing_indicator,
    send_whatsapp_audio_message,
    send_whatsapp_message,
)
from app.multimodal.speech.abena_text_to_speech import (
    AbenaTextToSpeech,
)
from app.multimodal.speech.speech_service import (
    SpeechService,
)
from app.multimodal.speech.text_to_speech import (
    TextToSpeech,
)
from app.multimodal.translation.translation_service import (
    TranslationService,
)
from app.multimodal.vision.image_analysis_service import (
    ImageAnalysisService,
)
from app.services.agricultural_assistant_service import (
    AgriculturalAssistantService,
)
from app.services.profile_service import (
    ProfileService,
)
from app.services.weather_service import (
    WeatherService,
)


# =========================================================
# CORRECTIF (31/08/2026) :
#
# Supabase/PostgreSQL renvoie parfois des timestamps avec un
# nombre de chiffres après la virgule différent de 3 ou 6
# (ex: ".52269", 5 chiffres, car les zéros de fin sont
# coupés). datetime.fromisoformat() de Python 3.10 est
# strict et rejette ce format avec "Invalid isoformat
# string", ce qui faisait planter le traitement de N'IMPORTE
# QUEL message WhatsApp de façon imprévisible. Cette fonction
# normalise la précision des microsecondes à exactement 6
# chiffres avant de parser, quel que soit le nombre de
# chiffres reçu.
# =========================================================

def _normalize_and_parse_timestamp(
    timestamp_str: str,
) -> datetime:

    normalized = timestamp_str.replace(
        "Z",
        "+00:00",
    )

    def _pad_microseconds(
        match: re.Match,
    ) -> str:

        digits = match.group(1)

        padded = (
            digits[:6]
            .ljust(6, "0")
        )

        return f".{padded}"

    normalized = re.sub(
        r"\.(\d+)",
        _pad_microseconds,
        normalized,
    )

    return datetime.fromisoformat(
        normalized
    )


# =========================================================
# CORRECTIF (31/08/2026) :
#
# Traduction + synthèse vocale + envoi WhatsApp, regroupés
# dans une fonction SYNCHRONE à part, pour pouvoir être
# exécutée via asyncio.to_thread() depuis le webhook async.
# Ce bloc était auparavant exécuté directement dans
# receive_webhook (async def), sans protection — exactement
# le même problème qu'on avait déjà corrigé pour
# assistant.process() au tout début du projet (event loop
# bloqué, /health ne répond plus, Render tue et redémarre
# l'instance en pleine génération). Observé en production
# réelle : un message vocal en Fon a fait planter le serveur
# pendant l'étape de synthèse audio, la réponse n'est jamais
# arrivée à l'agriculteur.
# =========================================================

def _synthesize_and_send_audio(
    sender_phone: str,
    answer: str,
    detected_language: str,
) -> bool:

    LANGUAGES_WITHOUT_LOCAL_VOICE = {
        "fon",
        "dendi",
        "bariba",
        "adja",
        "goun",
        "fulfulde",
    }

    sent_as_audio = False

    try:

        if (
            detected_language
            in AbenaTextToSpeech.VOICE_BY_LANGUAGE
        ):

            translated_answer = (
                translation_service
                .translate_from_french(
                    answer,
                    detected_language,
                )
            )

            print(
                "🌍 Réponse traduite "
                f"({detected_language}) :",
                translated_answer,
            )

            speech = (
                abena_text_to_speech.synthesize(
                    text=translated_answer,
                    language=detected_language,
                )
            )

        elif (
            detected_language
            in LANGUAGES_WITHOUT_LOCAL_VOICE
        ):

            answer_with_notice = (
                "J'ai bien compris votre "
                "question. Je n'ai pas encore "
                "de voix dans votre langue, "
                "je vous réponds donc en "
                "français pour l'instant.\n\n"
                + answer
            )

            speech = (
                text_to_speech.synthesize(
                    text=answer_with_notice,
                    language="fr",
                )
            )

        else:

            speech = (
                text_to_speech.synthesize(
                    text=answer,
                    language="fr",
                )
            )

        sent_as_audio = (
            send_whatsapp_audio_message(
                sender_phone,
                speech.audio_path,
            )
        )

        Path(
            speech.audio_path
        ).unlink(
            missing_ok=True
        )

    except Exception as e:

        print(
            "❌ Erreur génération/envoi "
            f"audio SikaGlé : {e}"
        )

    return sent_as_audio


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

text_to_speech = TextToSpeech()

abena_text_to_speech = AbenaTextToSpeech()

translation_service = TranslationService()

image_analysis_service = ImageAnalysisService()

weather_service = WeatherService()


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

                # =================================================
                # INDICATEUR "EN TRAIN D'ÉCRIRE"
                # =================================================

                if msg_id:

                    send_typing_indicator(
                        msg_id
                    )

                msg_type = msg.get(
                    "type",
                    "text",
                )

                is_voice_message = (
                    msg_type
                    in [
                        "audio",
                        "voice",
                    ]
                )

                detected_language = "fr"

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
                # IMAGE (photo de plante)
                # =================================================

                elif msg_type == "image":

                    media_id = (
                        msg
                        .get(
                            "image",
                            {},
                        )
                        .get(
                            "id",
                            "",
                        )
                    )

                # =================================================
                # DOCUMENT (non analysé pour l'instant)
                # =================================================

                elif msg_type == "document":

                    content = (
                        "[DOCUMENT] "
                        "ID: "
                        + str(
                            msg
                            .get(
                                "document",
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
                            _normalize_and_parse_timestamp(
                                created_at_str
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
                # PROFIL AGRICULTEUR (collecte progressive)
                # =================================================

                profile_service = ProfileService(
                    supabase
                )

                profile, profile_just_created = (
                    profile_service
                    .ensure_profile_exists(
                        user_id
                    )
                )

                onboarding_in_progress = (
                    msg_type == "text"
                    and not profile_service
                    .is_onboarding_complete(
                        profile
                    )
                )

                if onboarding_in_progress:

                    if profile_just_created:

                        reply_text = (
                            profile_service
                            .get_current_question(
                                profile
                            )
                        )

                    else:

                        reply_text = (
                            profile_service
                            .save_onboarding_answer(
                                profile,
                                content,
                            )
                        )

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

                    (
                        supabase
                        .table("users")
                        .update({
                            "credits":
                                user_credits
                                - 1,
                            "last_active_date":
                                today_str,
                        })
                        .eq(
                            "id",
                            user_id,
                        )
                        .execute()
                    )

                    send_whatsapp_message(
                        sender_phone,
                        reply_text,
                    )

                    continue

                # =================================================
                # MÉTÉO (contexte optionnel)
                # =================================================

                weather_context_text = None

                profile_latitude = profile.get(
                    "latitude"
                )

                profile_longitude = profile.get(
                    "longitude"
                )

                print(
                    "🌦️ Coordonnées du profil : "
                    f"lat={profile_latitude}, "
                    f"lon={profile_longitude}"
                )

                if (
                    profile_latitude is not None
                    and profile_longitude is not None
                ):

                    try:

                        weather_data = (
                            weather_service
                            .get_current_weather(
                                profile_latitude,
                                profile_longitude,
                            )
                        )

                        if weather_data:

                            weather_context_text = (
                                weather_service
                                .to_context_text(
                                    weather_data
                                )
                            )

                            print(
                                "🌦️ Contexte météo "
                                "récupéré :",
                                weather_context_text,
                            )

                        else:

                            print(
                                "🌦️ Météo indisponible "
                                "(get_current_weather a "
                                "retourné None)."
                            )

                    except Exception as e:

                        print(
                            "⚠️ Récupération météo "
                            f"échouée : {e}"
                        )

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
                                    media_file.file_path,
                                    mime_type=(
                                        media_file.mime_type
                                        or "audio/ogg"
                                    ),
                                )
                            )

                            content = (
                                transcription.text
                            )

                            detected_language = (
                                transcription.language
                                or "fr"
                            )

                            print(
                                "🎙️ Audio transcrit "
                                f"({detected_language}) :",
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
                # TRAITEMENT IMAGE (photo de plante)
                # =================================================

                if (
                    msg_type == "image"
                    and media_id
                ):

                    try:

                        image_meta = (
                            msg.get(
                                "image",
                                {},
                            )
                        )

                        image_mime_type = (
                            image_meta.get(
                                "mime_type",
                                "image/jpeg",
                            )
                        )

                        image_caption = (
                            image_meta.get(
                                "caption"
                            )
                        )

                        extension = (
                            ".png"
                            if "png"
                            in image_mime_type
                            else ".jpg"
                        )

                        with tempfile.TemporaryDirectory() as temp_dir:

                            image_path = os.path.join(
                                temp_dir,
                                f"{media_id}{extension}",
                            )

                            media_file = (
                                media_service.download(
                                    media_id=media_id,
                                    destination=image_path,
                                    media_type="image",
                                    mime_type=image_mime_type,
                                )
                            )

                            if not media_file.downloaded:

                                raise RuntimeError(
                                    "Le fichier image WhatsApp "
                                    "n'a pas été téléchargé."
                                )

                            observation = (
                                image_analysis_service.analyze(
                                    media_file.file_path,
                                    mime_type=(
                                        media_file.mime_type
                                        or image_mime_type
                                    ),
                                    caption=image_caption,
                                )
                            )

                            print(
                                "🖼️ Observation image :",
                                observation,
                            )

                            if not observation.photo_usable:

                                clarification_text = (
                                    observation.clarification_needed
                                    or (
                                        "Je n'arrive pas à bien voir "
                                        "cette photo. Peux-tu en "
                                        "renvoyer une plus nette et "
                                        "bien éclairée ?"
                                    )
                                )

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
                                            clarification_text,
                                    })
                                    .execute()
                                )

                                send_whatsapp_message(
                                    sender_phone,
                                    clarification_text,
                                )

                                continue

                            content = (
                                observation.to_query_text()
                            )

                    except Exception as e:

                        print(
                            f"❌ Erreur traitement image : {e}"
                        )

                        send_whatsapp_message(
                            sender_phone,
                            "Je n'ai pas pu analyser cette "
                            "photo. Peux-tu réessayer avec "
                            "une autre image ?",
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
                        input_type=(
                            "audio"
                            if is_voice_message
                            else "text"
                        ),
                        weather_context=(
                            weather_context_text
                        ),
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
                #
                # NOTE (correctif 31/08/2026) : la traduction +
                # synthèse vocale + envoi audio est maintenant
                # exécutée via asyncio.to_thread() (fonction
                # _synthesize_and_send_audio définie plus haut),
                # pour ne plus bloquer l'event loop pendant cette
                # étape potentiellement longue.
                # =================================================

                sent_as_audio = False

                if is_voice_message:

                    sent_as_audio = (
                        await asyncio.to_thread(
                            _synthesize_and_send_audio,
                            sender_phone,
                            answer,
                            detected_language,
                        )
                    )

                if not sent_as_audio:

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