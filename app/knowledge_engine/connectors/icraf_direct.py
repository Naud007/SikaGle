from __future__ import annotations

from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.connectors.registry import registry
from app.knowledge_engine.protocols.oai.client import OAIClient
from app.knowledge_engine.protocols.oai.normalizer import OAINormalizer
from app.knowledge_engine.protocols.oai.parser import OAIParser
from app.schemas.document import DocumentMetadata


class ICRAFDirectConnector(BaseConnector):
    """
    Connecteur OAI-PMH pour World Agroforestry (ICRAF), sur
    LEUR PROPRE instance Dataverse (data.worldagroforestry.org)
    — différent du connecteur "world_agroforestry" existant, qui
    pointait vers l'ancien set Harvard Dataverse "icraf",
    désormais marqué comme migré/obsolète par ICRAF lui-même.

    NOTE (licence, 03/09/2026) : licence mixte (CC / other selon
    re3data), pas de garantie globale — filtrage par document
    nécessaire via DataverseLicenseChecker, comme ICRISAT.
    """

    BASE_URL = "https://data.worldagroforestry.org/oai"

    def __init__(self):
        super().__init__("icraf_direct")

        self.client = OAIClient(self.BASE_URL)
        self.parser = OAIParser()
        self.normalizer = OAINormalizer()

    def discover(
        self,
    ) -> list[DocumentMetadata]:

        documents: list[DocumentMetadata] = []

        soup = self.client.list_records()

        while True:

            records = self.parser.parse_records(soup)

            for record in records:

                documents.append(
                    self.normalizer.normalize(
                        record,
                        source="World Agroforestry (ICRAF)",
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


registry.register(
    "icraf_direct",
    ICRAFDirectConnector,
)