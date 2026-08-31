from app.core.settings.validators import ConfigurationValidator
from app.core.config import settings
ConfigurationValidator.validate(settings)
from app.services.agricultural_assistant_service import (
    AgriculturalAssistantService,
)
from app.api.routes.fao import router as fao_router
from app.api.routes.oai_ingestion import router as oai_ingestion_router
from app.api.routes.ai import router as ai_router
from app.api.routes.health import router as health_router
from app.api.routes.system import router as system_router
from app.api.routes.webhook import router as webhook_router
from datetime import date, datetime
import os

from app.api.middlewares import (
    SecurityHeadersMiddleware,
)


from app.core.logging import logger

from app.core.monitoring import metrics

from app.api.routes.knowledge import router as knowledge_router

from fastapi import FastAPI, Request, Response
from supabase import create_client, Client

from app.integrations.whatsapp.sender import (
    send_whatsapp_message,
)

from app.knowledge_engine.ingestion.fao_ingestion_worker import (
    FAOIngestionWorker,
)


# =========================================================
# INITIALISATION FASTAPI
# =========================================================

app = FastAPI(
    title="SikaGlé API",
    version="1.0.0"
)

app.add_middleware(
    SecurityHeadersMiddleware,
)

logger.info("=" * 60)
logger.info("🌱 Démarrage de SikaGlé")
logger.info("Version : 1.0.0")
logger.info("=" * 60)

# =========================================================
# CONFIGURATION DES QUOTAS
# =========================================================

TRIAL_PERIOD_DAYS = 31
TRIAL_DAILY_LIMIT = 15
REGULAR_DAILY_LIMIT = 5


# =========================================================
# VARIABLES D'ENVIRONNEMENT
# =========================================================

VERIFY_TOKEN = os.getenv(
    "WHATSAPP_VERIFY_TOKEN",
    "sikagle_secret_token_2026"
)

WHATSAPP_TOKEN = os.getenv(
    "WHATSAPP_TOKEN",
    ""
)

WHATSAPP_PHONE_ID = os.getenv(
    "WHATSAPP_PHONE_ID",
    ""
)

SUPABASE_URL = os.getenv(
    "SUPABASE_URL",
    ""
)

SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    ""
)


# =========================================================
# INITIALISATION SUPABASE
# =========================================================

supabase: Client | None = None


if SUPABASE_URL and SUPABASE_KEY:

    try:

        supabase = create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

        logger.info("✅ Connexion Supabase initialisée.")

    except Exception as e:

        logger.exception("Erreur lors de l'initialisation de Supabase")



app.include_router(
    knowledge_router,
)
app.include_router(
    ai_router,
)
app.include_router(
    health_router,
)
app.include_router(
    fao_router,
)
app.include_router(
    oai_ingestion_router,
)
app.include_router(system_router)
app.include_router(
    webhook_router,
)
# =========================================================
# ASSISTANT AGRICOLE
# =========================================================

assistant = AgriculturalAssistantService()

