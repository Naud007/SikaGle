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
    def total_duplicates(
        self,
    ) -> int:
        """
        Les documents ignorés correspondent
        principalement aux doublons déjà indexés.
        """

        return self.total_skipped

    @property
    def duration_seconds(
        self,
    ) -> float:

        return sum(
            job.duration_seconds
            for job in self.jobs
        )

    @property
    def success_rate(
        self,
    ) -> float:

        total = self.total_documents

        if total == 0:
            return 100.0

        success = (
            total
            - self.total_failed
        )

        return round(
            success * 100 / total,
            2,
        )

    @property
    def average_documents_per_source(
        self,
    ) -> float:

        if self.total_sources == 0:
            return 0.0

        return round(
            self.total_documents
            / self.total_sources,
            2,
        )

    @property
    def average_duration_per_source(
        self,
    ) -> float:

        if self.total_sources == 0:
            return 0.0

        return round(
            self.duration_seconds
            / self.total_sources,
            2,
        )

    @property
    def documents_per_second(
        self,
    ) -> float:

        if self.duration_seconds == 0:
            return 0.0

        return round(
            self.total_documents
            / self.duration_seconds,
            2,
        )

    @property
    def downloads_saved(
        self,
    ) -> int:
        """
        Documents non téléchargés grâce
        au cache local.
        """

        return max(
            self.total_documents
            - self.total_downloaded,
            0,
        )

    def to_dict(
        self,
    ) -> dict:

        return {

            "sources": self.total_sources,

            "documents_found": self.total_documents,

            "downloaded": self.total_downloaded,

            "downloads_saved": self.downloads_saved,

            "validated": self.total_validated,

            "indexed": self.total_indexed,

            "duplicates": self.total_duplicates,

            "skipped": self.total_skipped,

            "failed": self.total_failed,

            "success_rate": self.success_rate,

            "average_documents_per_source":
                self.average_documents_per_source,

            "average_duration_per_source":
                self.average_duration_per_source,

            "documents_per_second":
                self.documents_per_second,

            "duration_seconds":
                round(
                    self.duration_seconds,
                    2,
                ),

            "jobs": [
                job.to_dict()
                for job in self.jobs
            ],
        }
