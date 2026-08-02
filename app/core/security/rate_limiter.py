"""
SikaGlé

Limiteur de débit simple en mémoire.
"""

from collections import defaultdict
from datetime import datetime, timedelta

from app.core.security.security_settings import (
    SecuritySettings,
)


class RateLimiter:
    """
    Limiteur de débit en mémoire.

    Chaque identifiant (IP, utilisateur, téléphone...)
    possède sa propre fenêtre de limitation.
    """

    def __init__(self):

        self.requests = defaultdict(list)

    def allow(
        self,
        identifier: str,
    ) -> bool:
        """
        Retourne True si la requête est autorisée.
        """

        now = datetime.utcnow()

        window = timedelta(
            seconds=SecuritySettings.RATE_LIMIT_WINDOW
        )

        history = self.requests[identifier]

        history[:] = [
            timestamp
            for timestamp in history
            if now - timestamp < window
        ]

        if (
            len(history)
            >= SecuritySettings.RATE_LIMIT
        ):
            return False

        history.append(now)

        return True
