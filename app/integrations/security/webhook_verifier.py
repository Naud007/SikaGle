from app.integrations.models.webhook_verification import (
    WebhookVerification,
)


class WebhookVerifier:

    def verify(
        self,
        mode: str,
        challenge: str,
        verify_token: str,
        expected_token: str,
    ) -> WebhookVerification:

        verified = (
            mode == "subscribe"
            and verify_token == expected_token
        )

        return WebhookVerification(
            mode=mode,
            challenge=challenge,
            verify_token=verify_token,
            verified=verified,
        )
