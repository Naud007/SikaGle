from fastapi import APIRouter
from pydantic import BaseModel

from app.ai.gemini_client import (
    test_gemini,
    list_gemini_models,
)

from app.ai.embeddings import test_embedding
from app.ai.rag_service import test_rag

from app.services.agricultural_assistant_service import (
    AgriculturalAssistantService,
)


# =========================================================
# ROUTER AI
# =========================================================

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


# =========================================================
# SERVICE ASSISTANT AGRICOLE
# =========================================================

assistant = AgriculturalAssistantService()


# =========================================================
# MODÈLE REQUÊTE CHAT
# =========================================================

class ChatRequest(BaseModel):

    user_id: str

    message: str

    language: str = "fr"

    channel: str = "api"


# =========================================================
# TEST GEMINI
# =========================================================

@router.get("/gemini-test")
def gemini_test():

    return test_gemini()


# =========================================================
# LISTE DES MODÈLES GEMINI
# =========================================================

@router.get("/models")
def gemini_models():

    return list_gemini_models()


# =========================================================
# TEST EMBEDDING
# =========================================================

@router.get("/embedding-test")
def embedding_test():

    return test_embedding()


# =========================================================
# TEST RAG
# =========================================================

@router.get("/rag-test")
def rag_test():

    return test_rag()


# =========================================================
# CHAT SIKAGLÉ
# =========================================================

@router.post("/chat")
def chat(
    request: ChatRequest,
):

    answer = assistant.process(
        user_id=request.user_id,
        message=request.message,
    )

    return {

        "status":
            "success",

        "user_id":
            request.user_id,

        "language":
            request.language,

        "channel":
            request.channel,

        "message":
            request.message,

        "answer":
            answer,
    }