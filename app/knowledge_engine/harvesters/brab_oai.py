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

        documents = []

        soup = self.client.list_records()

        while True:

            records = self.parser.parse_records(
                soup
            )

            for record in records:

                documents.append(
                    self.normalizer.normalize(
                        record,
                        source="BRAB",
                    )
                )

            token = (
                self.parser.parse_resumption_token(
                    soup
                )
            )

            if not token:
                break

            soup = (
                self.client.list_records_from_token(
                    token
                )
            )

        return documents
