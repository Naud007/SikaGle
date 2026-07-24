from pathlib import Path

from app.knowledge_engine.connectors.registry import registry

# Charger les connecteurs
import app.knowledge_engine.connectors.fao


# =========================================================
# CHEMINS
# =========================================================

BASE_DIR = Path("/app/knowledge")

FAO_RAW_DIR = BASE_DIR / "raw" / "fao"
FAO_ODS_DIR = FAO_RAW_DIR / "ods"
FAO_DATASETS_DIR = FAO_RAW_DIR / "datasets"


# =========================================================
# INITIALISATION DES DOSSIERS
# =========================================================

def init_knowledge_directories():

    FAO_ODS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    FAO_DATASETS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        f"[KNOWLEDGE] Dossier ODS : "
        f"{FAO_ODS_DIR}"
    )

    print(
        f"[KNOWLEDGE] Dossier datasets : "
        f"{FAO_DATASETS_DIR}"
    )


# =========================================================
# KNOWLEDGE ENGINE PRINCIPAL
# =========================================================

def run():

    print("=" * 50)
    print("SikaGlé Knowledge Engine")
    print("=" * 50)

    # Créer les dossiers nécessaires
    init_knowledge_directories()

    # Parcourir tous les connecteurs enregistrés
    for connector_class in registry.all():

        connector = connector_class()

        try:

            # -------------------------------------------------
            # 1. DÉCOUVERTE
            # -------------------------------------------------

            documents = connector.discover()

            print(
                f"{connector.source_name} : "
                f"{len(documents)} document(s) trouvé(s)"
            )

            # -------------------------------------------------
            # 2. TÉLÉCHARGEMENT
            # -------------------------------------------------

            for document in documents:

                print(
                    f"Document : "
                    f"{document.title}"
                )

                try:

                    file_path = connector.download(
                        document
                    )

                    if (
                        file_path
                        and file_path.exists()
                    ):

                        print(
                            f"✅ Téléchargé : "
                            f"{file_path}"
                        )

                    else:

                        print(
                            "⚠️ Aucun fichier "
                            "téléchargé."
                        )

                except Exception as e:

                    print(
                        f"❌ Erreur téléchargement : "
                        f"{e}"
                    )

        except Exception as e:

            print(
                f"❌ Erreur connecteur "
                f"{connector.source_name} : "
                f"{e}"
            )


# =========================================================
# TEST TÉLÉCHARGEMENT AGRIS ODS
# =========================================================

def test_fao_ods():

    print("=" * 50)
    print("SikaGlé - Test FAO AGRIS ODS")
    print("=" * 50)

    try:

        # Créer les dossiers
        init_knowledge_directories()

        # Import local
        from app.knowledge_engine.connectors.fao_ods import (
            FAOODSDownloader
        )

        downloader = FAOODSDownloader()

        file_path = downloader.download()

        if file_path:

            print(
                "✅ Réponse AGRIS reçue :",
                file_path
            )

            return {
                "status": "success",
                "file": str(file_path)
            }

        print(
            "⚠️ Aucune réponse reçue."
        )

        return {
            "status": "warning",
            "message": "Aucune réponse reçue"
        }

    except Exception as e:

        print(
            "❌ Erreur FAO AGRIS :",
            e
        )

        return {
            "status": "error",
            "message": str(e)
        }


# =========================================================
# TEST PARSER AGRIS ODS
# =========================================================

def test_fao_parser():

    print("=" * 50)
    print("SikaGlé - Test Parser FAO AGRIS")
    print("=" * 50)

    try:

        init_knowledge_directories()

        from app.knowledge_engine.connectors.fao_ods import (
            FAOODSDownloader
        )

        from app.knowledge_engine.parsers.fao_ods_parser import (
            FAOODSParser
        )

        # -------------------------------------------------
        # 1. Télécharger AGRIS ODS
        # -------------------------------------------------

        downloader = FAOODSDownloader()

        xml_path = downloader.download()

        if not xml_path:

            print(
                "❌ Téléchargement AGRIS impossible."
            )

            return {
                "status": "error",
                "message": "Téléchargement AGRIS impossible"
            }

        # -------------------------------------------------
        # 2. Parser AGRIS ODS
        # -------------------------------------------------

        parser = FAOODSParser(
            xml_path
        )

        documents = parser.parse()

        print("=" * 50)

        print(
            "Résultat du parsing :",
            len(documents),
            "document(s)"
        )

        print("=" * 50)

        # -------------------------------------------------
        # 3. Afficher les 10 premiers datasets
        # -------------------------------------------------

        for index, document in enumerate(
            documents[:10],
            start=1
        ):

            print(
                f"\nDocument {index}"
            )

            print(
                "Titre :",
                document.title
            )

            print(
                "URL :",
                document.url
            )

            if hasattr(
                document,
                "description"
            ):

                print(
                    "Description :",
                    document.description
                )

        return {
            "status": "success",
            "count": len(documents)
        }

    except Exception as e:

        print(
            "❌ Erreur parser FAO :",
            e
        )

        return {
            "status": "error",
            "message": str(e)
        }


# =========================================================
# TÉLÉCHARGEMENT DES DATASETS FAO
# =========================================================

