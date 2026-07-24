import xml.etree.ElementTree as ET
from pathlib import Path


class FAOODSParser:

    NS = {
        "dcat": "http://www.w3.org/ns/dcat#",
        "dc": "http://purl.org/dc/elements/1.1/",
        "dct": "http://purl.org/dc/terms/",
    }

    def __init__(self, xml_path: Path):
        self.xml_path = xml_path

    def parse(self):

        print("[FAO PARSER] Lecture du fichier AGRIS...")

        tree = ET.parse(self.xml_path)
        root = tree.getroot()

        datasets = root.findall(
            ".//dcat:Dataset",
            self.NS
        )

        print(
            f"[FAO PARSER] {len(datasets)} dataset(s) trouvé(s)."
        )

        # Afficher la structure du premier dataset
        if datasets:

            print("\n" + "=" * 50)
            print("[FAO PARSER] STRUCTURE DU PREMIER DATASET")
            print("=" * 50)

            first_dataset = datasets[0]

            for element in first_dataset.iter():

                tag = element.tag
                text = element.text.strip() if element.text else ""

                print(
                    f"TAG : {tag}"
                )

                if text:
                    print(
                        f"TEXT : {text[:300]}"
                    )

                print("-" * 30)

            print("=" * 50)

        return []
