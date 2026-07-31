from app.knowledge_engine.connectors.brab import BRABConnector


def test_connector_name():

    connector = BRABConnector()

    assert connector.name == "brab"


def test_connector_has_client():

    connector = BRABConnector()

    assert connector.client is not None


def test_connector_has_parser():

    connector = BRABConnector()

    assert connector.parser is not None


def test_connector_has_normalizer():

    connector = BRABConnector()

    assert connector.normalizer is not None
