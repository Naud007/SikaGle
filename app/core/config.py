import os


class Settings:
    """
    Configuration centrale de l'application.
    """

    def __init__(self):

        # ==========================
        # Environnement
        # ==========================

        self.ENVIRONMENT = os.getenv(
            "ENVIRONMENT",
            "development",
        )

        # ==========================
        # Gemini
        # ==========================

        self.GEMINI_API_KEY = os.getenv(
            "GEMINI_API_KEY",
            "",
        )

        self.GEMINI_EMBEDDING_MODEL = os.getenv(
            "GEMINI_EMBEDDING_MODEL",
            "gemini-embedding-001",
        )

        self.GEMINI_GENERATION_MODEL = os.getenv(
            "GEMINI_GENERATION_MODEL",
            "gemini-2.5-flash",
        )

        self.EMBEDDING_DIMENSION = int(
            os.getenv(
                "EMBEDDING_DIMENSION",
                "1536",
            )
        )

        # ==========================
        # Chroma
        # ==========================

        self.CHROMA_PATH = os.getenv(
            "CHROMA_PATH",
            "data/chroma",
        )

        # ==========================
        # Données
        # ==========================

        self.DATA_PATH = os.getenv(
            "DATA_PATH",
            "data",
        )


settings = Settings()
