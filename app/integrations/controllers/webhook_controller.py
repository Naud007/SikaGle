from app.integrations.models.webhook_verification import (
    WebhookVerification,
)
from app.integrations.security.signature_validator import (
    SignatureValidator,
)
from app.integrations.security.webhook_verifier import (
    WebhookVerifier,
)


class WebhookController:

    def __init__(self):

        self.verifier = (
            WebhookVerifier()
        )

        self.signature_validator = (
            SignatureValidator()
        )

    def verify_webhook(
        self,
        mode: str,
        challenge: str,
        verify_token: str,
        expected_token: str,
    ) -> WebhookVerification:

        return self.verifier.verify(
            mode=mode,
            challenge=challenge,
            verify_token=verify_token,
            expected_token=expected_token,
        )

    def validate_signature(
        self,
        payload: bytes,
        signature: str,
        app_secret: str,
    ) -> bool:

        return (
            self.signature_validator.validate(
                payload=payload,
                signature=signature,
                app_secret=app_secret,
            )
        )
