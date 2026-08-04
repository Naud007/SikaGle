"""
SikaGlé
Configuration centrale de l'application.

Toutes les configurations du projet passent par cette classe.
"""

from app.core.settings import EnvironmentLoader


class Settings:
    """
    Configuration globale de SikaGlé.
    """

    def __init__(self):

        # =====================================================
        # Application
        # =====================================================

        self.APP_NAME = EnvironmentLoader.get(
            "APP_NAME",
            "SikaGlé",
        )

        self.APP_VERSION = EnvironmentLoader.get(
            "APP_VERSION",
            "1.0.0",
        )

        self.ENVIRONMENT = EnvironmentLoader.get(
            "ENVIRONMENT",
            "development",
        )

        self.DEBUG = EnvironmentLoader.get_bool(
            "DEBUG",
            False,
        )

        # =====================================================
        # Gemini
        # =====================================================

        self.GEMINI_API_KEY = EnvironmentLoader.get_required(
            "GEMINI_API_KEY",
        )

        self.GEMINI_GENERATION_MODEL = EnvironmentLoader.get(
            "GEMINI_GENERATION_MODEL",
            "gemini-2.5-flash",
        )

        self.GEMINI_EMBEDDING_MODEL = EnvironmentLoader.get(
            "GEMINI_EMBEDDING_MODEL",
            "gemini-embedding-001",
        )

        self.EMBEDDING_DIMENSION = EnvironmentLoader.get_int(
            "EMBEDDING_DIMENSION",
            1536,
        )

        # =====================================================
        # ChromaDB
        # =====================================================

        self.CHROMA_PATH = EnvironmentLoader.get(
            "CHROMA_PATH",
            "data/chroma",
        )

        # =====================================================
        # Données
        # =====================================================

        self.DATA_PATH = EnvironmentLoader.get(
            "DATA_PATH",
            "data",
        )

        # =====================================================
        # Supabase
        # =====================================================

        self.SUPABASE_URL = EnvironmentLoader.get(
            "SUPABASE_URL",
            "",
        )

        self.SUPABASE_KEY = EnvironmentLoader.get(
            "SUPABASE_KEY",
            "",
        )

        # =====================================================
        # WhatsApp Cloud API
        # =====================================================

        self.WHATSAPP_TOKEN = EnvironmentLoader.get(
            "WHATSAPP_TOKEN",
            "",
        )

        self.WHATSAPP_PHONE_NUMBER_ID = EnvironmentLoader.get(
            "WHATSAPP_PHONE_NUMBER_ID",
            "",
        )

        self.WHATSAPP_VERIFY_TOKEN = EnvironmentLoader.get(
            "WHATSAPP_VERIFY_TOKEN",
            "",
        )

        # =====================================================
        # Production
        # =====================================================

        self.LOG_LEVEL = EnvironmentLoader.get(
            "LOG_LEVEL",
            "INFO",
        )

        self.API_HOST = EnvironmentLoader.get(
            "API_HOST",
            "0.0.0.0",
        )

        self.API_PORT = EnvironmentLoader.get_int(
            "API_PORT",
            8000,
        )


settings = Settings()
