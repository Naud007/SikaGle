from __future__ import annotations

from abc import ABC

from app.knowledge_engine.protocols.oai.client import (
    OAIClient,
)
from app.knowledge_engine.protocols.oai.normalizer import (
    OAINormalizer,
)
from app.knowledge_engine.protocols.oai.parser import (
    OAIParser,
)
from app.schemas.document import DocumentMetadata


class BaseOAIHarvester(ABC):
    """
    Classe de base pour tous les harvesters OAI-PMH.
    """

    BASE_URL: str = ""

    SOURCE: str = ""

    METADATA_PREFIX: str = "oai_dc"

    def __init__(self):

        self.client = OAIClient(
            self.BASE_URL
        )

        self.parser = OAIParser()

        self.normalizer = OAINormalizer()

    def harvest(
        self,
    ) -> list[DocumentMetadata]:

        documents: list[DocumentMetadata] = []

        soup = self.client.list_records(
            metadata_prefix=self.METADATA_PREFIX,
        )

        while True:

            records = self.parser.parse_records(
                soup
            )

            for record in records:

                documents.append(
                    self.normalizer.normalize(
                        record,
                        source=self.SOURCE,
                    )
                )

            token = self.parser.parse_resumption_token(
                soup
            )

            if token is None:
                break

            soup = self.client.list_records_from_token(
                token
            )

        return documents
