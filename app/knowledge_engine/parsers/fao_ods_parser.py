import xml.etree.ElementTree as ET
from pathlib import Path

from app.schemas.document import DocumentMetadata


class FAOODSParser:

    def __init__(self, xml_path: Path):

        self.xml_path = xml_path

    def parse(self):

        print(
            "[FAO PARSER] Lecture du fichier AGRIS..."
        )

        if not self.xml_path.exists():

            raise FileNotFoundError(
                f"Fichier introuvable : "
                f"{self.xml_path}"
            )

        documents = []

        context = ET.iterparse(
            self.xml_path,
            events=("end",)
        )

        for event, element in context:

            # On cherche les notices AGRIS
            if element.tag.lower().endswith(
                "record"
            ):

                try:

                    document = self.parse_record(
                        element
                    )

                    if document:

                        documents.append(
                            document
                        )

                except Exception as e:

                    print(
                        "[FAO PARSER] "
                        "Erreur notice :",
                        e
                    )

                element.clear()

        print(
            "[FAO PARSER]",
            len(documents),
            "document(s) analysé(s)."
        )

        return documents

    def parse_record(
        self,
        record
    ):

        title = ""

        abstract = ""

        url = ""

        # Recherche simple des champs
        for element in record.iter():

            tag = element.tag.lower()

            text = (
                element.text.strip()
                if element.text
                else ""
            )

            if not text:
                continue

            if (
                "title" in tag
                and not title
            ):

                title = text

            elif (
                "abstract" in tag
                and not abstract
            ):

                abstract = text

            elif (
                "identifier" in tag
                and (
                    text.startswith(
                        "http://"
                    )
                    or text.startswith(
                        "https://"
                    )
                )
                and not url
            ):

                url = text

        # Sans titre, on ignore la notice
        if not title:

            return None

        # Si aucun lien n'est disponible,
        # on utilise une URL AGRIS générique
        if not url:

            url = (
                "https://agris.fao.org/"
            )

        return DocumentMetadata(

            title=title,

            url=url,

            description=abstract,

        )
