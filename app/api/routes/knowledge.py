from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.knowledge_service import KnowledgeService

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)

service = KnowledgeService()


@router.get("/discover")
def discover(
    source: str,
):
    """
    Découvre les documents d'une source.
    """

    try:

        return service.discover(
            source=source,
        )

    except KeyError:

        raise HTTPException(
            status_code=404,
            detail=f"Source '{source}' introuvable.",
        )


@router.get("/discover/all")
def discover_all():
    """
    Découvre les documents de toutes les sources enregistrées.
    """

    return service.discover_all(
        [
            "brab",
        ]
    )
