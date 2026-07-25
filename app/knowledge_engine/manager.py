from pathlib import Path

from app.knowledge_engine.config import config
from app.knowledge_engine.connectors.registry import registry


# =========================================================
# CHARGEMENT DES CONNECTEURS
# =========================================================

import app.knowledge_engine.connectors.fao


# =========================================================
# CHEMINS
# =========================================================

FAO_RAW_DIR = (
    config.raw_dir
    / "fao"
)

FAO_ODS_DIR = (
    FAO_RAW_DIR
    / "ods"
)

FAO_DATASETS_DIR = (
    FAO_RAW_DIR
    / "datasets"
)


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

    print(
        "SikaGlé Knowledge Engine"
    )

    print("=" * 50)

    # Initialiser les dossiers
    init_knowledge_directories()

    # Parcourir les connecteurs enregistrés
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

    print(
        "SikaGlé - Test FAO AGRIS ODS"
    )

    print("=" * 50)

    try:

        # Créer les dossiers
        init_knowledge_directories()

        # Import local
        from app.knowledge_engine.connectors.fao_ods import (
            FAOODSDownloader
        )

        # Downloader
        downloader = FAOODSDownloader()

        # Télécharger le catalogue AGRIS
        file_path = downloader.download()

        if file_path:

            print(
                "✅ Réponse AGRIS reçue :",
                file_path
            )

            return {
                "status": "success",
                "file": str(
                    file_path
                )
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

    print(
        "SikaGlé - Test Parser FAO AGRIS"
    )

    print("=" * 50)

    try:

        init_knowledge_directories()

        # -------------------------------------------------
        # IMPORTS
        # -------------------------------------------------

        from app.knowledge_engine.connectors.fao_ods import (
            FAOODSDownloader
        )

        from app.knowledge_engine.parsers.fao_ods_parser import (
            FAOODSParser
        )

        # -------------------------------------------------
        # 1. TÉLÉCHARGER AGRIS ODS
        # -------------------------------------------------

        downloader = FAOODSDownloader()

        xml_path = downloader.download()

        if not xml_path:

            print(
                "❌ Téléchargement AGRIS impossible."
            )

            return {
                "status": "error",
                "message": (
                    "Téléchargement AGRIS impossible"
                )
            }

        # -------------------------------------------------
        # 2. PARSER AGRIS ODS
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
            "count": len(
                documents
            )
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

    print(
        "SikaGlé - Téléchargement des datasets FAO"
    )

    print("=" * 50)

    try:

        init_knowledge_directories()

        # -------------------------------------------------
        # 1. TÉLÉCHARGER LE CATALOGUE AGRIS
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
                "message": (
                    "AGRIS ODS indisponible"
                )
            }

        # -------------------------------------------------
        # 2. PARSER LE CATALOGUE AGRIS
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
        # 3. LIMITER LE NOMBRE DE DATASETS
        # -------------------------------------------------

        documents_to_download = (
            documents[:limit]
        )

        # -------------------------------------------------
        # 4. UTILISER LE DOWNLOADER CENTRALISÉ
        # -------------------------------------------------

        from app.knowledge_engine.connectors.fao_datasets import (
            FAODatasetsDownloader
        )

        dataset_downloader = (
            FAODatasetsDownloader()
        )

        downloaded_files = []

        # -------------------------------------------------
        # 5. TÉLÉCHARGER LES DATASETS
        # -------------------------------------------------

        for document in documents_to_download:

            try:

                # Conversion Pydantic URL -> str
                url = str(
                    document.url
                ).strip()

                # Vérification URL
                if not url:

                    print(
                        "⚠️ Dataset sans URL : "
                        f"{document.title}"
                    )

                    continue

                # Récupérer le nom du fichier
                filename = (
                    url.rstrip("/")
                    .split("/")
                    [-1]
                )

                if not filename:

                    filename = (
                        "dataset.xml"
                    )

                # -------------------------------------------------
                # TÉLÉCHARGEMENT VIA LE DOWNLOADER
                # -------------------------------------------------

                output_path = (
                    dataset_downloader.download(
                        url=url,
                        filename=filename
                    )
                )

                if output_path:

                    downloaded_files.append(
                        output_path
                    )

                    print(
                        f"✅ Dataset téléchargé : "
                        f"{output_path}"
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
            "count": len(
                downloaded_files
            ),
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
# + SAUVEGARDE DOCUMENTS
# =========================================================

def test_fao_dataset_parser(
    limit=10
):

    print("=" * 50)

    print(
        "SikaGlé - Test Parser Datasets FAO"
    )

    print("=" * 50)

    try:

        # -------------------------------------------------
        # INITIALISATION
        # -------------------------------------------------

        init_knowledge_directories()

        # -------------------------------------------------
        # 1. CHERCHER LES DATASETS LOCAUX
        # -------------------------------------------------

        dataset_files = sorted(
            FAO_DATASETS_DIR.glob(
                "*.xml"
            )
        )

        print(
            f"[FAO DATASET PARSER] "
            f"{len(dataset_files)} fichier(s) XML trouvé(s)."
        )

        # -------------------------------------------------
        # 2. SI AUCUN DATASET :
        #    TÉLÉCHARGEMENT AUTOMATIQUE
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
                result.get(
                    "status"
                )
                != "success"
            ):

                return result

            dataset_files = sorted(
                FAO_DATASETS_DIR.glob(
                    "*.xml"
                )
            )

        # -------------------------------------------------
        # 3. VÉRIFIER UNE DEUXIÈME FOIS
        # -------------------------------------------------

        if not dataset_files:

            return {

                "status":
                    "error",

                "message":
                    "Aucun dataset XML disponible "
                    "après téléchargement."

            }

        # -------------------------------------------------
        # 4. IMPORT DU PARSER
        # -------------------------------------------------

        from app.knowledge_engine.parsers.fao_dataset_parser import (
            FAODatasetParser
        )

        # -------------------------------------------------
        # 5. INITIALISER LE PARSER
        # -------------------------------------------------

        parser = FAODatasetParser()

        parsed_count = 0

        all_documents = []

        # -------------------------------------------------
        # 6. PARSER LES DATASETS
        # -------------------------------------------------

        for dataset_file in dataset_files[:limit]:

            print("=" * 50)

            print(
                f"[FAO DATASET PARSER] "
                f"Fichier : "
                f"{dataset_file.name}"
            )

            try:

                # Parser le dataset
                documents = parser.parse(
                    dataset_file
                )

                # Ajouter les documents
                # à la collection globale

                all_documents.extend(
                    documents
                )

                print(
                    f"✅ "
                    f"{len(documents)} document(s) "
                    f"trouvé(s)"
                )

                parsed_count += len(
                    documents
                )

                # -------------------------------------------------
                # AFFICHER LES 3 PREMIERS DOCUMENTS
                # -------------------------------------------------

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

        # =================================================
        # 7. SAUVEGARDE DANS DOCUMENT STORE
        # =================================================

        print("=" * 50)

        print(
            "[DOCUMENT STORE] "
            "Sauvegarde des documents FAO..."
        )

        from app.knowledge_engine.storage.document_store import (
            DocumentStore
        )

        document_store = DocumentStore()

        store_result = (
            document_store.add_documents(
                all_documents
            )
        )

        print(
            f"[DOCUMENT STORE] "
            f"{store_result['added']} "
            f"document(s) ajouté(s)."
        )

        print(
            f"[DOCUMENT STORE] "
            f"{store_result['total']} "
            f"document(s) au total."
        )

        print(
            f"[DOCUMENT STORE] "
            f"Fichier : "
            f"{store_result['file']}"
        )

        # =================================================
        # 8. RÉSULTAT FINAL
        # =================================================

        print("=" * 50)

        print(
            "✅ Parsing terminé."
        )

        print(
            f"Documents analysés : "
            f"{parsed_count}"
        )

        print(
            f"Documents ajoutés : "
            f"{store_result['added']}"
        )

        print(
            f"Documents dans la base : "
            f"{store_result['total']}"
        )

        print("=" * 50)

        return {

            "status":
                "success",

            "datasets":
                len(
                    dataset_files[:limit]
                ),

            "documents_parsed":
                parsed_count,

            "documents_added":
                store_result[
                    "added"
                ],

            "documents_total":
                store_result[
                    "total"
                ],

            "storage_file":
                store_result[
                    "file"
                ]

        }

    except Exception as e:

        print(
            "❌ Erreur parser datasets FAO :",
            e
        )

        return {

            "status":
                "error",

            "message":
                str(e)

        }


# =========================================================
# EXÉCUTION DIRECTE
# =========================================================

if __name__ == "__main__":

    run()
