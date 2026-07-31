from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.connectors.registry import ConnectorRegistry
from app.schemas.document import DocumentMetadata


class DummyConnector(BaseConnector):

    def __init__(self):
        super().__init__("dummy")

    def discover(self) -> list[DocumentMetadata]:
        return []


def test_register_connector():

    registry = ConnectorRegistry()

    registry.register(
        "dummy",
        DummyConnector,
    )

    assert "dummy" in registry.names()


def test_get_connector():

    registry = ConnectorRegistry()

    registry.register(
        "dummy",
        DummyConnector,
    )

    connector = registry.get(
        "dummy",
    )

    assert isinstance(
        connector,
        DummyConnector,
    )


def test_all_connectors():

    registry = ConnectorRegistry()

    registry.register(
        "dummy",
        DummyConnector,
    )

    connectors = registry.all()

    assert len(connectors) == 1

    assert isinstance(
        connectors[0],
        DummyConnector,
    )
