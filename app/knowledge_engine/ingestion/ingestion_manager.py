from app.knowledge_engine.connectors.registry import (
    registry,
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
    ) -> IngestionJob:

        job = IngestionJob(source=source)

        try:

            report = self.ingestor.ingest(
                source
            )

            job.report = report

            job.finish()

        except Exception as exc:

            job.fail(str(exc))

        return job

    def ingest_all(
        self,
    ) -> list[IngestionJob]:

        jobs = []

        for source in registry.names():

            jobs.append(
                self.ingest_source(source)
            )

        return jobs
