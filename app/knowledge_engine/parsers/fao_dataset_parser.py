from pathlib import Path
import xml.etree.ElementTree as ET


class FAODatasetParser:

    def __init__(self, datasets_dir=None):

        # ---------------------------------------------------------
        # DÉFINITION DU DOSSIER DES DATASETS
        # ---------------------------------------------------------

        if datasets_dir is None:

            datasets_dir = (
                Path(__file__).resolve()
                .parents[3]
                / "knowledge"
                / "raw"
                / "fao"
                / "datasets"
            )

        self.datasets_dir = Path(
            datasets_dir
        )

        # Création automatique du dossier
        self.datasets_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    # ---------------------------------------------------------
    # PARSER UN FICHIER XML
    # ---------------------------------------------------------

    def parse_file(self, xml_path):

        xml_path = Path(
            xml_path
        )

        print(
            f"[FAO DATASET PARSER] "
            f"Lecture : {xml_path.name}"
        )

        try:

            tree = ET.parse(
                xml_path
            )

            root = tree.getroot()

            print(
                f"[FAO DATASET PARSER] "
                f"Racine XML : {root.tag}"
            )

            return {
                "file": xml_path,
                "root": root
            }

        except Exception as e:

            print(
                f"❌ Erreur lecture "
                f"{xml_path.name} : {e}"
            )

            return None

    # ---------------------------------------------------------
    # PARSER TOUS LES DATASETS
    # ---------------------------------------------------------

    def parse_all(self):

        print("=" * 50)

        print(
            "[FAO DATASET PARSER] "
            "Analyse des datasets FAO"
        )

        print("=" * 50)

        # S'assurer que le dossier existe
        self.datasets_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            f"[FAO DATASET PARSER] "
            f"Dossier : {self.datasets_dir}"
        )

        # Rechercher les fichiers XML
        files = sorted(
            self.datasets_dir.glob(
                "*.xml"
            )
        )

        print(
            f"[FAO DATASET PARSER] "
            f"{len(files)} fichier(s) XML trouvé(s)."
        )

        # Aucun fichier
        if not files:

            print(
                "⚠️ Aucun dataset XML trouvé."
            )

            return []

        results = []

        # Parser chaque fichier
        for xml_file in files:

            result = self.parse_file(
                xml_file
            )

            if result is not None:

                results.append(
                    result
                )

        print(
            "=" * 50
        )

        print(
            f"[FAO DATASET PARSER] "
            f"{len(results)} dataset(s) analysé(s)."
        )

        print(
            "=" * 50
        )

        return results


# ---------------------------------------------------------
# TEST DIRECT DU PARSER
# ---------------------------------------------------------

if __name__ == "__main__":

    parser = FAODatasetParser()

    datasets = parser.parse_all()

    print(
        f"\nTotal : "
        f"{len(datasets)} dataset(s)"
    )

    for index, dataset in enumerate(
        datasets[:10],
        start=1
    ):

        print(
            f"{index}. "
            f"{dataset['file'].name}"
        )
