import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from app.knowledge_engine.filesystem.path_manager import (
    PathManager,
)


@dataclass
class IngestionReport:
    """
    Rapport d'exécution d'une ingestion.
    """

    source: str

    documents_found: int = 0

    downloaded: int = 0

    validated: int = 0

    indexed: int = 0

    skipped: int = 0

    filtered_out: int = 0

    failed: int = 0

    duration_seconds: float = 0.0

    errors: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )

    def add_error(
        self,
        message: str,
    ) -> None:
        """
        Enregistre une erreur.

        Le compteur failed est géré par le niveau
        d'orchestration qui connaît le document réellement
        en échec. Cela évite un double comptage.
        """

        self.errors.append(
            message
        )

    def add_warning(
        self,
        message: str,
    ) -> None:

        self.warnings.append(
            message
        )

    def to_dict(
        self,
    ) -> dict:

        return {

            "source":
                self.source,

            "documents_found":
                self.documents_found,

            "downloaded":
                self.downloaded,

            "validated":
                self.validated,

            "indexed":
                self.indexed,

            "skipped":
                self.skipped,

            "filtered_out":
                self.filtered_out,

            "failed":
                self.failed,

            "duration_seconds":
                round(
                    self.duration_seconds,
                    2,
                ),

            "errors":
                self.errors,

            "warnings":
                self.warnings,
        }

    def save(
        self,
    ) -> Path:
        """
        Sauvegarde le rapport d'ingestion au format JSON.
        """

        paths = PathManager()

        log_directory = (
            paths.logs_directory()
            / "ingestion"
        )

        log_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = (
            datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S"
            )
        )

        log_file = (
            log_directory
            / f"{timestamp}_{self.source}.json"
        )

        with open(
            log_file,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                self.to_dict(),
                f,
                ensure_ascii=False,
                indent=4,
            )

        return log_file