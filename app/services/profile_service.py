# =============================================================
# GESTION DU PROFIL AGRICULTEUR (version minimale)
#
# Collecte progressive au premier contact : langue préférée,
# culture(s), localisation — une question à la fois, pour
# rester naturel sur WhatsApp (texte comme audio).
#
# NOTE (portée actuelle) : la collecte ne se déclenche que
# pour les messages texte. Une photo ou un audio envoyé en
# premier message est traité normalement par l'assistant
# agricole, sans être bloqué par le questionnaire — conforme
# à la décision produit du 28/08/2026 de ne jamais retarder
# une demande agricole urgente derrière un profil incomplet.
# =============================================================

from datetime import datetime, timezone

from app.services.weather_service import (
    WeatherService,
)


ONBOARDING_QUESTIONS = {
    "language": (
        "Bonjour ! 👋 Je suis SikaGlé, votre assistant "
        "agricole.\n\nPour mieux vous aider, dans quelle "
        "langue préférez-vous recevoir mes réponses ?"
    ),
    "crops": (
        "D'accord 👍 Quelle(s) culture(s) cultivez-vous ?"
    ),
    "location": (
        "Merci 🙏 Dans quelle commune se trouve votre "
        "exploitation ?"
    ),
}

ONBOARDING_ORDER = [
    "language",
    "crops",
    "location",
]

ONBOARDING_COMPLETE_MESSAGE = (
    "Merci, votre profil est enregistré ✅\n\n"
    "Comment puis-je vous aider aujourd'hui ?"
)


class ProfileService:
    """
    Gère la table `profiles` (langue, cultures, localisation)
    et la collecte progressive au premier contact.
    """

    def __init__(
        self,
        supabase,
    ):

        self.supabase = supabase

    # =========================================================
    # LECTURE
    # =========================================================

    def get_profile(
        self,
        user_id,
    ) -> dict | None:

        response = (
            self.supabase
            .table("profiles")
            .select("*")
            .eq(
                "user_id",
                user_id,
            )
            .limit(1)
            .execute()
        )

        if response.data:

            return response.data[0]

        return None

    def ensure_profile_exists(
        self,
        user_id,
    ) -> tuple[dict, bool]:
        """
        Retourne (profil, was_just_created).

        was_just_created est True uniquement lors du tout
        premier contact de cet utilisateur : dans ce cas, le
        message entrant ne doit PAS être traité comme une
        réponse à la question de langue (il n'a jamais reçu
        cette question), mais déclencher son envoi.
        """

        profile = self.get_profile(
            user_id
        )

        if profile:

            return profile, False

        response = (
            self.supabase
            .table("profiles")
            .insert({
                "user_id": user_id,
                "onboarding_step":
                    ONBOARDING_ORDER[0],
            })
            .execute()
        )

        return response.data[0], True

    def is_onboarding_complete(
        self,
        profile: dict,
    ) -> bool:

        return (
            profile.get(
                "onboarding_step"
            )
            == "done"
        )

    def get_current_question(
        self,
        profile: dict,
    ) -> str:

        step = profile.get(
            "onboarding_step"
        )

        return ONBOARDING_QUESTIONS.get(
            step,
            ONBOARDING_QUESTIONS[
                ONBOARDING_ORDER[0]
            ],
        )

    # =========================================================
    # ÉCRITURE (réponse à l'étape en cours)
    # =========================================================

    def save_onboarding_answer(
        self,
        profile: dict,
        answer_text: str,
    ) -> str:
        """
        Enregistre la réponse de l'agriculteur pour l'étape de
        collecte en cours, avance à l'étape suivante, et
        retourne le message à renvoyer (question suivante, ou
        message de fin de collecte).

        NOTE (météo) : quand l'étape "location" vient d'être
        renseignée, on géocode immédiatement cette localisation
        et on met en cache les coordonnées (latitude/longitude)
        dans le profil, pour ne pas avoir à regéocoder à chaque
        message futur.
        """

        current_step = profile.get(
            "onboarding_step"
        )

        current_index = (
            ONBOARDING_ORDER.index(
                current_step
            )
            if current_step
            in ONBOARDING_ORDER
            else 0
        )

        next_index = (
            current_index + 1
        )

        is_last_step = (
            next_index
            >= len(ONBOARDING_ORDER)
        )

        next_step = (
            "done"
            if is_last_step
            else ONBOARDING_ORDER[
                next_index
            ]
        )

        update_payload = {
            current_step:
                answer_text.strip(),
            "onboarding_step":
                next_step,
        }

        if current_step == "location":

            self._add_geocoding(
                update_payload,
                answer_text.strip(),
            )

        (
            self.supabase
            .table("profiles")
            .update(update_payload)
            .eq(
                "id",
                profile["id"],
            )
            .execute()
        )

        if is_last_step:

            return (
                ONBOARDING_COMPLETE_MESSAGE
            )

        return ONBOARDING_QUESTIONS[
            next_step
        ]

    def _add_geocoding(
        self,
        update_payload: dict,
        location_text: str,
    ) -> None:
        """
        Tente de géocoder la localisation donnée et ajoute
        latitude/longitude/location_resolved_at au payload de
        mise à jour. En cas d'échec (lieu introuvable, API
        indisponible), n'ajoute rien : le profil reste
        utilisable sans météo plutôt que de bloquer la
        collecte.
        """

        try:

            weather_service = (
                WeatherService()
            )

            # =========================================================
            # CORRECTIF (30/08/2026) : ne plus concaténer le pays
            # dans le texte de recherche — ça cassait le géocodage
            # (ex: "Abomey calavi, Bénin" → variantes malformées).
            # WeatherService.geocode() priorise déjà les résultats
            # situés au Bénin en interne, sans avoir besoin qu'on
            # le lui précise dans le texte.
            # =========================================================

            coordinates = (
                weather_service.geocode(
                    location_text
                )
            )

            if coordinates:

                latitude, longitude = (
                    coordinates
                )

                update_payload[
                    "latitude"
                ] = latitude

                update_payload[
                    "longitude"
                ] = longitude

                update_payload[
                    "location_resolved_at"
                ] = (
                    datetime
                    .now(timezone.utc)
                    .isoformat()
                )

        except Exception as e:

            print(
                "⚠️ Géocodage échoué pour "
                f'"{location_text}" : {e}'
            )