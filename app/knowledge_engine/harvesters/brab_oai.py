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

    def __init__(self):
        super().__init__(self.BASE_URL)

    def harvest(self):

        soup = self.fetch(
            {
                "verb": "Identify",
            }
        )

        repository = soup.find(
            "repositoryName"
        )

        if repository:

            print(
                "[BRAB OAI] "
                f"Dépôt : {repository.text}"
            )

        return soup
