from uuid import uuid4

from app.schemas.user_request import (
    UserRequest,
)
from app.schemas.user_response import (
    UserResponse,
)


class UserService:

    def create(
        self,
        request: UserRequest,
    ) -> UserResponse:

        #
        # Implémentation V1 :
        # Stub prêt à être connecté
        # au User Repository.
        #

        return UserResponse(
            user_id=str(uuid4()),
            username=request.username,
            preferred_language=(
                request.preferred_language
            ),
            phone_number=request.phone_number,
            email=request.email,
        )

    def get(
        self,
        user_id: str,
    ) -> UserResponse:

        return UserResponse(
            user_id=user_id,
            username="",
            preferred_language="fr",
        )

    def update(
        self,
        user_id: str,
        request: UserRequest,
    ) -> UserResponse:

        return UserResponse(
            user_id=user_id,
            username=request.username,
            preferred_language=(
                request.preferred_language
            ),
            phone_number=request.phone_number,
            email=request.email,
        )
