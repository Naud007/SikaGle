"""
SikaGlé

Définition des niveaux d'alerte utilisés par la plateforme.
"""

from enum import Enum


class AlertLevel(str, Enum):
    """
    Niveaux de gravité des alertes.
    """

    INFO = "INFO"

    WARNING = "WARNING"

    ERROR = "ERROR"

    CRITICAL = "CRITICAL"
