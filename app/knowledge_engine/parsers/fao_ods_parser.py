import xml.etree.ElementTree as ET

from app.schemas.document import DocumentMetadata


class FAOODSParser:

    def __init__(self, xml_path):
        self.xml_path = xml_path

    def parse(self):

        print("[FAO PARSER] Lecture du fichier AGRIS...")

        tree = ET.parse(self.xml_path)
        root = tree.getroot()

        # Namespaces XML utilisés par AGRIS
        namespaces = {
            "dcat": "http://www.w3.org/ns/dcat#",
            "dc": "http://purl.org/dc/elements/1.1/",
            "dct": "http://purl.org/dc/terms/",
        }

        # Recherche des datasets
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

            # -------------------------------------------------
            # TITRE
            # -------------------------------------------------

            title_element = dataset.find(
                "dc:title",
                namespaces
            )

            title = (
                title_element.text.strip()
                if title_element is not None
                and title_element.text
                else "Dataset AGRIS"
            )

            # -------------------------------------------------
            # DESCRIPTION
            # -------------------------------------------------

            description_element = dataset.find(
                "dc:description",
                namespaces
            )

            description = (
                description_element.text.strip()
                if description_element is not None
                and description_element.text
                else None
            )

            # -------------------------------------------------
            # DATE DE MODIFICATION
            # -------------------------------------------------

            modified_element = dataset.find(
                "dct:modified",
                namespaces
            )

            published_at = (
                modified_element.text.strip()
                if modified_element is not None
                and modified_element.text
                else None
            )

            # -------------------------------------------------
            # IDENTIFIANT
            # -------------------------------------------------

            identifier_element = dataset.find(
                "dc:identifier",
                namespaces
            )

            identifier = (
                identifier_element.text.strip()
                if identifier_element is not None
                and identifier_element.text
                else None
            )

            # -------------------------------------------------
            # URL DE TÉLÉCHARGEMENT
            # -------------------------------------------------

            download_element = dataset.find(
                ".//dcat:downloadURL",
                namespaces
            )

            if (
                download_element is None
                or not download_element.text
            ):
                continue

            url = download_element.text.strip()

            # -------------------------------------------------
            # VÉRIFICATION DE L'URL
            # -------------------------------------------------

            if not url.startswith(
                ("http://", "https://")
            ):
                continue

            # -------------------------------------------------
            # CRÉATION DU DOCUMENT
            # -------------------------------------------------

            try:

                document = DocumentMetadata(
                    title=title,
                    url=url,
                    description=description,
                    published_at=published_at,
                    source="FAO AGRIS",
                )

                documents.append(document)

            except Exception as e:

                print(
                    f"[FAO PARSER] "
                    f"Document ignoré : {e}"
                )

        # -------------------------------------------------
        # RÉSULTAT FINAL
        # -------------------------------------------------

        print(
            f"[FAO PARSER] "
            f"{len(documents)} document(s) analysé(s)."
        )

        return documents
