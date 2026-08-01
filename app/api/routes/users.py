from fastapi import APIRouter

from app.application.user.user_service import (
    UserService,
)
from app.schemas.user_request import (
    UserRequest,
)
from app.schemas.user_response import (
    UserResponse,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

service = UserService()


@router.post(
    "",
    response_model=UserResponse,
)
def create_user(
    request: UserRequest,
) -> UserResponse:

    return service.create(
        request=request,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: str,
) -> UserResponse:

    return service.get(
        user_id=user_id,
    )


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: str,
    request: UserRequest,
) -> UserResponse:

    return service.update(
        user_id=user_id,
        request=request,
    )
