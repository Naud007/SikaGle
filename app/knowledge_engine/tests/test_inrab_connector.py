from app.knowledge_engine.connectors.inrab import INRABConnector


def test_inrab_connector():

    connector = INRABConnector()

    documents = connector.discover()

    print(f"{len(documents)} document(s) trouvé(s)")

    for document in documents[:5]:
        print("-" * 50)
        print(document.title)
        print(document.url)
