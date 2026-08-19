from fastapi import APIRouter

from app.knowledge_engine.ingestion.fao_ingestion_worker import (
    FAOIngestionWorker,
)

router = APIRouter()


@router.get("/knowledge/fao-dataset-pipeline-test")
def fao_dataset_pipeline_test(
    dataset_limit: int = 1,
    rag_limit: int = 3,
):
    try:
        worker = FAOIngestionWorker()

        return worker.run_batch(
            dataset_limit=dataset_limit,
            rag_limit=rag_limit,
        )

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


@router.get("/knowledge/fao-dataset-pipeline-auto")
def fao_dataset_pipeline_auto(
    rag_limit: int = 20,
    max_batches: int = 1,
):
    if rag_limit <= 0:
        return {
            "status": "error",
            "message": "rag_limit doit être supérieur à 0.",
        }

    if max_batches != 1:
        return {
            "status": "error",
            "message": (
                "Cette route exécute un seul batch "
                "à la fois. Le watcher PowerShell "
                "lance automatiquement le suivant."
            ),
        }

    try:
        worker = FAOIngestionWorker()

        result = worker.run_batch(
            dataset_limit=1,
            rag_limit=rag_limit,
        )

        return {
            "status": "success",
            "message": (
                "Batch FAO terminé. "
                "La progression est sauvegardée."
            ),
            "rag_limit": rag_limit,
            "max_batches": 1,
            "result": result,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


@router.get("/knowledge/fao-dataset-status")
def fao_dataset_status():
    try:
        worker = FAOIngestionWorker()
        state = worker.get_state()

        return {
            "status": "success",
            "pipeline_name": worker.PIPELINE_NAME,
            "dataset_offset": state.get("dataset_offset"),
            "document_offset": state.get("document_offset"),
            "documents_processed": state.get("documents_processed"),
            "datasets_completed": state.get("datasets_completed"),
            "pipeline_status": state.get("status"),
            "last_error": state.get("last_error"),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }