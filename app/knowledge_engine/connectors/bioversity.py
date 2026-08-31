from __future__ import annotations

from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.connectors.registry import registry
from app.knowledge_engine.protocols.oai.client import OAIClient
from app.knowledge_engine.protocols.oai.normalizer import OAINormalizer
from app.knowledge_engine.protocols.oai.parser import OAIParser
from app.schemas.document import DocumentMetadata


class BioversityConnector(BaseConnector):
    """
    Connecteur OAI-PMH pour la collection Alliance of
    Bioversity International and CIAT, hébergée sur Harvard
    Dataverse (set OAI-PMH "AllianceBioversityCIAT").

    NOTE (licence, 31/08/2026) : ce dépôt est officiellement
    en CC BY-NC-SA 4.0 (non-commercial), confirmé via re3data.
    C'est pour cela que "bioversity" figure dans
    OAIIngestionWorker.SOURCES_REQUIRING_LICENSE_CHECK — le
    filtrage par document exclura donc très probablement la
    quasi-totalité des documents de cette source (leur licence
    par défaut n'est pas permissive), sauf cas individuels où
    un chercheur aurait choisi une licence différente pour son
    propre dataset.
    """

    BASE_URL = "https://dataverse.harvard.edu/oai"

    OAI_SET = "AllianceBioversityCIAT"

    def __init__(self):
        super().__init__("bioversity")

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
                        source="Bioversity",
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
    "bioversity",
    BioversityConnector,
)