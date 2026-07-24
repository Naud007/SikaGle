from pathlib import Path

from app.knowledge_engine.connectors.registry import registry

# Charger les connecteurs
import app.knowledge_engine.connectors.fao


# =========================================================
# KNOWLEDGE ENGINE PRINCIPAL
# =========================================================

def run():
    """
    Lance le Knowledge Engine.

    1. Découvre les documents via les connecteurs.
    2. Télécharge les documents.
    """

    print("=" * 50)
    print("SikaGlé Knowledge Engine")
    print("=" * 50)

    for connector_class in registry.all():

        connector = connector_class()

        try:

            # -------------------------------------------------
            # 1. RECHERCHE DES DOCUMENTS
            # -------------------------------------------------

            documents = connector.discover()

            print(
                f"{connector.source_name} : "
                f"{len(documents)} document(s) trouvé(s)"
            )

            # -------------------------------------------------
            # 2. TÉLÉCHARGEMENT DES DOCUMENTS
            # -------------------------------------------------

            for document in documents:

                print(
                    f"Document : {document.title}"
                )

                try:

                    file_path = connector.download(
                        document
                    )

                    if (
                        file_path
                        and Path(file_path).exists()
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
# TEST TÉLÉCHARGEMENT FAO AGRIS ODS
# =========================================================

def test_fao_ods():

    print("=" * 50)
    print("SikaGlé - Test FAO AGRIS ODS")
    print("=" * 50)

    try:

        from app.knowledge_engine.connectors.fao_ods import (
            FAOODSDownloader
        )

        # -------------------------------------------------
        # 1. INITIALISER LE DOWNLOADER
        # -------------------------------------------------

        downloader = FAOODSDownloader()

        # -------------------------------------------------
        # 2. TÉLÉCHARGER LE CATALOGUE AGRIS
        # -------------------------------------------------

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
# TEST PARSER DU CATALOGUE AGRIS
# =========================================================

def test_fao_parser():

    print("=" * 50)
    print("SikaGlé - Test Parser FAO AGRIS")
    print("=" * 50)

    try:

        from app.knowledge_engine.connectors.fao_ods import (
            FAOODSDownloader
        )

        from app.knowledge_engine.parsers.fao_ods_parser import (
            FAOODSParser
        )

        # -------------------------------------------------
        # 1. TÉLÉCHARGER LE CATALOGUE AGRIS
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
        # 2. PARSER LE CATALOGUE
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
        # 3. AFFICHER LES 10 PREMIERS DATASETS
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
# TÉLÉCHARGEMENT DES DATASETS AGRIS
# =========================================================

def test_fao_datasets():

    print("=" * 50)
    print("SikaGlé - Téléchargement des datasets FAO")
    print("=" * 50)

    try:

        # -------------------------------------------------
        # 1. DOWNLOADER AGRIS
        # -------------------------------------------------

        from app.knowledge_engine.connectors.fao_ods import (
            FAOODSDownloader
        )

        # -------------------------------------------------
        # 2. PARSER DU CATALOGUE
        # -------------------------------------------------

        from app.knowledge_engine.parsers.fao_ods_parser import (
            FAOODSParser
        )

        # -------------------------------------------------
        # 3. TÉLÉCHARGEMENT DU CATALOGUE
        # -------------------------------------------------

        downloader = FAOODSDownloader()

        xml_path = downloader.download()

        if not xml_path:

            print(
                "❌ Impossible de télécharger "
                "le catalogue AGRIS."
            )

            return {
                "status": "error",
                "message": "Catalogue AGRIS indisponible"
            }

        # -------------------------------------------------
        # 4. PARSING DU CATALOGUE
        # -------------------------------------------------

        parser = FAOODSParser(
            xml_path
        )

        documents = parser.parse()

        print(
            f"[FAO DATASET] "
            f"{len(documents)} dataset(s) à télécharger."
        )

        # -------------------------------------------------
        # 5. DOSSIER DE DESTINATION
        # -------------------------------------------------

        datasets_dir = Path(
            "/app/knowledge/raw/fao/datasets"
        )

        datasets_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # -------------------------------------------------
        # 6. TÉLÉCHARGER LES 10 PREMIERS DATASETS
        # -------------------------------------------------

        downloaded_files = []

        for document in documents[:10]:

            try:

                # Pydantic HttpUrl -> str
                url = str(
                    document.url
                )

                # Nom du fichier
                filename = url.rstrip(
                    "/"
                ).split(
                    "/"
                )[-1]

                if not filename:

                    print(
                        f"⚠️ Nom de fichier "
                        f"impossible : {url}"
                    )

                    continue

                destination = (
                    datasets_dir
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

                # Télécharger le fichier
                import requests

                response = requests.get(
                    url,
                    timeout=120,
                    stream=True
                )

                response.raise_for_status()

                # Écriture du fichier
                with open(
                    destination,
                    "wb"
                ) as file:

                    for chunk in response.iter_content(
                        chunk_size=1024 * 1024
                    ):

                        if chunk:

                            file.write(
                                chunk
                            )

                print(
                    f"[FAO DATASET] "
                    f"Enregistré : "
                    f"{destination}"
                )

                print(
                    f"✅ Dataset téléchargé : "
                    f"{destination}"
                )

                downloaded_files.append(
                    destination
                )

            except Exception as e:

                print(
                    f"❌ Erreur téléchargement "
                    f"{document.url} : "
                    f"{e}"
                )

        # -------------------------------------------------
        # 7. RÉSULTAT
        # -------------------------------------------------

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
                str(file)
                for file in downloaded_files
            ]
        }

    except Exception as e:

        print(
            "❌ Erreur datasets FAO :",
            e
        )

        return {
            "status": "error",
            "message": str(e)
        }


# =========================================================
# TEST PARSER DES DATASETS FAO
# =========================================================

def test_fao_dataset_parser():

    print("=" * 50)
    print("SikaGlé - Test Parser des datasets FAO")
    print("=" * 50)

    try:

        from app.knowledge_engine.parsers.fao_dataset_parser import (
            FAODatasetParser
        )

        # -------------------------------------------------
        # 1. DOSSIER DES DATASETS
        # -------------------------------------------------

        datasets_dir = Path(
            "/app/knowledge/raw/fao/datasets"
        )

        # -------------------------------------------------
        # 2. VÉRIFIER LE DOSSIER
        # -------------------------------------------------

        if not datasets_dir.exists():

            print(
                "❌ Le dossier des datasets "
                "FAO n'existe pas."
            )

            return {
                "status": "error",
                "message": "Dossier datasets FAO introuvable"
            }

        # -------------------------------------------------
        # 3. INITIALISER LE PARSER
        # -------------------------------------------------

        parser = FAODatasetParser(
            datasets_dir
        )

        # -------------------------------------------------
        # 4. PARSER LES DATASETS
        # -------------------------------------------------

        datasets = parser.parse_all()

        # -------------------------------------------------
        # 5. RÉSULTAT
        # -------------------------------------------------

        print("=" * 50)

        print(
            "Résultat :",
            len(datasets),
            "dataset(s) analysé(s)"
        )

        print("=" * 50)

        return {
            "status": "success",
            "count": len(datasets)
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
