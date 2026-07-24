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

    print("=" * 50)

    print(
        "SikaGlé - Test FAO AGRIS"
    )

    print("=" * 50)

    try:

        # Import local pour éviter les problèmes
        # de chargement au démarrage de l'API
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

        else:

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


if __name__ == "__main__":

    run()
