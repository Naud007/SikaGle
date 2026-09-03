from __future__ import annotations

from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.connectors.registry import registry
from app.knowledge_engine.protocols.oai.client import OAIClient
from app.knowledge_engine.protocols.oai.normalizer import OAINormalizer
from app.knowledge_engine.protocols.oai.parser import OAIParser
from app.schemas.document import DocumentMetadata


class WorldAgroforestryConnector(BaseConnector):
    """
    Connecteur OAI-PMH pour World Agroforestry (ICRAF),
    hébergé sur Harvard Dataverse (set OAI-PMH
    "World_Agroforestry_ICRAF").

    NOTE (licence, 02/09/2026) : licence non vérifiée dans
    le détail au moment de la création de ce connecteur —
    c'est pour cela que "world_agroforestry" figure dans
    OAIIngestionWorker.SOURCES_REQUIRING_LICENSE_CHECK, qui
    vérifie la licence réelle de chaque document via
    DataverseLicenseChecker avant ingestion, comme pour
    IRRI/CIFOR/Bioversity.
    """

    BASE_URL = "https://dataverse.harvard.edu/oai"

    OAI_SET = "World_Agroforestry_ICRAF"

    def __init__(self):
        super().__init__("world_agroforestry")

        self.client = OAIClient(self.BASE_URL)
        self.parser = OAIParser()
        self.normalizer = OAINormalizer()

    def discover(
        self,
    ) -> list[DocumentMetadata]:

        documents: list[DocumentMetadata] = []

        soup = self.client.list_records(
            set_spec=self.OAI_SET
        )

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
    "world_agroforestry",
    WorldAgroforestryConnector,
)