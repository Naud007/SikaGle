from __future__ import annotations

from app.knowledge_engine.harvesters.base_oai import (
    BaseOAIHarvester,
)


class HarvesterRegistry:
    """
    Registre des harvesters.
    """

    def __init__(self):

        self._harvesters: dict[
            str,
            type[BaseOAIHarvester],
        ] = {}

    def register(
        self,
        name: str,
        harvester: type[BaseOAIHarvester],
    ) -> None:

        self._harvesters[name] = harvester

    def get(
        self,
        name: str,
    ) -> BaseOAIHarvester:

        return self._harvesters[name]()

    def list(self) -> list[str]:

        return sorted(self._harvesters.keys())
