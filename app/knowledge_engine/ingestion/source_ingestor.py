from time import perf_counter

from app.knowledge_engine.connectors.registry import (
    registry,
)
from app.knowledge_engine.filesystem.path_manager import (
    PathManager,
)
from app.knowledge_engine.filters import (
    AgriculturalRelevanceFilter,
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

        self.relevance_filter = (
            AgriculturalRelevanceFilter()
        )

    def ingest(
        self,
        source: str,
        limit: int | None = 5,
        offset: int = 0,
    ) -> IngestionReport:

        if limit is not None and limit <= 0:

            raise ValueError(
                "limit doit être supérieur à 0."
            )

        if offset < 0:

            raise ValueError(
                "offset ne peut pas être négatif."
            )

        report = IngestionReport(
            source=source,
        )

        started = perf_counter()

        connector = registry.get(
            source
        )

        all_documents = connector.discover()

        total_documents = len(
            all_documents
        )

        # =====================================================
        # SÉLECTION DES DOCUMENTS
        # =====================================================

        if limit is None:

            documents = all_documents[
                offset:
            ]

        else:

            documents = all_documents[
                offset:
                offset + limit
            ]

        report.documents_found = len(
            documents
        )

        print(
            f"[INGESTION] Source : {source}"
        )

        print(
            f"[INGESTION] Total disponible : "
            f"{total_documents}"
        )

        print(
            f"[INGESTION] Offset : {offset}"
        )

        if limit is None:

            print(
                "[INGESTION] Mode : TOUS LES DOCUMENTS"
            )

        else:

            print(
                f"[INGESTION] Limite : {limit}"
            )

        print(
            f"[INGESTION] Batch : "
            f"{len(documents)}"
        )

        # =====================================================
        # TRAITEMENT
        # =====================================================

        for document in documents:

            try:

                # =============================================
                # FILTRE DE PERTINENCE AGRICOLE
                # =============================================

                relevance = (
                    self.relevance_filter.analyze(
                        document.model_dump()
                    )
                )

                print(
                    "[RELEVANCE] "
                    f"{document.title} : "
                    f"{relevance.relevant} "
                    f"(score={relevance.score:.3f})"
                )

                if not relevance.relevant:

                    report.filtered_out += 1

                    report.add_warning(
                        f"{document.title} : "
                        f"document hors domaine agricole. "
                        f"{relevance.reason}"
                    )

                    print(
                        "⏭️ Document filtré : "
                        f"{document.title}"
                    )

                    continue

                # =============================================
                # PDF DISPONIBLE ?
                # =============================================

                if not document.attachments:

                    report.skipped += 1

                    report.add_warning(
                        f"{document.title} : "
                        "aucun PDF disponible."
                    )

                    continue

                attachment = (
                    document.attachments[0]
                )

                print(
                    "PDF URL =",
                    attachment.url,
                )

                # =============================================
                # CHEMIN LOCAL
                # =============================================

                pdf_path = (
                    self.paths.pdf_path(
                        source=document.source,
                        filename=attachment.filename,
                    )
                )

                # =============================================
                # TÉLÉCHARGEMENT
                # =============================================

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
                        f"{attachment.filename} "
                        "déjà présent sur le disque."
                    )

                # =============================================
                # INDEXATION
                # =============================================

                result = (
                    self.indexer.index_pdf(
                        pdf_path=pdf_path,
                        metadata=document.model_dump(),
                    )
                )

                print(
                    "INDEX RESULT =",
                    result,
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

                # =============================================
                # ERREURS
                # =============================================

                for error in result.get(
                    "errors",
                    [],
                ):

                    report.add_error(
                        error
                    )

                # =============================================
                # AVERTISSEMENTS
                # =============================================

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

        # =====================================================
        # DURÉE
        # =====================================================

        report.duration_seconds = (
            perf_counter()
            - started
        )

        return report