import requests
from pathlib import Path
from urllib.parse import urljoin

from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.connectors.registry import registry
from app.schemas.document import DocumentMetadata


class FAOConnector(BaseConnector):

    def __init__(self):
        super().__init__("fao")

        self.base_url = "https://openknowledge.fao.org"
        self.api_url = (
            f"{self.base_url}/server/api"
        )

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; SikaGle-KnowledgeEngine/1.0)"
            )
        }

    def _extract_uuid(
        self,
        document: DocumentMetadata,
    ) -> str:
        """
        Extrait l'UUID FAO depuis l'URL publique du document.
        """

        return (
            str(document.url)
        .    rstrip("/")
        .    split("/")[-1]
        )

    def _get_bundles(
        self,
        uuid: str,
    ) -> list[dict]:
        """
        Récupère les bundles associés à un document FAO.
        """

        bundles_url = (
            f"{self.api_url}"
            f"/core/items/{uuid}/bundles"
        )

        response = requests.get(
            bundles_url,
            headers=self.headers,
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        return (
            data
            .get("_embedded", {})
            .get("bundles", [])
        )

    def _get_bitstreams(
        self,
        bundle_uuid: str,
    ) -> list[dict]:
        """
        Récupère les bitstreams d'un bundle FAO.
        """

        response = requests.get(
            f"{self.api_url}"
            f"/core/bundles/{bundle_uuid}/bitstreams",
            headers=self.headers,
            timeout=60,
        )

        if response.status_code != 200:
            return []

        data = response.json()

        return (
            data
            .get("_embedded", {})
            .get("bitstreams", [])
        )

    def _find_pdf_url(
        self,
        bundles: list[dict],
    ) -> str | None:
        """
        Recherche l'URL du premier PDF disponible
        dans les bundles du document.
        """

        for bundle in bundles:

            bundle_uuid = bundle.get("uuid")

            if not bundle_uuid:
                continue

            bitstreams = self._get_bitstreams(
                bundle_uuid
            )

            for bitstream in bitstreams:

                name = (
                    bitstream
                    .get("name", "")
                    .lower()
                )

                if ".pdf" not in name:
                    continue

                bitstream_uuid = bitstream.get(
                    "uuid"
                )

                if not bitstream_uuid:
                    continue

                return (
                    f"{self.api_url}"
                    f"/core/bitstreams/"
                    f"{bitstream_uuid}"
                    f"/content"
                )

        return None

    
    def discover(self):

        self.log(
            "Recherche via l'API REST DSpace de la FAO..."
        )

        url = (
            f"{self.api_url}/core/items"
        )

        response = requests.get(
            url,
            headers=self.headers,
            params={
                "size": 20
            },
            timeout=60
        )

        self.log(
            f"Statut HTTP API : "
            f"{response.status_code}"
        )

        self.log(
            f"Taille réponse API : "
            f"{len(response.text)} caractères"
        )

        response.raise_for_status()

        data = response.json()

        documents = []

        # DSpace renvoie les éléments dans _embedded
        embedded = data.get(
            "_embedded",
            {}
        )

        items = embedded.get(
            "items",
            []
        )

        self.log(
            f"{len(items)} élément(s) reçu(s) de DSpace."
        )

        for item in items:

            uuid = item.get(
                "uuid"
            )

            name = item.get(
                "name"
            )

            if not uuid or not name:
                continue

            # URL publique de l'item
            item_url = (
                f"{self.base_url}"
                f"/items/{uuid}"
            )

            try:

                document = DocumentMetadata(
                    title=name,
                    source="FAO",
                    url=item_url,
                    document_type="publication"
                )

                documents.append(
                    document
                )

            except Exception as e:

                self.log(
                    f"⚠️ Élément ignoré : {e}"
                )

        self.log(
            f"{len(documents)} document(s) "
            f"FAO découvert(s)."
        )

        for document in documents[:10]:

            self.log(
                f"- {document.title}"
            )

        return documents

    def download(
        self,
        document: DocumentMetadata
    ) -> Path:

        self.log(
            f"Recherche du PDF : "
            f"{document.title}"
        )

        # Extraire l'UUID depuis l'URL publique
        uuid = self._extract_uuid(
            document
        )

        item_api_url = (
            f"{self.api_url}"
            f"/core/items/{uuid}"
        )

        response = requests.get(
            item_api_url,
            headers=self.headers,
            timeout=60
        )

        response.raise_for_status()

        item_data = response.json()

        # Chercher les bitstreams liés à l'item
        bundles = self._get_bundles(
            uuid
        )

        pdf_url = self._find_pdf_url(
            bundles
        )

        if not pdf_url:

            self.log(
                "⚠️ Aucun PDF trouvé."
            )

            return None

        self.log(
            f"PDF trouvé : {pdf_url}"
        )

        safe_name = "".join(
            c
            if c.isalnum()
            or c in (
                " ",
                "-",
                "_"
            )
            else "_"
            for c in document.title
        ).strip()

        safe_name = safe_name[:150]

        filename = (
            self.storage_dir
            / f"{safe_name}.pdf"
        )

        pdf_response = requests.get(
            pdf_url,
            headers=self.headers,
            timeout=120
        )

        pdf_response.raise_for_status()

        with open(
            filename,
            "wb"
        ) as file:

            file.write(
                pdf_response.content
            )

        self.log(
            f"✅ PDF téléchargé : "
            f"{filename}"
        )

        return filename


registry.register(
    "fao",
    FAOConnector
)
