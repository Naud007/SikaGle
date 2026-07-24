from app.knowledge_engine.connectors.registry import registry

# importe les connecteurs
import app.knowledge_engine.connectors.fao


def run():

    print("=" * 50)
    print("SikaGlé Knowledge Engine")
    print("=" * 50)

    for connector_class in registry.all():

        connector = connector_class()

        documents = connector.discover()

        print(f"{connector.source_name} : {len(documents)} document(s)")


if __name__ == "__main__":
    run()
