from datetime import datetime

from app.core.monitoring import metrics
from app.core.config import settings


class HealthService:

    def live(self):

        return {
            "status": "alive"
        }

    def ready(self):

        checks = {
            "configuration": bool(settings.GEMINI_API_KEY),
            "monitoring": True,
        }

        status = "ready"

        if not all(checks.values()):
            status = "not_ready"

        return {
            "status": status,
            "checks": checks
        }

    def health(self):

        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics.snapshot()
        }


health_service = HealthService()
