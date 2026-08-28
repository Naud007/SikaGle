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
    ) -> dict:
        """
        Retourne le profil de l'utilisateur, en le créant
        (étape de collecte "language") s'il n'existe pas
        encore.
        """

        profile = self.get_profile(
            user_id
        )

        if profile:

            return profile

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

        return response.data[0]

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