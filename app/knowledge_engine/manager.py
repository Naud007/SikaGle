from app.knowledge_engine.connectors.registry import registry

# Charge les connecteurs
import app.knowledge_engine.connectors.fao


def run():

    print("=" * 50)
    print("SikaGlé Knowledge Engine")
    print("=" * 50)

    for connector_class in registry.all():

        connector = connector_class()

        try:
            documents = connector.discover()

            print(
                f"{connector.source_name} : "
                f"{len(documents)} document(s) trouvé(s)"
            )

            for document in documents:

                print(f"Document : {document.title}")

                try:
                    file_path = connector.download(document)

                    if file_path and file_path.exists():
                        print(f"✅ Téléchargé : {file_path}")
                    else:
                        print("⚠️ Aucun fichier téléchargé.")

                except Exception as e:
                    print(
                        f"❌ Erreur téléchargement : {e}"
                    )

        except Exception as e:
            print(
                f"❌ Erreur connecteur "
                f"{connector.source_name} : {e}"
            )


if __name__ == "__main__":
    run()
