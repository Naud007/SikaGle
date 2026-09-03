from __future__ import annotations

from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.connectors.registry import registry
from app.knowledge_engine.protocols.ckan.client import CKANClient
from app.knowledge_engine.protocols.ckan.normalizer import (
    CKANNormalizer,
)
from app.schemas.document import DocumentMetadata


class IITAConnector(BaseConnector):
    """
    Connecteur CKAN pour IITA (International Institute of
    Tropical Agriculture), hébergé sur son propre dépôt
    (data.iita.org) — PAS Dataverse, contrairement à
    AfricaRice/IRRI/Bioversity/CIFOR/ICRISAT.

    NOTE (licence, 02/09/2026) : contrairement à Dataverse,
    l'API CKAN inclut déjà la licence de chaque jeu de données
    directement dans sa réponse (license_id, isopen) — pas
    besoin d'appel réseau séparé pour vérifier. Le filtrage se
    fait directement dans discover(), pas via
    OAIIngestionWorker.SOURCES_REQUIRING_LICENSE_CHECK (qui ne
    concerne que les sources Dataverse).

    IMPORTANT : chaque jeu de données CKAN nécessite un appel
    réseau séparé (get_package_details) pour connaître sa
    licence — avec 3490 jeux de données chez IITA, discover()
    peut prendre du temps. C'est pour cela qu'il tourne en
    local (comme convenu cette session pour tout gros volume),
    jamais sur Render.
    """

    BASE_URL = "https://data.iita.org"

    def __init__(self):
        super().__init__("iita")

        self.client = CKANClient(
            self.BASE_URL
        )

        self.normalizer = CKANNormalizer()

    def discover(
        self,
    ) -> list[DocumentMetadata]:

        documents: list[DocumentMetadata] = []

        package_names = (
            self.client.list_package_names()
        )

        total = len(
            package_names
        )

        print(
            "[IITA] "
            f"{total} jeux de données à examiner "
            "(récupération + filtrage licence, "
            "peut prendre du temps)..."
        )

        for index, package_name in enumerate(
            package_names,
            start=1,
        ):

            package = (
                self.client.get_package_details(
                    package_name
                )
            )

            if package is None:

                continue

            if not (
                self.normalizer
                .is_license_permissive(
                    package
                )
            ):

                continue

            documents.append(
                self.normalizer.normalize(
                    package,
                    source="IITA",
                )
            )

            if index % 100 == 0:

                print(
                    f"[IITA] {index}/{total} "
                    "examinés, "
                    f"{len(documents)} retenus "
                    "(licence permissive)."
                )

        print(
            "[IITA] Découverte terminée : "
            f"{len(documents)} documents retenus "
            f"sur {total} examinés."
        )

        return documents


registry.register(
    "iita",
    IITAConnector,
)