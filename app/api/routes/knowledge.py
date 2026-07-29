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
    Découverte → Téléchargement → Extraction →
    Chunking → Embedding → ChromaDB
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

        result = service.index_pdf(
            pdf_files[0],
            metadata={
                "title": document.title,
                "source": document.source,
                "url": str(document.url),
                "author": document.author,
                "published_at": (
                    str(document.published_at)
                    if document.published_at
                    else None
                ),
            },
        )

        return {
            "status": "success",
            "title": document.title,
            "source": document.source,
            "url": str(document.url),
            "indexed_chunks": result["indexed"],
            "collection_size": result["collection_size"],
            "characters": result["characters"],
            "txt": str(result["txt_path"]),
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
