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
        "[KNOWLEDGE] "
        f"Dossier ODS : "
        f"{FAO_ODS_DIR}"
    )

    print(
        "[KNOWLEDGE] "
        f"Dossier datasets : "
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

    # -----------------------------------------------------
    # INITIALISER LES DOSSIERS
    # -----------------------------------------------------

    init_knowledge_directories()

    # -----------------------------------------------------
    # PARCOURIR LES CONNECTEURS ENREGISTRÉS
    # -----------------------------------------------------

    for connector_class in registry.all():

        connector = connector_class()

        try:

            # =================================================
            # 1. DÉCOUVERTE
            # =================================================

            documents = (
                connector.discover()
            )

            print(
                f"{connector.source_name} : "
                f"{len(documents)} document(s) trouvé(s)"
            )


            # =================================================
            # 2. TÉLÉCHARGEMENT
            # =================================================

            for document in documents:

                print(
                    "Document : "
                    f"{document.title}"
                )

                try:

                    file_path = (
                        connector.download(
                            document
                        )
                    )


                    # -------------------------------------------------
                    # VÉRIFICATION FICHIER
                    # -------------------------------------------------

                    if (
                        file_path
                        and
                        Path(
                            file_path
                        ).exists()
                    ):

                        print(
                            "✅ Téléchargé : "
                            f"{file_path}"
                        )

                    else:

                        print(
                            "⚠️ Aucun fichier "
                            "téléchargé."
                        )


                except Exception as e:

                    print(
                        "❌ Erreur téléchargement : "
                        f"{e}"
                    )


        except Exception as e:

            print(
                "❌ Erreur connecteur "
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

        # -------------------------------------------------
        # INITIALISER LES DOSSIERS
        # -------------------------------------------------

        init_knowledge_directories()


        # -------------------------------------------------
        # IMPORT DOWNLOADER
        # -------------------------------------------------

        from app.knowledge_engine.connectors.fao_ods import (
            FAOODSDownloader
        )


        # -------------------------------------------------
        # CRÉER LE DOWNLOADER
        # -------------------------------------------------

        downloader = (
            FAOODSDownloader()
        )


        # -------------------------------------------------
        # TÉLÉCHARGER LE CATALOGUE AGRIS
        # -------------------------------------------------

        file_path = (
            downloader.download()
        )


        # -------------------------------------------------
        # VÉRIFIER LE FICHIER
        # -------------------------------------------------

        if (
            file_path
            and
            Path(
                file_path
            ).exists()
        ):

            print(
                "✅ Catalogue AGRIS enregistré : "
                f"{file_path}"
            )

            return {

                "status":
                    "success",

                "file":
                    str(
                        file_path
                    )

            }


        print(
            "⚠️ Aucun fichier AGRIS reçu."
        )

        return {

            "status":
                "warning",

            "message":
                "Aucun fichier AGRIS reçu"

        }


    except Exception as e:

        print(
            "❌ Erreur FAO AGRIS :",
            e
        )

        return {

            "status":
                "error",

            "message":
                str(
                    e
                )

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

        # -------------------------------------------------
        # INITIALISATION
        # -------------------------------------------------

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

        downloader = (
            FAOODSDownloader()
        )

        xml_path = (
            downloader.download()
        )


        # -------------------------------------------------
        # VÉRIFIER LE FICHIER
        # -------------------------------------------------

        if (
            not xml_path
            or
            not Path(
                xml_path
            ).exists()
        ):

            print(
                "❌ Téléchargement AGRIS impossible."
            )

            return {

                "status":
                    "error",

                "message":
                    "Téléchargement AGRIS impossible"

            }


        # -------------------------------------------------
        # 2. PARSER AGRIS ODS
        # -------------------------------------------------

        parser = (
            FAOODSParser(
                xml_path
            )
        )

        documents = (
            parser.parse()
        )


        print("=" * 50)

        print(
            "Résultat du parsing : "
            f"{len(documents)} document(s)"
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

            "status":
                "success",

            "count":
                len(
                    documents
                )

        }


    except Exception as e:

        print(
            "❌ Erreur parser FAO :",
            e
        )

        return {

            "status":
                "error",

            "message":
                str(
                    e
                )

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

        # =================================================
        # INITIALISATION
        # =================================================

        init_knowledge_directories()


        # =================================================
        # 1. DOWNLOADER AGRIS ODS
        # =================================================

        from app.knowledge_engine.connectors.fao_ods import (
            FAOODSDownloader
        )

        ods_downloader = (
            FAOODSDownloader()
        )


        # =================================================
        # 2. TÉLÉCHARGER LE CATALOGUE AGRIS
        # =================================================

        ods_path = (
            ods_downloader.download()
        )


        if (
            not ods_path
            or
            not Path(
                ods_path
            ).exists()
        ):

            print(
                "❌ Impossible de télécharger "
                "AGRIS ODS."
            )

            return {

                "status":
                    "error",

                "message":
                    "AGRIS ODS indisponible"

            }


        print(
            "✅ Catalogue AGRIS disponible : "
            f"{ods_path}"
        )


        # =================================================
        # 3. PARSER LE CATALOGUE AGRIS
        # =================================================

        from app.knowledge_engine.parsers.fao_ods_parser import (
            FAOODSParser
        )

        parser = (
            FAOODSParser(
                ods_path
            )
        )

        documents = (
            parser.parse()
        )


        print(
            "[FAO DATASET] "
            f"{len(documents)} dataset(s) "
            "découvert(s)."
        )


        # =================================================
        # 4. LIMITER LE NOMBRE
        # =================================================

        documents_to_download = (
            documents[:limit]
        )


        print(
            "[FAO DATASET] "
            f"{len(documents_to_download)} dataset(s) "
            "sélectionné(s)."
        )


        # =================================================
        # 5. DOWNLOADER DATASETS
        # =================================================

        from app.knowledge_engine.connectors.fao_datasets import (
            FAODatasetsDownloader
        )

        dataset_downloader = (
            FAODatasetsDownloader()
        )


        downloaded_files = []


        # =================================================
        # 6. TÉLÉCHARGER CHAQUE DATASET
        # =================================================

        for document in (
            documents_to_download
        ):

            try:

                # -----------------------------------------
                # URL
                # -----------------------------------------

                url = str(
                    document.url
                ).strip()


                if not url:

                    print(
                        "⚠️ Dataset sans URL : "
                        f"{document.title}"
                    )

                    continue


                # -----------------------------------------
                # NOM DU FICHIER
                # -----------------------------------------

                filename = (
                    url
                    .rstrip("/")
                    .split("/")
                    [-1]
                )


                if not filename:

                    filename = (
                        "dataset.xml"
                    )


                # -----------------------------------------
                # TÉLÉCHARGEMENT
                # -----------------------------------------

                output_path = (
                    dataset_downloader.download(
                        url=url,
                        filename=filename
                    )
                )


                # -----------------------------------------
                # VÉRIFICATION
                # -----------------------------------------

                if (
                    output_path
                    and
                    Path(
                        output_path
                    ).exists()
                ):

                    downloaded_files.append(
                        Path(
                            output_path
                        )
                    )

                    print(
                        "✅ Dataset disponible : "
                        f"{output_path}"
                    )

                else:

                    print(
                        "⚠️ Dataset non enregistré : "
                        f"{filename}"
                    )


            except Exception as e:

                print(
                    "❌ Erreur téléchargement "
                    f"{document.url} : "
                    f"{e}"
                )


        # =================================================
        # 7. RÉSULTAT
        # =================================================

        print("=" * 50)

        print(
            "✅ Téléchargement terminé : "
            f"{len(downloaded_files)} fichier(s)"
        )

        print("=" * 50)


        return {

            "status":
                "success",

            "count":
                len(
                    downloaded_files
                ),

            "files": [

                str(
                    path
                )

                for path
                in downloaded_files

            ]

        }


    except Exception as e:

        print(
            "❌ Erreur téléchargement "
            f"datasets FAO : "
            f"{e}"
        )

        return {

            "status":
                "error",

            "message":
                str(
                    e
                )

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

        # =================================================
        # 1. INITIALISATION
        # =================================================

        init_knowledge_directories()


        # =================================================
        # 2. CHERCHER LES DATASETS LOCAUX
        # =================================================

        dataset_files = sorted(
            FAO_DATASETS_DIR.glob(
                "*.xml"
            )
        )


        print(
            "[FAO DATASET PARSER] "
            f"{len(dataset_files)} fichier(s) XML "
            "trouvé(s)."
        )


        # =================================================
        # 3. TÉLÉCHARGEMENT AUTOMATIQUE SI NÉCESSAIRE
        # =================================================

        if not dataset_files:

            print(
                "⚠️ Aucun dataset FAO local trouvé."
            )

            print(
                "➡️ Téléchargement automatique "
                "des datasets..."
            )


            result = (
                download_fao_datasets(
                    limit=limit
                )
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


        # =================================================
        # 4. VÉRIFICATION FINALE
        # =================================================

        if not dataset_files:

            return {

                "status":
                    "error",

                "message":
                    "Aucun dataset XML disponible "
                    "après téléchargement."

            }


        print(
            "[FAO DATASET PARSER] "
            f"{len(dataset_files)} dataset(s) "
            "disponible(s) pour parsing."
        )


        # =================================================
        # 5. IMPORT PARSER
        # =================================================

        from app.knowledge_engine.parsers.fao_dataset_parser import (
            FAODatasetParser
        )


        parser = (
            FAODatasetParser()
        )


        parsed_count = 0

        all_documents = []


        # =================================================
        # 6. PARSER LES DATASETS
        # =================================================

        for dataset_file in (
            dataset_files[:limit]
        ):

            print("=" * 50)

            print(
                "[FAO DATASET PARSER] "
                f"Fichier : "
                f"{dataset_file.name}"
            )


            try:

                # -----------------------------------------
                # PARSER LE FICHIER XML
                # -----------------------------------------

                documents = (
                    parser.parse(
                        dataset_file
                    )
                )


                # -----------------------------------------
                # AJOUTER LES DOCUMENTS
                # -----------------------------------------

                all_documents.extend(
                    documents
                )


                print(
                    "✅ "
                    f"{len(documents)} document(s) "
                    "trouvé(s)"
                )


                parsed_count += (
                    len(
                        documents
                    )
                )


                # -----------------------------------------
                # AFFICHER LES 3 PREMIERS DOCUMENTS
                # -----------------------------------------

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
                    "❌ Erreur parsing "
                    f"{dataset_file.name} : "
                    f"{e}"
                )


        # =================================================
        # 7. VÉRIFIER LE RÉSULTAT DU PARSING
        # =================================================

        if not all_documents:

            print(
                "⚠️ Aucun document n'a été extrait "
                "des datasets FAO."
            )

            return {

                "status":
                    "warning",

                "datasets":
                    len(
                        dataset_files[:limit]
                    ),

                "documents_parsed":
                    0,

                "documents_added":
                    0,

                "documents_total":
                    0

            }


        # =================================================
        # 8. SAUVEGARDE DANS DOCUMENT STORE
        # =================================================

        print("=" * 50)

        print(
            "[DOCUMENT STORE] "
            "Sauvegarde des documents FAO..."
        )


        from app.knowledge_engine.storage.document_store import (
            DocumentStore
        )


        document_store = (
            DocumentStore()
        )


        store_result = (
            document_store.add_documents(
                all_documents
            )
        )


        print(
            "[DOCUMENT STORE] "
            f"{store_result['added']} "
            "document(s) ajouté(s)."
        )


        print(
            "[DOCUMENT STORE] "
            f"{store_result['total']} "
            "document(s) au total."
        )


        print(
            "[DOCUMENT STORE] "
            f"Fichier : "
            f"{store_result['file']}"
        )


        # =================================================
        # 9. RÉSULTAT FINAL
        # =================================================

        print("=" * 50)

        print(
            "✅ Parsing terminé."
        )


        print(
            "Documents analysés : "
            f"{parsed_count}"
        )


        print(
            "Documents ajoutés : "
            f"{store_result['added']}"
        )


        print(
            "Documents dans la base : "
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
                str(
                    e
                )

        }


# =========================================================
# EXÉCUTION DIRECTE
# =========================================================

if __name__ == "__main__":

    run()
