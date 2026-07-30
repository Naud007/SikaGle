from dataclasses import dataclass, field

from app.knowledge_engine.ingestion.ingestion_job import (
    IngestionJob,
)


@dataclass
class GlobalIngestionReport:
    """
    Rapport global d'une ingestion multi-sources.
    """

    jobs: list[IngestionJob] = field(
        default_factory=list
    )

    @property
    def total_sources(
        self,
    ) -> int:

        return len(self.jobs)

    @property
    def total_documents(
        self,
    ) -> int:

        return sum(
            job.report.documents_found
            for job in self.jobs
            if job.report
        )

    @property
    def total_downloaded(
        self,
    ) -> int:

        return sum(
            job.report.downloaded
            for job in self.jobs
            if job.report
        )

    @property
    def total_validated(
        self,
    ) -> int:

        return sum(
            job.report.validated
            for job in self.jobs
            if job.report
        )

    @property
    def total_indexed(
        self,
    ) -> int:

        return sum(
            job.report.indexed
            for job in self.jobs
            if job.report
        )

    @property
    def total_skipped(
        self,
    ) -> int:

        return sum(
            job.report.skipped
            for job in self.jobs
            if job.report
        )

    @property
    def total_failed(
        self,
    ) -> int:

        return sum(
            job.report.failed
            for job in self.jobs
            if job.report
        )

    @property
    def duration_seconds(
        self,
    ) -> float:

        return sum(
            job.duration_seconds
            for job in self.jobs
        )

    def to_dict(
        self,
    ) -> dict:

        return {

            "sources": self.total_sources,

            "documents_found": self.total_documents,

            "downloaded": self.total_downloaded,

            "validated": self.total_validated,

            "indexed": self.total_indexed,

            "skipped": self.total_skipped,

            "failed": self.total_failed,

            "duration_seconds": self.duration_seconds,

            "jobs": [
                job.to_dict()
                for job in self.jobs
            ],
        }
