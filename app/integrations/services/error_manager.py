from app.integrations.models.whatsapp_error import (
    WhatsAppError,
)


class ErrorManager:

    RETRYABLE_ERRORS = {
        "MEDIA_UNAVAILABLE",
        "META_API_UNAVAILABLE",
        "RATE_LIMIT",
    }

    def build(
        self,
        code: str,
        message: str,
        details: dict | None = None,
    ) -> WhatsAppError:

        return WhatsAppError(
            code=code,
            message=message,
            details=details or {},
            retryable=(
                code
                in self.RETRYABLE_ERRORS
            ),
        )
