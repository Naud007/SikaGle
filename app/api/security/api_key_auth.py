import secrets


class APIKeyAuth:

    def generate_key(
        self,
        length: int = 32,
    ) -> str:

        return secrets.token_hex(
            length
        )

    def verify_key(
        self,
        api_key: str,
        expected_key: str,
    ) -> bool:

        return secrets.compare_digest(
            api_key,
            expected_key,
        )
