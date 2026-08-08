from app.knowledge_engine.connectors.registry import (
    registry,
)
from app.knowledge_engine.ingestion.global_ingestion_report import (
    GlobalIngestionReport,
)
from app.knowledge_engine.ingestion.ingestion_job import (
    IngestionJob,
)
from app.knowledge_engine.ingestion.source_ingestor import (
    SourceIngestor,
)


class IngestionManager:
    """
    Orchestre l'ingestion d'une ou plusieurs sources.
    """

    def __init__(self):

        self.ingestor = SourceIngestor()

    def ingest_source(
        self,
        source: str,
        limit: int = 5,
        offset: int = 0,
    ) -> IngestionJob:

        job = IngestionJob(
            source=source,
        )

        try:

            report = self.ingestor.ingest(
                source=source,
                limit=limit,
                offset=offset,
            )

            job.report = report

            job.finish()

        except Exception as exc:

            job.fail(
                str(exc)
            )

        return job

    def ingest_all(
        self,
    ) -> GlobalIngestionReport:

        report = GlobalIngestionReport()

        for source in registry.names():

            job = self.ingest_source(
                source
            )

            report.jobs.append(
                job
            )

        return report