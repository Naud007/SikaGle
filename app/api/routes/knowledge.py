from fastapi import APIRouter, HTTPException

from app.services.knowledge_service import KnowledgeService

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)

service = KnowledgeService()


@router.post("/ingest-test")
def ingest_test():
    """
    Pipeline complet :
    Découverte -> Téléchargement -> Extraction -> Chunking
    """

    try:

        document = service.discover("brab")[0]

        pdf_files = service.download_document(
            "brab",
            document,
        )

        if not pdf_files:
            raise Exception(
                "Aucun PDF téléchargé."
            )

        result = service.process_pdf(
            pdf_files[0]
        )

        return {
            "status": "success",
            "title": document.title,
            "source": document.source,
            "pdf": str(pdf_files[0]),
            "txt": str(result["txt_path"]),
            "characters": result["characters"],
            "chunks": result["chunks_count"],
            "preview": (
                result["chunks"][0][:500]
                if result["chunks"]
                else ""
            ),
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
