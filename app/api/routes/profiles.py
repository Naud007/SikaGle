from fastapi import APIRouter

from app.application.profile.profile_service import (
    ProfileService,
)
from app.schemas.profile_request import (
    ProfileRequest,
)
from app.schemas.profile_response import (
    ProfileResponse,
)

router = APIRouter(
    prefix="/users",
    tags=["Profiles"],
)

service = ProfileService()


@router.get(
    "/{user_id}/profile",
    response_model=ProfileResponse,
)
def get_profile(
    user_id: str,
) -> ProfileResponse:

    return service.get(
        user_id=user_id,
    )


@router.patch(
    "/{user_id}/profile",
    response_model=ProfileResponse,
)
def update_profile(
    user_id: str,
    request: ProfileRequest,
) -> ProfileResponse:

    return service.update(
        user_id=user_id,
        request=request,
    )
