from __future__ import annotations

from app.knowledge_engine.protocols.oai.client import (
    OAIClient,
)
from app.knowledge_engine.protocols.oai.normalizer import (
    OAINormalizer,
)
from app.knowledge_engine.protocols.oai.parser import (
    OAIParser,
)


class BRABOAIHarvester:
    """
    Harvester OAI-PMH du BRAB.
    """

    BASE_URL = (
        "https://brab.bj/index.php/brab/oai"
    )

    def __init__(self):

        self.client = OAIClient(
            self.BASE_URL
        )

        self.parser = OAIParser()

        self.normalizer = OAINormalizer()

    def harvest(self):

        soup = self.client.list_records()

        records = self.parser.parse_records(
            soup
        )

        documents = [
            self.normalizer.normalize(
                record,
                source="BRAB",
            )
            for record in records
        ]

        return documents
