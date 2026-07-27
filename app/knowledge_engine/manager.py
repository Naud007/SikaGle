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
        f"Dossier ODS : {FAO_ODS_DIR}"
    )

    print(
        "[KNOWLEDGE] "
        f"Dossier datasets : {FAO_DATASETS_DIR}"
    )


# =========================================================
# KNOWLEDGE ENGINE PRINCIPAL
# =========================================================

def run():

    print("=" * 50)
    print("SikaGlé Knowledge Engine")
    print("=" * 50)

    init_knowledge_directories()

    for connector_class in registry.all():

        connector = connector_class()

        try:

            documents = connector.discover()

            print(
                f"{connector.source_name} : "
                f"{len(documents)} document(s) trouvé(s)"
            )

            for document in documents:

                print(
                    f"Document : {document.title}"
                )

                try:

                    result = connector.download(
                        document
                    )

                    if result:

                        print(
                            "✅ Téléchargement effectué."
                        )

                    else:

                        print(
                            "⚠️ Aucun résultat."
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
    print("SikaGlé - Test FAO AGRIS ODS")
    print("=" * 50)

    try:

        from app.knowledge_engine.connectors.fao_ods import (
            FAOODSDownloader
        )

        downloader = FAOODSDownloader()

        result = downloader.download()

        if not result:

            return {
                "status": "warning",
                "message": "Aucune donnée AGRIS reçue"
            }

        # -------------------------------------------------
        # ANCIEN FORMAT : PATH
        # -------------------------------------------------

        if isinstance(
            result,
            (str, Path)
        ):

            return {
                "status": "success",
                "mode": "file",
                "file": str(result)
            }

        # -------------------------------------------------
        # NOUVEAU FORMAT : MÉMOIRE
        # -------------------------------------------------

        if isinstance(
            result,
            dict
        ):

            content = result.get(
                "content",
                b""
            )

            return {
                "status": "success",
                "mode": "memory",
                "filename": result.get(
                    "filename"
                ),
                "url": result.get(
                    "url"
                ),
                "size": len(content)
            }

        return {
            "status": "error",
            "message": (
                "Format retourné par "
                "FAOODSDownloader non reconnu."
            )
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

        from app.knowledge_engine.connectors.fao_ods import (
            FAOODSDownloader
        )

        from app.knowledge_engine.parsers.fao_ods_parser import (
            FAOODSParser
        )

        downloader = FAOODSDownloader()

        ods_result = downloader.download()

        if not ods_result:

            return {
                "status": "error",
                "message": "Téléchargement AGRIS impossible"
            }

        # -------------------------------------------------
        # FORMAT FICHIER
        # -------------------------------------------------

        if isinstance(
            ods_result,
            (str, Path)
        ):

            parser = FAOODSParser(
                ods_result
            )

            documents = parser.parse()

        # -------------------------------------------------
        # FORMAT MÉMOIRE
        # -------------------------------------------------

        elif isinstance(
            ods_result,
            dict
        ):

            content = ods_result.get(
                "content"
            )

            if not content:

                return {
                    "status": "error",
                    "message": (
                        "Le catalogue AGRIS "
                        "ne contient aucune donnée XML."
                    )
                }

            # Le parser ODS actuel peut encore
            # nécessiter un fichier.
            # Cette branche sera adaptée séparément.

            return {
                "status": "warning",
                "message": (
                    "Catalogue AGRIS reçu en mémoire. "
                    "Le parser ODS doit être adapté "
                    "au mode mémoire."
                ),
                "filename": ods_result.get(
                    "filename"
                ),
                "size": len(content)
            }

        else:

            return {
                "status": "error",
                "message": (
                    "Format AGRIS ODS non reconnu."
                )
            }

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
    print(
        "SikaGlé - Téléchargement des datasets FAO"
    )
    print("=" * 50)

    try:

        # =================================================
        # 1. TÉLÉCHARGER LE CATALOGUE AGRIS
        # =================================================

        from app.knowledge_engine.connectors.fao_ods import (
            FAOODSDownloader
        )

        ods_downloader = FAOODSDownloader()

        ods_result = ods_downloader.download()

        if not ods_result:

            return {
                "status": "error",
                "message": "AGRIS ODS indisponible"
            }

        # =================================================
        # 2. PARSER LE CATALOGUE AGRIS
        # =================================================

        from app.knowledge_engine.parsers.fao_ods_parser import (
            FAOODSParser
        )

        # -------------------------------------------------
        # FORMAT ACTUEL DU ODS : FICHIER
        # -------------------------------------------------

        if isinstance(
            ods_result,
            (str, Path)
        ):

            ods_parser = FAOODSParser(
                ods_result
            )

            documents = ods_parser.parse()

        # -------------------------------------------------
        # FORMAT FUTUR : MÉMOIRE
        # -------------------------------------------------

        elif isinstance(
            ods_result,
            dict
        ):

            ods_content = ods_result.get(
                "content"
            )

            if not ods_content:

                return {
                    "status": "error",
                    "message": (
                        "Le catalogue AGRIS "
                        "est vide."
                    )
                }

            return {
                "status": "error",
                "message": (
                    "Le catalogue AGRIS est maintenant "
                    "en mémoire mais FAOODSParser "
                    "n'est pas encore adapté."
                )
            }

        else:

            return {
                "status": "error",
                "message": (
                    "Format du catalogue AGRIS "
                    "non reconnu."
                )
            }

        print(
            "[FAO DATASET] "
            f"{len(documents)} dataset(s) découvert(s)."
        )

        documents_to_download = (
            documents[:limit]
        )

        # =================================================
        # 3. DOWNLOADER LES DATASETS
        # =================================================

        from app.knowledge_engine.connectors.fao_datasets import (
            FAODatasetsDownloader
        )

        dataset_downloader = (
            FAODatasetsDownloader()
        )

        datasets = []

        # =================================================
        # 4. TÉLÉCHARGEMENT EN MÉMOIRE
        # =================================================

        for document in documents_to_download:

            try:

                url = str(
                    document.url
                ).strip()

                if not url:

                    print(
                        "⚠️ Dataset sans URL : "
                        f"{document.title}"
                    )

                    continue

                filename = (
                    url
                    .rstrip("/")
                    .split("/")[-1]
                )

                if not filename:

                    filename = "dataset.xml"

                dataset = (
                    dataset_downloader.download(
                        url=url,
                        filename=filename
                    )
                )

                if not isinstance(
                    dataset,
                    dict
                ):

                    print(
                        "⚠️ Format dataset incorrect : "
                        f"{filename}"
                    )

                    continue

                content = dataset.get(
                    "content"
                )

                if not content:

                    print(
                        "⚠️ Dataset vide : "
                        f"{filename}"
                    )

                    continue

                datasets.append(
                    dataset
                )

                print(
                    "✅ Dataset chargé en mémoire : "
                    f"{filename} "
                    f"({len(content)} octets)"
                )

            except Exception as e:

                print(
                    "❌ Erreur dataset : "
                    f"{e}"
                )

        # =================================================
        # 5. RÉSULTAT
        # =================================================

        return {
            "status": "success",

            "count": len(
                datasets
            ),

            "datasets": [
                {
                    "filename": dataset.get(
                        "filename"
                    ),

                    "url": dataset.get(
                        "url"
                    ),

                    "size": len(
                        dataset.get(
                            "content",
                            b""
                        )
                    )
                }

                for dataset in datasets
            ]
        }

    except Exception as e:

        print(
            "❌ Erreur téléchargement datasets FAO :",
            e
        )

        return {
            "status": "error",
            "message": str(e)
        }


# =========================================================
# TEST PARSER DES DATASETS FAO
# MODE 100 % MÉMOIRE
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
        # 1. CATALOGUE AGRIS
        # =================================================

        from app.knowledge_engine.connectors.fao_ods import (
            FAOODSDownloader
        )

        from app.knowledge_engine.parsers.fao_ods_parser import (
            FAOODSParser
        )

        ods_downloader = FAOODSDownloader()

        ods_result = ods_downloader.download()

        if not ods_result:

            return {
                "status": "error",
                "message": "AGRIS ODS indisponible"
            }

        # =================================================
        # 2. PARSER LE CATALOGUE
        # =================================================

        if isinstance(
            ods_result,
            (str, Path)
        ):

            ods_parser = FAOODSParser(
                ods_result
            )

            dataset_documents = (
                ods_parser.parse()
            )

        elif isinstance(
            ods_result,
            dict
        ):

            return {
                "status": "error",
                "message": (
                    "FAOODSParser doit encore être "
                    "adapté au mode mémoire."
                )
            }

        else:

            return {
                "status": "error",
                "message": (
                    "Format catalogue AGRIS non reconnu."
                )
            }

        if not dataset_documents:

            return {
                "status": "warning",
                "message": (
                    "Aucun dataset trouvé "
                    "dans le catalogue AGRIS."
                )
            }

        # =================================================
        # 3. DOWNLOADER DATASETS
        # =================================================

        from app.knowledge_engine.connectors.fao_datasets import (
            FAODatasetsDownloader
        )

        from app.knowledge_engine.parsers.fao_dataset_parser import (
            FAODatasetParser
        )

        dataset_downloader = (
            FAODatasetsDownloader()
        )

        dataset_parser = (
            FAODatasetParser()
        )

        all_documents = []

        datasets_processed = 0

        # =================================================
        # 4. TRAITEMENT DIRECT EN MÉMOIRE
        # =================================================

        for dataset_document in (
            dataset_documents[:limit]
        ):

            try:

                url = str(
                    dataset_document.url
                ).strip()

                if not url:

                    continue

                filename = (
                    url
                    .rstrip("/")
                    .split("/")[-1]
                )

                if not filename:

                    filename = "dataset.xml"

                print(
                    "[FAO PIPELINE] "
                    f"Téléchargement : {filename}"
                )

                dataset = (
                    dataset_downloader.download(
                        url=url,
                        filename=filename
                    )
                )

                if not isinstance(
                    dataset,
                    dict
                ):

                    print(
                        "⚠️ Dataset ignoré : "
                        "format incorrect."
                    )

                    continue

                xml_content = dataset.get(
                    "content"
                )

                if not xml_content:

                    print(
                        "⚠️ Dataset vide : "
                        f"{filename}"
                    )

                    continue

                # -----------------------------------------
                # PARSING DIRECT DES BYTES XML
                # -----------------------------------------

                documents = (
                    dataset_parser.parse(
                        xml_content=xml_content,
                        filename=filename,
                        source_url=url
                    )
                )

                all_documents.extend(
                    documents
                )

                datasets_processed += 1

                print(
                    "✅ "
                    f"{len(documents)} document(s) "
                    f"extrait(s) de {filename}"
                )

            except Exception as e:

                print(
                    "❌ Erreur traitement dataset : "
                    f"{e}"
                )

        # =================================================
        # 5. VÉRIFICATION
        # =================================================

        if not all_documents:

            return {
                "status": "warning",
                "datasets": datasets_processed,
                "documents_parsed": 0,
                "documents_added": 0,
                "documents_total": 0
            }

        # =================================================
        # 6. DOCUMENT STORE
        # =================================================

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

        # =================================================
        # 7. RÉSULTAT
        # =================================================

        return {
            "status": "success",

            "datasets":
                datasets_processed,

            "documents_parsed":
                len(
                    all_documents
                ),

            "documents_added":
                store_result.get(
                    "added",
                    0
                ),

            "documents_total":
                store_result.get(
                    "total",
                    0
                ),

            "storage_file":
                store_result.get(
                    "file"
                )
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
