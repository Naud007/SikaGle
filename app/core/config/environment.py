"""
SikaGlé
Environment Loader

Responsabilité :
- Lire les variables d'environnement
- Fournir des méthodes sécurisées pour récupérer les valeurs
- Centraliser l'accès à os.environ
"""

from __future__ import annotations

import os
from typing import Any


class EnvironmentLoader:
    """
    Gestionnaire central des variables d'environnement.
    """

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Retourne une variable d'environnement.

        Exemple :
            EnvironmentLoader.get("APP_NAME")
        """
        return os.getenv(key, default)

    @staticmethod
    def get_required(key: str) -> str:
        """
        Retourne une variable obligatoire.

        Lève une exception si elle est absente.
        """
        value = os.getenv(key)

        if value is None or value == "":
            raise RuntimeError(
                f"La variable d'environnement '{key}' est obligatoire."
            )

        return value

    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        """
        Convertit automatiquement une variable en booléen.
        """

        value = os.getenv(key)

        if value is None:
            return default

        return value.lower() in (
            "true",
            "1",
            "yes",
            "y",
            "on",
        )

    @staticmethod
    def get_int(key: str, default: int = 0) -> int:
        """
        Convertit automatiquement une variable en entier.
        """

        value = os.getenv(key)

        if value is None:
            return default

        return int(value)

    @staticmethod
    def get_float(key: str, default: float = 0.0) -> float:
        """
        Convertit automatiquement une variable en nombre décimal.
        """

        value = os.getenv(key)

        if value is None:
            return default

        return float(value)
