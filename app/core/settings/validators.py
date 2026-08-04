"""
Validation de la configuration de SikaGlé.
"""



class ConfigurationError(Exception):
    """Erreur de configuration."""
    pass


class ConfigurationValidator:

    @staticmethod
    def validate(settings):

        required_settings = {
            "GEMINI_API_KEY": settings.GEMINI_API_KEY,
        }

        missing = []

        for name, value in required_settings.items():

            if value is None:
                missing.append(name)
                continue

            if isinstance(value, str) and value.strip() == "":
                missing.append(name)

        if missing:

            message = (
                "\nConfiguration invalide.\n\n"
                "Variables manquantes :\n\n"
            )

            for item in missing:
                message += f" - {item}\n"

            raise ConfigurationError(message)

        return True
