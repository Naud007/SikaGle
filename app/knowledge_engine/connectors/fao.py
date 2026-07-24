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
        uuid = str(
            document.url
        ).rstrip(
            "/"
        ).split(
            "/"
        )[-1]

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
        bitstreams_url = (
            f"{self.api_url}"
            f"/core/items/{uuid}"
            f"/bundles"
        )

        bundles_response = requests.get(
            bitstreams_url,
            headers=self.headers,
            timeout=60
        )

        bundles_response.raise_for_status()

        bundles_data = bundles_response.json()

        bundles = (
            bundles_data
            .get(
                "_embedded",
                {}
            )
            .get(
                "bundles",
                []
            )
        )

        pdf_url = None

        for bundle in bundles:

            bundle_uuid = bundle.get(
                "uuid"
            )

            if not bundle_uuid:
                continue

            bitstreams_response = requests.get(
                f"{self.api_url}"
                f"/core/bundles/"
                f"{bundle_uuid}/bitstreams",
                headers=self.headers,
                timeout=60
            )

            if (
                bitstreams_response.status_code
                != 200
            ):
                continue

            bitstreams_data = (
                bitstreams_response.json()
            )

            bitstreams = (
                bitstreams_data
                .get(
                    "_embedded",
                    {}
                )
                .get(
                    "bitstreams",
                    []
                )
            )

            for bitstream in bitstreams:

                bitstream_name = (
                    bitstream
                    .get(
                        "name",
                        ""
                    )
                    .lower()
                )

                if ".pdf" not in bitstream_name:
                    continue

                bitstream_uuid = (
                    bitstream
                    .get(
                        "uuid"
                    )
                )

                if not bitstream_uuid:
                    continue

                pdf_url = (
                    f"{self.api_url}"
                    f"/core/bitstreams/"
                    f"{bitstream_uuid}"
                    f"/content"
                )

                break

            if pdf_url:
                break

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
