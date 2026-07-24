import xml.etree.ElementTree as ET
from pathlib import Path


class FAOODSParser:

    def __init__(self, xml_path: Path):
        self.xml_path = xml_path

    def parse(self):

        print(
            "[FAO PARSER] Inspection de la structure XML..."
        )

        if not self.xml_path.exists():
            raise FileNotFoundError(
                f"Fichier introuvable : {self.xml_path}"
            )

        documents = []

        try:

            # Lecture du fichier XML
            tree = ET.parse(self.xml_path)

            root = tree.getroot()

            print(
                "[FAO PARSER] Racine XML :",
                root.tag
            )

            print(
                "[FAO PARSER] Attributs racine :",
                root.attrib
            )

            # Afficher les premières balises
            print(
                "[FAO PARSER] Analyse des balises..."
            )

            tags = set()

            for element in root.iter():

                tags.add(element.tag)

                if len(tags) >= 30:
                    break

            for tag in tags:

                print(
                    "[FAO PARSER] Balise :",
                    tag
                )

            print(
                "[FAO PARSER] Nombre total "
                "d'éléments XML :",
                len(list(root.iter()))
            )

            return documents

        except Exception as e:

            print(
                "[FAO PARSER] Erreur lecture XML :",
                e
            )

            raise
