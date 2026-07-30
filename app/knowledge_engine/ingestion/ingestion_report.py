from dataclasses import dataclass, field


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

    failed: int = 0

    duration_seconds: float = 0.0

    errors: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)

    def add_error(
        self,
        message: str,
    ) -> None:
        self.failed += 1
        self.errors.append(message)

    def add_warning(
        self,
        message: str,
    ) -> None:
        self.warnings.append(message)

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "documents_found": self.documents_found,
            "downloaded": self.downloaded,
            "validated": self.validated,
            "indexed": self.indexed,
            "skipped": self.skipped,
            "failed": self.failed,
            "duration_seconds": self.duration_seconds,
            "errors": self.errors,
            "warnings": self.warnings,
        }
