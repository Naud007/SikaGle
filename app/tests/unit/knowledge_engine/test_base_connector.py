from pathlib import Path

from app.knowledge_engine.connectors.base import BaseConnector
from app.schemas.document import DocumentMetadata


class DummyConnector(BaseConnector):
    """
    Connecteur fictif utilisé pour les tests.
    """

    def __init__(self):
        super().__init__("dummy")

    def discover(self) -> list[DocumentMetadata]:
        return []


def test_connector_name():
    connector = DummyConnector()

    assert connector.name == "dummy"


def test_download_root_exists():
    connector = DummyConnector()

    assert isinstance(
        connector.DOWNLOAD_ROOT,
        Path,
    )


def test_logger_created():
    connector = DummyConnector()

    assert connector.logger is not None


def test_discover_returns_list():
    connector = DummyConnector()

    documents = connector.discover()

    assert isinstance(
        documents,
        list,
    )
