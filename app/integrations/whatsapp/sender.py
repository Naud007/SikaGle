"""
SikaGlé

Service d'envoi des messages WhatsApp.
"""

import os

import requests

from app.core.logging import logger


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
# INDICATEUR "EN TRAIN D'ÉCRIRE"
#
# NOTE :
#
# L'API WhatsApp Cloud ne propose qu'un seul type
# d'indicateur générique ("text"), quel que soit le type
# du message reçu (texte ou audio) — il n'existe pas de
# variante "enregistrement audio en cours" côté bot.
#
# Cet indicateur marque aussi automatiquement le message
# reçu comme lu, et disparaît de lui-même après 25 secondes
# ou dès qu'on envoie la vraie réponse (send_whatsapp_message).
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