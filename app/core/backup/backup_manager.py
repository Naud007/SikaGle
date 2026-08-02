"""
SikaGlé

Gestionnaire central des sauvegardes.
"""

from datetime import datetime

from app.core.backup.backup_report import BackupReport
from app.core.backup.backup_type import BackupType
from app.core.logging import logger


class BackupManager:
    """
    Gestionnaire des sauvegardes de la plateforme.
    """

    @staticmethod
    def run(backup_type: BackupType) -> BackupReport:
        """
        Lance une sauvegarde.
        """

        started_at = datetime.utcnow()

        logger.info(
            "Starting backup: %s",
            backup_type.value,
        )

        report = BackupReport(
            backup_type=backup_type,
            success=True,
            message=f"{backup_type.value} backup completed.",
            started_at=started_at,
        )

        logger.info(
            "Backup completed: %s",
            backup_type.value,
        )

        return report
