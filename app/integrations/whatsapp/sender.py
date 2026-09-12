"""
SikaGlé

Service d'envoi des messages WhatsApp.
"""

import os
from pathlib import Path

import requests

from app.core.logging import logger
from app.integrations.clients.whatsapp_client import (
    WhatsAppClient,
)


WHATSAPP_TOKEN = os.getenv(
    "WHATSAPP_TOKEN",
    "",
)

WHATSAPP_PHONE_ID = os.getenv(
    "WHATSAPP_PHONE_NUMBER_ID",
    "",
)


def send_whatsapp_message(
    to_phone: str,
    text_body: str,
) -> bool:
    """
    Envoie un message texte via WhatsApp Cloud API.
    """

    if (
        not WHATSAPP_TOKEN
        or not WHATSAPP_PHONE_ID
    ):
        logger.warning(
            "Variables WHATSAPP_TOKEN ou WHATSAPP_PHONE_NUMBER_ID manquantes."
        )
        return False

    url = (
        f"https://graph.facebook.com/v18.0/"
        f"{WHATSAPP_PHONE_ID}/messages"
    )

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "text",
        "text": {
            "body": text_body,
        },
    }

    try:

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30,
        )

        if response.status_code == 200:

            logger.info(
                "Message WhatsApp envoyé à %s",
                to_phone,
            )

            return True

        logger.error(
            "Échec d'envoi WhatsApp (%s): %s",
            response.status_code,
            response.text,
        )

        return False

    except Exception:

        logger.exception(
            "Erreur lors de l'envoi du message WhatsApp."
        )

        return False


# =============================================================
# ENVOI D'UN MESSAGE VIA MODÈLE (TEMPLATE)
#
# NOTE (12/09/2026) :
#
# Contrairement à send_whatsapp_message (texte libre), un
# modèle peut être envoyé à tout moment, même si le
# destinataire n'a jamais écrit à ce numéro WhatsApp Business
# — nécessaire pour notifier un agronome qui n'a pas encore
# interagi avec SikaGlé (règle des 24h de WhatsApp, erreur
# 131047 rencontrée en test réel le 12/09/2026).
# =============================================================

def send_whatsapp_template_message(
    to_phone: str,
    template_name: str,
    language_code: str,
    body_parameters: list[str],
) -> bool:
    """
    Envoie un message basé sur un modèle pré-approuvé par
    Meta. body_parameters doit contenir les valeurs dans le
    même ordre que les variables {{1}}, {{2}}, {{3}}... du
    modèle.
    """

    if (
        not WHATSAPP_TOKEN
        or not WHATSAPP_PHONE_ID
    ):
        logger.warning(
            "Variables WHATSAPP_TOKEN ou WHATSAPP_PHONE_NUMBER_ID manquantes."
        )
        return False

    url = (
        f"https://graph.facebook.com/v18.0/"
        f"{WHATSAPP_PHONE_ID}/messages"
    )

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": language_code,
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": value,
                        }
                        for value in body_parameters
                    ],
                }
            ],
        },
    }

    try:

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30,
        )

        if response.status_code == 200:

            logger.info(
                "Message modèle WhatsApp envoyé à %s",
                to_phone,
            )

            return True

        logger.error(
            "Échec d'envoi modèle WhatsApp (%s): %s",
            response.status_code,
            response.text,
        )

        return False

    except Exception:

        logger.exception(
            "Erreur lors de l'envoi du modèle WhatsApp."
        )

        return False


# =============================================================
# ENVOI D'UN MESSAGE AUDIO (réponse vocale de SikaGlé)
# =============================================================

def send_whatsapp_audio_message(
    to_phone: str,
    audio_path: Path,
    mime_type: str = "audio/mpeg",
) -> bool:
    """
    Envoie un message audio via WhatsApp Cloud API.
    """

    if (
        not WHATSAPP_TOKEN
        or not WHATSAPP_PHONE_ID
    ):
        logger.warning(
            "Variables WHATSAPP_TOKEN ou WHATSAPP_PHONE_NUMBER_ID manquantes."
        )
        return False

    try:

        client = WhatsAppClient()

        media_id = client.upload_media(
            file_path=audio_path,
            mime_type=mime_type,
        )

    except Exception:

        logger.exception(
            "Erreur lors de l'upload de l'audio "
            "vers WhatsApp."
        )

        return False

    url = (
        f"https://graph.facebook.com/v18.0/"
        f"{WHATSAPP_PHONE_ID}/messages"
    )

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "audio",
        "audio": {
            "id": media_id,
        },
    }

    try:

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30,
        )

        if response.status_code == 200:

            logger.info(
                "Message audio WhatsApp envoyé à %s",
                to_phone,
            )

            return True

        logger.error(
            "Échec d'envoi audio WhatsApp (%s): %s",
            response.status_code,
            response.text,
        )

        return False

    except Exception:

        logger.exception(
            "Erreur lors de l'envoi du message "
            "audio WhatsApp."
        )

        return False


# =============================================================
# INDICATEUR "EN TRAIN D'ÉCRIRE"
# =============================================================

def send_typing_indicator(
    message_id: str,
) -> bool:
    """
    Affiche l'indicateur "en train d'écrire..." à l'agriculteur,
    en référence au message qu'il vient d'envoyer.
    """

    if (
        not WHATSAPP_TOKEN
        or not WHATSAPP_PHONE_ID
    ):
        logger.warning(
            "Variables WHATSAPP_TOKEN ou WHATSAPP_PHONE_NUMBER_ID manquantes."
        )
        return False

    if not message_id:
        return False

    url = (
        f"https://graph.facebook.com/v18.0/"
        f"{WHATSAPP_PHONE_ID}/messages"
    )

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
        "typing_indicator": {
            "type": "text",
        },
    }

    try:

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=10,
        )

        if response.status_code == 200:

            logger.info(
                "Indicateur 'en train d'écrire' envoyé "
                "pour le message %s",
                message_id,
            )

            return True

        logger.error(
            "Échec envoi indicateur de frappe (%s): %s",
            response.status_code,
            response.text,
        )

        return False

    except Exception:

        logger.exception(
            "Erreur lors de l'envoi de l'indicateur "
            "de frappe WhatsApp."
        )

        return False