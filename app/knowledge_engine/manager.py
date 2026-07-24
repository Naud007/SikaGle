from app.knowledge_engine.connectors.registry import registry

# Charger les connecteurs
import app.knowledge_engine.connectors.fao


def run():
    """
    Lance le Knowledge Engine et exécute
    tous les connecteurs enregistrés.
    """

    print("=" * 50)
    print("SikaGlé Knowledge Engine")
    print("=" * 50)

    for connector_class in registry.all():

        connector = connector_class()

        try:
            # Recherche des documents
            documents = connector.discover()

            print(
                f"{connector.source_name} : "
                f"{len(documents)} document(s) trouvé(s)"
            )

            # Téléchargement des documents
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


def test_fao_ods():
    """
    Teste le téléchargement du catalogue
    principal AGRIS ODS.
    """

    print("=" * 50)
    print("SikaGlé - Test FAO AGRIS")
    print("=" * 50)

    try:
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


def test_fao_datasets():
    """
    Télécharge et teste les 10 premiers
    datasets AGRIS trouvés dans le catalogue.
    """

    print("=" * 50)
    print("SikaGlé - Téléchargement des datasets FAO AGRIS")
    print("=" * 50)

    try:
        from app.knowledge_engine.connectors.fao_ods import (
            FAOODSDownloader
        )

        from app.knowledge_engine.parsers.fao_ods_parser import (
            FAOODSParser
        )

        from app.knowledge_engine.connectors.fao_datasets import (
            FAODatasetsDownloader
        )

        # -------------------------------------------------
        # 1. Télécharger le catalogue principal AGRIS
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
        # 2. Parser le catalogue AGRIS
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
        # 3. Initialiser le downloader des datasets
        # -------------------------------------------------

        dataset_downloader = FAODatasetsDownloader()

        downloaded_files = []

        # -------------------------------------------------
        # 4. Télécharger les 10 premiers datasets
        # -------------------------------------------------

        for document in documents[:10]:

            try:
                # document.url est un objet Pydantic Url.
                # Conversion obligatoire en chaîne.
                url = str(
                    document.url
                )

                # Récupération du nom du fichier
                filename = url.split(
                    "/"
                )[-1]

                print(
                    f"\n[FAO DATASET] "
                    f"Téléchargement : {filename}"
                )

                print(
                    f"[FAO DATASET] URL : {url}"
                )

                # Téléchargement
                file_path = dataset_downloader.download(
                    url,
                    filename
                )

                if file_path:

                    downloaded_files.append(
                        str(file_path)
                    )

                    print(
                        f"✅ Dataset téléchargé : "
                        f"{file_path}"
                    )

                else:

                    print(
                        "⚠️ Aucun fichier téléchargé."
                    )

            except Exception as e:

                print(
                    f"❌ Erreur téléchargement "
                    f"{document.url} : {e}"
                )

        # -------------------------------------------------
        # 5. Résultat final
        # -------------------------------------------------

        print("=" * 50)

        print(
            f"✅ Téléchargement terminé : "
            f"{len(downloaded_files)} fichier(s)"
        )

        print("=" * 50)

        return {
            "status": "success",
            "total_datasets": len(documents),
            "downloaded": len(downloaded_files),
            "files": downloaded_files
        }

    except Exception as e:

        print(
            f"❌ Erreur datasets FAO : {e}"
        )

        return {
            "status": "error",
            "message": str(e)
        }


def test_fao_parser():
    """
    Teste le téléchargement et le parsing
    du catalogue principal AGRIS.
    """

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

        # 1. Télécharger le fichier AGRIS
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

        # 2. Parser le fichier XML
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

        # 3. Afficher les 10 premières notices
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
            "documents": len(documents)
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


if __name__ == "__main__":
    run()
