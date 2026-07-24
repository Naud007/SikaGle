from typing import Type

from app.knowledge_engine.connectors.base import BaseConnector


class ConnectorRegistry:
    """
    Registre central des connecteurs du Knowledge Engine.
    """

    def __init__(self):
        self._connectors: dict[str, Type[BaseConnector]] = {}

    def register(self, name: str, connector: Type[BaseConnector]):
        """
        Enregistre un connecteur.
        """
        self._connectors[name] = connector

    def get(self, name: str):
        """
        Retourne un connecteur par son nom.
        """
        return self._connectors.get(name)

    def all(self):
        """
        Retourne tous les connecteurs enregistrés.
        """
        return self._connectors.values()

    def names(self):
        """
        Retourne la liste des sources disponibles.
        """
        return list(self._connectors.keys())


registry = ConnectorRegistry()
