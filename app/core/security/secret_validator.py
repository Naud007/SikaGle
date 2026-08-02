"""
SikaGlé

Validation des secrets nécessaires au démarrage.
"""

from app.core.config import settings


class SecretValidationError(Exception):
    """
    Erreur levée lorsqu'un secret obligatoire est absent.
    """
    pass


class SecretValidator:
    """
    Vérifie que tous les secrets indispensables sont présents.
    """

    @staticmethod
    def validate() -> None:

        required = {
            "GEMINI_API_KEY": settings.GEMINI_API_KEY,
        }

        missing = []

        for name, value in required.items():

            if value is None:
                missing.append(name)
                continue

            if isinstance(value, str) and value.strip() == "":
                missing.append(name)

        if missing:

            message = (
                "\nSecrets de configuration manquants :\n\n"
            )

            for item in missing:
                message += f" - {item}\n"

            raise SecretValidationError(message)
