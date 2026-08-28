import asyncio
import os
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

                # =================================================
                # NOTE (correctif) :
                #
                # is_voice_message permet de savoir, plus loin, si
                # la question venait d'un message vocal, pour :
                # - transmettre input_type="audio" à
                #   assistant.process() (formatage adapté à la voix,
                #   sans markdown) ;
                # - répondre en audio plutôt qu'en texte.
                #
                # detected_language retient la langue réellement
                # détectée par SpeechToText (fr par défaut, ou yo/
                # fon/dendi) pour router la réponse vers la bonne
                # voix TTS plus loin (correctif Yoruba du
                # 28/08/2026).
                # =================================================

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
                # PROFIL AGRICULTEUR (collecte progressive)
                #
                # NOTE : la collecte ne se déclenche que pour les
                # messages TEXTE. Une photo ou un audio est
                # toujours traité normalement, sans être bloqué
                # par le questionnaire (décision produit du
                # 28/08/2026 : ne jamais retarder une demande
                # agricole urgente).
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
                # NOTE (correctif Yoruba du 28/08/2026) :
                #
                # Si la question venait d'un message vocal en une
                # langue locale supportée par Abena AI (Yoruba
                # pour l'instant), on traduit la réponse française
                # vers cette langue puis on synthétise l'audio via
                # Abena AI, au lieu du TTS français habituel. Sinon
                # (français), comportement inchangé (Gemini TTS).
                # =================================================

                sent_as_audio = False

                if is_voice_message:

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