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

    try:

        documents = service.discover(
            source="brab",
        )

        if not documents:

            raise HTTPException(
                status_code=404,
                detail="Aucun document trouvé.",
            )

        document = documents[0]

        if not document.attachments:

            raise HTTPException(
                status_code=404,
                detail="Aucune pièce jointe disponible.",
            )

        path = service.download_attachment(
            source="brab",
            attachment=document.attachments[0],
        )

        return {
            "title": document.title,
            "source": document.source,
            "article_url": str(document.url),
            "attachment": document.attachments[0],
            "saved_to": str(path),
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/process")
def process_pdf(
    pdf_path: str,
):

    try:

        output = service.process_pdf(
            Path(pdf_path),
        )

        return {
            "status": "success",
            "txt_file": str(output),
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
