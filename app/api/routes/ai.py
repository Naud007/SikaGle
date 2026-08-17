from fastapi import APIRouter

from app.ai.gemini_client import (
    test_gemini,
    list_gemini_models,
)

from app.ai.embeddings import test_embedding
from app.ai.rag_service import test_rag


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.get("/gemini-test")
def gemini_test():
    return test_gemini()


@router.get("/models")
def gemini_models():
    return list_gemini_models()


@router.get("/embedding-test")
def embedding_test():
    return test_embedding()


@router.get("/rag-test")
def rag_test():
    return test_rag()