import hashlib
import hmac


class SignatureValidator:

    def validate(
        self,
        payload: bytes,
        signature: str,
        app_secret: str,
    ) -> bool:

        expected_signature = (
            "sha256="
            + hmac.new(
                app_secret.encode(),
                payload,
                hashlib.sha256,
            ).hexdigest()
        )

        return hmac.compare_digest(
            expected_signature,
            signature,
        )
