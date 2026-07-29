from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.knowledge_service import KnowledgeService

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)

service = KnowledgeService()


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 5


@router.post("/ingest-test")
def ingest_test():

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

        return result

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

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
