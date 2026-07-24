import xml.etree.ElementTree as ET
from pathlib import Path

from app.schemas.document import DocumentMetadata


class FAOODSParser:

    # Namespaces utilisés par le fichier AGRIS
    NS = {
        "dcat": "http://www.w3.org/ns/dcat#",
        "dc": "http://purl.org/dc/elements/1.1/",
        "dct": "http://purl.org/dc/terms/",
    }

    def __init__(self, xml_path: Path):
        self.xml_path = xml_path

    def parse(self):

        print("[FAO PARSER] Lecture du fichier AGRIS...")

        if not self.xml_path.exists():
            raise FileNotFoundError(
                f"Fichier AGRIS introuvable : {self.xml_path}"
            )

        documents = []

        try:

            tree = ET.parse(self.xml_path)
            root = tree.getroot()

            # Recherche de tous les Dataset
            datasets = root.findall(
                ".//dcat:Dataset",
                self.NS
            )

            print(
                f"[FAO PARSER] {len(datasets)} dataset(s) trouvé(s)."
            )

            for dataset in datasets:

                # Titre
                title_element = dataset.find(
                    "dct:title",
                    self.NS
                )

                if title_element is None:
                    title_element = dataset.find(
                        "dc:title",
                        self.NS
                    )

                title = (
                    title_element.text.strip()
                    if title_element is not None
                    and title_element.text
                    else "Sans titre"
                )

                # Description
                description_element = dataset.find(
                    "dc:description",
                    self.NS
                )

                description = (
                    description_element.text.strip()
                    if description_element is not None
                    and description_element.text
                    else None
                )

                # Identifiant
                identifier_element = dataset.find(
                    "dc:identifier",
                    self.NS
                )

                identifier = (
                    identifier_element.text.strip()
                    if identifier_element is not None
                    and identifier_element.text
                    else None
                )

                # URL de téléchargement
                download_element = dataset.find(
                    "dcat:downloadURL",
                    self.NS
                )

                url = (
                    download_element.text.strip()
                    if download_element is not None
                    and download_element.text
                    else None
                )

                # Si aucune URL de téléchargement,
                # on utilise l'identifiant si c'est une URL
                if not url and identifier:
                    if identifier.startswith("http"):
                        url = identifier

                # On ignore les datasets sans URL exploitable
                if not url:
                    continue

                try:

                    document = DocumentMetadata(
                        title=title,
                        url=url,
                        description=description
                    )

                    documents.append(document)

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

        except Exception as e:

            print(
                f"[FAO PARSER] Erreur lecture XML : {e}"
            )

            raise
