"""
SikaGlé

Configuration de sécurité de la plateforme.
"""


class SecuritySettings:
    """
    Paramètres de sécurité.
    """

    # Nombre maximal de requêtes
    RATE_LIMIT = 100

    # Fenêtre du Rate Limiter (secondes)
    RATE_LIMIT_WINDOW = 60

    # Taille maximale d'une requête HTTP (1 Mo)
    MAX_REQUEST_SIZE = 1024 * 1024

    # Autoriser le mode debug ?
    ALLOW_DEBUG = False

    # Autoriser les origines CORS
    ALLOWED_ORIGINS = [
        "*",
    ]
