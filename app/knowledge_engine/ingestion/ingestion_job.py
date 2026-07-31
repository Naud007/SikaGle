from dataclasses import dataclass, field
from datetime import datetime

from app.knowledge_engine.ingestion.ingestion_report import (
    IngestionReport,
)


@dataclass
class IngestionJob:
    """
    Représente une exécution complète d'une ingestion.
    """

    source: str

    started_at: datetime = field(
        default_factory=datetime.utcnow
    )

    finished_at: datetime | None = None

    status: str = "RUNNING"

    report: IngestionReport | None = None

    def finish(self) -> None:
        """
        Termine le job.
        """

        self.finished_at = datetime.utcnow()

        self.status = "COMPLETED"

    def fail(
        self,
        reason: str | None = None,
    ) -> None:
        """
        Marque le job comme échoué.
        """

        self.finished_at = datetime.utcnow()

        self.status = "FAILED"

    @property
    def duration_seconds(self) -> float:
        """
        Durée totale du job.
        """

        end = self.finished_at or datetime.utcnow()

        return (end - self.started_at).total_seconds()

    def to_dict(self) -> dict:

        return {
            "source": self.source,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "finished_at": (
                self.finished_at.isoformat()
                if self.finished_at
                else None
            ),
            "duration_seconds": self.duration_seconds,
            "report": (
                self.report.to_dict()
                if self.report
                else None
            ),
        }
