from datetime import datetime, UTC

from app.schemas.health_response import (
    HealthResponse,
)


class HealthService:

    VERSION = "v1"

    def health(
        self,
    ) -> HealthResponse:

        return HealthResponse(
            status="healthy",
            service="SikaGlé API",
            version=self.VERSION,
            timestamp=(
                datetime.now(
                    UTC
                ).isoformat()
            ),
        )

    def ready(
        self,
    ) -> HealthResponse:

        return HealthResponse(
            status="ready",
            service="SikaGlé API",
            version=self.VERSION,
            timestamp=(
                datetime.now(
                    UTC
                ).isoformat()
            ),
        )

    def live(
        self,
    ) -> HealthResponse:

        return HealthResponse(
            status="alive",
            service="SikaGlé API",
            version=self.VERSION,
            timestamp=(
                datetime.now(
                    UTC
                ).isoformat()
            ),
        )
