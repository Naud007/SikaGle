from fastapi import APIRouter

from app.knowledge_engine.ingestion.oai_ingestion_worker import (
    OAIIngestionWorker,
)

router = APIRouter()


@router.get("/knowledge/oai-ingestion-status")
def oai_ingestion_status(
    source: str,
):
    try:

        worker = OAIIngestionWorker(
            source
        )

        state = worker.get_state()

        return {
            "status": "success",
            "source": source,
            "document_offset": state.get(
                "document_offset"
            ),
            "documents_processed": state.get(
                "documents_processed"
            ),
            "total_documents": state.get(
                "total_documents"
            ),
            "pipeline_status": state.get(
                "status"
            ),
            "last_error": state.get(
                "last_error"
            ),
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e),
        }


@router.get("/knowledge/oai-ingestion-batch")
def oai_ingestion_batch(
    source: str,
    rag_limit: int = 20,
):
    try:

        worker = OAIIngestionWorker(
            source
        )

        result = worker.run_batch(
            rag_limit=rag_limit
        )

        return result

    except Exception as e:

        return {
            "status": "error",
            "message": str(e),
        }