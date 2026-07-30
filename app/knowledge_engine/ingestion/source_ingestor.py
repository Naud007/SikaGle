from time import perf_counter

from app.knowledge_engine.connectors.registry import (
    registry,
)
from app.knowledge_engine.downloader import (
    Downloader,
)
from app.knowledge_engine.indexing import (
    KnowledgeIndexer,
)
from app.knowledge_engine.ingestion.ingestion_report import (
    IngestionReport,
)


class SourceIngestor:
    """
    Orchestre l'ingestion complète d'une source documentaire.
    """

    def __init__(self):

        self.downloader = Downloader()

        self.indexer = KnowledgeIndexer()

    def ingest(
        self,
        source: str,
    ) -> IngestionReport:

        report = IngestionReport(
            source=source,
        )

        started = perf_counter()

        connector = registry.get(source)

        documents = connector.discover()

        report.documents_found = len(
            documents
        )

        for document in documents:

            try:

                pdf_path = (
                    self.downloader.download(
                        document.url
                    )
                )

                report.downloaded += 1

                result = (
                    self.indexer.index_pdf(
                        pdf_path=pdf_path,
                        metadata=document.model_dump(),
                    )
                )

                if result["indexed"]:

                    report.indexed += 1

                    report.validated += 1

                else:

                    report.skipped += 1

                    for error in result.get(
                        "errors",
                        [],
                    ):

                        report.add_error(
                            error
                        )

                    for warning in result.get(
                        "warnings",
                        [],
                    ):

                        report.add_warning(
                            warning
                        )

            except Exception as exc:

                report.add_error(
                    str(exc)
                )

        report.duration_seconds = (
            perf_counter()
            - started
        )

        return report