def download_fao_datasets(
    limit=10
):

    print("=" * 50)
    print("SikaGlé - Téléchargement des datasets FAO")
    print("=" * 50)

    try:

        init_knowledge_directories()

        # -------------------------------------------------
        # 1. Télécharger le catalogue AGRIS
        # -------------------------------------------------

        from app.knowledge_engine.connectors.fao_ods import (
            FAOODSDownloader
        )

        downloader = FAOODSDownloader()

        ods_path = downloader.download()

        if not ods_path:

            print(
                "❌ Impossible de télécharger "
                "AGRIS ODS."
            )

            return {
                "status": "error",
                "message": "AGRIS ODS indisponible"
            }

        # -------------------------------------------------
        # 2. Parser le catalogue
        # -------------------------------------------------

        from app.knowledge_engine.parsers.fao_ods_parser import (
            FAOODSParser
        )

        parser = FAOODSParser(
            ods_path
        )

        documents = parser.parse()

        print(
            f"[FAO DATASET] "
            f"{len(documents)} dataset(s) à télécharger."
        )

        # -------------------------------------------------
        # 3. Limiter le nombre
        # -------------------------------------------------

        documents_to_download = documents[:limit]

        downloaded_files = []

        # -------------------------------------------------
        # 4. Télécharger chaque dataset
        # -------------------------------------------------

        import requests

        for document in documents_to_download:

            try:

                # Conversion Pydantic URL -> str
                url = str(
                    document.url
                )

                filename = url.split(
                    "/"
                )[-1]

                if not filename:

                    filename = (
                        "dataset.xml"
                    )

                output_path = (
                    FAO_DATASETS_DIR
                    / filename
                )

                print(
                    f"[FAO DATASET] "
                    f"Téléchargement : "
                    f"{filename}"
                )

                print(
                    f"[FAO DATASET] URL : "
                    f"{url}"
                )

                # Éviter de télécharger
                # deux fois le même fichier
                if output_path.exists():

                    print(
                        f"⚠️ Déjà présent : "
                        f"{output_path}"
                    )

                    downloaded_files.append(
                        output_path
                    )

                    continue

                response = requests.get(
                    url,
                    timeout=120
                )

                response.raise_for_status()

                output_path.write_bytes(
                    response.content
                )

                print(
                    f"[FAO DATASET] "
                    f"Enregistré : "
                    f"{output_path}"
                )

                print(
                    f"✅ Dataset téléchargé : "
                    f"{output_path}"
                )

                downloaded_files.append(
                    output_path
                )

            except Exception as e:

                print(
                    f"❌ Erreur téléchargement "
                    f"{document.url} : "
                    f"{e}"
                )

        print("=" * 50)

        print(
            f"✅ Téléchargement terminé : "
            f"{len(downloaded_files)} fichier(s)"
        )

        print("=" * 50)

        return {
            "status": "success",
            "count": len(downloaded_files),
            "files": [
                str(path)
                for path in downloaded_files
            ]
        }

    except Exception as e:

        print(
            "❌ Erreur téléchargement "
            f"datasets FAO : {e}"
        )

        return {
            "status": "error",
            "message": str(e)
        }


# =========================================================
# TEST PARSER DES DATASETS FAO
# =========================================================

def test_fao_dataset_parser(
    limit=10
):

    print("=" * 50)
    print("SikaGlé - Test Parser Datasets FAO")
    print("=" * 50)

    try:

        init_knowledge_directories()

        # -------------------------------------------------
        # 1. Vérifier si les datasets existent
        # -------------------------------------------------

        dataset_files = list(
            FAO_DATASETS_DIR.glob(
                "*.xml"
            )
        )

        # -------------------------------------------------
        # 2. Si aucun dataset :
        #    les télécharger automatiquement
        # -------------------------------------------------

        if not dataset_files:

            print(
                "⚠️ Aucun dataset FAO local trouvé."
            )

            print(
                "➡️ Téléchargement automatique "
                "des datasets..."
            )

            result = download_fao_datasets(
                limit=limit
            )

            if (
                result.get("status")
                != "success"
            ):

                return result

            dataset_files = list(
                FAO_DATASETS_DIR.glob(
                    "*.xml"
                )
            )

        # -------------------------------------------------
        # 3. Import du parser
        # -------------------------------------------------

        from app.knowledge_engine.parsers.fao_dataset_parser import (
            FAODatasetParser
        )

        parser = FAODatasetParser()

        parsed_count = 0

        # -------------------------------------------------
        # 4. Parser les datasets
        # -------------------------------------------------

        for dataset_file in dataset_files[:limit]:

            print("=" * 50)

            print(
                f"[FAO DATASET PARSER] "
                f"Fichier : "
                f"{dataset_file.name}"
            )

            try:

                documents = parser.parse(
                    dataset_file
                )

                print(
                    f"✅ "
                    f"{len(documents)} document(s) "
                    f"trouvé(s)"
                )

                parsed_count += len(
                    documents
                )

                # Afficher les 3 premiers
                # documents du dataset

                for index, document in enumerate(
                    documents[:3],
                    start=1
                ):

                    print(
                        f"\nDocument {index}"
                    )

                    print(
                        "Titre :",
                        document.title
                    )

                    print(
                        "URL :",
                        document.url
                    )

            except Exception as e:

                print(
                    f"❌ Erreur parsing "
                    f"{dataset_file.name} : "
                    f"{e}"
                )

        print("=" * 50)

        print(
            f"✅ Parsing terminé."
        )

        print(
            f"Documents analysés : "
            f"{parsed_count}"
        )

        print("=" * 50)

        return {
            "status": "success",
            "datasets": len(
                dataset_files[:limit]
            ),
            "documents": parsed_count
        }

    except Exception as e:

        print(
            "❌ Erreur parser datasets FAO :",
            e
        )

        return {
            "status": "error",
            "message": str(e)
        }


# =========================================================
# EXÉCUTION DIRECTE
# =========================================================

if __name__ == "__main__":

    run()
