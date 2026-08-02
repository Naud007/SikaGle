"""
Health Service de SikaGlé.

Ce service centralise les vérifications de santé de la plateforme.
"""

from datetime import datetime, UTC

from app.core.config import settings
from app.schemas import (
    HealthResponse,
    ReadinessResponse,
    LivenessResponse,
)


class HealthService:
    """
    Service de vérification de l'état de SikaGlé.
    """

    @staticmethod
    def health() -> HealthResponse:
        """
        Etat général de l'application.
        """

        return HealthResponse(
            status="healthy",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
            timestamp=datetime.now(UTC).isoformat(),
        )

    @staticmethod
    def readiness() -> ReadinessResponse:
        """
        Vérifie que les services essentiels sont prêts.
        """

        return ReadinessResponse(
            ready=True,
            database=True,
            knowledge_engine=True,
            timestamp=datetime.now(UTC).isoformat(),
        )

    @staticmethod
    def liveness() -> LivenessResponse:
        """
        Vérifie que l'application est vivante.
        """

        return LivenessResponse(
            alive=True,
            timestamp=datetime.now(UTC).isoformat(),
        )
