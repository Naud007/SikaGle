from __future__ import annotations

from fastapi import APIRouter

from app.knowledge_engine.harvesters import (
    registry,
)

router = APIRouter(
    prefix="/harvesters",
    tags=["Harvesters"],
)


@router.get(
    "/{name}",
)
def run_harvester(
    name: str,
):

    harvester = registry.get(name)

    documents = harvester.harvest()

    return {
        "harvester": name,
        "count": len(documents),
        "documents": documents,
    }
