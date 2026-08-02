"""
SikaGlé

Rapport d'exécution d'une sauvegarde.
"""

from dataclasses import dataclass, field
from datetime import datetime

from app.core.backup.backup_type import BackupType


@dataclass
class BackupReport:
    """
    Résultat d'une opération de sauvegarde.
    """

    backup_type: BackupType

    success: bool

    message: str

    started_at: datetime

    finished_at: datetime = field(
        default_factory=datetime.utcnow
    )
