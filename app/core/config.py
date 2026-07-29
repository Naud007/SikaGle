import os


class Settings:
    """
    Configuration centrale de l'application.
    """

    def __init__(self):

        self.GEMINI_API_KEY = os.getenv(
            "GEMINI_API_KEY",
            "",
        )

        self.CHROMA_PATH = os.getenv(
            "CHROMA_PATH",
            "data/chroma",
        )

        self.DATA_PATH = os.getenv(
            "DATA_PATH",
            "data",
        )

        self.ENVIRONMENT = os.getenv(
            "ENVIRONMENT",
            "development",
        )


settings = Settings()
