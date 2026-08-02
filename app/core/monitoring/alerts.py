"""
SikaGlé

Modèle représentant une alerte système.
"""

from dataclasses import dataclass
from datetime import datetime

from app.core.monitoring.alert_levels import AlertLevel


@dataclass
class Alert:
    """
    Représente une alerte émise par la plateforme.
    """

    level: AlertLevel

    source: str

    message: str

    timestamp: datetime = datetime.utcnow()
