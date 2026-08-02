"""
SikaGlé

Rapport de maintenance de la plateforme.
"""

from dataclasses import dataclass


@dataclass
class MaintenanceReport:
    """
    Représente l'état général de maintenance
    de la plateforme.
    """

    version: str

    environment: str

    healthy: bool

    monitoring_enabled: bool

    backups_enabled: bool

    security_enabled: bool
