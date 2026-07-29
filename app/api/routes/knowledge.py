from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.knowledge_service import KnowledgeService

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)

service = KnowledgeService()


class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        description="Question de l'utilisateur",
        min_length=3,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Nombre maximum de passages à récupérer",
    )


class DebugRequest(BaseModel):
    pdf_path: str = Field(
        ...,
        description="Chemin du fichier PDF à analyser",
    )


@router.post("/ingest-test")
def ingest_test():

    try:

        documents = service.discover("brab")

        if not documents:

            raise HTTPException(
                status_code=404,
                detail="Aucun document BRAB trouvé.",
            )

        document = documents[0]

        pdf_files = service.download_document(
            "brab",
            document,
        )

        if not pdf_files:

            raise HTTPException(
                status_code=404,
                detail="Aucun PDF téléchargé.",
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

        return result

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/debug")
def debug_pdf(
    request: DebugRequest,
):

    try:

        return service.debug_pdf(
            Path(request.pdf_path)
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/ask")
def ask(
    request: QuestionRequest,
):

    try:

        return service.ask(
            question=request.question,
            top_k=request.top_k,
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
