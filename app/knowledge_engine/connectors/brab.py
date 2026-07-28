from __future__ import annotations

from app.knowledge_engine.harvesters.base_oai import (
    BaseOAIHarvester,
)


class BRABOAIHarvester(BaseOAIHarvester):
    """
    Harvester OAI-PMH du BRAB.
    """

    BASE_URL = (
        "https://brab.bj/index.php/brab/oai"
    )

    SOURCE = "BRAB"
