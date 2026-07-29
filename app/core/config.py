import os


class Settings:
    """
    Configuration centrale de l'application.
    Toutes les variables d'environnement
    sont accessibles depuis cet objet.
    """

    def __init__(self):

        # Gemini
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

        # ChromaDB
        self.CHROMA_PATH = os.getenv(
            "CHROMA_PATH",
            "data/chroma",
        )

        # Données
        self.DATA_PATH = os.getenv(
            "DATA_PATH",
            "data",
        )

        # Environnement
        self.ENVIRONMENT = os.getenv(
            "ENVIRONMENT",
            "development",
        )


settings = Settings()
