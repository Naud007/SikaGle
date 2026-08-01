from fastapi import APIRouter

from app.application.system.health_service import (
    HealthService,
)
from app.schemas.health_response import (
    HealthResponse,
)

router = APIRouter(
    tags=["Health"],
)

service = HealthService()


@router.get(
    "/health",
    response_model=HealthResponse,
)
def health() -> HealthResponse:

    return service.health()


@router.get(
    "/ready",
    response_model=HealthResponse,
)
def ready() -> HealthResponse:

    return service.ready()


@router.get(
    "/live",
    response_model=HealthResponse,
)
def live() -> HealthResponse:

    return service.live()
