"""
SikaGlé

Gestionnaire central des alertes de la plateforme.
"""

from app.core.logging import logger
from app.core.monitoring.alerts import Alert
from app.core.monitoring.alert_levels import AlertLevel


class AlertManager:
    """
    Gestionnaire central des alertes.

    Toutes les alertes de la plateforme passent par ce composant.
    """

    @staticmethod
    def send(alert: Alert) -> None:
        """
        Traite une alerte.

        Pour la V1, les alertes sont enregistrées dans les logs.
        """

        message = (
            f"[{alert.level}] "
            f"[{alert.source}] "
            f"{alert.message}"
        )

        if alert.level == AlertLevel.INFO:
            logger.info(message)

        elif alert.level == AlertLevel.WARNING:
            logger.warning(message)

        elif alert.level == AlertLevel.ERROR:
            logger.error(message)

        elif alert.level == AlertLevel.CRITICAL:
            logger.critical(message)

        else:
            logger.info(message)
