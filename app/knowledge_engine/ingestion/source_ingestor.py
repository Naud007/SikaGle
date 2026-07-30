from time import perf_counter

from app.knowledge_engine.connectors.registry import (
    registry,
)
from app.knowledge_engine.filesystem.path_manager import (
    PathManager,
)
from app.knowledge_engine.indexing import (
    KnowledgeIndexer,
)
from app.knowledge_engine.ingestion.ingestion_report import (
    IngestionReport,
)
from app.knowledge_engine.utils.downloader import (
    Downloader,
)


class SourceIngestor:
    """
    Orchestre l'ingestion complète d'une source documentaire.
    """

    def __init__(self):

        self.downloader = Downloader()

        self.indexer = KnowledgeIndexer()

        self.paths = PathManager()

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

                if not document.attachments:

                    report.skipped += 1

                    report.add_warning(
                        f"{document.title} : aucun PDF disponible."
                    )

                    continue

                attachment = document.attachments[0]

                pdf_path = self.paths.pdf_path(
                    source=document.source,
                    filename=attachment.filename,
                )

                # =====================================
                # Évite le re-téléchargement
                # =====================================

                if not pdf_path.exists():

                    self.downloader.download_file(
                        url=str(
                            attachment.url
                        ),
                        destination=pdf_path,
                    )

                    report.downloaded += 1

                else:

                    report.add_warning(
                        f"{attachment.filename} déjà présent sur le disque."
                    )

                result = self.indexer.index_pdf(
                    pdf_path=pdf_path,
                    metadata=document.model_dump(),
                )

                if result.get(
                    "validated",
                    False,
                ):
                    report.validated += 1

                if result.get(
                    "indexed",
                    False,
                ):
                    report.indexed += 1

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

                report.failed += 1

                report.add_error(
                    f"{document.title} : {exc}"
                )

        report.duration_seconds = (
            perf_counter()
            - started
        )

        return report
