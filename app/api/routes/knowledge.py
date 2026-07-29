from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.services.knowledge_service import KnowledgeService

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)

service = KnowledgeService()


@router.get("/test-download")
def test_download():
    """
    Télécharge un document BRAB de test.
    """

    try:
        document = service.discover("brab")[0]

        saved_files = service.download_document(
            "brab",
            document,
        )

        return {
            "title": document.title,
            "source": document.source,
            "article_url": document.article_url,
            "attachment": (
                document.attachments[0].model_dump()
                if document.attachments
                else None
            ),
            "saved_to": (
                str(saved_files[0])
                if saved_files
                else None
            ),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/process")
def process_pdf(pdf_path: str):

    try:

        result = service.process_pdf(
            Path(pdf_path)
        )

        return {
            "status": "success",
            "txt_file": str(
                result["txt_path"]
            ),
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
