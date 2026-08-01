from datetime import UTC, datetime, timedelta

import jwt


class JWTAuth:

    ALGORITHM = "HS256"

    def create_token(
        self,
        payload: dict,
        secret_key: str,
        expires_in: int = 3600,
    ) -> str:

        data = payload.copy()

        data["exp"] = (
            datetime.now(UTC)
            + timedelta(
                seconds=expires_in
            )
        )

        return jwt.encode(
            data,
            secret_key,
            algorithm=self.ALGORITHM,
        )

    def verify_token(
        self,
        token: str,
        secret_key: str,
    ) -> dict:

        return jwt.decode(
            token,
            secret_key,
            algorithms=[
                self.ALGORITHM
            ],
        )
