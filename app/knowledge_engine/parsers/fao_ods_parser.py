import xml.etree.ElementTree as ET
from datetime import date

from app.schemas.document import DocumentMetadata


class FAOODSParser:

    def __init__(self, xml_path):
        self.xml_path = xml_path

    def parse(self):

        print("[FAO PARSER] Lecture du fichier AGRIS...")

        try:

            tree = ET.parse(self.xml_path)
            root = tree.getroot()

        except Exception as e:

            print(
                f"[FAO PARSER] Erreur lecture XML : {e}"
            )

            return []

        namespaces = {
            "dcat": "http://www.w3.org/ns/dcat#",
            "dc": "http://purl.org/dc/elements/1.1/",
            "dct": "http://purl.org/dc/terms/",
        }

        datasets = root.findall(
            ".//dcat:Dataset",
            namespaces
        )

        print(
            f"[FAO PARSER] "
            f"{len(datasets)} dataset(s) trouvé(s)."
        )

        documents = []

        for dataset in datasets:

            # =================================================
            # TITRE
            # =================================================

            title = self._get_text(
                dataset,
                [
                    "dc:title",
                    "dct:title",
                ],
                namespaces
            )

            if not title:
                title = "Dataset AGRIS"

            # =================================================
            # DESCRIPTION
            # =================================================

            description = self._get_text(
                dataset,
                [
                    "dc:description",
                    "dct:description",
                ],
                namespaces
            )

            # =================================================
            # DATE
            # =================================================

            published_at = self._parse_date(
                self._get_text(
                    dataset,
                    [
                        "dct:modified",
                        "dct:issued",
                    ],
                    namespaces
                )
            )

            # =================================================
            # IDENTIFIANT
            # =================================================

            identifier = self._get_text(
                dataset,
                [
                    "dc:identifier",
                    "dct:identifier",
                ],
                namespaces
            )

            # =================================================
            # URL
            # =================================================

            url = self._get_url(
                dataset,
                namespaces
            )

            if not url:

                if identifier:

                    url = (
                        "https://agris.fao.org/"
                        f"search/en/providers/122436/"
                        f"records/{identifier}"
                    )

                else:

                    continue

            # =================================================
            # CONTENU
            # =================================================

            content_parts = []

            if title:
                content_parts.append(title)

            if description:
                content_parts.append(description)

            content = "\n\n".join(
                content_parts
            )

            # =================================================
            # CRÉATION DOCUMENT
            # =================================================

            try:

                document = DocumentMetadata(

                    title=title,

                    source="FAO AGRIS",

                    url=url,

                    published_at=published_at,

                    language="fr",

                    country="Bénin",

                    document_type="agricultural_dataset",

                    description=description,

                    content=content,

                )

                documents.append(
                    document
                )

            except Exception as e:

                print(
                    f"[FAO PARSER] "
                    f"Document ignoré : {e}"
                )

        print(
            f"[FAO PARSER] "
            f"{len(documents)} document(s) analysé(s)."
        )

        return documents

    # =========================================================
    # OUTILS INTERNES
    # =========================================================

    def _get_text(
        self,
        element,
        paths,
        namespaces
    ):

        for path in paths:

            try:

                child = element.find(
                    path,
                    namespaces
                )

                if (
                    child is not None
                    and child.text
                    and child.text.strip()
                ):

                    return child.text.strip()

            except Exception:

                pass

        return None

    # =========================================================

    def _get_url(
        self,
        element,
        namespaces
    ):

        # downloadURL
        download_url = element.find(
            ".//dcat:downloadURL",
            namespaces
        )

        if (
            download_url is not None
            and download_url.text
        ):

            url = download_url.text.strip()

            if url.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                return url

        # landingPage
        landing_page = element.find(
            ".//dcat:landingPage",
            namespaces
        )

        if (
            landing_page is not None
            and landing_page.text
        ):

            url = landing_page.text.strip()

            if url.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                return url

        return None

    # =========================================================

    def _parse_date(
        self,
        value
    ):

        if not value:

            return None

        try:

            return date.fromisoformat(
                value[:10]
            )

        except Exception:

            return None
