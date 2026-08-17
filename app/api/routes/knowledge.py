from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.knowledge_engine.resolvers import OJSPDFResolver
from app.services.knowledge_service import KnowledgeService


router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)

service = KnowledgeService()

resolver = OJSPDFResolver()


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


# ==========================================================
# CHROMA
# ==========================================================

@router.get("/chroma-debug")
def chroma_debug():

    repo = (
        service
        .rag
        .retriever
        .vector
        .repository
    )

    return {
        "count": repo.count(),
        "store": type(repo.vectorstore).__name__,
    }

@router.get("/count")
def count_documents():

    return {
        "documents": (
            service
            .rag
            .retriever
            .vector
            .repository
            .count()
        )
    }


# ==========================================================
# SOURCES
# ==========================================================

@router.get("/sources")
def available_sources():

    return {
        "sources": service.available_sources()
    }


# ==========================================================
# INGESTION
# ==========================================================

@router.post("/ingest/all")
def ingest_all():

    try:

        report = service.ingest_all()

        return report.to_dict()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/ingest/{source}")
def ingest_source(
    source: str,
    all: bool = Query(
        default=False,
        description=(
            "Traiter automatiquement tous les "
            "documents disponibles."
        ),
    ),
    limit: int = Query(
        default=5,
        ge=1,
        le=20,
        description=(
            "Nombre de documents à traiter "
            "dans ce batch lorsque all=false."
        ),
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description=(
            "Position du premier document "
            "à traiter lorsque all=false."
        ),
    ),
):

    try:

        if (
            source
            not in service.available_sources()
        ):

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Source '{source}' inconnue."
                ),
            )

        job = service.ingest_source(
            source=source,
            limit=None if all else limit,
            offset=0 if all else offset,
        )

        return job.to_dict()

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ==========================================================
# DEBUG
# ==========================================================

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


@router.post("/debug/brab")
def debug_brab():

    try:

        documents = service.discover(
            "brab"
        )

        if not documents:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Aucun document trouvé."
                ),
            )

        document = documents[0]

        pdf_files = service.download_document(
            "brab",
            document,
        )

        if not pdf_files:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Aucun PDF téléchargé."
                ),
            )

        report = service.debug_pdf(
            pdf_files[0]
        )

        resolver_debug = resolver.inspect(
            str(document.url)
        )

        report.update(
            {
                "title": document.title,
                "source": document.source,
                "document_url": str(
                    document.url
                ),
                "attachments": [
                    {
                        "filename": (
                            attachment.filename
                        ),
                        "url": str(
                            attachment.url
                        ),
                    }
                    for attachment
                    in document.attachments
                ],
                "resolver": resolver_debug,
            }
        )

        return report

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ==========================================================
# QUESTIONS / RAG
# ==========================================================

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