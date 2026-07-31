from app.knowledge_engine.connectors.fao import FAOConnector


def test_connector_name():

    connector = FAOConnector()

    assert connector.name == "fao"


def test_connector_has_urls():

    connector = FAOConnector()

    assert connector.base_url.startswith("https://")

    assert connector.api_url.startswith("https://")


def test_connector_headers():

    connector = FAOConnector()

    assert "User-Agent" in connector.headers


def test_extract_uuid():

    connector = FAOConnector()

    class DummyDocument:

        url = "https://openknowledge.fao.org/items/123456"

    uuid = connector._extract_uuid(
        DummyDocument()
    )

    assert uuid == "123456"
