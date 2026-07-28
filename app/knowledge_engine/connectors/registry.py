from typing import Type

from app.knowledge_engine.connectors.base import (
    BaseConnector,
)


class ConnectorRegistry:
    """
    Registre central des connecteurs du Knowledge Engine.
    """

    def __init__(self):

        self._connectors: dict[
            str,
            Type[BaseConnector],
        ] = {}

    def register(
        self,
        name: str,
        connector: Type[BaseConnector],
    ) -> None:
        """
        Enregistre un connecteur.
        """

        self._connectors[name] = connector

    def get(
        self,
        name: str,
    ) -> BaseConnector:
        """
        Retourne une instance du connecteur.
        """

        connector = self._connectors.get(
            name
        )

        if connector is None:

            raise ValueError(
                f"Connecteur '{name}' introuvable."
            )

        return connector()

    def all(
        self,
    ) -> list[BaseConnector]:
        """
        Retourne toutes les instances des connecteurs.
        """

        return [
            connector()
            for connector in self._connectors.values()
        ]

    def names(
        self,
    ) -> list[str]:
        """
        Retourne les noms des connecteurs.
        """

        return sorted(
            self._connectors.keys()
        )


registry = ConnectorRegistry()
