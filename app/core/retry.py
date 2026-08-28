import time


# =============================================================
# NOUVELLE TENTATIVE AUTOMATIQUE (retry)
#
# Utilitaire générique pour réessayer un appel à Gemini (ou
# tout autre appel réseau) quand l'erreur est temporaire et
# indépendante de notre code (ex: 503 UNAVAILABLE "high
# demand", erreurs réseau passagères). Les autres erreurs
# (bug dans nos données, requête invalide, etc.) ne sont
# JAMAIS réessayées : on les laisse remonter immédiatement.
# =============================================================


RETRYABLE_MARKERS = [
    "503",
    "UNAVAILABLE",
    "high demand",
    "overloaded",
    "internal error",
    "500",
    "deadline exceeded",
    "timeout",
]


def _is_retryable(
    error: Exception,
) -> bool:

    message = str(error).lower()

    return any(
        marker.lower() in message
        for marker in RETRYABLE_MARKERS
    )


def call_with_retry(
    func,
    *args,
    max_attempts: int = 3,
    base_delay_seconds: float = 2.0,
    **kwargs,
):
    """
    Appelle func(*args, **kwargs), et réessaie automatiquement
    (avec un délai croissant) si l'erreur ressemble à une
    surcharge temporaire côté serveur (Gemini notamment).

    Après max_attempts tentatives infructueuses, l'exception
    d'origine est relancée telle quelle.
    """

    last_error: Exception | None = None

    for attempt in range(
        1,
        max_attempts + 1,
    ):

        try:

            return func(
                *args,
                **kwargs,
            )

        except Exception as error:

            last_error = error

            is_last_attempt = (
                attempt == max_attempts
            )

            if (
                not _is_retryable(error)
                or is_last_attempt
            ):

                raise

            delay = (
                base_delay_seconds
                * attempt
            )

            print(
                "⏳ Tentative "
                f"{attempt}/{max_attempts} "
                "échouée (erreur temporaire), "
                f"nouvel essai dans {delay:.0f}s : "
                f"{error}"
            )

            time.sleep(delay)

    # Ne devrait jamais être atteint, mais garde-fou :
    if last_error:
        raise last_error