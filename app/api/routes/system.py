from fastapi import APIRouter

from app.core.monitoring import metrics
from app.core.logging import logger


router = APIRouter()


@router.get("/")
def root():
    metrics.increment_requests()

    return {
        "status": "online",
        "message": "API SikaGlé fonctionnelle",
    }


@router.get("/metrics")
def get_metrics():
    return metrics.snapshot()


@router.get("/db-status")
def db_status():
    from app.main import supabase

    if not supabase:
        return {
            "database": "disconnected",
            "reason": "Variables Supabase manquantes",
        }

    try:
        response = (
            supabase
            .table("users")
            .select("id", count="exact")
            .limit(1)
            .execute()
        )

        return {
            "database": "connected",
            "status": "ok",
            "users_count": response.count or 0,
        }

    except Exception as e:
        logger.exception(
            "Erreur lors de la vérification Supabase"
        )

        return {
            "database": "error",
            "details": str(e),
        }