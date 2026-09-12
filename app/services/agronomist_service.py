from __future__ import annotations

import re


class AgronomistService:
    """
    Gère la mise en relation entre un agriculteur et un
    agronome humain — soit sur demande explicite, soit
    proposée automatiquement quand SikaGlé n'a pas assez
    d'information fiable pour répondre seul.

    NOTE (12/09/2026, MVP) : mise en relation simple, pas de
    calendrier ni de créneaux horaires. L'agronome reçoit un
    message WhatsApp avec les coordonnées de l'agriculteur et
    un résumé du problème, puis rappelle directement — en
    dehors de SikaGlé.
    """

    # =========================================================
    # MOTS-CLÉS DE DEMANDE EXPLICITE
    # =========================================================

    EXPLICIT_REQUEST_KEYWORDS = {
        "agronome",
        "agronomes",
        "expert",
        "experte",
        "technicien",
        "specialiste",
        "spécialiste",
        "conseiller humain",
        "vrai conseiller",
        "parler a quelqu'un",
        "parler à quelqu'un",
    }

    def __init__(
        self,
        supabase_client,
    ):

        self.supabase = supabase_client

    # =========================================================
    # DÉTECTION D'UNE DEMANDE EXPLICITE
    # =========================================================

    def is_explicit_request(
        self,
        message_text: str,
    ) -> bool:

        normalized = (
            message_text or ""
        ).lower()

        return any(
            keyword in normalized
            for keyword in self.EXPLICIT_REQUEST_KEYWORDS
        )

    # =========================================================
    # RECHERCHE DU MEILLEUR AGRONOME DISPONIBLE
    # =========================================================

    def find_best_agronomist(
        self,
        region: str | None = None,
        crop: str | None = None,
    ) -> dict | None:
        """
        Retourne l'agronome le plus adapté selon la région et
        la culture, avec une priorité décroissante :

        1. Région ET culture correspondent
        2. Seulement la région correspond
        3. N'importe quel agronome actif (dernier recours)

        Retourne None si aucun agronome actif n'existe.
        """

        response = (
            self.supabase
            .table("agronomists")
            .select("*")
            .eq(
                "is_active",
                True,
            )
            .execute()
        )

        agronomists = response.data or []

        if not agronomists:

            return None

        normalized_region = (
            (region or "")
            .strip()
            .lower()
        )

        normalized_crop = (
            (crop or "")
            .strip()
            .lower()
        )

        # =====================================================
        # PRIORITÉ 1 : région ET culture
        # =====================================================

        if normalized_region and normalized_crop:

            for agronomist in agronomists:

                regions = [
                    r.lower()
                    for r in agronomist.get(
                        "regions",
                        [],
                    )
                ]

                crops = [
                    c.lower()
                    for c in agronomist.get(
                        "specialty_crops",
                        [],
                    )
                ]

                if (
                    normalized_region in regions
                    and normalized_crop in crops
                ):

                    return agronomist

        # =====================================================
        # PRIORITÉ 2 : région seulement
        # =====================================================

        if normalized_region:

            for agronomist in agronomists:

                regions = [
                    r.lower()
                    for r in agronomist.get(
                        "regions",
                        [],
                    )
                ]

                if normalized_region in regions:

                    return agronomist

        # =====================================================
        # PRIORITÉ 3 : n'importe quel agronome actif
        # =====================================================

        return agronomists[0]

    # =========================================================
    # NOTIFIER L'AGRONOME
    # =========================================================

    def notify_agronomist(
        self,
        agronomist: dict,
        farmer_phone: str,
        farmer_name: str | None,
        issue_summary: str,
    ) -> str:
        """
        Construit le message à envoyer à l'agronome via
        WhatsApp. L'envoi effectif reste à la charge de
        l'appelant (webhook.py), qui a déjà accès à
        send_whatsapp_message.
        """

        display_name = (
            farmer_name
            or "un agriculteur"
        )

        return (
            f"🌱 Nouvelle demande SikaGlé\n\n"
            f"Agriculteur : {display_name}\n"
            f"Numéro : {farmer_phone}\n\n"
            f"Résumé du problème :\n"
            f"{issue_summary}\n\n"
            f"Merci de le contacter directement."
        )