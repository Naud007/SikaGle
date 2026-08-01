from app.schemas.profile_request import (
    ProfileRequest,
)
from app.schemas.profile_response import (
    ProfileResponse,
)


class ProfileService:

    def get(
        self,
        user_id: str,
    ) -> ProfileResponse:

        return ProfileResponse(
            user_id=user_id,
            preferred_language="fr",
            location=None,
            main_crops=[],
            persona=None,
        )

    def update(
        self,
        user_id: str,
        request: ProfileRequest,
    ) -> ProfileResponse:

        return ProfileResponse(
            user_id=user_id,
            preferred_language=(
                request.preferred_language
            ),
            location=request.location,
            main_crops=request.main_crops,
            persona=request.persona,
        )
