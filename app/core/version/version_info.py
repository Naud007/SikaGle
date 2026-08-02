"""
SikaGlé

Informations de version de la plateforme.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class VersionInfo:
    """
    Informations de version.
    """

    name: str

    version: str

    codename: str

    stage: str
