from __future__ import annotations

from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.connectors.registry import registry
from app.knowledge_engine.protocols.oai.client import OAIClient
from app.knowledge_engine.protocols.oai.normalizer import OAINormalizer
from app.knowledge_engine.protocols.oai.parser import OAIParser
from app.schemas.document import DocumentMetadata


class CIFORConnector(BaseConnector):
    """
    Connecteur OAI-PMH pour la collection CIFOR (Center for
    International Forestry Research), hébergée sur Harvard
    Dataverse (set OAI-PMH "CIFOR").

    NOTE (licence, 31/08/2026) : ce dépôt a des licences
    MIXTES d'un dataset à l'autre (confirmé via re3data :
    "DataLicense: CC" et "DataLicense: Copyrights" listées
    côte à côte, pas une licence unique). C'est pour cela que
    "cifor" figure dans
    OAIIngestionWorker.SOURCES_REQUIRING_LICENSE_CHECK.
    """

    BASE_URL = "https://dataverse.harvard.edu/oai"

    OAI_SET = "CIFOR"

    def __init__(self):
        super().__init__("cifor")

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
                        source="CIFOR",
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
    "cifor",
    CIFORConnector,
)