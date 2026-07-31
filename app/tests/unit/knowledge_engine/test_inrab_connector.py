from app.knowledge_engine.connectors.inrab import INRABConnector


def test_connector_name():

    connector = INRABConnector()

    assert connector.name == "inrab"


def test_connector_has_crawler():

    connector = INRABConnector()

    assert connector.crawler is not None


def test_connector_has_normalizer():

    connector = INRABConnector()

    assert connector.normalizer is not None
